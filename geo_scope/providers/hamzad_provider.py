"""
Hamzad Gateway Provider Adapter for GEO-Scope.
Classification: GATEWAY PROXIED (Hamzad AI Gateway).

Routes model execution requests to the centralized Hamzad AI Gateway.
Security Guarantee:
- GEO-Scope stores NO provider API keys (OpenAI, Gemini, Anthropic, Perplexity, etc.).
- All provider credentials, key rotation, and balance isolation remain securely inside Hamzad Gateway.
"""

import os
import httpx
from typing import Dict, Any, List, Optional
from geo_scope.providers.base import BaseProvider


DEFAULT_MODEL_MAP = {
    "gemini": "gemini-2.5-flash",
    "openai": "gpt-4o-mini",
    "claude": "anthropic/claude-3.5-sonnet",
    "perplexity": "sonar-pro",
    "groq": "qwen/qwen3.8-27b",
    "avalai": "gpt-4o-mini",
    "openrouter": "anthropic/claude-3.5-sonnet",
    "gapgpt": "gpt-5-nano",
    "local": "qwen2.5:1.5b-fast",
    "hamzad-fast": "hamzad-fast",
}


class HamzadProvider(BaseProvider):
    """
    Adapter that connects GEO-Scope to the existing Hamzad AI Gateway
    for secure, multi-provider inference without local secret storage.
    """

    def __init__(
        self,
        name: str = "hamzad_gateway",
        display_name: Optional[str] = None,
        target_provider: str = "gemini",
        target_model: Optional[str] = None,
        gateway_url: Optional[str] = None,
        api_key: Optional[str] = None,
        project_id: Optional[str] = None,
        timeout: float = 60.0,
        cost_per_1k: float = 1.0,
        search_grounded: Optional[bool] = None,
        client: Optional[httpx.AsyncClient] = None,
    ):
        model = target_model or DEFAULT_MODEL_MAP.get(target_provider, "gemini-2.5-flash")
        disp = display_name or f"Hamzad Gateway ({target_provider} / {model})"
        bias = f"Hamzad AI Gateway route -> {target_provider} ({model})"
        
        super().__init__(
            name=name,
            display_name=disp,
            bias_description=bias,
            cost_per_1k=cost_per_1k,
        )

        self.target_provider = target_provider
        self.target_model = model
        self.model = model
        self.gateway_url = (gateway_url or os.getenv("HAMZAD_GATEWAY_URL", "https://api.molavi.pro")).rstrip("/")
        self.api_key = api_key or os.getenv("HAMZAD_API_KEY") or os.getenv("HAMZAD_MASTER_API_KEY", "")
        self.project_id = project_id or os.getenv("HAMZAD_PROJECT_ID", "hamzad")
        self.timeout = float(os.getenv("HAMZAD_TIMEOUT", str(timeout)))
        self.connect_timeout = float(os.getenv("HAMZAD_CONNECT_TIMEOUT", "5.0"))
        self.response_kind = "gateway_proxied"
        self._client = client
        
        if search_grounded is not None:
            self.search_grounded = search_grounded
        else:
            self.search_grounded = target_provider in ("gemini", "perplexity")

    def is_available(self) -> bool:
        """
        Hamzad Gateway is available if a gateway URL is defined.
        No provider API keys are required locally in GEO-Scope.
        """
        return bool(self.gateway_url)

    async def check_health(self) -> Dict[str, Any]:
        """
        Performs a health check against the Hamzad Gateway.
        """
        if not self.gateway_url:
            return {"ok": False, "error": "HAMZAD_GATEWAY_URL not configured"}

        timeout_obj = httpx.Timeout(self.timeout, connect=min(self.connect_timeout, self.timeout))
        last_err = None
        for path in ["/gateway/health", "/health", "/"]:
            url = f"{self.gateway_url}{path}"
            try:
                if self._client is not None:
                    resp = await self._client.get(url)
                else:
                    async with httpx.AsyncClient(timeout=timeout_obj) as client:
                        resp = await client.get(url)
                if resp.status_code == 200:
                    return {
                        "ok": True,
                        "status_code": resp.status_code,
                        "path": path,
                        "gateway_url": self.gateway_url,
                        "response": resp.json() if "application/json" in resp.headers.get("content-type", "") else resp.text[:200],
                    }
            except Exception as e:
                last_err = e

        return {
            "ok": False,
            "error": str(last_err) if last_err else "Health endpoint returned non-200",
            "gateway_url": self.gateway_url,
        }

    async def smoke_check(self, prompt: str = "Reply with exactly OK.", model: str = "hamzad-fast") -> Dict[str, Any]:
        """
        Runs a minimal single-request smoke check against Hamzad Gateway.
        """
        prompt_item = {
            "prompt": prompt,
            "task_type": "geo_scope_smoke",
            "model": model,
            "max_tokens": 8,
            "temperature": 0,
        }
        resp_obj = await self.generate(prompt_item, execution_mode="live")
        return {
            "ok": resp_obj.is_success(),
            "status": resp_obj.status,
            "text": resp_obj.text,
            "latency_ms": resp_obj.latency_ms,
            "model": resp_obj.model,
            "provider": resp_obj.provider,
            "error": resp_obj.error,
            "metadata": resp_obj.metadata,
        }

    async def generate_response(self, prompt_item: Dict[str, Any]) -> str:
        """
        Sends prompt to Hamzad Gateway /api/models/generate and parses the response.
        """
        if not self.gateway_url:
            raise ValueError("HAMZAD_GATEWAY_URL is not configured.")

        query = prompt_item.get("query") or prompt_item.get("prompt", "")
        if not query:
            raise ValueError("Empty prompt query provided.")

        provider = prompt_item.get("provider") or self.target_provider
        model = prompt_item.get("model") or self.target_model
        task_type = prompt_item.get("task_type", "geo_scope_smoke" if model == "hamzad-fast" else "geo_audit")
        max_tokens = prompt_item.get("max_tokens", 8 if "smoke" in str(task_type) else 2000)
        temperature = prompt_item.get("temperature", 0.0 if "smoke" in str(task_type) else 0.7)

        endpoint = f"{self.gateway_url}/api/models/generate"
        payload = {
            "task_type": task_type,
            "project_id": self.project_id,
            "prompt": query,
            "model": model,
            "fallback_allowed": prompt_item.get("fallback_allowed", False),
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if provider and provider not in ("hamzad_gateway", "hamzad"):
            payload["provider"] = provider

        headers = {
            "Content-Type": "application/json",
            "X-Project-ID": self.project_id,
        }
        if self.api_key:
            headers["X-API-Key"] = self.api_key

        timeout_obj = httpx.Timeout(self.timeout, connect=min(self.connect_timeout, self.timeout))
        if self._client is not None:
            response = await self._client.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
        else:
            async with httpx.AsyncClient(timeout=timeout_obj) as client:
                response = await client.post(endpoint, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

        if isinstance(data, dict) and data.get("ok") is False:
            error_type = data.get("error_type", "GATEWAY_ERROR")
            details = data.get("details", error_type)
            raise RuntimeError(f"Hamzad Gateway returned error: {error_type} - {details}")

        # Extract generated content
        content = ""
        if isinstance(data, dict):
            content = data.get("content", "")
            if not content and "choices" in data and isinstance(data["choices"], list) and data["choices"]:
                content = data["choices"][0].get("message", {}).get("content", "")
        elif isinstance(data, str):
            content = data

        if not content:
            raise ValueError("Hamzad Gateway returned an empty response.")

        # Extract citations / metadata
        meta = data.get("meta", {}) if isinstance(data, dict) else {}
        actual_model = meta.get("actual_model") or (data.get("model") if isinstance(data, dict) else model)
        actual_provider = meta.get("actual_provider") or (data.get("provider") if isinstance(data, dict) else provider)
        usage = data.get("usage", {}) if isinstance(data, dict) else {}
        citations = data.get("citations", []) if isinstance(data, dict) else []

        self.last_evidence = {
            "gateway_url": self.gateway_url,
            "requested_provider": provider,
            "requested_model": model,
            "actual_provider": actual_provider,
            "actual_model": actual_model,
            "model": actual_model,
            "usage": usage,
            "citations": citations,
            "meta": meta,
            "raw_payload": data if isinstance(data, dict) else {"text": data},
            "latency": meta.get("latency", 0.0),
        }

        return content

    @classmethod
    def for_provider(
        cls,
        target_provider: str,
        target_model: Optional[str] = None,
        **kwargs,
    ) -> "HamzadProvider":
        """
        Convenience factory for instantiating a HamzadProvider for a specific backend provider.
        """
        model = target_model or DEFAULT_MODEL_MAP.get(target_provider, "gemini-2.5-flash")
        name = f"hamzad_{target_provider}"
        disp = f"Hamzad Gateway ({target_provider} / {model})"
        return cls(
            name=name,
            display_name=disp,
            target_provider=target_provider,
            target_model=model,
            **kwargs,
        )
