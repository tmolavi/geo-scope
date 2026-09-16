"""
Comprehensive Unit and Integration Tests for GEO-Scope Live Provider Integration Milestone.
Validates:
  - ModelRunner mode handling (LIVE vs SIMULATION)
  - Zero silent simulation fallback
  - Structured failure recording & persistence
  - ProviderRegistry alias resolution & availability diagnostics
  - Raw response persistence without leaking secrets
  - Manifest generation and audit metadata
  - Metrics safety: failed requests excluded from zero-visibility calculations
  - CLI commands (--mode live, --mode simulation, providers table)
"""

import asyncio
import json
import os
import pytest
import subprocess
import sys

from geo_scope.engine.execution_mode import ExecutionMode
from geo_scope.engine.model_runner import ModelRunner
from geo_scope.engine.persistence import RawRunStore, get_git_commit, compute_dataset_hash
from geo_scope.engine.algo_analyzer import AlgoAnalyzer
from geo_scope.engine.feature_extractor import parse_model_response
from geo_scope.providers.base import BaseProvider, classify_provider_exception
from geo_scope.providers.models import ProviderResponse, sanitize_sensitive_data
from geo_scope.providers.registry import ProviderRegistry, registry


class MockSuccessProvider(BaseProvider):
    def __init__(self, name="mock_success", is_grounded=True):
        super().__init__(name=name, display_name=f"Mock Success ({name})")
        self.search_grounded = is_grounded
        self.response_kind = "search_enabled" if is_grounded else "direct_completion"
        self.called_with = []

    async def generate_response(self, prompt_item):
        self.called_with.append(prompt_item)
        self.last_evidence = {
            "citations": ["https://techcrunch.com/2026/crm", "https://g2.com/products/hubspot"],
            "model": self.name,
            "usage": {"prompt_tokens": 12, "completion_tokens": 45, "total_tokens": 57},
            "raw_payload": {"choices": [{"text": "1. HubSpot: Recommended CRM"}]},
        }
        return "1. HubSpot: Top recommended solution for startups.\n2. Salesforce: Enterprise option."


class MockFailingProvider(BaseProvider):
    def __init__(self, name="mock_fail", error_type="auth_error", secret_leak="SUPER_SECRET_BEARER_TOKEN_123"):
        super().__init__(name=name, display_name=f"Mock Fail ({name})")
        self.error_type = error_type
        self.secret_leak = secret_leak

    async def generate_response(self, prompt_item):
        if self.error_type == "auth_error":
            raise ValueError(f"Missing API key or invalid token: {self.secret_leak}")
        elif self.error_type == "timeout":
            import httpx
            raise httpx.ReadTimeout("Connection timed out after 45.0s")
        elif self.error_type == "rate_limit":
            import httpx
            req = httpx.Request("POST", "https://api.example.com")
            resp = httpx.Response(429, request=req)
            raise httpx.HTTPStatusError("Rate limit exceeded", request=req, response=resp)
        else:
            raise RuntimeError(f"Unexpected provider crash with secret: {self.secret_leak}")


@pytest.fixture
def sample_prompt():
    return {
        "id": "test_q1",
        "query": "What is the best CRM software in 2026?",
        "target_brand": "HubSpot",
        "expected_entities": ["HubSpot", "Salesforce", "Zoho CRM"],
        "niche": "crm_sales",
        "language": "en",
        "intent": "commercial_direct",
    }


# =========================================================================
# 1. ExecutionMode Tests
# =========================================================================

def test_execution_mode_enum():
    assert ExecutionMode.LIVE == "live"
    assert ExecutionMode.SIMULATION == "simulation"
    assert ExecutionMode.from_string("live") == ExecutionMode.LIVE
    assert ExecutionMode.from_string("simulation") == ExecutionMode.SIMULATION
    assert ExecutionMode.from_string("simulate") == ExecutionMode.SIMULATION
    assert ExecutionMode.from_string("SIMULATE") == ExecutionMode.SIMULATION
    assert ExecutionMode.LIVE.is_live()
    assert ExecutionMode.SIMULATION.is_simulation()

    with pytest.raises(ValueError, match="Unknown execution mode"):
        ExecutionMode.from_string("invalid_mode")


# =========================================================================
# 2. ModelRunner & Zero Silent Fallback Tests
# =========================================================================

def test_model_runner_simulation_invokes_simulator_only(sample_prompt):
    runner = ModelRunner(mode=ExecutionMode.SIMULATION, seed=42)
    records = asyncio.run(runner.execute_batch([sample_prompt], ["perplexity_sonar"]))
    assert len(records) == 1
    assert records[0]["status"] == "success"
    assert records[0]["provenance"]["execution_mode"] == "simulation"
    assert records[0]["provenance"]["response_kind"] == "simulated"
    assert "simulation-profile" in records[0]["provenance"]["model_id"]
    assert records[0]["response_text"] != ""


def test_model_runner_live_invokes_provider_registry(sample_prompt):
    custom_reg = ProviderRegistry()
    mock_p = MockSuccessProvider("test_live_prov")
    custom_reg.register(mock_p)

    runner = ModelRunner(mode=ExecutionMode.LIVE, providers=custom_reg)
    records = asyncio.run(runner.execute_batch([sample_prompt], ["test_live_prov"]))

    assert len(records) == 1
    assert len(mock_p.called_with) == 1
    assert records[0]["status"] == "success"
    assert records[0]["provenance"]["execution_mode"] == "live"
    assert records[0]["provenance"]["provider_id"] == "test_live_prov"
    assert "HubSpot" in records[0]["response_text"]
    assert records[0]["provenance"]["fallback_disabled"] is True


def test_model_runner_live_never_silently_simulates_on_failure(sample_prompt):
    custom_reg = ProviderRegistry()
    failing_p = MockFailingProvider("failing_prov", error_type="auth_error")
    custom_reg.register(failing_p)

    runner = ModelRunner(mode=ExecutionMode.LIVE, providers=custom_reg)
    records = asyncio.run(runner.execute_batch([sample_prompt], ["failing_prov"]))

    assert len(records) == 1
    assert records[0]["status"] == "failed"
    assert records[0]["error"] is not None
    assert records[0]["error"]["type"] == "missing_credentials"
    assert records[0]["provenance"]["execution_mode"] == "live"
    assert records[0]["provenance"]["fallback_disabled"] is True
    # Crucial: Must NEVER substitute simulated text!
    assert records[0]["response_text"] == ""
    assert "simulation" not in records[0]["provenance"]["model_id"]


def test_model_runner_missing_api_key_returns_structured_failure(sample_prompt, monkeypatch):
    monkeypatch.delenv("PERPLEXITY_API_KEY", raising=False)
    runner = ModelRunner(mode=ExecutionMode.LIVE)
    records = asyncio.run(runner.execute_batch([sample_prompt], ["perplexity_sonar"]))

    assert len(records) == 1
    assert records[0]["status"] == "failed"
    assert records[0]["error"]["type"] == "missing_credentials"
    assert records[0]["provenance"]["execution_mode"] == "live"
    assert records[0]["response_text"] == ""
    assert records[0]["provenance"]["fallback_disabled"] is True


def test_model_runner_continues_other_providers_when_one_fails(sample_prompt):
    custom_reg = ProviderRegistry()
    good_p = MockSuccessProvider("good_p")
    bad_p = MockFailingProvider("bad_p", error_type="rate_limit")
    custom_reg.register(good_p)
    custom_reg.register(bad_p)

    runner = ModelRunner(mode=ExecutionMode.LIVE, providers=custom_reg)
    records = asyncio.run(runner.execute_batch([sample_prompt], ["good_p", "bad_p"]))

    assert len(records) == 2
    good_rec = next(r for r in records if r["model"] == "good_p")
    bad_rec = next(r for r in records if r["model"] == "bad_p")

    assert good_rec["status"] == "success"
    assert good_rec["response_text"] != ""

    assert bad_rec["status"] == "failed"
    assert bad_rec["status"] != "success"
    assert bad_rec["response_text"] == ""
    assert bad_rec["error"]["type"] == "rate_limit"


# =========================================================================
# 3. ProviderRegistry Tests
# =========================================================================

def test_provider_registry_aliases():
    assert registry.get("openai").name == "openai_completion"
    assert registry.get("chatgpt_search").name == "openai_completion"
    assert registry.get("perplexity").name == "perplexity_sonar"
    assert registry.get("gemini").name == "gemini_grounding"
    assert registry.get("claude").name == "claude_completion"
    assert registry.get("anthropic").name == "claude_completion"
    assert registry.get("claude_3_7").name == "claude_completion"


def test_provider_registry_resolve_unknown():
    with pytest.raises(ValueError, match="Unknown provider: 'nonexistent'"):
        registry.resolve("nonexistent")


def test_provider_registry_availability_table():
    diag = registry.check_availability()
    assert isinstance(diag, list)
    assert any(row["provider"] == "OpenAI" for row in diag)
    assert any(row["provider"] == "Perplexity" for row in diag)
    assert any(row["provider"] == "Gemini" for row in diag)
    assert any(row["provider"] == "Anthropic" for row in diag)
    assert any(row["provider"] == "Simulation" for row in diag)

    table_str = registry.format_availability_table()
    assert "Provider" in table_str
    assert "Configured" in table_str
    assert "Mode support" in table_str


# =========================================================================
# 4. Raw Persistence & Storage Design Tests
# =========================================================================

def test_raw_persistence_writes_records_and_manifest(tmp_path, sample_prompt):
    store = RawRunStore(base_dir=str(tmp_path / "runs"), experiment_id="EXP-TEST-001")
    custom_reg = ProviderRegistry()
    p = MockSuccessProvider("persisted_p")
    custom_reg.register(p)

    runner = ModelRunner(mode=ExecutionMode.LIVE, providers=custom_reg, run_store=store, experiment_id="EXP-TEST-001")
    records = asyncio.run(runner.execute_batch([sample_prompt], ["persisted_p"]))

    # Verify raw jsonl was created
    raw_file = os.path.join(store.raw_dir, "persisted_p.jsonl")
    assert os.path.exists(raw_file)

    with open(raw_file, "r", encoding="utf-8") as f:
        line = f.readline()
        saved = json.loads(line)
        assert saved["experiment_id"] == "EXP-TEST-001"
        assert saved["provider"] == "persisted_p"
        assert saved["execution_mode"] == "live"
        assert saved["status"] == "success"
        assert "citations_raw" in saved
        assert "latency_ms" in saved

    # Verify manifest creation
    manifest = store.create_manifest(
        execution_mode="live",
        providers={"persisted_p": p.get_metadata()},
        models={"persisted_p": "persisted_p"},
        prompts=[sample_prompt],
        started_at="2026-09-16T12:00:00Z",
        finished_at="2026-09-16T12:00:05Z",
        configuration={"seed": 42},
    )
    assert os.path.exists(store.manifest_path)
    assert manifest["execution_mode"] == "live"
    assert manifest["total_prompts"] == 1
    assert "prompt_dataset_hash" in manifest


def test_persistence_sanitizes_secrets_and_api_keys(tmp_path, sample_prompt):
    store = RawRunStore(base_dir=str(tmp_path / "runs"), experiment_id="EXP-SECRET-001")
    custom_reg = ProviderRegistry()
    failing_p = MockFailingProvider("leaky_p", secret_leak="SUPER_SECRET_KEY_999")
    custom_reg.register(failing_p)

    runner = ModelRunner(mode=ExecutionMode.LIVE, providers=custom_reg, run_store=store, experiment_id="EXP-SECRET-001")
    records = asyncio.run(runner.execute_batch([sample_prompt], ["leaky_p"]))

    raw_file = os.path.join(store.raw_dir, "leaky_p.jsonl")
    assert os.path.exists(raw_file)

    with open(raw_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "SUPER_SECRET_KEY_999" not in content


# =========================================================================
# 5. Metrics Safety (Failure ≠ Zero Visibility)
# =========================================================================

def test_metrics_safety_failed_request_excluded_from_zero_visibility(sample_prompt):
    # Setup 1 successful response and 1 failed response for the same query
    prompt1 = {**sample_prompt, "id": "q1"}
    prompt2 = {**sample_prompt, "id": "q2"}

    # Success parses into mentioned=True
    good_parsed = parse_model_response(
        prompt1,
        "openai_completion",
        "1. HubSpot: Great CRM solution.",
        {"execution_mode": "live", "status": "success"},
    )
    assert good_parsed["status"] == "success"
    assert good_parsed["target_mentioned"] is True

    # Failed provider call
    failed_parsed = parse_model_response(
        prompt2,
        "perplexity_sonar",
        "",
        {"execution_mode": "live", "status": "failed", "error": {"type": "rate_limit", "message": "429"}},
    )
    assert failed_parsed["status"] == "failed"
    assert failed_parsed["target_mentioned"] is None  # Unobserved, NOT False

    records = [good_parsed, failed_parsed]
    analyzer = AlgoAnalyzer(records, "HubSpot", ["Salesforce"])
    analysis = analyzer.compute_full_analysis()

    # Perplexity should have status: failed, NOT 0% visibility falsely indicating non-mention
    pplx_stats = analysis["share_of_model"]["by_model"]["perplexity_sonar"]
    assert pplx_stats["status"] == "failed"
    assert pplx_stats["successful_queries"] == 0
    assert pplx_stats["failed_queries"] == 1
    assert pplx_stats["observed_mention_rate_pct"] is None

    # Overall SOV should be 100% (1 mention out of 1 valid observation), not 50%!
    assert analysis["summary"]["overall_sov"] == 100.0
    assert analysis["summary"]["successful_executions"] == 1
    assert analysis["summary"]["failed_executions"] == 1


def test_zero_successful_observations_returns_null_and_insufficient_data(sample_prompt):
    # Setup ONLY failed records (0 successful observations)
    failed_parsed = parse_model_response(
        sample_prompt,
        "perplexity_sonar",
        "",
        {"execution_mode": "live", "status": "failed", "error": {"type": "missing_credentials", "message": "No key"}},
    )
    records = [failed_parsed]
    analyzer = AlgoAnalyzer(records, "HubSpot", ["Salesforce", "Zoho CRM"])
    analysis = analyzer.compute_full_analysis()

    summary = analysis["summary"]
    assert summary["successful_executions"] == 0
    assert summary["failed_executions"] == 1
    assert summary["measurement_status"] == "insufficient_data"
    assert summary["reason"] == "no successful observations"
    assert summary["overall_sov"] is None
    assert summary["overall_top1_rate"] is None

    # Model breakdown
    pplx_stats = analysis["share_of_model"]["by_model"]["perplexity_sonar"]
    assert pplx_stats["status"] == "failed"
    assert pplx_stats["measurement_status"] == "insufficient_data"
    assert pplx_stats["mention_rate_pct"] is None
    assert pplx_stats["top1_rate_pct"] is None

    # Competitor matrix
    for comp in analysis["competitor_matrix"]:
        assert comp["measurement_status"] == "insufficient_data"
        assert comp["mention_rate_pct"] is None
        assert comp["top1_rate_pct"] is None
        assert comp["share_of_voice_pct"] is None


# =========================================================================
# 6. CLI Smoke Tests
# =========================================================================

def test_cli_providers_table():
    res = subprocess.run([sys.executable, "-m", "geo_scope.cli", "providers"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "Provider" in res.stdout
    assert "Configured" in res.stdout
    assert "OpenAI" in res.stdout
    assert "Perplexity" in res.stdout
    assert "Gemini" in res.stdout
    assert "Anthropic" in res.stdout


def test_cli_mode_simulation_banner(tmp_path):
    out_dir = str(tmp_path / "sim_out")
    res = subprocess.run(
        [sys.executable, "-m", "geo_scope.cli", "run", "--mode", "simulation", "--count", "1", "--out", out_dir],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0
    assert "GEO-Scope Synthetic Benchmark" in res.stdout
    assert "Execution mode: SIMULATION" in res.stdout
    assert "Results are synthetic" in res.stdout


def test_cli_mode_live_missing_key_explicit_failure_no_fallback(tmp_path):
    out_dir = str(tmp_path / "live_out")
    env = {**os.environ, "PERPLEXITY_API_KEY": ""}
    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "geo_scope.cli",
            "run",
            "--mode",
            "live",
            "--providers",
            "perplexity_sonar",
            "--count",
            "1",
            "--out",
            out_dir,
        ],
        env=env,
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0
    assert "GEO-Scope Live Benchmark" in res.stdout
    assert "Execution mode: LIVE" in res.stdout
    assert "Synthetic fallback: DISABLED" in res.stdout
    assert "Status: FAILED" in res.stdout
    assert "Simulation fallback: disabled" in res.stdout

    # Verify raw failure was persisted to raw/perplexity_sonar.jsonl
    raw_file = os.path.join(out_dir, "runs")
    run_subdirs = os.listdir(raw_file)
    assert len(run_subdirs) == 1
    pplx_raw = os.path.join(raw_file, run_subdirs[0], "raw", "perplexity_sonar.jsonl")
    assert os.path.exists(pplx_raw)
    with open(pplx_raw, "r", encoding="utf-8") as f:
        data = json.loads(f.readline())
        assert data["status"] == "failed"
        assert data["execution_mode"] == "live"
        assert data["error"]["type"] == "missing_credentials"
