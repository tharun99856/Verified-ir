from ir.model import BinOp, BinOpKind, Const, Field


def test_field_holds_a_name():
    expr = Field(name="age")

    assert expr.name == "age"


def test_const_holds_a_value():
    expr = Const(value=18)

    assert expr.value == 18


def test_binop_holds_kind_and_operands():
    expr = BinOp(op=BinOpKind.ADD, left=Field(name="score"), right=Const(value=5))

    assert expr.op == BinOpKind.ADD
    assert expr.left == Field(name="score")
    assert expr.right == Const(value=5)
