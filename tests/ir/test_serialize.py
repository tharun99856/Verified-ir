from ir.model import Claims, Hints, Pipeline, Take
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
