from dataclasses import dataclass


@dataclass
class RetrievalCandidate:

    chunk: dict

    score: float

    query_type: str

    query_text: str

    index:int

    rerank_score: float = 0.0