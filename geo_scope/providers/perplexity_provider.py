"""
Perplexity AI Provider (Sonar / Sonar Pro Search)
Classification: LIVE SEARCH-GROUNDED (Real-time web crawl & synthesis).
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
            cost_per_1k=5.00,
        )
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY", "")
        self.model = os.getenv("PERPLEXITY_MODEL", model)
        self.response_kind = "search_enabled"
        self.search_grounded = True
        self.provider_class = "answer_engine"

    def is_available(self) -> bool:
        return bool(self.api_key)

    async def generate_response(self, prompt_item: Dict[str, Any]) -> str:
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY is not set.")

        url = "https://api.perplexity.ai/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        prompt_policy = prompt_item.get("prompt_policy", "neutral")
        query = prompt_item.get("query") or prompt_item.get("prompt", "")

        if prompt_policy == "forced_list":
            system_prompt = "You are an accurate, citation-focused search AI. Answer user queries with direct recommendations, bullet points, and source citations."
        else:
            system_prompt = "You are a neutral, citation-focused AI search assistant. Answer the user prompt directly, factually, and objectively with verified citations."

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {"role": "user", "content": query},
            ],
            "temperature": 0.2,
            "return_citations": True,
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            citations = data.get("citations", [])
            self.last_evidence = {
                "citations": citations,
                "model": data.get("model", self.model),
                "usage": data.get("usage", {}),
                "raw_payload": data,
                "request_settings": {"temperature": 0.2, "search_grounded": True},
                "search_results": data.get("search_results", []),
            }
            if citations:
                content += "\n\n### Grounding Citations:\n"
                for c in citations:
                    content += f"- [Source]({c})\n"
            return content
