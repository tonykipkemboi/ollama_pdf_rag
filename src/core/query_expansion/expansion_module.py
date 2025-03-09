from typing import List, Union

from .base import QueryExpansionStrategy


class QueryExpansionModule:
    """
    A class that uses a chosen QueryExpansionStrategy to expand user queries.
    """

    def __init__(self, strategy: QueryExpansionStrategy):
        self.strategy = strategy

    def set_strategy(self, strategy: QueryExpansionStrategy):
        self.strategy = strategy

    def expand_query(self, query: str) -> Union[str, List[str]]:
        return self.strategy.expand_query(query)
