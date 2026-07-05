from ir.model import CompareKind, Condition, Const, Filter


def test_filter_holds_input_output_and_condition():
    cond = Condition(field="age", cmp=CompareKind.GT, value=Const(value=18))
    op = Filter(input="users", output="adults", condition=cond)

    assert op.input == "users"
    assert op.output == "adults"
    assert op.condition == cond
