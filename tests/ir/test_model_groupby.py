from ir.model import GroupBy


def test_groupby_holds_input_output_and_key():
    op = GroupBy(input="orders", output="by_customer", key="customer_id")

    assert op.input == "orders"
    assert op.output == "by_customer"
    assert op.key == "customer_id"
