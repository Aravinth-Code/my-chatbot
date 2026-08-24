from openai import OpenAI

from app.core.config import settings


class OpenAIChat:

    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.chat_model
        self.temperature = settings.chat_temperature

    def complete(self, messages: list[dict[str, str]]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=messages,
        )
        return response.choices[0].message.content
