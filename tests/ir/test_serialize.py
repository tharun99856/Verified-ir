from ir.model import Claims, GroupBy, Hints, Pipeline, Sort, Take
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
