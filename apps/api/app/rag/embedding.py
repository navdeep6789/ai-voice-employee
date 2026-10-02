from abc import ABC, abstractmethod
from typing import List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class EmbeddingProvider(ABC):
    """Abstract base class for vector/lexical embeddings in the RAG pipeline."""

    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        pass

    @abstractmethod
    def embed_query(self, query: str) -> List[float]:
        pass

    @abstractmethod
    def compute_similarity(self, query_vec: List[float], doc_vecs: List[List[float]]) -> List[float]:
        pass


class LocalHybridEmbeddingProvider(EmbeddingProvider):
    """
    High-speed, offline, deterministic embedding engine using TF-IDF + n-gram vectorization.
    Requires zero external API calls or paid services, ensuring complete privacy and free local operation.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            max_features=2048,
            norm="l2"
        )
        self.is_fitted = False
        self._corpus: List[str] = []

    def fit_corpus(self, texts: List[str]):
        if not texts:
            return
        self._corpus = texts
        self.vectorizer.fit(texts)
        self.is_fitted = True

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not self.is_fitted:
            self.fit_corpus(texts)
        matrix = self.vectorizer.transform(texts)
        return matrix.toarray().tolist()

    def embed_query(self, query: str) -> List[float]:
        if not self.is_fitted and self._corpus:
            self.fit_corpus(self._corpus)
        if not self.is_fitted:
            # Fallback uniform vector if not yet fitted
            return [0.0] * 10
        matrix = self.vectorizer.transform([query])
        return matrix.toarray()[0].tolist()

    def compute_similarity(self, query_vec: List[float], doc_vecs: List[List[float]]) -> List[float]:
        if not doc_vecs or not query_vec:
            return []
        q_arr = np.array([query_vec])
        d_arr = np.array(doc_vecs)
        scores = cosine_similarity(q_arr, d_arr)[0]
        return scores.tolist()


# Global singleton instance for local embedding
local_embedding_engine = LocalHybridEmbeddingProvider()
