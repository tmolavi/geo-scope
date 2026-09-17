# Comprehensive test suite for GEO-Scope Public Benchmark & Evidence Dataset v1
import json
import os
import shutil
import tempfile
from pathlib import Path
import pytest

from geo_scope.benchmark.models import (
    BenchmarkManifest,
    PromptRecord,
    ObservationRecord,
    CitationEvidenceRecord,
    BrandBenchmarkMetrics,
    ProviderBenchmarkMetrics,
    BenchmarkMetrics,
    MetricEstimate,
    StatisticalFactorAnalysis,
)
from geo_scope.benchmark.hasher import (
    compute_file_sha256,
    compute_bytes_sha256,
    compute_dataset_checksums,
    compute_composite_hash,
    write_checksums_file,
    verify_dataset_checksums,
)
from geo_scope.benchmark.calculator import (
    BenchmarkCalculator,
    calculate_bootstrap_ci,
    make_metric_estimate,
)
from geo_scope.benchmark.builder import BenchmarkBuilder
from geo_scope.benchmark.reproducer import BenchmarkReproducer
from geo_scope.mcp_server import handle_tool_call


def test_bootstrap_ci_calculation():
    # Empty data
    low, high = calculate_bootstrap_ci([])
    assert low is None
    assert high is None

    # Single item
    low, high = calculate_bootstrap_ci([1])
    assert low == 1.0
    assert high == 1.0

    # Multiple items
    data = [1, 1, 1, 0, 1, 0, 1, 1]
    low, high = calculate_bootstrap_ci(data, n_resamples=500, ci=0.95, seed=42)
    assert low is not None and high is not None
    assert 0.0 <= low <= high <= 1.0


def test_zero_success_metric_semantics():
    calc = BenchmarkCalculator()
    brands = [{"name": "AcmeCorp", "is_target": True}]
    providers = [{"id": "mock_p"}]

    # Zero successful observations (all failed)
    obs = [
        {"observation_id": "o1", "status": "failed", "provider_id": "mock_p"},
        {"observation_id": "o2", "status": "failed", "provider_id": "mock_p"},
    ]
    metrics = calc.compute(
        prompts=[],
        observations=obs,
        citations=[],
        brands=brands,
        providers=providers,
        dataset_id="test-empty",
    )

    assert metrics.successful_observations == 0
    assert metrics.failed_observations == 2
    b_metrics = metrics.brands[0]
    assert b_metrics.mention_rate.value is None
    assert b_metrics.mention_rate.status == "insufficient_data"
    assert b_metrics.top1_rate.value is None
    assert b_metrics.top1_rate.status == "insufficient_data"
    assert b_metrics.share_of_model.value is None
    assert b_metrics.share_of_model.status == "insufficient_data"


def test_hasher_and_tamper_detection(tmp_path):
    # Setup dummy directory
    d = tmp_path / "dataset"
    d.mkdir()
    (d / "file1.txt").write_text("Hello World\n", encoding="utf-8")
    (d / "file2.json").write_text('{"key": "value"}\n', encoding="utf-8")

    # Generate checksums
    write_checksums_file(d)
    assert (d / "checksums.sha256").exists()

    # Initial verification should pass
    res = verify_dataset_checksums(d)
    assert res["valid"] is True
    assert len(res["verified_files"]) == 2
    assert len(res["mismatches"]) == 0

    # Tamper with file1
    (d / "file1.txt").write_text("Tampered content\n", encoding="utf-8")
    res_tampered = verify_dataset_checksums(d)
    assert res_tampered["valid"] is False
    assert len(res_tampered["mismatches"]) == 1
    assert res_tampered["mismatches"][0]["file"] == "file1.txt"

    # Add unauthorized extra file
    (d / "file1.txt").write_text("Hello World\n", encoding="utf-8")  # restore
    (d / "extra.txt").write_text("Unauthorized\n", encoding="utf-8")
    res_extra = verify_dataset_checksums(d)
    assert res_extra["valid"] is False
    assert "extra.txt" in res_extra["extra_files"]


def test_builder_and_reproducer_roundtrip(tmp_path):
    builder = BenchmarkBuilder(dataset_id="test-benchmark-v1")
    prompts = [
        {"prompt_id": "p1", "text": "Best CRM", "intent_stratum": "commercial", "language": "en", "target_brand": "HubSpot", "competitors": ["Salesforce"]},
        {"prompt_id": "p2", "text": "HubSpot vs Salesforce", "intent_stratum": "comparative", "language": "en", "target_brand": "HubSpot", "competitors": ["Salesforce"]},
    ]
    brands = [
        {"name": "HubSpot", "is_target": True, "domain": "hubspot.com"},
        {"name": "Salesforce", "is_target": False, "domain": "salesforce.com"},
    ]
    providers = [
        {"id": "prov1", "name": "Provider One", "search_grounded": True},
    ]
    observations = [
        {
            "observation_id": "o1",
            "prompt_id": "p1",
            "provider_id": "prov1",
            "model": "prov1",
            "execution_mode": "synthetic",
            "status": "success",
            "brand_mentioned": True,
            "brand_rank": 1,
            "is_top1": True,
            "sentiment": "positive",
            "timestamp": "2026-03-15T12:00:00Z",
        },
        {
            "observation_id": "o2",
            "prompt_id": "p2",
            "provider_id": "prov1",
            "model": "prov1",
            "execution_mode": "synthetic",
            "status": "success",
            "brand_mentioned": False,
            "brand_rank": None,
            "is_top1": False,
            "sentiment": "neutral",
            "timestamp": "2026-03-15T12:00:00Z",
        },
    ]
    citations = [
        {"citation_id": "c1", "prompt_id": "p1", "provider_id": "prov1", "domain": "hubspot.com", "url": "https://hubspot.com", "cited_for_brand": "HubSpot"}
    ]

    pkg_dir = builder.build_package(
        out_dir=tmp_path,
        prompts=prompts,
        observations=observations,
        citations=citations,
        brands=brands,
        providers=providers,
        execution_mode="synthetic",
        research_status="demo_only",
    )

    assert pkg_dir.exists()
    assert (pkg_dir / "manifest.json").exists()
    assert (pkg_dir / "checksums.sha256").exists()
    assert (pkg_dir / "metrics.json").exists()

    reproducer = BenchmarkReproducer()
    res = reproducer.verify_and_reproduce(pkg_dir)
    assert res["success"] is True
    assert res["checksums_valid"] is True
    assert res["metrics_matched"] is True
    assert len(res["differences"]) == 0


def test_reference_benchmark_dataset_verification():
    ref_dir = Path("benchmark/geo-scope-benchmark-2026.1")
    assert ref_dir.exists(), "Reference benchmark dataset directory must exist"

    reproducer = BenchmarkReproducer()
    res = reproducer.verify_and_reproduce(ref_dir)
    assert res["success"] is True, f"Reference dataset reproduction failed: {res.get('differences')}"
    assert res["checksums_valid"] is True
    assert res["metrics_matched"] is True


@pytest.mark.asyncio
async def test_mcp_benchmark_tools():
    ref_dir = "benchmark/geo-scope-benchmark-2026.1"

    # Test verify_benchmark tool
    v_res = await handle_tool_call("verify_benchmark", {"dataset_path": ref_dir})
    assert v_res["valid"] is True
    assert len(v_res["verified_files"]) >= 8

    # Test reproduce_benchmark tool
    r_res = await handle_tool_call("reproduce_benchmark", {"dataset_path": ref_dir, "tolerance": 0.05})
    assert r_res["success"] is True
    assert r_res["metrics_matched"] is True
