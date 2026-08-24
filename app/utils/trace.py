import contextvars
import uuid


_trace_id = contextvars.ContextVar(
    "trace_id",
    default=None,
)


def create_trace_id() -> str:

    trace_id = str(
        uuid.uuid4()
    )

    _trace_id.set(
        trace_id
    )

    return trace_id



def get_trace_id():

    return _trace_id.get()