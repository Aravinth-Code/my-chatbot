from openai import OpenAI

from app.core.config import settings


class OpenAIEmbeddings:

    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.embedding_model
        self.batch_size = settings.embedding_batch_size

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        embeddings: list[list[float]] = []
        for start in range(0, len(texts), self.batch_size):
            batch = texts[start:start + self.batch_size]
            embeddings.extend(self._embed_batch(batch))

        return embeddings

    def _embed_batch(self, batch: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(
            model=self.model,
            input=batch,
        )
        return [item.embedding for item in response.data]
