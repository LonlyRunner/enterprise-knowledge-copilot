class AgentEvaluator:


    def success(
        self,
        expected,
        actual,
    ):


        return (
            expected
            in
            actual
        )