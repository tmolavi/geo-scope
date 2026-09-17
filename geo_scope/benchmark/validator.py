# Provider Validation and Integrity Protection Layer for GEO-Scope Benchmarks
import asyncio
import os
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
import httpx
from pydantic import BaseModel, Field

from geo_scope.providers.hamzad_provider import HamzadProvider
from geo_scope.providers.models import sanitize_sensitive_data


# Display friendly names for common benchmark providers
PROVIDER_DISPLAY_NAMES: Dict[str, str] = {
    "gemini": "Gemini 2.5 Flash",
    "gemini-2.5-flash": "Gemini 2.5 Flash",
    "gemini_grounding": "Gemini 2.5 Flash",
    "openai": "GPT-4o",
    "gpt-4o": "GPT-4o",
    "openai_completion": "GPT-4o",
    "gpt-4o-mini": "GPT-4o Mini",
    "claude": "Claude",
    "claude-3-5-sonnet": "Claude",
    "claude-3-5-sonnet-20241022": "Claude",
    "claude_completion": "Claude",
    "perplexity": "Perplexity",
    "sonar": "Perplexity",
    "sonar-pro": "Perplexity",
    "perplexity_sonar": "Perplexity",
}


class ProviderValidationResult(BaseModel):
    requested: str
    verified_model: Optional[str] = None
    provider: Optional[str] = None
    fallback_detected: bool = False
    status: str = "PENDING"  # "PASS" | "FAIL"
    latency_ms: Optional[float] = None
    status_code: Optional[int] = None
    response_snippet: Optional[str] = None
    error: Optional[str] = None
    validated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def is_valid(self) -> bool:
        return self.status == "PASS" and not self.fallback_detected

    def to_manifest_dict(self) -> Dict[str, Any]:
        """
        Formats record for inclusion in manifest.json provider_validation.
        """
        return {
            "requested": self.requested,
            "verified_model": self.verified_model,
            "provider": self.provider,
            "fallback_detected": self.fallback_detected,
            "status": self.status,
            "latency_ms": self.latency_ms,
            "error": self.error,
            "validated_at": self.validated_at,
        }


def normalize_model_identifier(model: str) -> str:
    """
    Normalizes provider/model strings (e.g. 'gemini-2.5-flash', 'google/gemini-2.5-flash', 'gpt-4o').
    """
    m = model.strip().lower()
    if "/" in m:
        m = m.split("/")[-1]
    return m


def models_match(requested: str, actual: str) -> bool:
    """
    Checks whether actual returned model matches the requested model specification.
    """
    if not actual:
        return False

    req_norm = normalize_model_identifier(requested)
    act_norm = normalize_model_identifier(actual)

    if req_norm == act_norm:
        return True

    # Common canonical mappings & aliases
    aliases = {
        "gemini-2.5-flash": ["gemini", "gemini-2.5-flash", "models/gemini-2.5-flash", "gemini_grounding"],
        "gemini-1.5-flash": ["gemini-1.5-flash", "models/gemini-1.5-flash"],
        "gpt-4o": ["openai", "gpt-4o", "gpt-4o-2024-05-13", "gpt-4o-2024-08-06", "openai_completion"],
        "gpt-4o-mini": ["gpt-4o-mini", "gpt-4o-mini-2024-07-18"],
        "claude-3-5-sonnet": ["claude", "claude-3-5-sonnet-20241022", "claude-3-5-sonnet-20240620", "claude-3-5-sonnet", "claude_completion"],
        "claude-3-7-sonnet": ["claude-3-7-sonnet-20250219", "claude-3-7-sonnet"],
        "sonar": ["perplexity", "sonar", "perplexity_sonar"],
        "sonar-pro": ["sonar-pro", "perplexity_sonar"],
    }

    for canon, syns in aliases.items():
        if (req_norm == canon or req_norm in syns) and (act_norm == canon or act_norm in syns):
            return True

    return False


class ProviderValidator:
    """
    Integrity protection and pre-flight validation engine for benchmark providers.
    Verifies that providers resolve to genuine target models through Hamzad Gateway
    without falling back to placeholder or surrogate models (e.g. qwen).
    """

    def __init__(
        self,
        gateway_url: Optional[str] = None,
        project_id: Optional[str] = None,
        api_key: Optional[str] = None,
        client: Optional[httpx.AsyncClient] = None,
        timeout: float = 15.0,
    ):
        self.gateway_url = (gateway_url or os.getenv("HAMZAD_GATEWAY_URL", "https://api.molavi.pro")).rstrip("/")
        self.project_id = project_id or os.getenv("HAMZAD_PROJECT_ID", "hamzad")
        self.api_key = api_key or os.getenv("HAMZAD_API_KEY") or os.getenv("HAMZAD_MASTER_API_KEY")
        self.client = client
        self.timeout = timeout

    async def validate_provider(
        self,
        provider_or_model: str,
        prompt: str = "Reply with exactly OK.",
    ) -> ProviderValidationResult:
        """
        Sends a single smoke query to validate provider routing, model identity, and fallback state.
        """
        provider_adapter = HamzadProvider(
            name=f"hamzad_{provider_or_model}",
            target_provider=provider_or_model,
            target_model=provider_or_model,
            gateway_url=self.gateway_url,
            project_id=self.project_id,
            api_key=self.api_key,
            client=self.client,
            timeout=self.timeout,
        )

        prompt_item = {
            "prompt": prompt,
            "task_type": "geo_scope_validation",
            "model": provider_or_model,
            "fallback_allowed": False,
            "max_tokens": 8,
            "temperature": 0.0,
        }

        t0 = time.time()
        try:
            resp_obj = await provider_adapter.generate(prompt_item, execution_mode="live")
            latency_ms = round((time.time() - t0) * 1000, 2)
        except Exception as exc:
            latency_ms = round((time.time() - t0) * 1000, 2)
            return ProviderValidationResult(
                requested=provider_or_model,
                status="FAIL",
                latency_ms=latency_ms,
                error=f"Connection or execution error: {str(exc)}",
            )

        raw = resp_obj.raw or {}
        meta = raw.get("meta") or resp_obj.metadata.get("meta") or {}
        actual_model = meta.get("actual_model") or raw.get("model") or resp_obj.model
        resp_provider = raw.get("provider") or resp_obj.provider
        fallback_active = meta.get("fallback_active", False)

        result = ProviderValidationResult(
            requested=provider_or_model,
            verified_model=actual_model,
            provider=resp_provider,
            fallback_detected=bool(fallback_active),
            latency_ms=latency_ms,
            response_snippet=resp_obj.text[:100] if resp_obj.text else None,
        )

        # Integrity Check 1: Provider failure
        if not resp_obj.is_success():
            result.status = "FAIL"
            result.error = resp_obj.error.get("message") if resp_obj.error else "Inference returned failure"
            return result

        # Integrity Check 2: Fallback active
        if fallback_active:
            result.status = "FAIL"
            result.error = f"fallback detected (routed to {actual_model} via {resp_provider})"
            return result

        # Integrity Check 3: Model mismatch
        if not models_match(provider_or_model, actual_model):
            result.status = "FAIL"
            result.error = f"model mismatch: requested '{provider_or_model}' but received '{actual_model}'"
            return result

        # Passed all integrity criteria
        result.status = "PASS"
        return result

    async def validate_all(
        self,
        providers: List[str],
        prompt: str = "Reply with exactly OK.",
    ) -> Dict[str, ProviderValidationResult]:
        """
        Validates multiple providers sequentially to prevent concurrency spikes or transient rate limits.
        """
        results: Dict[str, ProviderValidationResult] = {}
        for p in providers:
            res = await self.validate_provider(p, prompt=prompt)
            results[p] = res
            await asyncio.sleep(0.1)
        return results

    def format_report(self, results: Dict[str, ProviderValidationResult]) -> str:
        """
        Formats validation results into the standard Provider Validation Report.
        """
        lines = ["Provider Validation Report\n"]
        for p, res in results.items():
            display_name = PROVIDER_DISPLAY_NAMES.get(p, p)
            lines.append(display_name)
            if res.is_valid():
                lines.append("PASS\n")
            else:
                if res.fallback_detected:
                    lines.append("FAILED - fallback detected\n")
                else:
                    lines.append(f"FAILED - {res.error or 'validation failed'}\n")

        return "\n".join(lines).strip()
