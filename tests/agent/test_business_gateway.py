import pytest

from app.services.business_gateway import (
    MockBusinessGateway,
)


@pytest.mark.asyncio
async def test_query_existing_order():

    gateway = MockBusinessGateway()


    result = await gateway.query_order(
        "XN-2026-000381",
        tenant_id="tenant001",
        user_id="user001",
    )


    assert result["success"] is True

    assert (
        result["data"]["status"]
        == "shipping"
    )


@pytest.mark.asyncio
async def test_query_missing_order():

    gateway = MockBusinessGateway()


    result = await gateway.query_order(
        "XN-9999-999999",
        tenant_id="tenant001",
        user_id="user001",
    )


    assert result["success"] is False