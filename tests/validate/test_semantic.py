import pytest

from ir.model import (
    Claims,
    CompareKind,
    Condition,
    Const,
    Field,
    Filter,
    GroupBy,
    Hints,
    Map,
    Pipeline,
    Reduce,
    ReducerKind,
    Sort,
    Take,
)
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


def test_op_referencing_its_own_output_as_input_is_rejected():
    pipeline = Pipeline(
        ir_version=1,
        contract_version=1,
        ops=[Sort(input="same", output="same", key="score")],
        claims=Claims(complexity="O(n log n)", stable=False),
        hints=Hints(),
    )

    result = validate_semantic(pipeline)

    assert result.outcome == "rejected"
    assert result.stage == "semantic"


def test_input_referencing_a_later_output_is_rejected():
    pipeline = Pipeline(
        ir_version=1,
        contract_version=1,
        ops=[
            GroupBy(input="later", output="grouped", key="k"),
            Sort(input="raw", output="later", key="score"),
        ],
        claims=Claims(complexity="O(n log n)", stable=False),
        hints=Hints(),
    )

    result = validate_semantic(pipeline)

    assert result.outcome == "rejected"
    assert result.stage == "semantic"


def test_sort_with_empty_key_is_rejected():
    pipeline = Pipeline(
        ir_version=1,
        contract_version=1,
        ops=[Sort(input="users", output="sorted", key="")],
        claims=Claims(complexity="O(n log n)", stable=False),
        hints=Hints(),
    )

    result = validate_semantic(pipeline)

    assert result.outcome == "rejected"
    assert result.stage == "semantic"


@pytest.mark.parametrize(
    "op",
    [
        GroupBy(input="orders", output="grouped", key=""),
        Map(input="items", output="mapped", assign="", expr=Field(name="price")),
        Filter(
            input="users",
            output="filtered",
            condition=Condition(field="", cmp=CompareKind.GT, value=Const(value=1)),
        ),
        Reduce(input="prices", output="total", reducer=ReducerKind.SUM, field=""),
    ],
)
def test_other_ops_reject_empty_field_references(op):
    pipeline = Pipeline(
        ir_version=1,
        contract_version=1,
        ops=[op],
        claims=Claims(complexity="O(n)", stable=False),
        hints=Hints(),
    )

    result = validate_semantic(pipeline)

    assert result.outcome == "rejected"
    assert result.stage == "semantic"


def test_unused_intermediate_output_is_rejected_as_dangling():
    pipeline = Pipeline(
        ir_version=1,
        contract_version=1,
        ops=[
            Filter(
                input="users",
                output="adults",
                condition=Condition(field="age", cmp=CompareKind.GT, value=Const(value=18)),
            ),
            Sort(input="users", output="sorted", key="score"),
            Take(input="sorted", output="top10", count=10),
        ],
        claims=Claims(complexity="O(n log n)", stable=False),
        hints=Hints(),
    )

    result = validate_semantic(pipeline)

    assert result.outcome == "rejected"
    assert result.stage == "semantic"
    assert result.evidence == ["adults"]
