import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.rag.context import (
    ContextBuilder,
    ContextDegrader,
    ContextWindowExceededError,
    ConversationSummarizer,
    PromptBuilder,
    TokenAwareHistorySelector,
    TokenAwareRagContextSelector,
    TokenBudget,
    TokenCounter,
    TokenGuard,
)

from app.repositories.conversation import (
    ConversationRepository,
)

from app.repositories.message import (
    MessageRepository,
)


logger = logging.getLogger(__name__)


class ChatContextService:


    def __init__(
        self,
        session: AsyncSession,
        llm_client,
    ):

        self.session = session

        self.llm_client = llm_client


        self.conversation_repository = (
            ConversationRepository(
                session
            )
        )


        self.message_repository = (
            MessageRepository(
                session
            )
        )


        self.token_counter = TokenCounter()

        self.token_budget = TokenBudget()


        self.history_selector = (
            TokenAwareHistorySelector(
                token_counter=self.token_counter
            )
        )


        self.rag_context_selector = (
            TokenAwareRagContextSelector(
                token_counter=self.token_counter
            )
        )


        self.context_builder = ContextBuilder(
            token_counter=self.token_counter,
            token_budget=self.token_budget,
            history_selector=self.history_selector,
            rag_context_selector=self.rag_context_selector,
        )


        self.prompt_builder = PromptBuilder()


        self.token_guard = TokenGuard(
            token_counter=self.token_counter,
            token_budget=self.token_budget,
        )


        self.context_degrader = (
            ContextDegrader()
        )


    async def build_context(
        self,
        *,
        conversation_id: UUID,
        knowledge_base_id: UUID,
        question: str,
    ):

        conversation = (
            await self.conversation_repository
            .get_by_id_and_knowledge_base(
                conversation_id=conversation_id,
                knowledge_base_id=knowledge_base_id,
            )
        )


        if conversation is None:
            raise ValueError(
                "Conversation not found"
            )


        history_candidates = (
            await self.message_repository
            .list_after_checkpoint(
                conversation_id=conversation.id,
                checkpoint_message_id=(
                    conversation.summary_message_id
                ),
                limit=200,
            )
        )


        runtime_context = (
            self.context_builder
            .build_conversation_context(
                summary=conversation.summary,
                history_candidates=history_candidates,
                question=question,
            )
        )


        return (
            conversation,
            runtime_context,
        )