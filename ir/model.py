from dataclasses import dataclass


@dataclass(frozen=True)
class Field:
    name: str


@dataclass(frozen=True)
class Const:
    value: object


@dataclass(frozen=True)
class Take:
    input: str
    output: str
    count: int
