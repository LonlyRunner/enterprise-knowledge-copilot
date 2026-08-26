from langgraph.checkpoint.redis import (
    AsyncRedisSaver,
)
import logging

logger = logging.getLogger(__name__)


class CheckpointerManager:
    """
    LangGraph Redis Async Checkpointer
    """


    def __init__(
        self,
        redis_url: str,
    ):

        self.redis_url = redis_url

        self.context = None

        self.checkpointer = None


    async def get_checkpointer(self):


        if self.checkpointer is None:


            self.context = (
                AsyncRedisSaver.from_conn_string(
                    self.redis_url
                )
            )


            self.checkpointer = (
                await self.context.__aenter__()
            )


            await (
                self.checkpointer.setup()
            )


            logger.info("langgraph_checkpointer_initialized")


        return self.checkpointer
