import logging
from uuid import UUID
import uuid

from app.metrics import (
    RequestMetrics,
    CostCalculator,
)


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
from app.utils.timer import Timer

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

        self.cost_calculator = CostCalculator()


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

    async def generate_answer(
            self,
            *,
            runtime_context,
            question: str,
            conversation_id: UUID,
    ):

        max_degradation_attempts = 50

        degradation_attempt = 0

        while True:

            built_prompt = (
                self.prompt_builder
                .build_answer_prompt(
                    summary=runtime_context.summary,
                    history=runtime_context.history,
                    rag_chunks=runtime_context.rag_chunks,
                    question=question,
                )
            )

            try:

                self.token_guard.validate(
                    built_prompt
                )

                logger.info(
                    "context pipeline success "
                    "conversation_id=%s "
                    "summary=%s "
                    "history=%s "
                    "rag_chunks=%s "
                    "attempt=%s",
                    conversation_id,
                    runtime_context.summary_tokens,
                    runtime_context.history_tokens,
                    len(runtime_context.rag_chunks),
                    degradation_attempt,
                )

                break


            except ContextWindowExceededError:

                degradation_attempt += 1

                logger.warning(
                    "context overflow "
                    "conversation_id=%s "
                    "attempt=%s",
                    conversation_id,
                    degradation_attempt,
                )

                if (
                        degradation_attempt
                        > max_degradation_attempts
                ):
                    raise

                degraded_context = (
                    self.context_degrader
                    .degrade(
                        runtime_context
                    )
                )

                if degraded_context is None:
                    raise

                runtime_context = (
                    degraded_context
                )

        llm_timer = Timer()

        llm_timer.start()

        result = (
            await self.llm_client.chat(
                message=(
                    f"""
        {built_prompt.system_prompt}

        {built_prompt.user_prompt}
        """.strip()
                )
            )
        )

        llm_latency = (
            llm_timer.elapsed_ms()
        )
        metrics = RequestMetrics(

            trace_id=str(
                uuid.uuid4()
            ),

            summary_tokens=(
                runtime_context.summary_tokens
            ),

            history_tokens=(
                runtime_context.history_tokens
            ),

            rag_context_tokens=(
                runtime_context.rag_context_tokens
            ),

            question_tokens=(
                runtime_context.question_tokens
            ),

            input_tokens=(
                result.usage.prompt_tokens
            ),

            output_tokens=(
                result.usage.completion_tokens
            ),

            total_tokens=(
                result.usage.total_tokens
            ),

            model=result.model,

            llm_latency_ms=(
                llm_latency
            ),

            retrieval_latency_ms=0,

            selected_chunk_count=(
                len(runtime_context.rag_chunks)
            ),

            degradation_attempts=(
                degradation_attempt
            ),

            total_cost=(
                self.cost_calculator.calculate(
                    input_tokens=result.usage.prompt_tokens,
                    output_tokens=result.usage.completion_tokens,
                )
            ),
        )

        logger.info(
            "llm metrics "
            "conversation_id=%s "
            "latency_ms=%s",
            conversation_id,
            llm_latency,
        )

        logger.info(
            "rag_request_metrics",
            extra={
                "trace_id":
                    metrics.trace_id,

                "model":
                    metrics.model,

                "input_tokens":
                    metrics.input_tokens,

                "output_tokens":
                    metrics.output_tokens,

                "latency":
                    metrics.llm_latency_ms,

                "degradation":
                    metrics.degradation_attempts,
            }
        )

        return (
            result,
            metrics,
            runtime_context,
        )