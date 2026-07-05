from ir.model import BinOp, BinOpKind, Const, Field, Map


def test_map_holds_input_output_assign_and_expr():
    expr = BinOp(op=BinOpKind.MUL, left=Field(name="price"), right=Const(value=2))
    op = Map(input="items", output="doubled", assign="price", expr=expr)

    assert op.input == "items"
    assert op.output == "doubled"
    assert op.assign == "price"
    assert op.expr == expr
