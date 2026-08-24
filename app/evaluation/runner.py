class EvaluationRunner:


    def __init__(
        self,
        rag_service,
        retrieval_evaluator,
        generation_evaluator,
    ):

        self.rag_service = (
            rag_service
        )

        self.retrieval_evaluator = (
            retrieval_evaluator
        )

        self.generation_evaluator = (
            generation_evaluator
        )


    async def run(
        self,
        cases,
    ):


        results=[]


        for case in cases:


            result = (
                await self.rag_service.chat(
                    question=case.question
                )
            )


            results.append(
                {
                    "case_id":
                    case.id,


                    "answer":
                    result["answer"]
                }
            )


        return results