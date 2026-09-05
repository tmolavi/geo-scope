"""Regression coverage for measurement integrity and provider boundaries."""

import asyncio
import json
import random
import subprocess
import sys

import httpx
import pytest

from geo_scope.engine.model_runner import ModelRunner
from geo_scope.engine.query_generator import generate_prompt_dataset
from geo_scope.engine.feature_extractor import (
    detect_brand_positions,
    parse_model_response,
    extract_citations_and_domains,
)
from geo_scope.engine.algo_analyzer import AlgoAnalyzer
from geo_scope.engine.report_generator import generate_experiment_artifacts
from geo_scope.engine.response_import import load_responses
from geo_scope.providers.base import BaseProvider
from geo_scope.providers.registry import ProviderRegistry


class RecordingProvider(BaseProvider):
    def __init__(self, fail=False):
        super().__init__("recording", "Recording test double")
        self.calls = []
        self.fail = fail

    async def generate_response(self, prompt):
        self.calls.append(prompt)
        if self.fail:
            raise ValueError("private-provider-error-secret")
        return "1. HubSpot: suitable for this query."


@pytest.fixture
def prompt():
    return {
        "id": "q1",
        "query": "Compare CRM options",
        "target_brand": "HubSpot",
        "expected_entities": ["HubSpot", "Salesforce", "Zoho CRM"],
        "language": "en",
        "intent": "comparative",
    }


def test_live_calls_provider_and_keeps_evidence(prompt):
    registry = ProviderRegistry()
    provider = RecordingProvider()
    registry.register(provider)
    records = asyncio.run(ModelRunner(mode="live", providers=registry).execute_batch([prompt], ["recording"]))
    assert provider.calls == [prompt]
    assert records[0]["response_text"].startswith("1. HubSpot")
    assert records[0]["provenance"]["execution_mode"] == "live"
    assert records[0]["provenance"]["response_kind"] == "direct_completion"


def test_failed_live_never_simulates_or_exposes_secrets(prompt):
    registry = ProviderRegistry()
    registry.register(RecordingProvider(fail=True))
    with pytest.raises(RuntimeError) as exc:
        asyncio.run(ModelRunner(mode="live", providers=registry).execute_batch([prompt], ["recording"]))
    assert "no simulated fallback" in str(exc.value)
    assert "private-provider-error-secret" not in str(exc.value)


def test_missing_key_rejected_before_calls(prompt, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="not configured"):
        asyncio.run(ModelRunner(mode="live").execute_batch([prompt], ["openai_completion"]))


def test_simulation_is_repeatable_and_does_not_touch_global_rng(prompt):
    before = random.getstate()
    runner = ModelRunner(seed=7)
    first = asyncio.run(runner.execute_batch([prompt]))
    second = asyncio.run(runner.execute_batch([prompt]))
    assert [r["response_text"] for r in first] == [r["response_text"] for r in second]
    assert random.getstate() == before
    assert generate_prompt_dataset(total_count=20, seed=7) == generate_prompt_dataset(total_count=20, seed=7)


def test_paragraph_rank_unknown_but_mention_order_known():
    text = "Salesforce is a strong option.\nHubSpot is good for marketing.\nZoho CRM is affordable."
    result = detect_brand_positions(text, ["Salesforce", "HubSpot", "Zoho CRM"])
    assert [v["rank"] for v in result.values()] == [None, None, None]
    assert [v["mention_order"] for v in result.values()] == [1, 2, 3]
    assert not any(v["is_top_1"] for v in result.values())


@pytest.mark.parametrize(
    "text,rank",
    [("۲. **HubSpot**: good", 2), ("3) HubSpot: good", 3), ("1. Salesforce beats HubSpot", None), ("0. HubSpot", None)],
)
def test_explicit_rank_requires_brand_heading(text, rank):
    assert detect_brand_positions(text, ["HubSpot"])["HubSpot"]["rank"] == rank


def test_unknown_ranks_do_not_bias_average(prompt):
    records = [
        parse_model_response(prompt, "test", "HubSpot is useful."),
        parse_model_response({**prompt, "id": "q2"}, "test", "2. HubSpot: useful"),
    ]
    data = AlgoAnalyzer(records, "HubSpot", ["Salesforce"]).compute_full_analysis()
    assert data["share_of_model"]["by_model"]["test"]["avg_rank"] == 2
    assert data["share_of_model"]["by_model"]["test"]["rank_unknown_count"] == 1
    assert data["summary"]["overall_sov"] == 100
    assert data["summary"]["overall_top1_rate"] == 0
    assert data["algorithmic_factors"]["status"] == "hypothesis_prior_not_fitted"


def test_provider_citations_override_unverified_text_links(prompt):
    record = parse_model_response(
        prompt,
        "test",
        "HubSpot https://fabricated.example",
        {"execution_mode": "live", "provider_evidence": {"citations": ["https://g2.com/categories/crm"]}},
    )
    assert record["citation_basis"] == "provider_metadata"
    assert record["citation_count"] == 1
    assert record["citations"][0]["domain"] == "g2.com"
    _, sources = extract_citations_and_domains("https://notreddit.com https://reddit.com.evil.example")
    assert all(s["category"] == "other_web" for s in sources)


def test_archive_roundtrip_and_html_escaping(prompt, tmp_path):
    prompt = {**prompt, "target_brand": "<script>x</script>", "expected_entities": ["<script>x</script>"]}
    record = parse_model_response(prompt, "test", "A neutral response", {"execution_mode": "live"})
    analysis = AlgoAnalyzer([record], prompt["target_brand"], []).compute_full_analysis()
    artifacts = generate_experiment_artifacts(analysis, [record], [prompt], str(tmp_path))
    imported = load_responses(artifacts["raw_responses_json"])
    assert imported[0]["response_text"] == "A neutral response"
    assert imported[0]["provenance"]["source_execution_mode"] == "live"
    assert imported[0]["provenance"]["execution_mode"] == "imported"
    html = (tmp_path / "report.html").read_text()
    assert "<script>x</script>" not in html
    assert "MODE: live" in html
    assert json.loads((tmp_path / "experiment.json").read_text())["records"] == [record]


def test_windows_legacy_console_does_not_crash(tmp_path):
    import os

    env = {**os.environ, "PYTHONIOENCODING": "cp1252", "GEO_SCOPE_HISTORY_FILE": str(tmp_path / "history.json")}
    result = subprocess.run(
        [sys.executable, "-m", "geo_scope.cli", "run", "--count", "1", "--out", str(tmp_path)],
        env=env,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr


def test_gemini_keeps_grounding_metadata(prompt, monkeypatch):
    from geo_scope.providers.gemini_provider import GeminiProvider

    original = httpx.AsyncClient

    def handler(request):
        assert "key=" not in str(request.url)
        assert request.headers["x-goog-api-key"] == "test-only"
        assert json.loads(request.content)["tools"] == [{"google_search": {}}]
        return httpx.Response(
            200,
            json={
                "candidates": [
                    {
                        "content": {"parts": [{"text": "HubSpot"}]},
                        "groundingMetadata": {"groundingChunks": [{"web": {"uri": "https://example.org/evidence"}}]},
                    }
                ]
            },
        )

    monkeypatch.setattr(httpx, "AsyncClient", lambda **kw: original(transport=httpx.MockTransport(handler)))
    provider = GeminiProvider(api_key="test-only")
    assert asyncio.run(provider.generate_response(prompt)) == "HubSpot"
    assert provider.last_evidence["grounding_metadata"]["groundingChunks"]


def test_ollama_real_http_contract_without_key(prompt, monkeypatch):
    from geo_scope.providers.ollama_provider import OllamaProvider

    original = httpx.AsyncClient

    def handler(request):
        assert request.url.path == "/api/generate"
        assert "authorization" not in request.headers
        assert json.loads(request.content)["stream"] is False
        return httpx.Response(200, json={"response": "1. HubSpot: useful"})

    monkeypatch.setattr(httpx, "AsyncClient", lambda **kw: original(transport=httpx.MockTransport(handler)))
    assert asyncio.run(OllamaProvider().generate_response(prompt)).startswith("1. HubSpot")


def test_keyless_wrapper_local_contract(prompt, monkeypatch):
    from geo_scope.providers.keyless_wrapper_provider import KeylessWrapperProvider

    def handler(request):
        assert request.url.host == "127.0.0.1"
        assert json.loads(request.content)["stream"] is False
        return httpx.Response(
            200, json={"model": "keyless-gpt-4o-mini", "choices": [{"message": {"content": "HubSpot"}}]}
        )

    original = httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kw: original(transport=httpx.MockTransport(handler)))
    provider = KeylessWrapperProvider()
    assert asyncio.run(provider.generate_response(prompt)) == "HubSpot"
    assert provider.last_evidence["grounding"] == "unverified"


def test_openrouter_does_not_accept_paid_model(prompt, monkeypatch):
    from geo_scope.providers.openrouter_provider import OpenRouterProvider

    monkeypatch.setenv("OPENROUTER_API_KEY", "test-only")
    monkeypatch.setenv("OPENROUTER_MODEL", "paid-model")
    with pytest.raises(ValueError, match=":free"):
        asyncio.run(OpenRouterProvider().generate_response(prompt))


def test_public_provider_requires_noncommercial_opt_in(prompt, monkeypatch):
    from geo_scope.providers.public_research_provider import PublicResearchProvider

    monkeypatch.delenv("GEO_SCOPE_NONCOMMERCIAL", raising=False)
    provider = PublicResearchProvider()
    assert not provider.is_available()
    with pytest.raises(ValueError, match="noncommercial"):
        asyncio.run(provider.generate_response(prompt))


def test_empty_provider_selection_is_rejected(prompt):
    with pytest.raises(ValueError, match="at least one"):
        asyncio.run(ModelRunner().execute_batch([prompt], []))


def test_mcp_live_uses_provider_and_reports_mode(monkeypatch):
    from geo_scope.mcp_server import handle_tool_call
    from geo_scope.providers.ollama_provider import OllamaProvider

    calls = []

    async def generate(self, prompt):
        calls.append(prompt["query"])
        return "1. HubSpot: useful"

    monkeypatch.setattr(OllamaProvider, "generate_response", generate)
    result = asyncio.run(
        handle_tool_call(
            "audit_ai_visibility", {"brand": "HubSpot", "mode": "live", "models": ["ollama_local"], "prompt_count": 2}
        )
    )
    assert len(calls) == 2
    assert result["execution_mode"] == "live"
    assert len(result["records"]) == 2


def test_server_failed_run_clears_stale_results(monkeypatch):
    from geo_scope.server import STATE, BenchmarkRequest, execute_pipeline_sync

    STATE["analysis_results"] = {"old": "result"}

    async def fail(*args, **kwargs):
        raise RuntimeError("private error")

    monkeypatch.setattr(ModelRunner, "execute_batch", fail)
    execute_pipeline_sync(BenchmarkRequest(prompt_count=1))
    assert STATE["analysis_results"] is None
    assert STATE["is_running"] is False
    assert STATE["current_status"].startswith("Failed")
