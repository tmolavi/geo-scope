"""Official free-model access using the user's own OpenRouter account."""

import os
import httpx
from geo_scope.providers.base import BaseProvider


class OpenRouterProvider(BaseProvider):
    def __init__(self):
        super().__init__("openrouter_free", "OpenRouter free models (Direct Completion)")
        self.api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.model = os.getenv("OPENROUTER_MODEL", "openrouter/free")

    def is_available(self):
        return bool(self.api_key)

    async def generate_response(self, prompt_item):
        if not self.is_available():
            raise ValueError("OPENROUTER_API_KEY is required")
        if self.model != "openrouter/free" and not self.model.endswith(":free"):
            raise ValueError("Select a :free model or openrouter/free")
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt_item["query"]}],
                    "temperature": 0.2,
                    "max_tokens": 2048,
                },
            )
            response.raise_for_status()
            data = response.json()
        self.last_evidence = {
            "resolved_model": data.get("model"),
            "usage": data.get("usage", {}),
            "request_settings": {"temperature": 0.2, "max_tokens": 2048},
        }
        return data["choices"][0]["message"]["content"]
