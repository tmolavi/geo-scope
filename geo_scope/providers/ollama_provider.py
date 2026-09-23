"""
Ollama Provider for Local & Open-Source LLMs (DeepSeek, Llama 3, Qwen)
"""

import os
import httpx
from typing import Dict, Any
from geo_scope.providers.base import BaseProvider


class OllamaProvider(BaseProvider):
    def __init__(self, host: str = "http://localhost:11434", model: str = "deepseek-r1:14b"):
        super().__init__(
            name="ollama_local",
            display_name=f"Ollama Local ({model})",
            bias_description="Local open-weight inference without cloud web search grounding",
            cost_per_1k=0.0,
        )
        self.host = os.getenv("OLLAMA_HOST", host).rstrip("/")
        self.model = os.getenv("OLLAMA_MODEL", model)

    async def generate_response(self, prompt_item: Dict[str, Any]) -> str:
        url = f"{self.host}/api/generate"
        prompt_policy = prompt_item.get("prompt_policy", "neutral")
        query = prompt_item.get("query") or prompt_item.get("prompt", "")

        if prompt_policy == "forced_list":
            user_prompt = f"Analyze and recommend solutions with pros/cons and structured lists:\n\n{query}"
        else:
            user_prompt = query

        payload = {
            "model": self.model,
            "prompt": user_prompt,
            "stream": False,
            "options": {"temperature": 0.2, "num_predict": 1024},
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            self.last_evidence = {
                "model": data.get("model", self.model),
                "eval_count": data.get("eval_count"),
                "request_settings": {"temperature": 0.2, "num_predict": 1024},
            }
            return data.get("response", "")
