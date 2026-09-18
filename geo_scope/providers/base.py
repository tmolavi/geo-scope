"""
Base Provider Interface for GEO-Scope
Defines the standard contract for all AI search and LLM engines.
"""

from abc import ABC, abstractmethod
import asyncio
import time
from typing import Dict, Any, List, Optional
import httpx

from geo_scope.providers.models import ProviderResponse, sanitize_sensitive_data


def classify_provider_exception(exc: Exception) -> Dict[str, Any]:
    """
    Classifies an exception into a structured error dictionary.
    Distinguishes non-retryable errors (auth, bad request) from retryable (timeout, 429, 5xx).
    Never leaks sensitive headers, keys, or tokens in the message.
    """
    msg = str(exc)
    # Sanitize any key-like tokens from message
    if any(w in msg.lower() for w in ("key", "token", "secret", "authorization")):
        cleaned_msg = f"{type(exc).__name__}: Credential or authentication issue."
    else:
        cleaned_msg = f"{type(exc).__name__}: {msg}"

    if isinstance(exc, httpx.HTTPStatusError):
        code = exc.response.status_code
        if code in (401, 403):
            return {"type": "auth_error", "message": f"HTTP {code} Authentication/Permission failure", "retryable": False}
        elif code in (400, 422):
            return {"type": "invalid_request", "message": f"HTTP {code} Bad request payload", "retryable": False}
        elif code == 429:
            return {"type": "rate_limit", "message": "HTTP 429 Rate limit exceeded", "retryable": True}
        elif code >= 500:
            return {"type": "server_error", "message": f"HTTP {code} Provider server error", "retryable": True}
        return {"type": "http_error", "message": f"HTTP {code} error", "retryable": False}
    elif isinstance(exc, (httpx.TimeoutException, asyncio.TimeoutError)):
        return {"type": "timeout", "message": "Request timed out", "retryable": True}
    elif isinstance(exc, (httpx.ConnectError, httpx.NetworkError)):
        return {"type": "network_error", "message": "Connection/Network failure", "retryable": True}
    elif isinstance(exc, ValueError) and any(w in msg.lower() for w in ("not set", "missing", "api_key", "unconfigured")):
        return {"type": "missing_credentials", "message": cleaned_msg, "retryable": False}
    else:
        return {"type": "provider_error", "message": cleaned_msg, "retryable": False}


class BaseProvider(ABC):
    """
    Abstract base class for all AI/LLM search engine providers.
    """

    def __init__(self, name: str, display_name: str, bias_description: str = "", cost_per_1k: float = 0.0):
        self.response_kind = "direct_completion"
        self.last_evidence = {}
        self.name = name
        self.display_name = display_name
        self.bias_description = bias_description
        self.cost_per_1k = cost_per_1k
        self.search_grounded = False
        self.provider_class = "llm"  # "llm" | "answer_engine" | "recorded"

    @abstractmethod
    async def generate_response(self, prompt_item: Dict[str, Any]) -> str:
        """
        Executes a prompt against the AI engine and returns the response string with citations.
        """
        pass

    async def generate(
        self,
        prompt_item: Dict[str, Any],
        *,
        execution_mode: str = "live",
        max_retries: int = 2,
    ) -> ProviderResponse:
        """
        Standard generation contract: invokes the provider, measures latency,
        handles conservative retries, and returns a normalized ProviderResponse.
        Never falls back to simulation.
        """
        model_id = getattr(self, "model", self.name)
        if not self.is_available():
            err_msg = f"{self.display_name} is not configured or missing API credentials."
            return ProviderResponse(
                provider=self.name,
                model=model_id,
                execution_mode=execution_mode,
                provider_class=self.provider_class,
                text="",
                citations=[],
                raw={},
                metadata={"search_grounded": self.is_search_grounded(), "fallback_disabled": True},
                latency_ms=0.0,
                usage={},
                status="failed",
                error={"type": "missing_credentials", "message": err_msg, "retryable": False},
            )

        attempts = 0
        last_error = None
        start_time = time.perf_counter()

        while attempts <= max_retries:
            attempts += 1
            try:
                text = await self.generate_response(prompt_item)
                latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                evidence = getattr(self, "last_evidence", {}) or {}
                raw_payload = evidence.get("raw_payload") or evidence
                citations = evidence.get("citations") or []
                usage = evidence.get("usage") or {}

                return ProviderResponse(
                    provider=self.name,
                    model=evidence.get("model") or model_id,
                    execution_mode=execution_mode,
                    provider_class=self.provider_class,
                    text=text if isinstance(text, str) else "",
                    citations=list(citations),
                    raw=sanitize_sensitive_data(raw_payload),
                    metadata=sanitize_sensitive_data({
                        "search_grounded": self.is_search_grounded(),
                        "response_kind": self.response_kind,
                        "retries_attempted": attempts - 1,
                        "grounding_metadata": evidence.get("grounding_metadata", {}),
                    }),
                    latency_ms=latency_ms,
                    usage=sanitize_sensitive_data(usage),
                    status="success",
                    error=None,
                )
            except Exception as exc:
                last_error = classify_provider_exception(exc)
                if not last_error.get("retryable") or attempts > max_retries:
                    break
                await asyncio.sleep(0.5 * (2 ** (attempts - 1)))

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return ProviderResponse(
            provider=self.name,
            model=model_id,
            execution_mode=execution_mode,
            provider_class=self.provider_class,
            text="",
            citations=[],
            raw={},
            metadata={"search_grounded": self.is_search_grounded(), "fallback_disabled": True, "retries_attempted": attempts},
            latency_ms=latency_ms,
            usage={},
            status="failed",
            error=last_error or {"type": "unknown_error", "message": "Provider failed without specific exception", "retryable": False},
        )

    def is_available(self) -> bool:
        """
        Returns True if the provider is configured (e.g., API key is present or is local/simulation).
        """
        return True

    def is_search_grounded(self) -> bool:
        """
        Returns True if this provider is actively grounded in live web search index.
        """
        return bool(self.search_grounded or self.response_kind == "search_enabled")

    def estimate_cost(self, prompt_count: int) -> float:
        """
        Returns the estimated API cost in USD for running N prompts.
        """
        return (prompt_count / 1000.0) * self.cost_per_1k

    def get_metadata(self) -> Dict[str, Any]:
        """
        Returns serializable provider metadata.
        """
        return {
            "id": self.name,
            "response_kind": self.response_kind,
            "model_id": getattr(self, "model", None),
            "display_name": self.display_name,
            "bias_description": self.bias_description,
            "cost_per_1k_usd": self.cost_per_1k,
            "is_available": self.is_available(),
            "search_grounded": self.is_search_grounded(),
            "mode_support": ["live"],
        }
