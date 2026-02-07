from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum

class HandlingStatus(Enum):
    HANDLED = "HANDLED"
    UNHANDLED = "UNHANDLED"
    AMBIGUOUS = "AMBIGUOUS"

@dataclass
class LogEvent:
    timestamp: datetime
    level: str
    message: str
    job_id: str
    process_name: str
    activity: Optional[str]
    fingerprint: Optional[str]
    raw: dict
    
@dataclass
class ErrorEvent:
    error_id:str
    timestamp: datetime
    message: str
    activity: Optional[str]
    fingerprint: Optional[str]
    raw_event: LogEvent
    handling_status: HandlingStatus = None

@dataclass
class ExecutionSegment:
    segment_id: str
    job_id: str
    phase: str
    start_time: datetime
    end_time: Optional[datetime]
    events: list[LogEvent]

@dataclass
class AIReasonerInput:
    error: ErrorEvent
    handling_status: HandlingStatus
    process_name: str
    job_id: str