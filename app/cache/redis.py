import redis


client=redis.Redis(
    host="localhost",
    port=6379
)


def get_cache(
    key
):

    return client.get(key)



def set_cache(
    key,
    value,
    ttl=3600
):

    client.set(
        key,
        value,
        ex=ttl
    )