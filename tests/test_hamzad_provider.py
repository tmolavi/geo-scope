# Comprehensive Test Suite for Hamzad Gateway Provider Adapter
import os
import json
import pytest
import httpx

from geo_scope.providers.hamzad_provider import HamzadProvider, DEFAULT_MODEL_MAP
from geo_scope.providers.registry import ProviderRegistry
from geo_scope.engine.model_runner import ModelRunner
from geo_scope.engine.execution_mode import ExecutionMode
from geo_scope.engine.persistence import RawRunStore
from geo_scope.mavi.engine import MAVIEngine


@pytest.mark.asyncio
async def test_hamzad_provider_initialization_and_metadata():
    provider = HamzadProvider(
        name="hamzad_gemini",
        target_provider="gemini",
        target_model="gemini-2.5-flash",
        gateway_url="http://mock-gateway:8000",
        project_id="test_project",
    )
    assert provider.name == "hamzad_gemini"
    assert provider.target_provider == "gemini"
    assert provider.target_model == "gemini-2.5-flash"
    assert provider.gateway_url == "http://mock-gateway:8000"
    assert provider.project_id == "test_project"
    assert provider.is_available() is True
    assert provider.is_search_grounded() is True

    meta = provider.get_metadata()
    assert meta["id"] == "hamzad_gemini"
    assert meta["is_available"] is True
    assert meta["search_grounded"] is True
    assert meta["response_kind"] == "gateway_proxied"


@pytest.mark.asyncio
async def test_hamzad_provider_mock_successful_generation():
    captured_requests = []

    def handler(request: httpx.Request):
        captured_requests.append(request)
        return httpx.Response(
            status_code=200,
            json={
                "ok": True,
                "model": "gemini-2.5-flash",
                "provider": "gemini",
                "content": "HubSpot is a leading CRM platform for inbound marketing and sales.",
                "citations": ["https://www.hubspot.com"],
                "usage": {"prompt_tokens": 25, "completion_tokens": 15, "total_tokens": 40},
                "meta": {"tier": 2, "actual_model": "gemini-2.5-flash", "actual_provider": "gemini", "latency": 0.45},
            },
        )

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    provider = HamzadProvider(
        name="hamzad_test",
        target_provider="gemini",
        target_model="gemini-2.5-flash",
        gateway_url="http://mock-gateway:8000",
        api_key="master_key_123",
        project_id="geo_scope",
        client=mock_client,
    )

    prompt_item = {"id": "p1", "query": "best crm software for marketing"}
    resp = await provider.generate(prompt_item, execution_mode="live")

    assert resp.status == "success"
    assert resp.text == "HubSpot is a leading CRM platform for inbound marketing and sales."
    assert resp.model == "gemini-2.5-flash"
    assert resp.provider == "hamzad_test"
    assert "https://www.hubspot.com" in resp.citations
    assert resp.usage.get("total_tokens") == 40
    assert resp.error is None

    # Verify outgoing request
    assert len(captured_requests) == 1
    req = captured_requests[0]
    assert str(req.url) == "http://mock-gateway:8000/api/models/generate"
    assert req.headers["X-Project-ID"] == "geo_scope"
    assert req.headers["X-API-Key"] == "master_key_123"
    sent_payload = json.loads(req.content.decode("utf-8"))
    assert sent_payload["prompt"] == "best crm software for marketing"
    assert sent_payload["provider"] == "gemini"
    assert sent_payload["model"] == "gemini-2.5-flash"
    assert sent_payload["fallback_allowed"] is False


@pytest.mark.asyncio
async def test_hamzad_provider_gateway_error_response():
    def handler(request: httpx.Request):
        return httpx.Response(
            status_code=200,
            json={
                "ok": False,
                "status": "error",
                "error_type": "PROVIDER_RATE_LIMIT",
                "details": "Upstream rate limit reached.",
            },
        )

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    provider = HamzadProvider(gateway_url="http://mock-gateway:8000", client=mock_client)

    resp = await provider.generate({"query": "test query"}, execution_mode="live", max_retries=0)
    assert resp.status == "failed"
    assert resp.is_failed() is True
    assert resp.error is not None
    assert "PROVIDER_RATE_LIMIT" in str(resp.error.get("message", ""))


@pytest.mark.asyncio
async def test_hamzad_provider_timeout_handling():
    def handler(request: httpx.Request):
        raise httpx.ReadTimeout("Connection timed out")

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    provider = HamzadProvider(gateway_url="http://mock-gateway:8000", timeout=5.0, client=mock_client)

    resp = await provider.generate({"query": "slow query"}, execution_mode="live", max_retries=0)
    assert resp.status == "failed"
    assert resp.error["type"] == "timeout"
    assert resp.error["retryable"] is True


@pytest.mark.asyncio
async def test_hamzad_provider_routing_selection():
    registry = ProviderRegistry()

    # 1. Resolve hamzad gateway alias
    p_gw = registry.resolve("hamzad")
    assert isinstance(p_gw, HamzadProvider)
    assert p_gw.target_provider == "gemini"

    # 2. Resolve specific provider targets
    p_openai = registry.resolve("hamzad_openai")
    assert isinstance(p_openai, HamzadProvider)
    assert p_openai.target_provider == "openai"
    assert p_openai.target_model == "gpt-4o-mini"

    p_claude = registry.resolve("hamzad_claude")
    assert isinstance(p_claude, HamzadProvider)
    assert p_claude.target_provider == "claude"

    p_groq = registry.resolve("hamzad_groq")
    assert isinstance(p_groq, HamzadProvider)
    assert p_groq.target_provider == "groq"

    # 3. Factory convenience
    custom_p = HamzadProvider.for_provider("perplexity", target_model="sonar-pro")
    assert custom_p.name == "hamzad_perplexity"
    assert custom_p.target_provider == "perplexity"
    assert custom_p.target_model == "sonar-pro"
    assert custom_p.search_grounded is True


@pytest.mark.asyncio
async def test_hamzad_secret_isolation():
    # Verify GEO-Scope holds no model provider secrets (OpenAI/Gemini/Anthropic/Perplexity keys)
    provider = HamzadProvider(
        name="hamzad_gemini",
        target_provider="gemini",
        gateway_url="http://mock-gateway:8000",
        api_key="gw_master_token",
    )
    # The provider only has the gateway token, zero provider credentials
    assert not hasattr(provider, "gemini_api_key")
    assert not hasattr(provider, "openai_api_key")
    assert not hasattr(provider, "anthropic_api_key")

    def handler(request: httpx.Request):
        return httpx.Response(
            status_code=200,
            json={
                "ok": True,
                "content": "Safe content without leaked keys.",
                "meta": {"actual_model": "gemini-2.5-flash", "authorization": "secret_internal_token"},
            },
        )

    provider._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    resp = await provider.generate({"query": "test query"}, execution_mode="live")
    
    # Raw response sanitization ensures internal authorization tokens are stripped
    assert "authorization" not in resp.raw.get("meta", {})
    assert resp.status == "success"


@pytest.mark.asyncio
async def test_hamzad_model_runner_and_raw_persistence_compatibility(tmp_path):
    run_store = RawRunStore(base_dir=str(tmp_path), experiment_id="TEST-HAMZAD-001")
    registry = ProviderRegistry()

    def handler(request: httpx.Request):
        return httpx.Response(
            status_code=200,
            json={
                "ok": True,
                "model": "gemini-2.5-flash",
                "provider": "gemini",
                "content": "1. HubSpot: Great CRM tool with strong marketing features.",
                "citations": ["https://hubspot.com"],
                "usage": {"total_tokens": 50},
                "meta": {"actual_model": "gemini-2.5-flash", "latency": 0.3},
            },
        )

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    provider = HamzadProvider(
        name="hamzad_gateway",
        target_provider="gemini",
        target_model="gemini-2.5-flash",
        gateway_url="http://mock-gateway:8000",
        client=mock_client,
    )
    registry.register(provider)

    runner = ModelRunner(
        mode=ExecutionMode.LIVE,
        providers=registry,
        run_store=run_store,
        experiment_id="TEST-HAMZAD-001",
    )

    prompts = [{"id": "p_01", "query": "best crm tool", "niche": "crm", "intent": "commercial"}]
    results = await runner.execute_batch(prompts, models=["hamzad_gateway"])

    assert len(results) == 1
    res = results[0]
    assert res["status"] == "success"
    assert "HubSpot" in res["response_text"]
    assert res["model"] == "hamzad_gateway"

    # Verify RawRunStore recorded the raw observation in jsonl file
    raw_file = tmp_path / "TEST-HAMZAD-001" / "raw" / "hamzad_gateway.jsonl"
    assert raw_file.exists()
    lines = raw_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    persisted = json.loads(lines[0])
    assert persisted["experiment_id"] == "TEST-HAMZAD-001"
    assert persisted["provider"] == "hamzad_gateway"
    assert persisted["status"] == "success"


@pytest.mark.asyncio
async def test_hamzad_mavi_l5_integration():
    mavi = MAVIEngine()
    
    # Simulate L5 observations collected via Hamzad Gateway
    geoscope_data = {
        "experiment_id": "EXP-HAMZAD-001",
        "execution_mode": "live",
        "summary": {
            "total_ai_executions": 10,
            "successful_executions": 10,
            "failed_executions": 0,
            "overall_sov": 80.0,
            "overall_top1_rate": 50.0,
            "overall_citation_rate": 60.0,
        },
        "share_of_model": {
            "by_model": {
                "hamzad_gemini": {"successful_queries": 5, "mention_rate_pct": 80.0},
                "hamzad_openai": {"successful_queries": 5, "mention_rate_pct": 80.0},
            }
        },
    }

    report = mavi.measure(
        target_brand="HubSpot",
        experiment_data=geoscope_data,
    )
    l5_layer = report.layers.get("L5")
    assert l5_layer is not None
    assert l5_layer.status == "measured"
    assert l5_layer.source_type == "observed_live"
    assert l5_layer.score is not None
    assert l5_layer.score > 60.0
    assert l5_layer.provenance.execution_mode == "live"


@pytest.mark.asyncio
async def test_hamzad_optional_real_smoke_test():
    if os.getenv("GEO_SCOPE_HAMZAD_SMOKE_TEST", "").lower() not in ("true", "1", "yes"):
        pytest.skip("Skipping real Hamzad Gateway smoke test (GEO_SCOPE_HAMZAD_SMOKE_TEST not enabled).")

    gateway_url = os.getenv("HAMZAD_GATEWAY_URL", "http://localhost:8000")
    provider = HamzadProvider(
        name="hamzad_smoke",
        target_provider=os.getenv("HAMZAD_SMOKE_PROVIDER", "gemini"),
        target_model=os.getenv("HAMZAD_SMOKE_MODEL", "gemini-2.5-flash"),
        gateway_url=gateway_url,
    )

    resp = await provider.generate({"query": "Hello from GEO-Scope benchmark operational test."}, execution_mode="live")
    assert resp.status == "success"
    assert len(resp.text) > 0
