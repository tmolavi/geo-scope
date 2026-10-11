"""
Google Gemini Provider (Search Grounding Enabled)
Classification: LIVE SEARCH-GROUNDED (Google Search Grounding Tool).
"""

import os
import httpx
from typing import Dict, Any
from geo_scope.providers.base import BaseProvider


class GeminiProvider(BaseProvider):
    def __init__(self, api_key: str = None, model: str = "gemini-2.5-flash"):
        super().__init__(
            name="gemini_grounding",
            display_name=f"Google Gemini ({model})",
            bias_description="Google Search Index, Knowledge Graph & Wikidata",
            cost_per_1k=3.50,
        )
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.response_kind = "search_enabled"
        self.model = os.getenv("GEMINI_MODEL", model)
        self.search_grounded = True
        self.provider_class = "answer_engine"
        self.avalai_mode = bool(self.api_key and self.api_key.startswith("aa-"))

    def is_available(self) -> bool:
        return bool(self.api_key)

    async def generate_response(self, prompt_item: Dict[str, Any]) -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set.")

        query = prompt_item.get("query") or prompt_item.get("prompt", "")

        if self.avalai_mode:
            # Route via AvalAI Google Search Grounded responses API
            url = "https://api.avalai.ir/v1/responses"
            payload = {
                "model": self.model,
                "tools": [{"type": "web_search"}],
                "input": query,
            }
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                content_text = ""
                citations = []
                for item in data.get("output", []):
                    if item.get("type") == "message":
                        msg_content = item.get("content", [{}])[0]
                        content_text = msg_content.get("text", "")
                        for ann in msg_content.get("annotations", []):
                            if ann.get("type") == "url_citation" and ann.get("url"):
                                citations.append(ann["url"])
                
                self.last_evidence = {
                    "grounding_metadata": {"citations": citations},
                    "citations": citations,
                    "usage": data.get("usage", {}),
                    "model": self.model,
                    "raw_payload": data,
                    "request_settings": {"temperature": 0.2, "search_grounded": True},
                }
                if citations:
                    content_text += "\n\n### Grounding Citations:\n"
                    for c in citations:
                        content_text += f"- [Source]({c})\n"
                return content_text

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        payload = {
            "contents": [{"parts": [{"text": query}]}],
            "tools": [{"google_search": {}}],
            "generationConfig": {"temperature": 0.2},
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(url, json=payload, headers={"x-goog-api-key": self.api_key})
            response.raise_for_status()
            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                raise ValueError("Gemini returned no candidates")
            candidate = candidates[0]
            grounding_meta = candidate.get("groundingMetadata", {})
            citations = []
            for chunk in grounding_meta.get("groundingChunks", []):
                web = chunk.get("web", {})
                if web.get("uri"):
                    citations.append(web["uri"])

            self.last_evidence = {
                "grounding_metadata": grounding_meta,
                "citations": citations,
                "usage": data.get("usageMetadata", {}),
                "model": self.model,
                "raw_payload": data,
                "request_settings": {"temperature": 0.2, "search_grounded": True},
            }
            return "\n".join(part.get("text", "") for part in candidate["content"]["parts"])
