from uuid import uuid4

from app.gateway.schemas import (
    GatewayRequest,
    GatewayResponse,
)
from app.rag.service import RagService


class GatewayService:

    def __init__(
            self,
            rag_service=None,
            agent_executor=None,
            agent_graph=None,
            limiter=None
    ):

        self.rag_service = rag_service

        self.agent_executor = agent_executor

        self.agent_graph = agent_graph

        self.limiter = limiter


    async def execute(
        self,
        request: GatewayRequest,
    ) -> GatewayResponse:

        request_id = str(uuid4())

        task_id = str(uuid4())

        trace_id = str(uuid4())

        if self.limiter:

            allowed = await self.limiter.check(

                f"user:{request.user_id}"

            )

            if not allowed:
                return GatewayResponse(

                    request_id=request_id,

                    trace_id=trace_id,

                    status="failed",

                    answer="rate limit exceeded",

                )

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
                task_id=task_id,
                status="completed",
                answer="chat mode not implemented",

            )

    async def _execute_rag(
            self,
            request,
            request_id,
            task_id,
            trace_id,
    ):

        if self.rag_service is None:
            return GatewayResponse(
                request_id=request_id,
                trace_id=trace_id,
                task_id=task_id,
                status="failed",
                answer="RAG service unavailable",
            )

        result = await self.rag_service.query(

            knowledge_base_id=request.knowledge_base_id,

            question=request.message,

            top_k=3,
        )

        return GatewayResponse(

            request_id=request_id,

            trace_id=trace_id,

            status="completed",

            answer=result.answer,

            citations=[
                source.model_dump()
                for source in result.sources
            ],
            usage=result.get(
                "usage",
                {}
            )

        )

    async def _execute_agent(
            self,
            request,
            request_id,
            task_id,
            trace_id,
    ):

        if self.agent_graph is None:
            return GatewayResponse(

                request_id=request_id,

                trace_id=trace_id,
                task_id=task_id,

                status="failed",

                answer="Agent unavailable"


            )

        state = {

            "question":
                request.message,

            "intent":
                None,

            "answer":
                None,

            "tenant_id":
                request.tenant_id or "default",

            "user_id":
                request.user_id or "demo-user",

            "trace_id":
                trace_id,

            "need_human_review":
                False,

            "human_action":
                None,

        }

        result = await self.agent_graph.ainvoke(
            state
        )

        return GatewayResponse(

            request_id=request_id,

            trace_id=trace_id,

            status="completed",

            answer=result.get(
                "answer"
            ),

            agent_steps=[

                {
                    "agent":
                        result.get("intent"),

                    "status":
                        "completed",

                }

            ],
            usage=result.get(
                "usage",
                {}
            )

        )