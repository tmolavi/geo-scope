"""
Anthropic Claude Provider (Claude 3.5 / 3.7 Sonnet)
"""

import os
import httpx
from typing import Dict, Any
from geo_scope.providers.base import BaseProvider


class ClaudeProvider(BaseProvider):
    def __init__(self, api_key: str = None, model: str = "claude-3-7-sonnet-20250219"):
        super().__init__(
            name="claude_3_7",
            display_name="Anthropic Claude 3.7",
            bias_description="In-depth analytical synthesis, pros/cons balance, technical documentation",
            cost_per_1k=8.00
        )
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.model = model

    def is_available(self) -> bool:
        return bool(self.api_key)

    async def generate_response(self, prompt_item: Dict[str, Any]) -> str:
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set.")

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "max_tokens": 1024,
            "temperature": 0.2,
            "messages": [
                {"role": "user", "content": f"Answer concisely with rankings, comparison tables, and citations:\n\n{prompt_item.get('query', '')}"}
            ]
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"]
