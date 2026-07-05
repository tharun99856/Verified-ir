from ir.model import Field


def test_field_holds_a_name():
    expr = Field(name="age")

    assert expr.name == "age"
