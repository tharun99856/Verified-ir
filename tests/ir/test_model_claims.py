from ir.model import Claims


def test_claims_holds_complexity_and_stable():
    claims = Claims(complexity="O(n log n)", stable=True)

    assert claims.complexity == "O(n log n)"
    assert claims.stable is True


def test_claims_mutates_and_aliasing_default_false():
    claims = Claims(complexity="O(n)", stable=False)

    assert claims.mutates is False
    assert claims.aliasing is False
