# Unit and integration tests for Model Provenance & Dual Benchmark Modes
import pytest
from geo_scope.benchmark.models import (
    BenchmarkExecutionMode,
    ObservationRecord,
    BenchmarkMetrics,
    BenchmarkManifest,
    BrandBenchmarkMetrics,
)
from geo_scope.benchmark.calculator import BenchmarkCalculator
from geo_scope.benchmark.builder import BenchmarkBuilder
from geo_scope.benchmark.profile import BenchmarkProfile


def test_benchmark_execution_mode_enum():
    assert BenchmarkExecutionMode.STRICT.value == "strict"
    assert BenchmarkExecutionMode.DISCOVERY.value == "discovery"
    assert BenchmarkExecutionMode("strict") == BenchmarkExecutionMode.STRICT
    assert BenchmarkExecutionMode("discovery") == BenchmarkExecutionMode.DISCOVERY


def test_observation_record_provenance_defaults():
    obs = ObservationRecord(
        observation_id="OBS-001",
        prompt_id="PRM-001",
        provider_id="gemini",
        model="gemini-2.5-flash",
        status="success",
        brand_mentioned=True,
        is_top1=True,
        top1_brand="HubSpot",
        mentioned_brands=["HubSpot"],
        timestamp="2026-09-17T12:00:00Z",
    )
    assert obs.requested_provider is None
    assert obs.requested_model is None
    assert obs.actual_provider is None
    assert obs.actual_model is None
    assert obs.fallback_active is False
    assert obs.execution_class == "native"


def test_observation_record_with_fallback_provenance():
    obs = ObservationRecord(
        observation_id="OBS-002",
        prompt_id="PRM-002",
        provider_id="claude-3-5-sonnet",
        model="qwen/qwen3.8-27b",
        requested_provider="claude-3-5-sonnet",
        requested_model="claude-3-5-sonnet",
        actual_provider="openrouter",
        actual_model="qwen/qwen3.8-27b",
        fallback_active=True,
        execution_class="fallback",
        status="success",
        brand_mentioned=False,
        is_top1=False,
        top1_brand="Salesforce",
        mentioned_brands=["Salesforce"],
        timestamp="2026-09-17T12:00:00Z",
    )
    assert obs.requested_provider == "claude-3-5-sonnet"
    assert obs.actual_model == "qwen/qwen3.8-27b"
    assert obs.fallback_active is True
    assert obs.execution_class == "fallback"

    d = obs.model_dump()
    assert d["requested_provider"] == "claude-3-5-sonnet"
    assert d["actual_model"] == "qwen/qwen3.8-27b"
    assert d["fallback_active"] is True
    assert d["execution_class"] == "fallback"


def test_calculator_metric_stratification_discovery_mode():
    brands = [{"name": "HubSpot", "domain": "hubspot.com", "is_target": True}, {"name": "Salesforce", "domain": "salesforce.com", "is_target": False}]
    providers = [{"id": "gemini-2.5-flash"}, {"id": "claude-3-5-sonnet"}]
    prompts = [{"prompt_id": "PRM-1", "stratum": "commercial_direct"}, {"prompt_id": "PRM-2", "stratum": "commercial_direct"}]

    # 1 Native observation (HubSpot top-1)
    native_obs = {
        "observation_id": "OBS-1",
        "prompt_id": "PRM-1",
        "provider_id": "gemini-2.5-flash",
        "model": "gemini-2.5-flash",
        "status": "success",
        "brand_mentioned": True,
        "is_top1": True,
        "top1_brand": "HubSpot",
        "mentioned_brands": ["HubSpot"],
        "requested_provider": "gemini-2.5-flash",
        "requested_model": "gemini-2.5-flash",
        "actual_provider": "google",
        "actual_model": "gemini-2.5-flash",
        "fallback_active": False,
        "execution_class": "native",
        "latency_ms": 500,
    }

    # 1 Fallback observation (Salesforce top-1)
    fallback_obs = {
        "observation_id": "OBS-2",
        "prompt_id": "PRM-2",
        "provider_id": "claude-3-5-sonnet",
        "model": "qwen/qwen3.8-27b",
        "status": "success",
        "brand_mentioned": False,
        "is_top1": False,
        "top1_brand": "Salesforce",
        "mentioned_brands": ["Salesforce"],
        "requested_provider": "claude-3-5-sonnet",
        "requested_model": "claude-3-5-sonnet",
        "actual_provider": "openrouter",
        "actual_model": "qwen/qwen3.8-27b",
        "fallback_active": True,
        "execution_class": "fallback",
        "latency_ms": 600,
    }

    calc = BenchmarkCalculator()
    metrics = calc.compute(
        prompts=prompts,
        observations=[native_obs, fallback_obs],
        citations=[],
        brands=brands,
        providers=providers,
        benchmark_mode="discovery",
    )

    assert metrics.benchmark_mode == "discovery"
    assert metrics.execution_class_breakdown["native"] == 1
    assert metrics.execution_class_breakdown["fallback"] == 1
    assert metrics.execution_class_breakdown["failed"] == 0

    # Total observed visibility (blended 2 success observations)
    assert metrics.total_observations == 2
    assert metrics.successful_observations == 2
    assert metrics.total_observed_visibility["sample_size"] == 2
    assert metrics.total_observed_visibility["brands"]["HubSpot"]["mention_rate"] == 50.0
    assert metrics.total_observed_visibility["brands"]["HubSpot"]["top1_rate"] == 50.0

    # Native visibility (1 native observation)
    assert metrics.native_visibility["sample_size"] == 1
    assert metrics.native_visibility["brands"]["HubSpot"]["mention_rate"] == 100.0
    assert metrics.native_visibility["brands"]["HubSpot"]["top1_rate"] == 100.0

    # Fallback visibility (1 fallback observation)
    assert metrics.fallback_visibility["sample_size"] == 1
    assert metrics.fallback_visibility["brands"]["HubSpot"]["mention_rate"] == 0.0
    assert metrics.fallback_visibility["brands"]["Salesforce"]["mention_rate"] == 100.0


def test_calculator_metric_stratification_strict_mode():
    brands = [{"name": "HubSpot", "domain": "hubspot.com", "is_target": True}, {"name": "Salesforce", "domain": "salesforce.com", "is_target": False}]
    providers = [{"id": "gemini-2.5-flash"}, {"id": "claude-3-5-sonnet"}]
    prompts = [{"prompt_id": "PRM-1", "stratum": "commercial_direct"}, {"prompt_id": "PRM-2", "stratum": "commercial_direct"}]

    # 1 Native observation (HubSpot top-1)
    native_obs = {
        "observation_id": "OBS-1",
        "prompt_id": "PRM-1",
        "provider_id": "gemini-2.5-flash",
        "model": "gemini-2.5-flash",
        "status": "success",
        "brand_mentioned": True,
        "is_top1": True,
        "top1_brand": "HubSpot",
        "mentioned_brands": ["HubSpot"],
        "requested_provider": "gemini-2.5-flash",
        "requested_model": "gemini-2.5-flash",
        "actual_provider": "google",
        "actual_model": "gemini-2.5-flash",
        "fallback_active": False,
        "execution_class": "native",
        "latency_ms": 500,
    }

    # 1 Strict-failed observation (fallback rejected in strict mode)
    failed_obs = {
        "observation_id": "OBS-2",
        "prompt_id": "PRM-2",
        "provider_id": "claude-3-5-sonnet",
        "model": "qwen/qwen3.8-27b",
        "status": "failed",
        "brand_mentioned": False,
        "is_top1": False,
        "top1_brand": None,
        "mentioned_brands": [],
        "requested_provider": "claude-3-5-sonnet",
        "requested_model": "claude-3-5-sonnet",
        "actual_provider": "openrouter",
        "actual_model": "qwen/qwen3.8-27b",
        "fallback_active": True,
        "execution_class": "failed",
        "error": {"type": "fallback_detected_strict_mode", "message": "Fallback model rejected in strict mode"},
    }

    calc = BenchmarkCalculator()
    metrics = calc.compute(
        prompts=prompts,
        observations=[native_obs, failed_obs],
        citations=[],
        brands=brands,
        providers=providers,
        benchmark_mode="strict",
    )

    assert metrics.benchmark_mode == "strict"
    assert metrics.execution_class_breakdown["native"] == 1
    assert metrics.execution_class_breakdown["fallback"] == 0
    assert metrics.execution_class_breakdown["failed"] == 1

    # In strict mode, total success count is only the native one
    assert metrics.successful_observations == 1
    assert metrics.total_observations == 2

    # Native visibility has HubSpot at 100.0 (1/1 success)
    assert metrics.native_visibility["sample_size"] == 1
    assert metrics.native_visibility["brands"]["HubSpot"]["mention_rate"] == 100.0

    # Fallback visibility has sample size 0 in strict mode
    assert metrics.fallback_visibility["sample_size"] == 0


def test_benchmark_manifest_provenance_and_mode(tmp_path):
    builder = BenchmarkBuilder(dataset_id="test-provenance-2026.1")

    obs = [
        {
            "observation_id": "OBS-1",
            "prompt_id": "PRM-1",
            "provider_id": "gemini-2.5-flash",
            "model": "gemini-2.5-flash",
            "status": "success",
            "brand_mentioned": True,
            "is_top1": True,
            "top1_brand": "HubSpot",
            "mentioned_brands": ["HubSpot"],
            "requested_provider": "gemini-2.5-flash",
            "requested_model": "gemini-2.5-flash",
            "actual_provider": "google",
            "actual_model": "gemini-2.5-flash",
            "fallback_active": False,
            "execution_class": "native",
            "timestamp": "2026-09-17T12:00:00Z",
        }
    ]

    model_prov = {
        "gemini-2.5-flash": {
            "requested": "gemini-2.5-flash",
            "verified_model": "gemini-2.5-flash",
            "fallback_detected": False,
            "status": "native",
        }
    }

    out_dir = str(tmp_path / "bmk")
    pkg_path = builder.build_package(
        out_dir=out_dir,
        prompts=[{"prompt_id": "PRM-1", "prompt_text": "Best CRM", "intent_stratum": "commercial_direct", "entity_targets": ["HubSpot"]}],
        observations=obs,
        citations=[],
        brands=[{"brand": "HubSpot", "name": "HubSpot", "domain": "hubspot.com", "is_target": True}],
        providers=[{"id": "gemini-2.5-flash", "provider_id": "gemini-2.5-flash"}],
        benchmark_mode="strict",
        model_provenance=model_prov,
    )

    manifest_file = tmp_path / "bmk" / "test-provenance-2026.1" / "manifest.json"
    if not manifest_file.exists():
        manifest_file = tmp_path / "bmk" / "manifest.json"
    assert manifest_file.exists()

    import json
    with open(manifest_file, "r") as f:
        data = json.load(f)

    assert data["benchmark_mode"] == "strict"
    assert "model_provenance" in data
    assert data["model_provenance"]["gemini-2.5-flash"]["status"] == "native"
