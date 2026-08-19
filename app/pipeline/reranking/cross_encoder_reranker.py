from sentence_transformers import CrossEncoder

from app.core.config import settings


class CrossEncoderReranker:

    def __init__(self):
        self.model = CrossEncoder(settings.reranker_model)

    def score(self, query: str, texts: list[str]) -> list[float]:
        if not texts:
            return []

        pairs = [(query, text) for text in texts]
        return self.model.predict(pairs).tolist()
