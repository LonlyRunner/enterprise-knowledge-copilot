from langgraph.checkpoint.memory import (
    MemorySaver,
)


def create_checkpointer(
    redis_url: str | None = None,
):


    if not redis_url:

        return MemorySaver()


    from langgraph.checkpoint.redis import (
        RedisSaver,
    )


    saver = RedisSaver.from_conn_string(
        redis_url
    )


    return saver