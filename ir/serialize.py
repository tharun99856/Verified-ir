import json

from ir.model import Claims, Hints, Pipeline, Take


def _emit_op(op):
    if isinstance(op, Take):
        return {"op": "take", "input": op.input, "output": op.output, "count": op.count}
    raise ValueError(f"unknown op type: {type(op)!r}")


def _parse_op(data):
    kind = data["op"]
    if kind == "take":
        return Take(input=data["input"], output=data["output"], count=data["count"])
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
