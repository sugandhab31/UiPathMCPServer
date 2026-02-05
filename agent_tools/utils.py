from datetime import datetime
import json, re
import uuid
from typing import Optional
from schema.models import *

def normalize_logs(raw_logs: list[dict]) -> list[LogEvent]:
    events = []

    for log in raw_logs:
        raw_msg = json.loads(log["RawMessage"])
        # print(log["Message"])
        events.append(
            LogEvent(
                timestamp=datetime.fromisoformat(raw_msg["timeStamp"].replace("Z","+00:00")),
                level=log["Level"],
                message=log["Message"],
                job_id=log["JobKey"],
                process_name=log["ProcessName"],
                activity=raw_msg.get("fileName"),
                fingerprint=raw_msg.get("fingerprint")
            )            
        )

    return sorted(events, key=lambda e: e.timestamp)

def segment_execution(events: list[LogEvent]) -> list[ExecutionSegment]:
    segments = []
    current_segment = None

    def start_segment(phase, event):
        return ExecutionSegment(
            segment_id=str(uuid.uuid4()),
            job_id=event.job_id,
            phase=phase,
            start_time=event.timestamp,
            end_time=None,
            events=[event]
        )

    for event in events:
        msg = event.message.lower()

        if "execution started" in msg:
            current_segment = start_segment("INIT", event)
            segments.append(current_segment)

        elif "execution ended" in msg:
            if current_segment:
                current_segment.events.append(event)
                current_segment.end_time = event.timestamp
                current_segment = None

        else:
            if not current_segment:
                current_segment = start_segment("EXECUTION", event)
                segments.append(current_segment)
            else:
                current_segment.events.append(event)

    return segments

def extract_error_events(segments: list[ExecutionSegment]) -> list[ErrorEvent]:
    errors = []

    for segment in segments:
        for event in segment.events:
            if event.level.lower() == "error":
                errors.append(
                    ErrorEvent(
                        error_id=str(uuid.uuid4()),
                        segment_id=segment.segment_id,
                        timestamp=event.timestamp,
                        activity=event.activity,
                        message=event.message,
                        exception_type=extract_exception_type(event.message),
                        fingerprint=event.fingerprint,
                        raw_event=event
                    )
                )

    return errors

def extract_exception_type(message: str) -> Optional[str]:
    if "could not find the user-interface" in message.lower():
        return "UI_ELEMENT_NOT_FOUND"
    if "timeout" in message.lower():
        return "TIMEOUT"
    if "nullreference" in message.lower():
        return "NULL_REFERENCE"
    return None

def detect_job_end_state(events: list[LogEvent]) -> str:
    messages = [e.message.lower() for e in events]

    if any("execution ended" in m for m in messages):
        if any(e.level.lower() == "error" for e in events):
            return "UNKNOWN"    #Logs contain mixed signals (very common in UiPath)
        return "SUCCESS"   #Job ran to completion with no errors
    
    if any(e.level.lower() == "error" for e in events):
        return "FAULTED"        #Job shows errors and no clean end signal
    return "UNKNOWN"       #Logs contain mixed signals (very common in UiPath)


def execution_continued_after_error(
        error: ErrorEvent,
        events: list[LogEvent]
) -> bool:
    """
    Returns True if meaningful execution happened after the error.
    """
    for event in events:
        if event.timestamp > error.timestamp:
            if event.level.lower() == "info":
                if "execution ended" not in event.message.lower():
                    return True

    return False

def classify_error_handling(
        errors: list[ErrorEvent],
        events: list[LogEvent]
) -> dict[str, HandingStatus]:
    """
    Returns:
    { error_id: HandlingStatus }
    """
    job_state = detect_job_end_state(events)
    results = {}

    for error in errors:
        continued = execution_continued_after_error(error, events)

        if job_state == "FAULTED":
            results[error.error_id] = HandingStatus.UNHANDLED
        elif job_state == "SUCCESS" and continued:
            results[error.error_id] = HandingStatus.HANDLED
        elif job_state == "UNKNOWN":
            if continued:
                results[error.error_id] = HandingStatus.AMBIGUOUS
            else:
                results[error.error_id] = HandingStatus.UNHANDLED
        else:
            results[error.error_id] = HandingStatus.AMBIGUOUS