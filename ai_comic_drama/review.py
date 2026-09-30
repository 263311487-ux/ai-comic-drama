"""Provider-neutral content review records."""
from dataclasses import dataclass, asdict
from typing import Dict, Any
import time
@dataclass
class Review:
    status: str
    reviewer: str
    basis: str
    review_type: str = "content"
    created_at: int = 0
    evidence: Dict[str, Any] = None
    def to_dict(self):
        d=asdict(self); d["created_at"]=self.created_at or int(time.time()); d["evidence"]=self.evidence or {}; return d
