from ir.model import CompareKind, Condition, Const


def test_condition_holds_field_cmp_and_value():
    cond = Condition(field="age", cmp=CompareKind.GT, value=Const(value=18))

    assert cond.field == "age"
    assert cond.cmp == CompareKind.GT
    assert cond.value == Const(value=18)
