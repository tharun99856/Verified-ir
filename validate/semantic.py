from explain.explanation import Explanation
from ir.model import Pipeline


def validate_semantic(pipeline: Pipeline) -> Explanation:
    return Explanation(stage="semantic", outcome="ok", rule="SEMANTIC_OK")
