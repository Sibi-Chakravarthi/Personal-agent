import ollama
from typing import Generator

class LLM:
    def __init__(self, model: str = "qwen2.5:14b"):
        self.model = model
        self.client = ollama.Client()

    def chat(self, messages: list[dict], stream: bool = False) -> str | Generator:
        response = self.client.chat(
            model=self.model,
            messages=messages,
            stream=stream
        )
        if stream:
            return response
        return response["message"]["content"]

    def is_available(self) -> bool:
        try:
            models = self.client.list()
            return any(self.model in m["name"] for m in models["models"])
        except Exception:
            return False