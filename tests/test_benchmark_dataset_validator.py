import pytest
from pathlib import Path
from geo_scope.benchmark.dataset_validator import validate_benchmark_dataset, format_validation_report
from geo_scope.benchmark.reproducer import BenchmarkReproducer


def test_validate_benchmark_dataset_success():
    release_dir = Path("benchmark/releases/global-ai-answers-2026.1")
    res = validate_benchmark_dataset(release_dir)
    assert res["status"] == "PASS"
    assert res["passed"] is True
    assert res["checks"]["required_files"]["passed"] is True
    assert res["checks"]["checksum_matches"]["passed"] is True
    assert res["checks"]["prompts_valid"]["passed"] is True
    assert res["checks"]["raw_responses_exist"]["passed"] is True
    assert res["checks"]["observations_metadata"]["passed"] is True
    assert res["checks"]["no_secrets_detected"]["passed"] is True

    report = format_validation_report(res)
    assert "Overall Status: PASS" in report


def test_reproduce_global_benchmark():
    release_dir = Path("benchmark/releases/global-ai-answers-2026.1")
    reproducer = BenchmarkReproducer()
    res = reproducer.verify_and_reproduce(release_dir)
    assert res["success"] is True
    assert res["checksums_valid"] is True
    assert res["metrics_matched"] is True
    assert len(res["differences"]) == 0
