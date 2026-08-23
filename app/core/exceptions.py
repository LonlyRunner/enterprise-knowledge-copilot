class AppException(Exception):

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class LLMException(AppException):
    pass


class LLMTimeoutException(LLMException):

    def __init__(self):
        super().__init__(
            message="LLM request timed out",
            code="LLM_TIMEOUT",
            status_code=504,
        )


class LLMRateLimitException(LLMException):

    def __init__(self):
        super().__init__(
            message="LLM rate limit exceeded",
            code="LLM_RATE_LIMIT",
            status_code=429,
        )


class LLMAuthenticationException(LLMException):

    def __init__(self):
        super().__init__(
            message="LLM authentication failed",
            code="LLM_AUTH_FAILED",
            status_code=502,
        )


class LLMServiceException(LLMException):

    def __init__(self, message: str = "LLM service unavailable"):
        super().__init__(
            message=message,
            code="LLM_SERVICE_ERROR",
            status_code=502,
        )