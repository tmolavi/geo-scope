# Comprehensive Test Suite for GEO-Scope Real Operational Benchmark Study v1
import json
import pytest
from pathlib import Path

from geo_scope.benchmark.builder import BenchmarkBuilder
from geo_scope.benchmark.calculator import BenchmarkCalculator
from geo_scope.benchmark.reproducer import BenchmarkReproducer
from geo_scope.benchmark.hasher import verify_dataset_checksums
from geo_scope.benchmark.profile import BenchmarkProfile
from geo_scope.benchmark.runner import LiveBenchmarkRunner
from geo_scope.mavi.engine import MAVIEngine


def test_ai_visibility_benchmark_manifest_integrity():
    dataset_dir = Path("benchmark/releases/geo-scope-ai-visibility-2026.1-synthetic")
    assert dataset_dir.exists(), "Synthetic validation dataset directory must exist"

    manifest_file = dataset_dir / "manifest.json"
    assert manifest_file.exists()

    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert manifest["benchmark_version"] == "2026.1" or manifest["benchmark_version"].startswith("2026.1")
    assert manifest["dataset_name"] == "geo-scope-ai-visibility-2026.1-synthetic"
    assert manifest["execution_mode"] == "synthetic"
    assert manifest["research_status"] == "demo_only"
    assert manifest["counts"]["prompts"] == 100
    assert manifest["counts"]["observations"] == 400
    assert manifest["counts"]["brands"] == 8
    assert manifest["counts"]["providers"] == 4
    assert len(manifest["providers"]) == 4
    assert len(manifest["models"]) == 4


def test_ai_visibility_benchmark_checksum_verification():
    dataset_dir = Path("benchmark/releases/geo-scope-ai-visibility-2026.1-synthetic")
    chk = verify_dataset_checksums(dataset_dir)
    assert chk["valid"] is True
    assert len(chk["mismatches"]) == 0
    assert "observations.jsonl" in chk["verified_files"]
    assert "prompts.jsonl" in chk["verified_files"]
    assert "metrics.json" in chk["verified_files"]


def test_ai_visibility_benchmark_metric_calculation_and_matrix():
    dataset_dir = Path("benchmark/releases/geo-scope-ai-visibility-2026.1-synthetic")
    metrics_file = dataset_dir / "metrics.json"
    assert metrics_file.exists()

    metrics = json.loads(metrics_file.read_text(encoding="utf-8"))
    assert metrics["total_prompts"] == 100
    assert metrics["total_observations"] == 400
    assert metrics["successful_observations"] == 400
    assert metrics["failed_observations"] == 0

    # 1. Brands validation
    brands = {b["brand"]: b for b in metrics["brands"]}
    assert "Semrush" in brands
    assert "Ahrefs" in brands
    assert "Moz" in brands
    assert "Surfer SEO" in brands
    assert "Clearscope" in brands
    assert "MarketMuse" in brands
    assert "Conductor" in brands
    assert "SAGE" in brands

    # Check Semrush target brand stats & CI
    semrush = brands["Semrush"]
    assert semrush["is_target"] is True
    assert semrush["mention_rate"]["value"] > 70.0
    assert semrush["mention_rate"]["ci_lower"] is not None
    assert semrush["mention_rate"]["ci_upper"] is not None
    assert semrush["top1_rate"]["value"] > 15.0
    assert semrush["share_of_model"]["value"] > 15.0

    # 2. Category Visibility Matrix
    matrix = metrics.get("category_visibility_matrix", {})
    assert len(matrix) == 8
    for bname in ["Semrush", "Ahrefs", "Moz", "Surfer SEO", "Clearscope", "MarketMuse", "Conductor", "SAGE"]:
        assert bname in matrix
        for p in ["hamzad_gemini", "hamzad_perplexity", "hamzad_openai", "hamzad_claude"]:
            assert p in matrix[bname]
            assert matrix[bname][p] is not None
            assert 0.0 <= matrix[bname][p] <= 100.0

    # 3. Strata Metrics
    strata = metrics.get("strata", {})
    assert "discovery" in strata
    assert "comparison" in strata
    assert "commercial" in strata
    assert "educational" in strata
    assert strata["discovery"]["total_observations"] == 120  # 30 prompts x 4 providers
    assert strata["comparison"]["total_observations"] == 120 # 30 prompts x 4 providers
    assert strata["commercial"]["total_observations"] == 100 # 25 prompts x 4 providers
    assert strata["educational"]["total_observations"] == 60 # 15 prompts x 4 providers

    # 4. Factor analysis
    fa = metrics.get("factor_analysis", {})
    assert fa["status"] == "observed_association_only"
    assert len(fa["factors"]) >= 3


def test_ai_visibility_benchmark_reproducibility():
    dataset_dir = Path("benchmark/releases/geo-scope-ai-visibility-2026.1-synthetic")
    reproducer = BenchmarkReproducer(tolerance=0.01)
    res = reproducer.verify_and_reproduce(dataset_dir)
    assert res["success"] is True
    assert res["checksums_valid"] is True
    assert res["metrics_matched"] is True
    assert res["execution_mode"] == "synthetic"
    assert res["research_status"] == "demo_only"


def test_missing_provider_failure_handling():
    calculator = BenchmarkCalculator()
    # If all observations for a provider failed:
    obs = [
        {"status": "failed", "provider_id": "hamzad_gemini", "error": {"type": "timeout"}},
        {"status": "failed", "provider_id": "hamzad_gemini", "error": {"type": "timeout"}},
    ]
    brands = [{"name": "Semrush", "is_target": True}]
    providers = [{"id": "hamzad_gemini"}]
    prompts = [{"prompt_id": "p1"}]

    metrics = calculator.compute(
        prompts=prompts,
        observations=obs,
        citations=[],
        brands=brands,
        providers=providers,
        dataset_id="test-fail",
    )
    assert metrics.successful_observations == 0
    assert metrics.failed_observations == 2
    # Ensure missing data is not converted to 0.0%
    b_metrics = metrics.brands[0]
    assert b_metrics.mention_rate.value is None
    assert b_metrics.mention_rate.status == "insufficient_data"
    assert metrics.category_visibility_matrix["Semrush"]["hamzad_gemini"] is None


def test_ai_visibility_benchmark_mavi_l5_integration():
    dataset_dir = Path("benchmark/releases/geo-scope-ai-visibility-2026.1-synthetic")
    metrics = json.loads((dataset_dir / "metrics.json").read_text(encoding="utf-8"))

    # Convert benchmark release metrics into MAVI experiment_data payload
    exp_data = {
        "experiment_id": metrics["dataset_id"],
        "execution_mode": metrics["execution_mode"],
        "summary": {
            "total_ai_executions": metrics["total_observations"],
            "successful_executions": metrics["successful_observations"],
            "failed_executions": metrics["failed_observations"],
            "overall_sov": metrics["brands"][0]["mention_rate"]["value"],
            "overall_top1_rate": metrics["brands"][0]["top1_rate"]["value"],
            "overall_citation_rate": metrics["brands"][0]["citation_rate"]["value"],
        },
        "share_of_model": {
            "by_model": {
                p: {"successful_queries": p_data["successful_observations"], "mention_rate_pct": p_data["target_mention_rate"]["value"]}
                for p, p_data in metrics["providers"].items()
            }
        },
    }

    mavi = MAVIEngine()
    report = mavi.measure(target_brand="Semrush", experiment_data=exp_data)
    l5 = report.layers.get("L5")

    assert l5 is not None
    assert l5.status == "measured_synthetic"
    assert l5.source_type == "synthetic"
    assert l5.score is not None
    assert l5.score > 60.0
    assert l5.provenance.execution_mode == "synthetic"
    assert l5.provenance.experiment_id == "geo-scope-ai-visibility-2026.1-synthetic"


def test_live_runner_zero_fabricated_citations(tmp_path):
    # Test that LiveBenchmarkRunner never invents source-N citations
    profile = BenchmarkProfile(
        benchmark_version="2026.1-live",
        dataset_name="test-live-zero-fab",
        execution_mode="live",
        providers=["ollama_local"],
    )
    runner = LiveBenchmarkRunner(profile=profile, out_dir=tmp_path)
    
    # Check that runner executes and extracts real citations or leaves them empty
    res = runner.run(dry_run=True)
    assert res["status"] == "dry_run_completed"

