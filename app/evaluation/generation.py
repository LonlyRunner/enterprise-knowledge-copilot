class GenerationEvaluator:



    def keyword_match(
        self,
        answer:str,
        expected_answer:str,
    ):


        expected_words = (
            expected_answer.split()
        )


        matched = 0


        for word in expected_words:

            if word in answer:

                matched += 1


        if not expected_words:

            return 0


        return (
            matched /
            len(expected_words)
        )