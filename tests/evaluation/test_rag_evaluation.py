from app.evaluation.retrieval import RetrievalEvaluator


async def test_recall():

    evaluator = RetrievalEvaluator()


    score=evaluator.recall_at_k(
        [
            "chunk1",
            "chunk2"
        ],
        [
            "chunk1"
        ],
        2
    )


    assert score == 1