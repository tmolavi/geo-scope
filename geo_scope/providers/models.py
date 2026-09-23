"""
Data models and normalization contracts for AI Search & LLM Providers.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import copy


SENSITIVE_KEYS = {
    "api_key",
    "apikey",
    "authorization",
    "auth",
    "token",
    "secret",
    "password",
    "x-api-key",
    "x-goog-api-key",
    "bearer",
}


def sanitize_sensitive_data(item: Any) -> Any:
    """
    Recursively strips API keys, bearer tokens, and secrets from payloads and metadata.
    """
    if isinstance(item, dict):
        sanitized = {}
        for k, v in item.items():
            if str(k).lower() in SENSITIVE_KEYS:
                continue
            if isinstance(v, str) and ("bearer " in v.lower() or "sk-" in v.lower()):
                continue
            sanitized[k] = sanitize_sensitive_data(v)
        return sanitized
    elif isinstance(item, list):
        return [sanitize_sensitive_data(v) for v in item]
    return item


@dataclass
class ProviderResponse:
    """
    Standardized, normalized response produced by all GEO-Scope provider adapters.
    Adheres strictly to the scientific measurement contract.
    """
    provider: str
    model: str
    execution_mode: str
    provider_class: str = "llm"  # "llm" | "answer_engine" | "recorded"
    text: str = ""
    citations: List[str] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    latency_ms: float = 0.0
    usage: Dict[str, Any] = field(default_factory=dict)
    status: str = "success"  # 'success' | 'failed'
    error: Optional[Dict[str, Any]] = None

    # Scientific Measurement Contract fields
    prompt_policy: str = "neutral"  # "neutral" | "forced_list"
    requested_provider: Optional[str] = None
    requested_model: Optional[str] = None
    actual_provider: Optional[str] = None
    actual_model: Optional[str] = None
    search_grounded: Optional[bool] = None
    prompt_language: str = "unknown"
    country_iso: str = "unknown"
    locale: str = "unknown"
    region: str = "unknown"
    repeat_index: int = 0
    comparison_batch_id: Optional[str] = None
    comparison_window_started_at: Optional[str] = None
    comparison_window_completed_at: Optional[str] = None

    # Cost accounting
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    provider_reported_cost: Optional[float] = None
    cost_status: str = "unreported"  # "reported" | "unreported" | "estimated_external"

    def __post_init__(self):
        # Guarantee no secrets ever leak into raw payload or metadata
        self.raw = sanitize_sensitive_data(self.raw)
        self.metadata = sanitize_sensitive_data(self.metadata)
        if self.citations is None:
            self.citations = []
        if self.requested_provider is None:
            self.requested_provider = self.metadata.get("requested_provider", self.provider)
        if self.actual_provider is None:
            self.actual_provider = self.metadata.get("actual_provider", self.provider)
        if self.requested_model is None:
            self.requested_model = self.metadata.get("requested_model", self.model)
        if self.actual_model is None:
            self.actual_model = self.metadata.get("actual_model", self.model)
        if self.search_grounded is None:
            self.search_grounded = self.metadata.get("search_grounded", self.provider_class == "answer_engine")

        # Extract tokens from usage if available
        if self.usage:
            if self.input_tokens is None:
                self.input_tokens = self.usage.get("prompt_tokens") or self.usage.get("input_tokens")
            if self.output_tokens is None:
                self.output_tokens = self.usage.get("completion_tokens") or self.usage.get("output_tokens")
            if self.total_tokens is None:
                self.total_tokens = self.usage.get("total_tokens") or (
                    (self.input_tokens or 0) + (self.output_tokens or 0) if (self.input_tokens or self.output_tokens) else None
                )
            if self.provider_reported_cost is None and "cost" in self.usage:
                self.provider_reported_cost = float(self.usage["cost"])
                self.cost_status = "reported"

    def is_success(self) -> bool:
        return self.status == "success"

    def is_failed(self) -> bool:
        return self.status == "failed"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "provider_class": self.provider_class,
            "execution_mode": self.execution_mode,
            "prompt_policy": self.prompt_policy,
            "requested_provider": self.requested_provider,
            "actual_provider": self.actual_provider,
            "requested_model": self.requested_model,
            "actual_model": self.actual_model,
            "search_grounded": self.search_grounded,
            "text": self.text,
            "citations": self.citations,
            "raw": self.raw,
            "metadata": self.metadata,
            "latency_ms": self.latency_ms,
            "usage": self.usage,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "provider_reported_cost": self.provider_reported_cost,
            "cost_status": self.cost_status,
            "prompt_language": self.prompt_language,
            "country_iso": self.country_iso,
            "locale": self.locale,
            "region": self.region,
            "repeat_index": self.repeat_index,
            "comparison_batch_id": self.comparison_batch_id,
            "comparison_window_started_at": self.comparison_window_started_at,
            "comparison_window_completed_at": self.comparison_window_completed_at,
            "status": self.status,
            "error": self.error,
        }

    def to_raw_record(
        self,
        experiment_id: str,
        run_id: str,
        prompt_id: str,
        prompt: str,
        timestamp: Optional[str] = None,
        extra_fields: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Builds the canonical raw persistence record for auditability.
        Guarantees strict provenance, explicit locale, repeat index, and temporal window IDs.
        """
        ts = timestamp or datetime.now(timezone.utc).isoformat()
        extra = extra_fields or {}

        # Fallback to unknown if locale fields not provided (never infer silently)
        prompt_language = extra.get("language") or self.prompt_language or "unknown"
        country_iso = extra.get("country_iso") or self.country_iso or "unknown"
        locale = extra.get("locale") or self.locale or "unknown"
        region = extra.get("region") or self.region or "unknown"
        prompt_policy = extra.get("prompt_policy") or self.prompt_policy or "neutral"
        repeat_index = extra.get("repeat_index", self.repeat_index)
        comparison_batch_id = extra.get("comparison_batch_id") or self.comparison_batch_id
        comparison_window_started_at = extra.get("comparison_window_started_at") or self.comparison_window_started_at
        comparison_window_completed_at = extra.get("comparison_window_completed_at") or self.comparison_window_completed_at

        return {
            "experiment_id": experiment_id,
            "run_id": run_id,
            "prompt_id": prompt_id,
            "prompt": prompt,
            "prompt_policy": prompt_policy,
            "provider": self.provider,
            "requested_provider": self.requested_provider or self.provider,
            "actual_provider": self.actual_provider or self.provider,
            "model": self.model,
            "requested_model": self.requested_model or self.model,
            "actual_model": self.actual_model or self.model,
            "provider_class": self.provider_class,
            "search_grounded": self.search_grounded if self.search_grounded is not None else (self.provider_class == "answer_engine"),
            "execution_mode": self.execution_mode,
            "repeat_index": repeat_index,
            "comparison_batch_id": comparison_batch_id,
            "comparison_window_started_at": comparison_window_started_at,
            "comparison_window_completed_at": comparison_window_completed_at,
            "prompt_language": prompt_language,
            "country_iso": country_iso,
            "locale": locale,
            "region": region,
            "timestamp_utc": ts,
            "latency_ms": self.latency_ms,
            "status": self.status,
            "response_text": self.text,
            "citations": self.citations,
            "citations_raw": self.citations,
            "raw_payload": self.raw,
            "metadata": self.metadata,
            "usage": self.usage,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "provider_reported_cost": self.provider_reported_cost,
            "cost_status": self.cost_status,
            "error": self.error,
        }
