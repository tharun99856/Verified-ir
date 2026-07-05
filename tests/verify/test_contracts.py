from ir.model import Take
from verify.contracts import compose_complexity


def test_single_take_composes_to_ok():
    ops = [Take(input="a", output="b", count=10)]

    assert compose_complexity(ops) == "O(k)"
