"""
Perplexity AI Provider (Sonar / Sonar Pro Search)
"""

import os
import httpx
from typing import Dict, Any
from geo_scope.providers.base import BaseProvider


class PerplexityProvider(BaseProvider):
    def __init__(self, api_key: str = None, model: str = "sonar-pro"):
        super().__init__(
            name="perplexity_sonar",
            display_name=f"Perplexity ({model})",
            bias_description="Real-time multi-source crawl, Reddit UGC & review density",
            cost_per_1k=5.00
        )
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY", "")
        self.model = model

    def is_available(self) -> bool:
        return bool(self.api_key)

    async def generate_response(self, prompt_item: Dict[str, Any]) -> str:
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY is not set.")

        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an accurate, citation-focused search AI. Answer user queries with direct recommendations, bullet points, and source citations."
                },
                {"role": "user", "content": prompt_item.get("query", "")}
            ],
            "temperature": 0.2,
            "return_citations": True
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            citations = data.get("citations", [])
            if citations:
                content += "\n\n### Grounding Citations:\n"
                for c in citations:
                    content += f"- [Source]({c})\n"
            return content
