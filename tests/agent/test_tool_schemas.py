from app.tools.order import query_order_tool


def test_query_order_schema():

    assert query_order_tool.name == "query_order"

    assert query_order_tool.side_effect is False

    assert (
        query_order_tool.requires_approval
        is False
    )


def test_query_order_required_argument():

    schema = query_order_tool.input_schema

    assert "order_id" in schema["required"]

    assert (
        schema["additionalProperties"]
        is False
    )