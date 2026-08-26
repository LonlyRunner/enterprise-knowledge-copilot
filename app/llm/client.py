from app.core.config import get_settings
from app.llm.base import BaseLLMClient
from app.llm.providers.deepseek import DeepSeekLLMClient
from functools import lru_cache




def create_llm_client() -> BaseLLMClient:

    settings = get_settings()

    provider = settings.llm_provider.lower()

    if provider == "deepseek":
        return DeepSeekLLMClient()

    raise ValueError(
        f"Unsupported LLM provider: {provider}"
    )


@lru_cache(maxsize=1)
def get_shared_llm_client() -> BaseLLMClient:
    """Reuse one provider client per API process (HTTP keep-alive pool)."""
    return create_llm_client()


async def close_shared_llm_client() -> None:
    if get_shared_llm_client.cache_info().currsize:
        await get_shared_llm_client().close()
        get_shared_llm_client.cache_clear()
