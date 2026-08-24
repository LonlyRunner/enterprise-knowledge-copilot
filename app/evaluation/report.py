from dataclasses import dataclass



@dataclass
class EvaluationReport:


    recall_at_k:float


    precision_at_k:float


    mrr:float


    faithfulness:float


    relevance:float