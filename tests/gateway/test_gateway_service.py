import pytest

from app.gateway.service import GatewayService
from app.gateway.schemas import GatewayRequest



@pytest.mark.asyncio
async def test_gateway_chat():


    service = GatewayService()


    request = GatewayRequest(

        message="hello"

    )


    result = await service.execute(
        request
    )


    assert result.status == "completed"

    assert result.request_id is not None