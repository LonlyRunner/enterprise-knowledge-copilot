import pytest


from app.tools.registry import (
    create_tool_registry,
)

from app.services.business_gateway import (
    MockBusinessGateway,
)


@pytest.fixture
def registry():

    return create_tool_registry(
        MockBusinessGateway()
    )


def test_customer_tools_registered(
    registry,
):

    schemas = registry.schemas()


    tool_names = [
        item["function"]["name"]
        for item in schemas
    ]


    assert (
        "query_order"
        in tool_names
    )


    assert (
        "query_logistics"
        in tool_names
    )


    assert (
        "create_ticket"
        in tool_names
    )


def test_query_order_schema(
    registry,
):

    tool = registry.get(
        "query_order"
    )


    assert tool is not None


    definition = (
        tool.definition
    )


    assert (
        definition.name
        ==
        "query_order"
    )


    assert (
        definition.side_effect
        is False
    )


    assert (
        "order_id"
        in definition.input_schema["required"]
    )



def test_query_logistics_schema(
    registry,
):

    tool = registry.get(
        "query_logistics"
    )


    assert tool is not None


    assert (
        tool.definition.name
        ==
        "query_logistics"
    )


@pytest.mark.asyncio
async def test_query_order_execute(
    registry,
):

    tool = registry.get(
        "query_order"
    )


    result = await tool.execute(
        {
            "order_id":
            "XN-2026-000381"
        },

        tenant_id="tenant001",

        user_id="user001",

        trace_id="trace001",
    )


    assert (
        result["success"]
        is True
    )


    assert (
        result["data"]["status"]
        ==
        "shipping"
    )



@pytest.mark.asyncio
async def test_query_logistics_execute(
    registry,
):

    tool = registry.get(
        "query_logistics"
    )


    result = await tool.execute(
        {
            "order_id":
            "XN-2026-000381"
        },

        tenant_id="tenant001",

        user_id="user001",

        trace_id="trace001",
    )


    assert (
        result["success"]
        is True
    )


    assert (
        "eta"
        in result["data"]
    )



def test_create_ticket_requires_approval(
    registry,
):

    tool = registry.get(
        "create_ticket"
    )


    assert tool is not None


    assert (
        tool.definition.side_effect
        is True
    )


    assert (
        tool.definition.requires_approval
        is True
    )