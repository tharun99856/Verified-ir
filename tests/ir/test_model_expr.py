from ir.model import Const, Field


def test_field_holds_a_name():
    expr = Field(name="age")

    assert expr.name == "age"


def test_const_holds_a_value():
    expr = Const(value=18)

    assert expr.value == 18
