from abc import ABC, abstractmethod
from typing import List


class QueryExpansionStrategy(ABC):
    """
    Abstract base class for all query expansion strategies.
    """

    @abstractmethod
    def expand_query(self, query: str) -> str or List[str]:
        """
        Given a user query, return an expanded (or compressed, paraphrased, etc.)
        version of the query.
        """
        pass
