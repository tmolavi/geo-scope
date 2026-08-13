"""
OpenAI Provider (GPT-4o Direct Completion)
Note: Standard OpenAI /v1/chat/completions provides direct LLM generation based on model knowledge.
Classification: LIVE BUT NOT SEARCH-GROUNDED (Unless piped through an external search tool).
"""

import os
import httpx
from typing import Dict, Any
from geo_scope.providers.base import BaseProvider


class OpenAIProvider(BaseProvider):
    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        super().__init__(
            name="chatgpt_search",
            display_name=f"OpenAI {model} (Direct LLM Completion)",
            bias_description="Pre-trained parametric knowledge & synthesis (Direct LLM completion, not real-time search-grounded)",
            cost_per_1k=7.50
        )
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model

    def is_available(self) -> bool:
        return bool(self.api_key)

    async def generate_response(self, prompt_item: Dict[str, Any]) -> str:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set.")

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert market analyst. Answer user queries with direct recommendations, rankings, comparisons, and cite authoritative sources where known."
                },
                {"role": "user", "content": prompt_item.get("query", "")}
            ],
            "temperature": 0.2
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
