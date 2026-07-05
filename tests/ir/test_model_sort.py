from ir.model import Sort


def test_sort_holds_input_output_and_key():
    op = Sort(input="adults", output="sorted", key="score")

    assert op.input == "adults"
    assert op.output == "sorted"
    assert op.key == "score"
    assert op.descending is False


def test_sort_descending_defaults_to_false_but_can_be_set():
    op = Sort(input="a", output="b", key="score", descending=True)

    assert op.descending is True
