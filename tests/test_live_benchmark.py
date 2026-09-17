# Comprehensive Test Suite for GEO-Scope Live Benchmark & Public Research Release v1
import json
import os
import shutil
import tempfile
from pathlib import Path
import pytest

from geo_scope.benchmark.profile import BenchmarkProfile, SamplingConfig, CostLimits
from geo_scope.benchmark.runner import LiveBenchmarkRunner, estimate_benchmark_cost
from geo_scope.benchmark.reproducer import BenchmarkReproducer
from geo_scope.benchmark.hasher import verify_dataset_checksums
from geo_scope.engine.algo_analyzer import AlgoAnalyzer
from geo_scope.engine.execution_mode import ExecutionMode
from geo_scope.providers.models import sanitize_sensitive_data


def test_profile_loading_and_validation():
    profile_path = "benchmark/profiles/geo-scope-live-2026.1.yaml"
    assert Path(profile_path).exists()

    profile = BenchmarkProfile.from_file(profile_path)
    assert profile.benchmark_version == "2026.1-live"
    assert profile.execution_mode == "live"
    assert profile.research_status == "experimental_observation"
    assert len(profile.providers) >= 4
    assert profile.sampling.niche == "crm_sales"
    assert profile.sampling.target_brand == "HubSpot"
    assert len(profile.sampling.competitors) >= 3
    assert profile.cost_limits.max_prompts > 0


def test_synthetic_vs_live_mode_separation(tmp_path):
    # Test synthetic forces demo_only
    syn_file = tmp_path / "syn.yaml"
    syn_file.write_text("benchmark_version: '2026.1'\nexecution_mode: 'synthetic'\nresearch_status: 'peer_review_ready'", encoding="utf-8")
    syn_profile = BenchmarkProfile.from_file(syn_file)
    assert syn_profile.execution_mode == "synthetic"
    assert syn_profile.research_status == "demo_only"

    # Test live uses experimental_observation
    live_file = tmp_path / "live.yaml"
    live_file.write_text("benchmark_version: '2026.1-live'\nexecution_mode: 'live'\nresearch_status: 'demo_only'", encoding="utf-8")
    live_profile = BenchmarkProfile.from_file(live_file)
    assert live_profile.execution_mode == "live"
    assert live_profile.research_status == "experimental_observation"


def test_cost_estimation():
    profile = BenchmarkProfile(
        benchmark_version="2026.1-live",
        dataset_name="test-cost",
        execution_mode="live",
        providers=["perplexity_sonar", "gemini_grounding", "openai_completion"],
        sampling=SamplingConfig(count=20),
        cost_limits=CostLimits(max_prompts=15, max_cost_usd=5.0),
    )
    est = estimate_benchmark_cost(profile)
    assert est["prompt_count"] == 15
    assert est["provider_count"] == 3
    assert est["total_inferences"] == 45
    assert est["estimated_cost_usd"] > 0
    assert est["within_budget"] is True


def test_live_runner_dry_run(tmp_path):
    profile = BenchmarkProfile(
        benchmark_version="2026.1-live",
        dataset_name="test-dry-run",
        execution_mode="live",
        providers=["perplexity_sonar"],
        cost_limits=CostLimits(dry_run=True),
    )
    runner = LiveBenchmarkRunner(profile, out_dir=tmp_path)
    res = runner.run(dry_run=True)
    assert res["dry_run"] is True
    assert res["status"] == "dry_run_completed"
    assert "cost_estimate" in res


def test_live_runner_resume_logic(tmp_path):
    profile = BenchmarkProfile(
        benchmark_version="2026.1-live",
        dataset_name="test-resume-dataset",
        execution_mode="live",
        providers=["ollama_local"],
        sampling=SamplingConfig(count=2),
    )

    runner = LiveBenchmarkRunner(profile, out_dir=tmp_path)
    state_file = tmp_path / f".{profile.dataset_name}_partial.jsonl"
    
    # Pre-populate state file with 1 completed observation
    state_file.write_text(json.dumps({
        "observation_id": "obs_00001",
        "prompt_id": "prompt_0001",
        "provider_id": "ollama_local",
        "model": "ollama_local",
        "execution_mode": "live",
        "status": "success",
        "brand_mentioned": True,
        "brand_rank": 1,
        "is_top1": True,
        "timestamp": "2026-03-16T10:00:00Z",
    }) + "\n", encoding="utf-8")

    # When runner executes with resume=True, it loads partial records
    res = runner.run(resume=True)
    assert res["success"] is True
    assert res["total_observations"] >= 2


def test_secret_sanitization_in_raw_persistence():
    sensitive_payload = {
        "headers": {
            "Authorization": "Bearer sk-proj-12345SECRET",
            "x-api-key": "secret-key-abcdef",
            "Content-Type": "application/json",
        },
        "response": {"text": "Clean response", "api_key": "hidden_secret"},
    }
    sanitized = sanitize_sensitive_data(sensitive_payload)
    assert "Authorization" not in sanitized["headers"]
    assert "x-api-key" not in sanitized["headers"]
    assert sanitized["headers"]["Content-Type"] == "application/json"
    assert "api_key" not in sanitized["response"]
    assert sanitized["response"]["text"] == "Clean response"


def test_prior_vs_observed_factor_separation():
    records = [
        {"query_id": "q1", "query_text": "best crm for sales", "intent": "commercial", "status": "success", "target_mentioned": True, "target_is_top_1": True, "model": "perplexity_sonar"},
        {"query_id": "q2", "query_text": "hubspot vs salesforce", "intent": "comparative", "status": "success", "target_mentioned": True, "target_is_top_1": False, "model": "chatgpt_search"},
    ]
    analyzer = AlgoAnalyzer(records, target_brand="HubSpot", competitors=["Salesforce"])
    analysis = analyzer.compute_full_analysis()
    factors = analysis["algorithmic_factors"]["factors"]

    assert len(factors) > 0
    for f in factors:
        assert "factor" in f
        assert "prior_weight" in f
        assert "observed_effect" in f
        assert "confidence_interval" in f
        assert f["status"] == "observed_association"
        # Prior is NOT overwritten by observed effect
        assert f["prior_weight"] != f["observed_effect"]


def test_live_reference_dataset_verification_and_reproduction():
    ref_dir = Path("benchmark/geo-scope-benchmark-2026.1-live")
    assert ref_dir.exists(), "Live reference benchmark dataset directory must exist"

    # 1. SHA-256 Checksums
    chk = verify_dataset_checksums(ref_dir)
    assert chk["valid"] is True
    assert len(chk["mismatches"]) == 0

    # 2. Reproduction
    reproducer = BenchmarkReproducer(tolerance=0.05)
    res = reproducer.verify_and_reproduce(ref_dir)
    assert res["success"] is True
    assert res["execution_mode"] == "live"
    assert res["research_status"] == "experimental_observation"
    assert res["checksums_valid"] is True
    assert res["metrics_matched"] is True
