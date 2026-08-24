from app.core.config import get_settings
from app.llm.base import BaseLLMClient
from app.llm.providers.deepseek import DeepSeekLLMClient




def create_llm_client() -> BaseLLMClient:

    settings = get_settings()

    provider = settings.llm_provider.lower()

    if provider == "deepseek":
        return DeepSeekLLMClient()

    raise ValueError(
        f"Unsupported LLM provider: {provider}"
    )