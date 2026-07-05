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
