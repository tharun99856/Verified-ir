from ir.model import Claims, CompareKind, Condition, Const, Filter, Hints, Pipeline, Sort, Take
from validate.semantic import validate_semantic


def _chained_pipeline():
    return Pipeline(
        ir_version=1,
        contract_version=1,
        ops=[
            Filter(
                input="users",
                output="adults",
                condition=Condition(field="age", cmp=CompareKind.GT, value=Const(value=18)),
            ),
            Sort(input="adults", output="sorted", key="score", descending=True),
            Take(input="sorted", output="top10", count=10),
        ],
        claims=Claims(complexity="O(n log n)", stable=True),
        hints=Hints(),
    )


def test_well_formed_chained_pipeline_passes_semantic_validation():
    result = validate_semantic(_chained_pipeline())

    assert result.outcome == "ok"
    assert result.stage == "semantic"
