from ir.model import CompareKind, Condition, Const, Filter, Sort, Take
from verify.contracts import compose_complexity


def test_single_take_composes_to_ok():
    ops = [Take(input="a", output="b", count=10)]

    assert compose_complexity(ops) == "O(k)"


def test_single_sort_composes_to_on_log_n():
    ops = [Sort(input="a", output="b", key="score")]

    assert compose_complexity(ops) == "O(n log n)"


def test_filter_then_take_composes_to_on_filter_dominates():
    ops = [
        Filter(
            input="a",
            output="b",
            condition=Condition(field="age", cmp=CompareKind.GT, value=Const(value=18)),
        ),
        Take(input="b", output="c", count=10),
    ]

    assert compose_complexity(ops) == "O(n)"


def test_filter_sort_take_composes_to_on_log_n_sort_dominates():
    ops = [
        Filter(
            input="a",
            output="b",
            condition=Condition(field="age", cmp=CompareKind.GT, value=Const(value=18)),
        ),
        Sort(input="b", output="c", key="score"),
        Take(input="c", output="d", count=10),
    ]

    assert compose_complexity(ops) == "O(n log n)"


def test_empty_pipeline_composes_to_o1():
    assert compose_complexity([]) == "O(1)"
