import httpx




def is_retryable_exception(
    exc: Exception,
) -> bool:

    return isinstance(
        exc,
        RETRYABLE_EXCEPTIONS,
    )

class DocumentLockBusyException(
    Exception
):
    pass

RETRYABLE_EXCEPTIONS = (
    httpx.TimeoutException,
    httpx.ConnectError,
    httpx.RemoteProtocolError,
    DocumentLockBusyException,
)