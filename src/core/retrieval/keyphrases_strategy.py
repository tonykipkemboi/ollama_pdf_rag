from collections import Counter
from typing import List

import spacy
from base import RetrievalStrategy, ScoredChunk

# TODO: duplicate in document.py!
nlp = spacy.load("en_core_web_sm")


def extract_content_words(text: str) -> List[str]:
    # TODO: duplicate in document.py!
    """
    Extract content words from text using spaCy.
    Only tokens with POS tags in {NOUN, PROPN, ADJ} are considered.
    Return their lower-case lemmas (including duplicates).
    """
    doc = nlp(text)
    valid_pos = {"NOUN", "PROPN", "ADJ"}
    return [
        token.lemma_.lower()
        for token in doc
        if token.pos_ in valid_pos and token.is_alpha
    ]


def compute_frequency_score(query_words: List[str], chunk_words: List[str]) -> int:
    """
    Compute a frequency-based score as the dot product of query and chunk word counts.
    """
    query_freq = Counter(query_words)
    chunk_freq = Counter(chunk_words)
    # Sum up freq(query_word) * freq(chunk_word) for words in both.
    return sum(query_freq[w] * chunk_freq[w] for w in query_freq if w in chunk_freq)


class KeyphraseRetrievalStrategy(RetrievalStrategy):
    def __init__(self, chunks):
        self.chunks = chunks

    def retrieve(self, query: str, top_k: int) -> List[ScoredChunk]:
        query_words = extract_content_words(query)

        scores = {}
        for chunk in self.chunks:
            chunk_words = chunk.keywords
            score = compute_frequency_score(query_words, chunk_words)
            scores[chunk.id] = score

        sorted_ids = sorted(scores.keys(), key=lambda cid: scores[cid], reverse=True)

        results = []
        for cid in sorted_ids:
            if scores[cid] > 0:
                results.append(ScoredChunk(chunk_id=cid, keyphrase_score=scores[cid]))
            if len(results) == top_k:
                break

        return results
