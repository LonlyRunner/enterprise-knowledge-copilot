import time
import uuid


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


        print(
            f"[TRACE START]"
            f"{name}"
            f" trace={self.trace_id}"
        )



    def end(
        self,
        name,
    ):

        cost = (
            time.time()
            -
            self.start_time
        )


        print(
            f"[TRACE END]"
            f"{name}"
            f" cost={cost:.3f}s"
        )