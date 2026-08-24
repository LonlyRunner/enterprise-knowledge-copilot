import json


def encode_sse(
    event: str,
    data: dict,
) -> str:

    payload = json.dumps(
        data,
        ensure_ascii=False,
    )

    return (
        f"event: {event}\n"
        f"data: {payload}\n\n"
    )