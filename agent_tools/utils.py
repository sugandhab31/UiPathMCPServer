from datetime import datetime
import json
from schema.models import LogEvent

def normalize_logs(raw_logs: list[dict]) -> list[LogEvent]:
    events = []

    for log in raw_logs:
        raw_msg = json.loads(log["RawMessage"])

        events.append(
            LogEvent(
                timestamp=datetime.fromisoformat(raw_msg["timeStamp"].replace("Z","+00:00")),
                level=log["level"],
                message=log["Message"],
                job_id=log["JobKey"],
                process_name=log["ProcessName"],
                activity=raw_msg.get("fileName"),
                fingerprint=raw_msg.get("fingerprint"),
                raw=log
            )            
        )

        return sorted(events, key=lambda e: e.timestamp)
    

