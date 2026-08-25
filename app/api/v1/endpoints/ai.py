from fastapi import APIRouter, Depends

from app.api.v1.endpoints.agent import router
from app.gateway.schemas import (
    GatewayRequest,
    GatewayResponse,
)

from app.gateway.service import GatewayService






gateway_service = GatewayService()



@router.post(
    "/chat",
    response_model=GatewayResponse,
)
async def ai_chat(
    request: GatewayRequest,
):

    return await gateway_service.execute(
        request
    )



@router.post(
    "/agent",
    response_model=GatewayResponse,
)
async def ai_agent(
    request: GatewayRequest,
):

    request.mode = "agent"


    return await gateway_service.execute(
        request
    )



@router.post(
    "/rag",
    response_model=GatewayResponse,
)
async def ai_rag(
    request: GatewayRequest,
):

    request.mode = "rag"


    return await gateway_service.execute(
        request
    )