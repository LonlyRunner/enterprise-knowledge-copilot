from langgraph.checkpoint.redis import (
    AsyncRedisSaver,
)


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


            print(
                "Async Redis Checkpointer initialized"
            )


        return self.checkpointer