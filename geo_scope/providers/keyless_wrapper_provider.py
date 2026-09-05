"""Adapter for a user-run OpenAI-compatible local wrapper."""

import os
import httpx
from geo_scope.providers.base import BaseProvider


class KeylessWrapperProvider(BaseProvider):
    """Opt-in local adapter; no hosted endpoint or external key discovery."""

    def __init__(self, host=None, model=None):
        super().__init__(
            "keyless_local",
            "User-run keyless wrapper (DuckDuckGo mediated)",
            "Local OpenAI-compatible wrapper; search grounding is unverified",
        )
        self.host = (host or os.getenv("KEYLESS_WRAPPER_HOST", "http://127.0.0.1:1337")).rstrip("/")
        self.model = model or os.getenv("KEYLESS_WRAPPER_MODEL", "keyless-gpt-4o-mini")
        self.response_kind = "local_wrapper_unverified_search"

    async def generate_response(self, prompt_item):
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt_item.get("query", "")}],
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(f"{self.host}/v1/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
        self.last_evidence = {
            "model": data.get("model", self.model),
            "usage": data.get("usage", {}),
            "request_settings": {"stream": False},
            "grounding": "unverified",
        }
        choices = data.get("choices", [])
        if not choices or not choices[0].get("message", {}).get("content"):
            raise ValueError("keyless wrapper returned no completion")
        return choices[0]["message"]["content"]
