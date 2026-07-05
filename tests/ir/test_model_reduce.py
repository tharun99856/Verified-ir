from ir.model import Reduce, ReducerKind


def test_reduce_holds_input_output_reducer_and_field():
    op = Reduce(input="prices", output="total", reducer=ReducerKind.SUM, field="price")

    assert op.input == "prices"
    assert op.output == "total"
    assert op.reducer == ReducerKind.SUM
    assert op.field == "price"


def test_reduce_field_defaults_to_none_for_count():
    op = Reduce(input="items", output="n", reducer=ReducerKind.COUNT)

    assert op.field is None
