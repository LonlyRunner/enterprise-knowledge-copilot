from app.agent.agent import NativeAgent

from app.llm.client import create_llm_client

from app.tools.base import ToolRegistry

from app.tools.executor import DefaultToolExecutor


from app.tools.order import QueryOrderTool

from app.tools.logistics import QueryLogisticsTool

from app.tools.ticket import CreateTicketTool


from app.services.business_gateway import (
    MockBusinessGateway,
)




def create_native_agent():


    llm = create_llm_client()


    registry = ToolRegistry()


    business_gateway = (
        MockBusinessGateway()
    )


    registry.register(
        QueryOrderTool(
            business_gateway
        )
    )


    registry.register(
        QueryLogisticsTool(
            business_gateway
        )
    )


    registry.register(
        CreateTicketTool(
            business_gateway
        )
    )


    executor = DefaultToolExecutor(
        registry
    )


    return NativeAgent(

        llm=llm,

        executor=executor,

        registry=registry,

    )