from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import BaseModel


class ScoredChunk(BaseModel):
    chunk_id: str
    embedding_score: Optional[float] = None
    keyphrase_score: Optional[float] = None
    combined_score: Optional[float] = None


class RetrievalStrategy(ABC):
    @abstractmethod
    def retrieve(self, query: str, top_k: int) -> List[ScoredChunk]:
        pass
