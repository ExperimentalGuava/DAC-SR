from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class ComponentScore:
    name: str
    score: float
    weight: float
    value: Dict[str, Any]
    meta: Optional[Dict[str, Any]] = None


@dataclass
class Snapshot:
    ts: datetime
    asset: str
    components: List[ComponentScore]
    schema_version: str

    @property
    def sr(self) -> float:
        total_w = sum(c.weight for c in self.components) or 1.0
        return sum(c.score * c.weight for c in self.components) / total_w
