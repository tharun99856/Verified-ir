from dataclasses import dataclass


@dataclass(frozen=True)
class Take:
    input: str
    output: str
    count: int
