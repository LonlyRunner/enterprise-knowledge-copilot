class QueryRewriter:


    def rewrite(
        self,
        *,
        question,
        history,
    ):


        if not history:
            return question


        return (
            f"{history[-1].content}"
            f"\n{question}"
        )