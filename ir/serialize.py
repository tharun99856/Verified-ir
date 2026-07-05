import json

from ir.model import (
    BinOp,
    BinOpKind,
    Claims,
    CompareKind,
    Condition,
    Const,
    Field,
    Filter,
    GroupBy,
    Hints,
    Pipeline,
    Reduce,
    ReducerKind,
    Sort,
    Take,
)


def _emit_expr(expr):
    if isinstance(expr, Const):
        return {"kind": "const", "value": expr.value}
    if isinstance(expr, Field):
        return {"kind": "field", "name": expr.name}
    if isinstance(expr, BinOp):
        return {
            "kind": "binop",
            "op": expr.op.value,
            "left": _emit_expr(expr.left),
            "right": _emit_expr(expr.right),
        }
    raise ValueError(f"unknown expr type: {type(expr)!r}")


def _parse_expr(data):
    kind = data["kind"]
    if kind == "const":
        return Const(value=data["value"])
    if kind == "field":
        return Field(name=data["name"])
    if kind == "binop":
        return BinOp(
            op=BinOpKind(data["op"]),
            left=_parse_expr(data["left"]),
            right=_parse_expr(data["right"]),
        )
    raise ValueError(f"unknown expr kind: {kind!r}")


def _emit_condition(condition):
    return {
        "field": condition.field,
        "cmp": condition.cmp.value,
        "value": _emit_expr(condition.value),
    }


def _parse_condition(data):
    return Condition(
        field=data["field"],
        cmp=CompareKind(data["cmp"]),
        value=_parse_expr(data["value"]),
    )


def _emit_op(op):
    if isinstance(op, Take):
        return {"op": "take", "input": op.input, "output": op.output, "count": op.count}
    if isinstance(op, Sort):
        return {
            "op": "sort",
            "input": op.input,
            "output": op.output,
            "key": op.key,
            "descending": op.descending,
        }
    if isinstance(op, GroupBy):
        return {"op": "groupby", "input": op.input, "output": op.output, "key": op.key}
    if isinstance(op, Reduce):
        return {
            "op": "reduce",
            "input": op.input,
            "output": op.output,
            "reducer": op.reducer.value,
            "field": op.field,
            "init": op.init,
        }
    if isinstance(op, Filter):
        return {
            "op": "filter",
            "input": op.input,
            "output": op.output,
            "condition": _emit_condition(op.condition),
        }
    raise ValueError(f"unknown op type: {type(op)!r}")


def _parse_op(data):
    kind = data["op"]
    if kind == "take":
        return Take(input=data["input"], output=data["output"], count=data["count"])
    if kind == "sort":
        return Sort(
            input=data["input"],
            output=data["output"],
            key=data["key"],
            descending=data.get("descending", False),
        )
    if kind == "groupby":
        return GroupBy(input=data["input"], output=data["output"], key=data["key"])
    if kind == "reduce":
        return Reduce(
            input=data["input"],
            output=data["output"],
            reducer=ReducerKind(data["reducer"]),
            field=data.get("field"),
            init=data.get("init"),
        )
    if kind == "filter":
        return Filter(
            input=data["input"],
            output=data["output"],
            condition=_parse_condition(data["condition"]),
        )
    raise ValueError(f"unknown op kind: {kind!r}")


def _emit_claims(claims):
    return {
        "complexity": claims.complexity,
        "stable": claims.stable,
        "mutates": claims.mutates,
        "aliasing": claims.aliasing,
    }


def _parse_claims(data):
    return Claims(
        complexity=data["complexity"],
        stable=data["stable"],
        mutates=data.get("mutates", False),
        aliasing=data.get("aliasing", False),
    )


def _emit_hints(hints):
    return {"suggested_algorithm": hints.suggested_algorithm}


def _parse_hints(data):
    return Hints(suggested_algorithm=data.get("suggested_algorithm"))


class JsonSerializer:
    def emit(self, pipeline: Pipeline) -> str:
        data = {
            "ir_version": pipeline.ir_version,
            "contract_version": pipeline.contract_version,
            "ops": [_emit_op(op) for op in pipeline.ops],
            "claims": _emit_claims(pipeline.claims),
            "hints": _emit_hints(pipeline.hints),
        }
        return json.dumps(data)

    def parse(self, text: str) -> Pipeline:
        data = json.loads(text)
        return Pipeline(
            ir_version=data["ir_version"],
            contract_version=data["contract_version"],
            ops=[_parse_op(op) for op in data["ops"]],
            claims=_parse_claims(data["claims"]),
            hints=_parse_hints(data["hints"]),
        )
