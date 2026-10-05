"""Hugging Face Inference Providers adapter.

The adapter uses the OpenAI-compatible Hugging Face router.  Credentials are
read only from the local environment and are never included in evidence,
metadata, or error messages.
"""

import os
from typing import Any, Dict

import httpx

from geo_scope.providers.base import BaseProvider


class HuggingFaceProvider(BaseProvider):
    """Run an instruct model through Hugging Face Inference Providers.

    This is intentionally opt-in: the public demos remain keyless and
    deterministic, while a live run uses the caller's own HF account/token.
    """

    def __init__(self):
        model = os.getenv("HF_MODEL", "Qwen/Qwen2.5-7B-Instruct")
        super().__init__(
            name="huggingface_inference",
            display_name=f"Hugging Face Inference ({model})",
            bias_description="User-account inference through Hugging Face; not web-search grounded",
            cost_per_1k=0.0,
        )
        self.api_key = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN", "")
        self.model = model
        self.endpoint = os.getenv(
            "HF_INFERENCE_ENDPOINT",
            "https://router.huggingface.co/v1/chat/completions",
        )

    def is_available(self) -> bool:
        return bool(self.api_key)

    async def generate_response(self, prompt_item: Dict[str, Any]) -> str:
        if not self.is_available():
            raise ValueError("HF_TOKEN is required for Hugging Face live inference")

        query = prompt_item.get("query") or prompt_item.get("prompt", "")
        system = (
            "Answer neutrally and factually. Do not invent citations or claim "
            "web access. If evidence is unavailable, say so clearly."
        )
        if prompt_item.get("prompt_policy") == "forced_list":
            system += " Use a numbered list when the question asks for recommendations."

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": query},
            ],
            "temperature": 0.2,
            "max_tokens": 1024,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(self.endpoint, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        choices = data.get("choices") or []
        if not choices or not choices[0].get("message", {}).get("content"):
            raise ValueError("Hugging Face returned an empty completion")

        # Keep only non-secret provenance. The raw payload is sanitized again
        # by BaseProvider before it enters the measurement bundle.
        self.last_evidence = {
            "model": data.get("model", self.model),
            "requested_model": self.model,
            "actual_model": data.get("model", self.model),
            "requested_provider": "huggingface_inference",
            "actual_provider": "huggingface_inference",
            "usage": data.get("usage", {}),
            "request_settings": {"temperature": 0.2, "max_tokens": 1024},
        }
        return choices[0]["message"]["content"]
