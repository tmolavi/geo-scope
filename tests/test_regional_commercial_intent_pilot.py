"""
Validation and Quality Gate Tests for GEO-Scope Regional Commercial AI Visibility Pilot 2026.1 (Iran & Türkiye).
Verifies:
1. Directory structure and required evidence files
2. Cryptographic SHA-256 integrity of all artifacts
3. Prompt universe: 24 unique unbranded neutral buyer prompts (12 IR, 12 TR)
4. Stratified intent distribution (4 intents x 3 per market)
5. Schema conformance: prompt schema, manifest schema, metrics schema
6. Neutrality check (zero brand mentions in buyer questions)
7. Cost estimation ($10 ceiling, $2.64 estimated for 144 planned observations)
8. Provider governance and honest NOT_RUN / PROVIDER_UNAVAILABLE gating
9. Entity registry completeness for both markets
"""

import json
from pathlib import Path
import pytest
import jsonschema

from geo_scope.benchmark.hasher import verify_dataset_checksums

REPO_ROOT = Path(__file__).parent.parent
PILOT_DIR = REPO_ROOT / "benchmarks" / "regional-commercial-intent-2026.1"
SCHEMA_DIR = REPO_ROOT / "schemas" / "v0.3"


def test_pilot_directory_and_required_evidence_files_exist():
    assert PILOT_DIR.is_dir(), f"Pilot directory missing at {PILOT_DIR}"
    required_files = [
        "manifest.json",
        "prompts.jsonl",
        "run-config.json",
        "methodology.md",
        "limitations.md",
        "README.md",
        "entities.json",
        "metrics.json",
        "raw_responses.jsonl",
        "observations.jsonl",
        "errors.jsonl",
        "checksums.sha256",
    ]
    for filename in required_files:
        filepath = PILOT_DIR / filename
        assert filepath.exists(), f"Required evidence file missing: {filename}"


def test_pilot_cryptographic_checksums_intact():
    res = verify_dataset_checksums(PILOT_DIR)
    assert res["valid"] is True, f"Checksum verification failed: {res}"
    assert len(res["mismatches"]) == 0
    assert len(res["missing_files"]) == 0
    assert len(res["verified_files"]) >= 10


def test_pilot_prompt_dataset_schema_and_distribution():
    prompt_schema = json.loads((SCHEMA_DIR / "prompt.schema.json").read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(prompt_schema)

    prompts_file = PILOT_DIR / "prompts.jsonl"
    lines = [line.strip() for line in prompts_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    
    assert len(lines) == 24, f"Expected exactly 24 prompts, found {len(lines)}"

    ir_prompts = []
    tr_prompts = []
    intents = {}
    intent_groups = {}
    topics = set()
    prompt_ids = set()

    for idx, line in enumerate(lines, 1):
        obj = json.loads(line)
        errors = list(validator.iter_errors(obj))
        assert not errors, f"Prompt at line {idx} failed schema validation: {[e.message for e in errors]}"

        pid = obj["id"]
        assert pid not in prompt_ids, f"Duplicate prompt ID: {pid}"
        prompt_ids.add(pid)

        lang = obj["language"]
        if lang == "fa":
            ir_prompts.append(obj)
            assert obj["locale"] == "fa-IR"
            assert obj["country_iso"] == "IR"
        elif lang == "tr":
            tr_prompts.append(obj)
            assert obj["locale"] == "tr-TR"
            assert obj["country_iso"] == "TR"
        else:
            pytest.fail(f"Unexpected language in prompt: {lang}")

        # Intent distribution
        intent = obj["intent"]
        intents[intent] = intents.get(intent, 0) + 1

        grp = obj.get("intent_group")
        intent_groups[grp] = intent_groups.get(grp, 0) + 1

        topics.add(obj.get("topic"))
        assert obj["prompt_policy"] == "neutral"
        assert obj["source_type"] == "research_questions"

    # Exactly 12 prompts per market
    assert len(ir_prompts) == 12
    assert len(tr_prompts) == 12

    # Exactly 4 intent groups with 6 prompts each (3 IR + 3 TR)
    expected_intent_groups = ["best_recommendation", "comparison", "pricing_vendor_selection", "criteria_guidance"]
    for eg in expected_intent_groups:
        assert intent_groups.get(eg) == 6, f"Intent group {eg} has {intent_groups.get(eg)} prompts, expected 6"

    # Per market intent balance
    for market_prompts, market_name in [(ir_prompts, "Iran"), (tr_prompts, "Turkiye")]:
        market_groups = {}
        for p in market_prompts:
            g = p.get("intent_group")
            market_groups[g] = market_groups.get(g, 0) + 1
        for eg in expected_intent_groups:
            assert market_groups.get(eg) == 3, f"{market_name} missing balanced 3 prompts for {eg}"

    # Verify all 6 commercial service topics covered
    assert "seo_agencies" in topics
    assert "geo_service_providers" in topics
    assert "ai_visibility_measurement_tools" in topics
    assert "technical_seo_auditing" in topics
    assert "digital_pr_providers" in topics
    assert "ai_search_consulting" in topics


def test_pilot_prompt_neutrality():
    """Verify all 24 prompts are completely unbranded buyer queries."""
    branded_terms = [
        "inten", "اینتن", "web24", "وب24", "وب ۲۴", "novin", "نوین", "triboon", "تریبون",
        "dimarketing", "دی مارکتینگ", "دی‌مارکتینگ", "zeo", "webtures", "roas", "semtr",
        "stradiji", "b2press", "semrush", "ahrefs"
    ]
    prompts_file = PILOT_DIR / "prompts.jsonl"
    lines = [json.loads(line) for line in prompts_file.read_text(encoding="utf-8").splitlines() if line.strip()]

    for p in lines:
        query_lower = p["query"].lower()
        for b in branded_terms:
            assert b not in query_lower, f"Brand term '{b}' found in neutral prompt: {p['id']} - {p['query']}"


def test_pilot_manifest_schema_and_metadata():
    manifest_schema = json.loads((SCHEMA_DIR / "manifest.schema.json").read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(manifest_schema)

    manifest_file = PILOT_DIR / "manifest.json"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))

    errors = list(validator.iter_errors(manifest))
    assert not errors, f"Manifest failed schema validation: {[e.message for e in errors]}"

    assert manifest["benchmark_version"] == "regional-commercial-intent-2026.1"
    assert manifest["execution_mode"] == "empirical"
    assert manifest["total_prompts"] == 24
    assert manifest["repeat_count"] == 2
    assert manifest["measurement_status"] == "NOT_RUN"
    assert set(manifest["provider_matrix"]) == {"chatgpt_search", "gemini_grounding", "perplexity_sonar"}

    for p in manifest["provider_matrix"]:
        assert manifest["provider_status"][p] == "PROVIDER_UNAVAILABLE"


def test_pilot_metrics_schema_conformance():
    metrics_schema = json.loads((SCHEMA_DIR / "metrics.schema.json").read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(metrics_schema)

    metrics_file = PILOT_DIR / "metrics.json"
    metrics = json.loads(metrics_file.read_text(encoding="utf-8"))

    errors = list(validator.iter_errors(metrics))
    assert not errors, f"Metrics failed schema validation: {[e.message for e in errors]}"

    assert metrics["mode"] == "empirical"
    assert metrics["measurement_status"] == "NOT_RUN"
    assert "provider_breakdown" in metrics
    for p in ["chatgpt_search", "gemini_grounding", "perplexity_sonar"]:
        pb = metrics["provider_breakdown"][p]
        assert pb["metric_denominator_n"] == 0
        assert pb["attempted_n"] == 0
        assert pb["status"] == "PROVIDER_UNAVAILABLE"


def test_pilot_run_config_budget_and_cost_estimation():
    config_file = PILOT_DIR / "run-config.json"
    config = json.loads(config_file.read_text(encoding="utf-8"))

    assert config["benchmark_id"] == "regional-commercial-intent-2026.1"
    assert config["status"] == "NOT_RUN"
    
    # 24 prompts x 3 engines x 2 repeats = 144
    sampling = config["sampling_plan"]
    assert sampling["total_unique_prompts"] == 24
    assert sampling["engines_count"] == 3
    assert sampling["repetitions_per_prompt"] == 2
    assert sampling["total_planned_observations"] == 144

    # Budget checks
    budget = config["budget"]
    assert budget["budget_ceiling_usd"] == 10.00
    assert budget["estimated_execution_cost_usd"] <= 10.00
    assert budget["within_budget"] is True
    assert budget["estimated_execution_cost_usd"] == 2.64


def test_pilot_entities_registry_coverage():
    entities_file = PILOT_DIR / "entities.json"
    entities = json.loads(entities_file.read_text(encoding="utf-8"))

    assert len(entities) >= 10
    ir_entities = [e for e in entities if e.get("market") == "IR"]
    tr_entities = [e for e in entities if e.get("market") == "TR"]

    assert len(ir_entities) >= 5
    assert len(tr_entities) >= 5

    ir_ids = {e["id"] for e in ir_entities}
    tr_ids = {e["id"] for e in tr_entities}

    assert {"inten", "web24", "novin", "triboon", "dimarketing"}.issubset(ir_ids)
    assert {"zeo", "webtures", "roas", "semtr", "b2press"}.issubset(tr_ids)

    for e in entities:
        assert "id" in e
        assert len(e.get("names", [])) >= 1
        assert len(e.get("domains", [])) >= 1
        assert "do_not_confuse" in e
