from explain.explanation import Explanation
from ir.model import Filter, GroupBy, Map, Pipeline, Reduce, Sort


def _field_references(op):
    if isinstance(op, Sort):
        return [("key", op.key)]
    if isinstance(op, GroupBy):
        return [("key", op.key)]
    if isinstance(op, Map):
        return [("assign", op.assign)]
    if isinstance(op, Filter):
        return [("condition.field", op.condition.field)]
    if isinstance(op, Reduce) and op.field is not None:
        return [("field", op.field)]
    return []


def validate_semantic(pipeline: Pipeline) -> Explanation:
    output_position = {op.output: i for i, op in enumerate(pipeline.ops)}

    for op in pipeline.ops:
        for field_name, value in _field_references(op):
            if not value:
                return Explanation(
                    stage="semantic",
                    outcome="rejected",
                    rule="EMPTY_FIELD_REFERENCE",
                    evidence=[field_name],
                    suggestion=f"'{field_name}' must be a non-empty field name",
                )

    for i, op in enumerate(pipeline.ops):
        defined_at = output_position.get(op.input)
        if defined_at is not None and defined_at >= i:
            return Explanation(
                stage="semantic",
                outcome="rejected",
                rule="USE_BEFORE_DEFINE",
                evidence=[op.input],
                suggestion=(
                    f"'{op.input}' is not defined before it is used "
                    f"(it is the output of a later or the same op)"
                ),
            )

    consumed = {op.input for op in pipeline.ops}
    last_output = pipeline.ops[-1].output if pipeline.ops else None
    for op in pipeline.ops:
        if op.output != last_output and op.output not in consumed:
            return Explanation(
                stage="semantic",
                outcome="rejected",
                rule="DANGLING_OUTPUT",
                evidence=[op.output],
                suggestion=f"'{op.output}' is never used by any later op and is not the final result",
            )

    return Explanation(stage="semantic", outcome="ok", rule="SEMANTIC_OK")
