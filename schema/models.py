from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import json

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


