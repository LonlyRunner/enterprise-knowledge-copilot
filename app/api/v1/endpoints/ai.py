from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.ext.asyncio import AsyncSession


from app.db.dependencies import get_db


from app.gateway.service import GatewayService


from app.gateway.schemas import (
    GatewayRequest,
    GatewayResponse,
)
from app.agent.langgraph.graph import (
    create_customer_graph,
)

from app.rag.service import RagService

from app.agent.runtime import (
    create_agent_graph,
)

router = APIRouter(
    prefix="/ai",
    tags=["AI Gateway"]
)


agent_graph = create_customer_graph(
    order_agent=None,
    rag_agent=None,
)

def create_gateway_service(
    session: AsyncSession,
):

    rag_service = RagService(
        session=session
    )


    agent_graph = create_agent_graph()


    return GatewayService(

        rag_service=rag_service,

        agent_graph=agent_graph,

    )


@router.post(
    "/chat",
    response_model=GatewayResponse,
)
async def ai_chat(
    request: GatewayRequest,
    db: AsyncSession = Depends(get_db),
):

    gateway_service = create_gateway_service(
        db
    )

    return await gateway_service.execute(
        request
    )



@router.post(
    "/agent",
    response_model=GatewayResponse,
)
async def ai_agent(
    request: GatewayRequest,
    db: AsyncSession = Depends(get_db),
):

    gateway_service = create_gateway_service(
        db
    )

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
    db: AsyncSession = Depends(get_db),
):

    gateway_service = create_gateway_service(
        db
    )


    request.mode = "rag"


    return await gateway_service.execute(
        request
    )