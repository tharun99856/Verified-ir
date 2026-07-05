from ir.model import Hints


def test_hints_suggested_algorithm_defaults_to_none():
    hints = Hints()

    assert hints.suggested_algorithm is None


def test_hints_holds_suggested_algorithm():
    hints = Hints(suggested_algorithm="partial_sort")

    assert hints.suggested_algorithm == "partial_sort"
