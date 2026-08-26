class RetrievalEvaluator:
    @staticmethod
    def recall_at_k(retrieved_ids, relevant_ids, k: int) -> float:
        if k <= 0 or not relevant_ids:
            return 0.0
        retrieved = set(retrieved_ids[:k])
        relevant = set(relevant_ids)
        return len(retrieved & relevant) / len(relevant)

    @staticmethod
    def precision_at_k(retrieved_ids, relevant_ids, k: int) -> float:
        if k <= 0:
            return 0.0
        retrieved = set(retrieved_ids[:k])
        relevant = set(relevant_ids)
        return len(retrieved & relevant) / k

    @staticmethod
    def reciprocal_rank(retrieved_ids, relevant_ids) -> float:
        relevant = set(relevant_ids)
        for index, item in enumerate(retrieved_ids):
            if item in relevant:
                return 1.0 / (index + 1)
        return 0.0

    @staticmethod
    def hit_rate(retrieved, relevant) -> int:
        return int(bool(set(retrieved) & set(relevant)))

    @staticmethod
    def keyword_recall(contents: list[str], keywords: list[str], k: int) -> float:
        """Recall expected evidence phrases when chunk ids are unavailable."""
        if not keywords:
            return 1.0
        text = "\n".join(contents[: max(0, k)]).lower()
        return sum(keyword.lower() in text for keyword in keywords) / len(keywords)

    @staticmethod
    def evaluate(
        retrieved_ids: list[str],
        relevant_ids: list[str],
        *,
        k: int = 5,
        retrieved_contents: list[str] | None = None,
        expected_keywords: list[str] | None = None,
    ) -> dict[str, float]:
        contents = retrieved_contents or []
        keywords = expected_keywords or []
        if relevant_ids:
            return {
                "retrieval.hit_rate": float(RetrievalEvaluator.hit_rate(retrieved_ids[:k], relevant_ids)),
                "retrieval.recall_at_k": RetrievalEvaluator.recall_at_k(retrieved_ids, relevant_ids, k),
                "retrieval.mrr": RetrievalEvaluator.reciprocal_rank(retrieved_ids, relevant_ids),
            }
        if keywords:
            matching_rank = next(
                (index + 1 for index, content in enumerate(contents) if any(word.lower() in content.lower() for word in keywords)),
                None,
            )
            return {
                "retrieval.hit_rate": float(RetrievalEvaluator.keyword_recall(contents, keywords, k) > 0),
                "retrieval.recall_at_k": RetrievalEvaluator.keyword_recall(contents, keywords, k),
                "retrieval.mrr": 1.0 / matching_rank if matching_rank else 0.0,
            }
        return {}
