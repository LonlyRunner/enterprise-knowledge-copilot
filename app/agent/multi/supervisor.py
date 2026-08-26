from app.agent.multi.state import (
    MultiAgentState,
)
import logging

logger = logging.getLogger(__name__)



async def supervisor_node(
    state,
    router,
):

    result = await router.route(
        state["question"]
    )


    logger.info("supervisor_route", extra={"agent": result.agent, "reason": result.reason})


    state["next_agent"] = result.agent

    state["route_reason"] = result.reason


    return state
