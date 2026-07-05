from dataclasses import dataclass
from enum import Enum
from typing import Union


class BinOpKind(Enum):
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"


@dataclass(frozen=True)
class Field:
    name: str


@dataclass(frozen=True)
class Const:
    value: object


@dataclass(frozen=True)
class BinOp:
    op: BinOpKind
    left: "Expr"
    right: "Expr"


Expr = Union[Field, Const, BinOp]


@dataclass(frozen=True)
class Take:
    input: str
    output: str
    count: int
