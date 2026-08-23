import math
from collections import Counter

from app.rag.models import (
    DocumentChunk,
    SearchResult,
)
from app.rag.tokenizer import (
    SimpleTokenizer,
)


class BM25Retriever:

    def __init__(
        self,
        k1: float = 1.5,
        b: float = 0.75,
    ):
        self.k1 = k1
        self.b = b

        self.tokenizer = (
            SimpleTokenizer()
        )

        self.documents: list[
            DocumentChunk
        ] = []

        self.document_tokens: list[
            list[str]
        ] = []

        self.document_frequencies: dict[
            str,
            int
        ] = {}

        self.avg_document_length = 0.0

    def index(
        self,
        documents: list[DocumentChunk],
    ) -> None:

        self.documents = documents

        self.document_tokens = [
            self.tokenizer.tokenize(
                document.content
            )
            for document in documents
        ]

        if not self.document_tokens:
            self.avg_document_length = 0
            return

        total_length = sum(
            len(tokens)
            for tokens
            in self.document_tokens
        )

        self.avg_document_length = (
            total_length
            / len(self.document_tokens)
        )

        self.document_frequencies = {}

        for tokens in self.document_tokens:

            unique_tokens = set(
                tokens
            )

            for token in unique_tokens:

                self.document_frequencies[
                    token
                ] = (
                    self.document_frequencies.get(
                        token,
                        0,
                    )
                    + 1
                )

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[SearchResult]:

        query_tokens = (
            self.tokenizer.tokenize(
                query
            )
        )

        results = []

        for index, document in enumerate(
            self.documents
        ):

            score = self._score_document(
                query_tokens=query_tokens,
                document_tokens=(
                    self.document_tokens[
                        index
                    ]
                ),
            )

            results.append(
                SearchResult(
                    chunk=document,
                    score=score,
                )
            )

        results.sort(
            key=lambda item: item.score,
            reverse=True,
        )

        return results[:top_k]

    def _score_document(
        self,
        query_tokens: list[str],
        document_tokens: list[str],
    ) -> float:

        if not document_tokens:
            return 0.0

        frequencies = Counter(
            document_tokens
        )

        document_length = len(
            document_tokens
        )

        score = 0.0

        for token in query_tokens:

            frequency = frequencies.get(
                token,
                0,
            )

            if frequency == 0:
                continue

            idf = self._idf(
                token
            )

            numerator = (
                frequency
                * (
                    self.k1
                    + 1
                )
            )

            denominator = (
                frequency
                + self.k1
                * (
                    1
                    - self.b
                    + self.b
                    * (
                        document_length
                        / self.avg_document_length
                    )
                )
            )

            score += (
                idf
                * numerator
                / denominator
            )

        return score

    def _idf(
        self,
        token: str,
    ) -> float:

        total_documents = len(
            self.documents
        )

        document_frequency = (
            self.document_frequencies.get(
                token,
                0,
            )
        )

        return math.log(
            1
            + (
                total_documents
                - document_frequency
                + 0.5
            )
            / (
                document_frequency
                + 0.5
            )
        )