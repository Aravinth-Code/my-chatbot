import math

from app.core.config import settings
from app.models.document_chunks import DocumentChunk


class MMRSelector:

    def __init__(self):
        self.lambda_param = settings.mmr_lambda

    def select(
        self,
        query_embedding: list[float],
        candidates: list[tuple[DocumentChunk, float]],
        top_k: int,
    ) -> list[tuple[DocumentChunk, float]]:
        remaining = list(candidates)
        selected: list[tuple[DocumentChunk, float]] = []

        while remaining and len(selected) < top_k:
            best_index = max(
                range(len(remaining)),
                key=lambda i: self._mmr_score(query_embedding, remaining[i][0], selected),
            )
            selected.append(remaining.pop(best_index))

        return selected

    def _mmr_score(
        self,
        query_embedding: list[float],
        candidate: DocumentChunk,
        selected: list[tuple[DocumentChunk, float]],
    ) -> float:
        relevance = self._cosine_similarity(candidate.embedding, query_embedding)

        if not selected:
            redundancy = 0.0
        else:
            redundancy = max(
                self._cosine_similarity(candidate.embedding, other.embedding)
                for other, _ in selected
            )

        return self.lambda_param * relevance - (1 - self.lambda_param) * redundancy

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
