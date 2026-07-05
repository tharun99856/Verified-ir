from explain.explanation import Explanation
from ir.model import Pipeline


def validate_semantic(pipeline: Pipeline) -> Explanation:
    output_position = {op.output: i for i, op in enumerate(pipeline.ops)}

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

    return Explanation(stage="semantic", outcome="ok", rule="SEMANTIC_OK")
