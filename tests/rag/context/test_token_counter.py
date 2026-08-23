from app.rag.context import TokenCounter


def test_count_empty_text_returns_zero():
    counter = TokenCounter()

    assert counter.count_text("") == 0
    assert counter.count_text(None) == 0


def test_count_text_returns_positive_tokens():
    counter = TokenCounter()

    tokens = counter.count_text(
        "4000元报销需要哪些人审批？"
    )

    assert tokens > 0


def test_longer_text_uses_more_tokens():
    counter = TokenCounter()

    short_tokens = counter.count_text(
        "那超过两万呢？"
    )

    long_tokens = counter.count_text(
        "单笔报销金额超过20000元需要哪些人员审批？"
    )

    assert long_tokens > short_tokens