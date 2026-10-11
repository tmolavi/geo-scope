"""
OpenAI Provider (GPT-4o Direct Completion)
Note: Standard OpenAI /v1/chat/completions provides direct LLM generation based on model knowledge.
Classification: LIVE BUT NOT SEARCH-GROUNDED (Direct API completion, parametric knowledge).
"""

import os
import httpx
from typing import Dict, Any
from geo_scope.providers.base import BaseProvider


class OpenAIProvider(BaseProvider):
    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        super().__init__(
            name="openai_completion",
            display_name=f"OpenAI {model} (Direct LLM Completion)",
            bias_description="Pre-trained parametric knowledge & synthesis (Direct LLM completion, not real-time search-grounded)",
            cost_per_1k=7.50,
        )
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("OPENAI_MODEL", model)
        self.avalai_mode = bool(self.api_key and self.api_key.startswith("aa-"))
        if self.avalai_mode:
            self.search_grounded = True
            self.provider_class = "answer_engine"
            self.response_kind = "search_enabled"
            self.display_name = f"ChatGPT Search ({self.model} Web)"
        else:
            self.search_grounded = False
            self.provider_class = "llm"
            self.response_kind = "direct_completion"

    def is_available(self) -> bool:
        return bool(self.api_key)

    async def generate_response(self, prompt_item: Dict[str, Any]) -> str:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set.")

        prompt_policy = prompt_item.get("prompt_policy", "neutral")
        query = prompt_item.get("query") or prompt_item.get("prompt", "")

        if self.avalai_mode:
            # Route via AvalAI ChatGPT Search responses API
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
                    "citations": citations,
                    "model": data.get("model", self.model),
                    "usage": data.get("usage", {}),
                    "raw_payload": data,
                    "request_settings": {"temperature": 0.2, "search_grounded": True},
                }
                if citations:
                    content_text += "\n\n### Grounding Citations:\n"
                    for c in citations:
                        content_text += f"- [Source]({c})\n"
                return content_text

        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        if prompt_policy == "forced_list":
            system_prompt = "You are an expert market analyst. Answer user queries with direct recommendations, rankings, comparisons, and cite authoritative sources where known."
        else:
            system_prompt = "You are a neutral AI assistant. Answer the user prompt directly, factually, and objectively without bias."

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
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            self.last_evidence = {
                "model": data.get("model", self.model),
                "usage": data.get("usage", {}),
                "citations": [],
                "raw_payload": data,
                "request_settings": {"temperature": 0.2, "search_grounded": False},
            }
            return content
