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
