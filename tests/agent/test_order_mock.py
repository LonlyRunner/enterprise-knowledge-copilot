import pytest

from app.services.business_gateway import MockBusinessGateway


@pytest.mark.asyncio
async def test_mock_order_dataset_supports_list_and_logistics():
    gateway = MockBusinessGateway()
    orders = await gateway.list_orders(tenant_id="default", user_id="demo-user")
    assert len(orders) >= 4
    assert orders[0]["order_id"] == "XN-2026-000381"

    logistics = await gateway.query_logistics(
        "XN-2026-000381", tenant_id="default", user_id="demo-user"
    )
    assert logistics["success"] is True
    assert logistics["data"]["events"]
    assert logistics["data"]["tracking_no"] == "SF2026082100381"


@pytest.mark.asyncio
async def test_mock_ticket_is_created_in_memory():
    gateway = MockBusinessGateway()
    result = await gateway.create_ticket(
        "XN-2026-000381",
        "设备到货后外包装破损",
        tenant_id="default",
        user_id="demo-user",
    )
    assert result["success"] is True
    assert result["data"]["status"] == "pending_review"
    assert len(gateway.tickets) == 1
