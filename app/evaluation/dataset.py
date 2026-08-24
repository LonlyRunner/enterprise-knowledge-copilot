import json

from pathlib import Path

from app.evaluation.models import (
    EvaluationCase,
)



class EvaluationDataset:


    def load(
        self,
        path:str,
    ) -> list[EvaluationCase]:


        data=json.loads(
            Path(path)
            .read_text(
                encoding="utf-8"
            )
        )


        return [
            EvaluationCase(
                id=item["id"],
                question=item["question"],
                expected_answer=item["expected_answer"],
                relevant_chunk_ids=item[
                    "relevant_chunk_ids"
                ],
            )
            for item in data
        ]