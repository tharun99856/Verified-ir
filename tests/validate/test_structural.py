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


def test_unknown_op_name_is_rejected():
    data = _valid_pipeline_dict()
    data["ops"][0] = {"op": "join", "input": "a", "output": "b"}

    result = validate_structural(data)

    assert result.outcome == "rejected"
    assert result.stage == "structural"


def test_sort_missing_required_key_field_is_rejected():
    data = _valid_pipeline_dict()
    data["ops"][1] = {"op": "sort", "input": "adults", "output": "sorted"}

    result = validate_structural(data)

    assert result.outcome == "rejected"
    assert result.stage == "structural"


def test_ops_not_a_list_is_rejected():
    data = _valid_pipeline_dict()
    data["ops"] = {"op": "take", "input": "a", "output": "b", "count": 1}

    result = validate_structural(data)

    assert result.outcome == "rejected"
    assert result.stage == "structural"


def test_sort_with_stray_count_and_no_key_is_rejected():
    # The exact example from the design spec (section 6): a sort node
    # carrying an unrelated "count" field and missing its required "key".
    data = _valid_pipeline_dict()
    data["ops"][1] = {"op": "sort", "input": "adults", "output": "sorted", "count": 10}

    result = validate_structural(data)

    assert result.outcome == "rejected"
    assert result.stage == "structural"
