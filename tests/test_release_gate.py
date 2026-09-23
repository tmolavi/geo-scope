"""
Tests for Benchmark Release Quality Gate and Provider Identity Integrity.
"""

import json
from pathlib import Path
import pytest
from geo_scope.release_gate import evaluate_release_gate


def test_release_gate_fails_on_missing_evidence_files(tmp_path):
    # Empty directory
    res = evaluate_release_gate(tmp_path)
    assert res["passed"] is False
    assert res["status"] == "FAIL"
    assert res["checks"]["evidence_artifacts_completeness"]["passed"] is False


def test_release_gate_detects_simulation_in_live_release(tmp_path):
    # Setup mock dataset structure
    manifest = {
        "schema_version": "0.3.0",
        "benchmark_version": "2026.2",
        "execution_mode": "live",
        "provider_matrix": ["perplexity_sonar"],
        "prompt_policy": "neutral",
        "repeat_count": 5,
        "comparison_batch_id": "test-batch",
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (tmp_path / "prompts.jsonl").write_text('{"id":"p1","query":"q"}\n', encoding="utf-8")
    (tmp_path / "entities.json").write_text('[]', encoding="utf-8")
    (tmp_path / "metrics.json").write_text('{"provider_breakdown":{"p":{"attempted_n":1,"successful_n":1,"failed_n":0,"metric_denominator_n":1}}}', encoding="utf-8")
    (tmp_path / "errors.jsonl").write_text('', encoding="utf-8")
    (tmp_path / "methodology.md").write_text('# Methodology', encoding="utf-8")
    (tmp_path / "limitations.md").write_text('# Limitations', encoding="utf-8")
    (tmp_path / "checksums.sha256").write_text('', encoding="utf-8")

    # Contaminated raw response marked simulation
    raw_record = {
        "provider": "perplexity_sonar",
        "requested_provider": "perplexity_sonar",
        "actual_provider": "perplexity_sonar",
        "model": "sonar",
        "requested_model": "sonar",
        "actual_model": "sonar",
        "execution_mode": "simulation",  # Contamination!
        "response_text": "Sample text",
        "citations": [],
    }
    (tmp_path / "raw_responses.jsonl").write_text(json.dumps(raw_record) + "\n", encoding="utf-8")
    (tmp_path / "observations.jsonl").write_text('{"provider":"perplexity_sonar"}\n', encoding="utf-8")

    res = evaluate_release_gate(tmp_path)
    assert res["checks"]["no_simulation_records"]["passed"] is False
    assert res["passed"] is False


def test_release_gate_detects_provider_mismatch(tmp_path):
    manifest = {
        "schema_version": "0.3.0",
        "benchmark_version": "2026.2",
        "execution_mode": "live",
        "provider_matrix": ["perplexity_sonar"],
        "prompt_policy": "neutral",
        "repeat_count": 5,
        "comparison_batch_id": "test-batch",
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (tmp_path / "prompts.jsonl").write_text('{"id":"p1","query":"q"}\n', encoding="utf-8")
    (tmp_path / "entities.json").write_text('[]', encoding="utf-8")
    (tmp_path / "metrics.json").write_text('{"provider_breakdown":{"p":{"attempted_n":1,"successful_n":1,"failed_n":0,"metric_denominator_n":1}}}', encoding="utf-8")
    (tmp_path / "errors.jsonl").write_text('', encoding="utf-8")
    (tmp_path / "methodology.md").write_text('# Methodology', encoding="utf-8")
    (tmp_path / "limitations.md").write_text('# Limitations', encoding="utf-8")
    (tmp_path / "checksums.sha256").write_text('', encoding="utf-8")
    (tmp_path / "observations.jsonl").write_text('{"provider":"perplexity_sonar"}\n', encoding="utf-8")

    # Raw response with provider mismatch (surrogate / unrequested provider)
    raw_record = {
        "provider": "perplexity_sonar",
        "requested_provider": "perplexity_sonar",
        "actual_provider": "ollama_fallback",  # Mismatch!
        "model": "sonar",
        "requested_model": "sonar",
        "actual_model": "llama-3-8b",
        "execution_mode": "live",
        "fallback_used": True,
        "response_text": "Sample text",
        "citations": [],
    }
    (tmp_path / "raw_responses.jsonl").write_text(json.dumps(raw_record) + "\n", encoding="utf-8")

    res = evaluate_release_gate(tmp_path)
    assert res["checks"]["no_provider_mismatch"]["passed"] is False
    assert res["checks"]["no_hidden_fallback"]["passed"] is False
    assert res["passed"] is False


def test_release_gate_enforces_repeat_count(tmp_path):
    manifest = {
        "schema_version": "0.3.0",
        "benchmark_version": "2026.2",
        "execution_mode": "live",
        "provider_matrix": ["perplexity_sonar"],
        "prompt_policy": "neutral",
        "repeat_count": 2,  # Insufficient repeats for empirical release (< 5)
        "comparison_batch_id": "test-batch",
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (tmp_path / "prompts.jsonl").write_text('{"id":"p1","query":"q"}\n', encoding="utf-8")
    (tmp_path / "entities.json").write_text('[]', encoding="utf-8")
    (tmp_path / "raw_responses.jsonl").write_text('{"provider":"p","requested_provider":"p","actual_provider":"p","model":"m","requested_model":"m","actual_model":"m"}\n', encoding="utf-8")
    (tmp_path / "observations.jsonl").write_text('{"provider":"p"}\n', encoding="utf-8")
    (tmp_path / "metrics.json").write_text('{"provider_breakdown":{"p":{"attempted_n":1,"successful_n":1,"failed_n":0,"metric_denominator_n":1}}}', encoding="utf-8")
    (tmp_path / "errors.jsonl").write_text('', encoding="utf-8")
    (tmp_path / "methodology.md").write_text('# Methodology', encoding="utf-8")
    (tmp_path / "limitations.md").write_text('# Limitations', encoding="utf-8")
    (tmp_path / "checksums.sha256").write_text('', encoding="utf-8")

    res = evaluate_release_gate(tmp_path)
    assert res["checks"]["repeat_protocol_enforcement"]["passed"] is False
    assert res["passed"] is False
