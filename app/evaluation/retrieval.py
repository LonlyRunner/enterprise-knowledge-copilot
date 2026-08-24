class RetrievalEvaluator:


    def recall_at_k(
        self,
        retrieved_ids,
        relevant_ids,
        k:int,
    ):


        retrieved=set(
            retrieved_ids[:k]
        )


        relevant=set(
            relevant_ids
        )


        return (
            len(
                retrieved & relevant
            )
            /
            len(relevant)
        )

    def precision_at_k(
            retrieved_ids,
            relevant_ids,
            k,
    ):
        retrieved = set(
            retrieved_ids[:k]
        )

        relevant = set(
            relevant_ids
        )

        return (
                len(
                    retrieved & relevant
                )
                /
                k
        )

    def reciprocal_rank(
            retrieved_ids,
            relevant_ids,
    ):

        for index, item in enumerate(
                retrieved_ids
        ):

            if item in relevant_ids:
                return 1 / (index + 1)

        return 0

    def hit_rate(
            retrieved,
            relevant,
    ):

        return (
            1
            if set(retrieved)
               &
               set(relevant)
            else 0
        )