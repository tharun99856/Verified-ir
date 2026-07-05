from ir.model import (
    BinOp,
    BinOpKind,
    Claims,
    CompareKind,
    Condition,
    Const,
    Filter,
    GroupBy,
    Hints,
    Pipeline,
    Reduce,
    ReducerKind,
    Sort,
    Take,
)
from ir.serialize import JsonSerializer


def test_round_trip_pipeline_with_take_only():
    pipeline = Pipeline(
        ir_version=1,
        contract_version=1,
        ops=[Take(input="sorted", output="top10", count=10)],
        claims=Claims(complexity="O(k)", stable=False),
        hints=Hints(),
    )

    serializer = JsonSerializer()
    wire = serializer.emit(pipeline)
    result = serializer.parse(wire)

    assert result == pipeline


def test_round_trip_pipeline_with_sort():
    pipeline = Pipeline(
        ir_version=1,
        contract_version=1,
        ops=[Sort(input="adults", output="sorted", key="score", descending=True)],
        claims=Claims(complexity="O(n log n)", stable=True),
        hints=Hints(),
    )

    serializer = JsonSerializer()
    result = serializer.parse(serializer.emit(pipeline))

    assert result == pipeline


def test_round_trip_pipeline_with_reduce():
    pipeline = Pipeline(
        ir_version=1,
        contract_version=1,
        ops=[Reduce(input="prices", output="total", reducer=ReducerKind.SUM, field="price")],
        claims=Claims(complexity="O(n)", stable=False),
        hints=Hints(),
    )

    serializer = JsonSerializer()
    result = serializer.parse(serializer.emit(pipeline))

    assert result == pipeline


def test_round_trip_reduce_with_count_has_no_field():
    pipeline = Pipeline(
        ir_version=1,
        contract_version=1,
        ops=[Reduce(input="items", output="n", reducer=ReducerKind.COUNT)],
        claims=Claims(complexity="O(n)", stable=False),
        hints=Hints(),
    )

    serializer = JsonSerializer()
    result = serializer.parse(serializer.emit(pipeline))

    assert result == pipeline


def test_round_trip_pipeline_with_filter_over_const():
    cond = Condition(field="age", cmp=CompareKind.GT, value=Const(value=18))
    pipeline = Pipeline(
        ir_version=1,
        contract_version=1,
        ops=[Filter(input="users", output="adults", condition=cond)],
        claims=Claims(complexity="O(n)", stable=False),
        hints=Hints(),
    )

    serializer = JsonSerializer()
    result = serializer.parse(serializer.emit(pipeline))

    assert result == pipeline


def test_round_trip_pipeline_with_filter_over_nested_binop():
    nested_value = BinOp(op=BinOpKind.ADD, left=Const(value=10), right=Const(value=8))
    cond = Condition(field="age", cmp=CompareKind.GT, value=nested_value)
    pipeline = Pipeline(
        ir_version=1,
        contract_version=1,
        ops=[Filter(input="users", output="adults", condition=cond)],
        claims=Claims(complexity="O(n)", stable=False),
        hints=Hints(),
    )

    serializer = JsonSerializer()
    result = serializer.parse(serializer.emit(pipeline))

    assert result == pipeline
    assert isinstance(result.ops[0].condition.value, BinOp)


def test_round_trip_pipeline_with_groupby():
    pipeline = Pipeline(
        ir_version=1,
        contract_version=1,
        ops=[GroupBy(input="orders", output="by_customer", key="customer_id")],
        claims=Claims(complexity="O(n)", stable=False),
        hints=Hints(),
    )

    serializer = JsonSerializer()
    result = serializer.parse(serializer.emit(pipeline))

    assert result == pipeline
