from uuid import uuid4

from app.gateway.schemas import (
    GatewayRequest,
    GatewayResponse,
)


class GatewayService:


    def __init__(
        self,
        rag_service=None,
        agent_executor=None,
    ):

        self.rag_service = rag_service

        self.agent_executor = agent_executor



    async def execute(
        self,
        request: GatewayRequest,
    ) -> GatewayResponse:


        request_id = str(uuid4())

        trace_id = str(uuid4())


        if request.mode == "rag":

            return await self._execute_rag(
                request,
                request_id,
                trace_id,
            )


        elif request.mode == "agent":

            return await self._execute_agent(
                request,
                request_id,
                trace_id,
            )


        else:

            return GatewayResponse(
                request_id=request_id,
                trace_id=trace_id,
                status="completed",
                answer="chat mode not implemented",
            )



    async def _execute_rag(
        self,
        request,
        request_id,
        trace_id,
    ):


        if self.rag_service is None:

            return GatewayResponse(
                request_id=request_id,
                trace_id=trace_id,
                status="failed",
                answer="RAG service unavailable",
            )


        result = await self.rag_service.query(
            request.message
        )


        return GatewayResponse(

            request_id=request_id,

            trace_id=trace_id,

            status="completed",

            answer=result.get(
                "answer"
            ),

            citations=result.get(
                "citations",
                []
            )

        )



    async def _execute_agent(
        self,
        request,
        request_id,
        trace_id,
    ):


        if self.agent_executor is None:

            return GatewayResponse(

                request_id=request_id,

                trace_id=trace_id,

                status="failed",

                answer="Agent unavailable"

            )


        result = await self.agent_executor.run(
            request.message
        )


        return GatewayResponse(

            request_id=request_id,

            trace_id=trace_id,

            status="completed",

            answer=result

        )