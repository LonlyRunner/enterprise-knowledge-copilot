from dataclasses import dataclass


@dataclass
class EvaluationCase:


    id:str


    question:str


    expected_answer:str


    relevant_chunk_ids:list[str]