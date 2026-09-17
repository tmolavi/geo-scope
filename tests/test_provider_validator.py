import pytest
import httpx
import json
from geo_scope.benchmark.validator import (
    ProviderValidator,
    ProviderValidationResult,
    models_match,
    normalize_model_identifier,
)
from geo_scope.benchmark.models import BenchmarkManifest


def test_model_normalization_and_matching():
    assert normalize_model_identifier("google/gemini-2.5-flash") == "gemini-2.5-flash"
    assert normalize_model_identifier("openai/gpt-4o") == "gpt-4o"
    assert normalize_model_identifier("models/gemini-2.5-flash") == "gemini-2.5-flash"

    # Matching logic
    assert models_match("gemini-2.5-flash", "gemini-2.5-flash") is True
    assert models_match("gemini", "gemini-2.5-flash") is True
    assert models_match("gpt-4o", "gpt-4o-2024-08-06") is True
    assert models_match("claude-3-5-sonnet", "claude-3-5-sonnet-20241022") is True
    assert models_match("sonar-pro", "sonar-pro") is True

    # Non-matching logic (fallbacks or surrogates)
    assert models_match("claude-3-5-sonnet", "qwen/qwen3.8-27b") is False
    assert models_match("sonar-pro", "qwen/qwen3.8-27b") is False
    assert models_match("gemini-2.5-flash", "gpt-4o") is False


@pytest.mark.asyncio
async def test_validator_mock_native_success():
    def handler(request: httpx.Request):
        payload = json.loads(request.content.decode("utf-8"))
        model = payload.get("model")
        if model == "gemini-2.5-flash":
            return httpx.Response(
                status_code=200,
                json={
                    "ok": True,
                    "model": "gemini-2.5-flash",
                    "provider": "gemini",
                    "content": "OK",
                    "meta": {"actual_model": "gemini-2.5-flash", "fallback_active": False},
                },
            )
        elif model == "gpt-4o":
            return httpx.Response(
                status_code=200,
                json={
                    "ok": True,
                    "model": "gpt-4o",
                    "provider": "avalai",
                    "content": "OK",
                    "meta": {"actual_model": "gpt-4o", "fallback_active": False},
                },
            )
        return httpx.Response(status_code=404, text="Not Found")

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    validator = ProviderValidator(gateway_url="http://mock-gateway", client=client)

    res_gemini = await validator.validate_provider("gemini-2.5-flash")
    assert res_gemini.is_valid() is True
    assert res_gemini.status == "PASS"
    assert res_gemini.fallback_detected is False
    assert res_gemini.verified_model == "gemini-2.5-flash"

    res_gpt = await validator.validate_provider("gpt-4o")
    assert res_gpt.is_valid() is True
    assert res_gpt.status == "PASS"
    assert res_gpt.fallback_detected is False
    assert res_gpt.verified_model == "gpt-4o"


@pytest.mark.asyncio
async def test_validator_mock_fallback_rejection():
    def handler(request: httpx.Request):
        return httpx.Response(
            status_code=200,
            json={
                "ok": True,
                "model": "qwen/qwen3.8-27b",
                "provider": "groq",
                "content": "OK",
                "meta": {"actual_model": "qwen/qwen3.8-27b", "fallback_active": True},
            },
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    validator = ProviderValidator(gateway_url="http://mock-gateway", client=client)

    res = await validator.validate_provider("claude-3-5-sonnet")
    assert res.is_valid() is False
    assert res.status == "FAIL"
    assert res.fallback_detected is True
    assert "fallback detected" in res.error
    assert res.verified_model == "qwen/qwen3.8-27b"


@pytest.mark.asyncio
async def test_validator_mock_model_mismatch_rejection():
    def handler(request: httpx.Request):
        return httpx.Response(
            status_code=200,
            json={
                "ok": True,
                "model": "llama-3-8b",
                "provider": "groq",
                "content": "OK",
                "meta": {"actual_model": "llama-3-8b", "fallback_active": False},
            },
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    validator = ProviderValidator(gateway_url="http://mock-gateway", client=client)

    res = await validator.validate_provider("gemini-2.5-flash")
    assert res.is_valid() is False
    assert res.status == "FAIL"
    assert "model mismatch" in res.error


@pytest.mark.asyncio
async def test_validator_mock_http_error():
    def handler(request: httpx.Request):
        return httpx.Response(status_code=500, text="Internal Gateway Error")

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    validator = ProviderValidator(gateway_url="http://mock-gateway", client=client)

    res = await validator.validate_provider("gpt-4o")
    assert res.is_valid() is False
    assert res.status == "FAIL"
    assert "error" in res.error.lower() or "500" in str(res.error)


def test_format_validation_report():
    results = {
        "gemini-2.5-flash": ProviderValidationResult(
            requested="gemini-2.5-flash",
            verified_model="gemini-2.5-flash",
            provider="gemini",
            fallback_detected=False,
            status="PASS",
        ),
        "gpt-4o": ProviderValidationResult(
            requested="gpt-4o",
            verified_model="gpt-4o",
            provider="avalai",
            fallback_detected=False,
            status="PASS",
        ),
        "claude-3-5-sonnet": ProviderValidationResult(
            requested="claude-3-5-sonnet",
            verified_model="qwen/qwen3.8-27b",
            provider="groq",
            fallback_detected=True,
            status="FAIL",
            error="fallback detected",
        ),
        "sonar-pro": ProviderValidationResult(
            requested="sonar-pro",
            verified_model="qwen/qwen3.8-27b",
            provider="groq",
            fallback_detected=True,
            status="FAIL",
            error="fallback detected",
        ),
    }

    validator = ProviderValidator()
    report = validator.format_report(results)
    expected = (
        "Provider Validation Report\n\n"
        "Gemini 2.5 Flash\nPASS\n\n"
        "GPT-4o\nPASS\n\n"
        "Claude\nFAILED - fallback detected\n\n"
        "Perplexity\nFAILED - fallback detected"
    )
    assert report == expected


def test_manifest_provider_validation_serialization():
    manifest = BenchmarkManifest(
        dataset_id="geo-scope-benchmark-2026.1",
        created_at="2026-09-17T11:00:00Z",
        description="Test benchmark",
        provider_validation={
            "gemini-2.5-flash": {
                "requested": "gemini-2.5-flash",
                "verified_model": "gemini-2.5-flash",
                "provider": "gemini",
                "fallback_detected": False,
                "status": "PASS",
                "validated_at": "2026-09-17T11:00:00Z",
            }
        },
    )
    data = manifest.model_dump()
    assert "provider_validation" in data
    assert data["provider_validation"]["gemini-2.5-flash"]["status"] == "PASS"
