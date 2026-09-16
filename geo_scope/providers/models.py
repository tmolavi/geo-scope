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
    """
    provider: str
    model: str
    execution_mode: str
    text: str = ""
    citations: List[str] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    latency_ms: float = 0.0
    usage: Dict[str, Any] = field(default_factory=dict)
    status: str = "success"  # 'success' | 'failed'
    error: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        # Guarantee no secrets ever leak into raw payload or metadata
        self.raw = sanitize_sensitive_data(self.raw)
        self.metadata = sanitize_sensitive_data(self.metadata)
        if self.citations is None:
            self.citations = []

    def is_success(self) -> bool:
        return self.status == "success"

    def is_failed(self) -> bool:
        return self.status == "failed"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "execution_mode": self.execution_mode,
            "text": self.text,
            "citations": self.citations,
            "raw": self.raw,
            "metadata": self.metadata,
            "latency_ms": self.latency_ms,
            "usage": self.usage,
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
    ) -> Dict[str, Any]:
        """
        Builds the canonical raw persistence record for auditability.
        """
        ts = timestamp or datetime.now(timezone.utc).isoformat()
        return {
            "experiment_id": experiment_id,
            "run_id": run_id,
            "prompt_id": prompt_id,
            "provider": self.provider,
            "model": self.model,
            "execution_mode": self.execution_mode,
            "timestamp": ts,
            "prompt": prompt,
            "raw_response": self.text,
            "raw_provider_payload": self.raw,
            "citations_raw": self.citations,
            "provider_metadata": self.metadata,
            "latency_ms": self.latency_ms,
            "usage": self.usage,
            "status": self.status,
            "error": self.error,
        }
