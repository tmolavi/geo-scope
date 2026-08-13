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
            cost_per_1k=0.0
        )
        self.host = host
        self.model = model

    async def generate_response(self, prompt_item: Dict[str, Any]) -> str:
        url = f"{self.host}/api/generate"
        payload = {
            "model": self.model,
            "prompt": f"Analyze and recommend solutions with pros/cons and structured lists:\n\n{prompt_item.get('query', '')}",
            "stream": False
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
