from typing import List

from base import RetrievalStrategy, ScoredChunk


class EmbeddingsRetrievalStrategy(RetrievalStrategy):
    def __init__(self, vector_store):
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int) -> List[ScoredChunk]:
        results = self.vector_store.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["distances"],
        )

        # Flatten the nested lists of ids and distances.
        ids = sum(results.get("ids", []), [])
        distances = sum(results.get("distances", []), [])

        retrieved_chunks = []
        for cid, distance in zip(ids, distances):
            retrieved_chunks.append(ScoredChunk(chunk_id=cid, embedding_score=distance))

        return retrieved_chunks
