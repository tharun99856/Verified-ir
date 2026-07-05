from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class Explanation:
    stage: str
    outcome: str
    rule: str
    evidence: List[str] = field(default_factory=list)
    declared: Optional[str] = None
    derived: Optional[str] = None
    suggestion: Optional[str] = None
