"""
Google Gemini Provider (Search Grounding Enabled)
"""

import os
import httpx
from typing import Dict, Any
from geo_scope.providers.base import BaseProvider


class GeminiProvider(BaseProvider):
    def __init__(self, api_key: str = None, model: str = "gemini-1.5-pro"):
        super().__init__(
            name="gemini_grounding",
            display_name=f"Google Gemini ({model})",
            bias_description="Google Search Index, Knowledge Graph & Wikidata",
            cost_per_1k=3.50
        )
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model = model

    def is_available(self) -> bool:
        return bool(self.api_key)

    async def generate_response(self, prompt_item: Dict[str, Any]) -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt_item.get("query", "")}]}],
            "tools": [{"google_search": {}}],
            "generationConfig": {"temperature": 0.2}
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return "No response returned from Gemini."
            return candidates[0]["content"]["parts"][0]["text"]
