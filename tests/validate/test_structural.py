import json

from ir.model import Claims, CompareKind, Condition, Const, Filter, Hints, Pipeline, Sort, Take
from ir.serialize import JsonSerializer
from validate.structural import validate_structural


def _valid_pipeline_dict():
    pipeline = Pipeline(
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
        hints=Hints(suggested_algorithm="partial_sort"),
    )
    return json.loads(JsonSerializer().emit(pipeline))


def test_valid_pipeline_passes_structural_validation():
    result = validate_structural(_valid_pipeline_dict())

    assert result.outcome == "ok"
    assert result.stage == "structural"
