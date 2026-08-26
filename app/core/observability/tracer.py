import time
import uuid
import logging

logger = logging.getLogger(__name__)


class AgentTracer:


    def __init__(
        self,
        trace_id=None,
    ):

        self.trace_id = (
            trace_id
            or
            str(uuid.uuid4())
        )



    def start(
        self,
        name,
    ):

        self.start_time = (
            time.time()
        )


        logger.info("agent_trace_start", extra={"agent": name, "trace_id": self.trace_id})



    def end(
        self,
        name,
    ):

        cost = (
            time.time()
            -
            self.start_time
        )


        logger.info("agent_trace_end", extra={"agent": name, "trace_id": self.trace_id, "latency_ms": round(cost * 1000, 2)})
