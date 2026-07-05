from ir.model import Take


def test_take_holds_input_output_and_count():
    op = Take(input="sorted", output="top10", count=10)

    assert op.input == "sorted"
    assert op.output == "top10"
    assert op.count == 10
