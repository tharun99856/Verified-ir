from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union


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


class CompareKind(Enum):
    GT = "gt"
    LT = "lt"
    GTE = "gte"
    LTE = "lte"
    EQ = "eq"
    NEQ = "neq"


@dataclass(frozen=True)
class Condition:
    field: str
    cmp: CompareKind
    value: Expr


@dataclass(frozen=True)
class Filter:
    input: str
    output: str
    condition: Condition


@dataclass(frozen=True)
class Map:
    input: str
    output: str
    assign: str
    expr: Expr


class ReducerKind(Enum):
    SUM = "sum"
    PRODUCT = "product"
    MIN = "min"
    MAX = "max"
    COUNT = "count"


@dataclass(frozen=True)
class Reduce:
    input: str
    output: str
    reducer: ReducerKind
    field: Optional[str] = None
    init: Optional[object] = None


@dataclass(frozen=True)
class Sort:
    input: str
    output: str
    key: str
    descending: bool = False


@dataclass(frozen=True)
class Take:
    input: str
    output: str
    count: int
