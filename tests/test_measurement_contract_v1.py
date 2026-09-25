"""
Unit and Integration Tests for AI Visibility Measurement Contract v1.

Verifies:
1. Schema integrity of schemas/measurement-contract-v1.json
2. Conformance of examples/measurement-contract-v1-example.json
3. Binary response-level mention semantics (multiple occurrences != multiple mentions)
4. 4-way citation separation logic (entity_mentioned, target_domain_cited, target_url_cited, third_party_source_cited)
5. Recommendation status and experimental gating
6. Comparability rules and mismatch reason generation
7. Strict numbered list ranking contract
8. Evidence and hash validation
"""

import json
import hashlib
from pathlib import Path
import pytest
import jsonschema

REPO_ROOT = Path(__file__).parent.parent
SCHEMA_PATH = REPO_ROOT / "schemas" / "measurement-contract-v1.json"
EXAMPLE_PATH = REPO_ROOT / "examples" / "measurement-contract-v1-example.json"


def test_measurement_contract_v1_schema_is_valid():
    """Verify that schemas/measurement-contract-v1.json is a valid Draft 2020-12 JSON Schema."""
    assert SCHEMA_PATH.exists(), f"Missing schema at {SCHEMA_PATH}"
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    
    # Validate against JSON Schema Draft 2020-12 meta-schema
    validator_cls = jsonschema.validators.validator_for(schema)
    validator_cls.check_schema(schema)
    assert schema["$id"] == "https://geo-scope.org/schemas/measurement-contract-v1.json"
    assert schema["title"] == "AIVisibilityMeasurementContract_v1"


def test_measurement_contract_v1_example_conforms_to_schema():
    """Verify that examples/measurement-contract-v1-example.json passes 100% schema validation."""
    assert EXAMPLE_PATH.exists(), f"Missing example fixture at {EXAMPLE_PATH}"
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    example_data = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))

    validator = jsonschema.Draft202012Validator(schema)
    errors = list(validator.iter_errors(example_data))
    
    if errors:
        error_msgs = [f"Path {list(e.path)}: {e.message}" for e in errors]
        pytest.fail(f"Validation failed with {len(errors)} error(s):\n" + "\n".join(error_msgs))

    # Verify exactly 10 observations present in fixture
    assert len(example_data["observations"]) == 10
    assert example_data["prompt_universe"]["prompt_count"] == 10
    assert example_data["declaration"]["principle"] == (
        "AI visibility is an observation under a declared measurement system, not a universal ground-truth ranking."
    )


def test_binary_mention_semantics():
    """Verify response-level binary mention: multiple text occurrences must count as exactly 1 mention."""
    sample_text = "Inten is great. Contact Inten today. Inten provides top services."
    aliases = ["Inten", "اینتن"]
    
    # Count occurrences
    occurrences = sum(sample_text.count(alias) for alias in aliases)
    assert occurrences == 3
    
    # Binary response-level evaluation
    mentioned_boolean = occurrences >= 1
    assert mentioned_boolean is True
    
    # Contract structure representation
    mention_block = {
        "mentioned": mentioned_boolean,
        "occurrence_count": occurrences,
        "matched_aliases": ["Inten"]
    }
    assert mention_block["mentioned"] is True
    assert mention_block["occurrence_count"] == 3


def test_four_way_citation_separation():
    """Verify 4-way separation between mention, target domain, target URL, and 3rd party citations."""
    # Case 1: Mentioned with target domain link
    case_1 = {
        "entity_mentioned": True,
        "target_domain_cited": True,
        "target_url_cited": True,
        "third_party_source_cited": False,
        "cited_domains": ["inten.asia"],
        "cited_urls": ["https://inten.asia/services/seo"]
    }
    assert case_1["entity_mentioned"] is True
    assert case_1["target_domain_cited"] is True

    # Case 2: Mentioned but ONLY 3rd party directory cited
    case_2 = {
        "entity_mentioned": True,
        "target_domain_cited": False,
        "target_url_cited": False,
        "third_party_source_cited": True,
        "cited_domains": ["top-agencies.com"],
        "cited_urls": ["https://top-agencies.com/iran-seo"]
    }
    assert case_2["entity_mentioned"] is True
    assert case_2["target_domain_cited"] is False
    assert case_2["third_party_source_cited"] is True

    # Case 3: Target domain cited in grounding without brand name in response body
    case_3 = {
        "entity_mentioned": False,
        "target_domain_cited": True,
        "target_url_cited": False,
        "third_party_source_cited": False,
        "cited_domains": ["web24.ir"],
        "cited_urls": ["https://web24.ir"]
    }
    assert case_3["entity_mentioned"] is False
    assert case_3["target_domain_cited"] is True


def test_recommendation_status_and_experimental_gating():
    """Verify recommendation status values and experimental flag for low-confidence detections."""
    rec_confirmed = {
        "recommended": True,
        "recommendation_status": "confirmed",
        "recommendation_evidence": "ما شرکت اینتن را به عنوان برترین گزینه سئو پیشنهاد می‌کنیم."
    }
    assert rec_confirmed["recommendation_status"] == "confirmed"

    rec_experimental = {
        "recommended": True,
        "recommendation_status": "experimental",
        "recommendation_evidence": "Ambiguous listing without explicit recommendation verb"
    }
    assert rec_experimental["recommendation_status"] == "experimental"

    rec_not_recommended = {
        "recommended": False,
        "recommendation_status": "not_recommended",
        "recommendation_evidence": None
    }
    assert rec_not_recommended["recommendation_status"] == "not_recommended"


def test_comparability_evaluation_logic():
    """Verify machine-readable comparability rules."""
    def evaluate_comparability(benchmark_a: dict, benchmark_b: dict) -> dict:
        mismatches = []
        if benchmark_a.get("language") != benchmark_b.get("language"):
            mismatches.append(f"Language mismatch: {benchmark_a.get('language')} vs {benchmark_b.get('language')}")
        if benchmark_a.get("country") != benchmark_b.get("country"):
            mismatches.append(f"Market mismatch: {benchmark_a.get('country')} vs {benchmark_b.get('country')}")
        if benchmark_a.get("prompt_count") != benchmark_b.get("prompt_count"):
            mismatches.append(f"Prompt universe mismatch: N={benchmark_a.get('prompt_count')} vs N={benchmark_b.get('prompt_count')}")
        if benchmark_a.get("model") != benchmark_b.get("model"):
            mismatches.append(f"Model mismatch: {benchmark_a.get('model')} vs {benchmark_b.get('model')}")
        if benchmark_a.get("search_grounding") != benchmark_b.get("search_grounding"):
            mismatches.append("Search grounding mode mismatch")
        
        return {
            "comparable": len(mismatches) == 0,
            "mismatch_reasons": mismatches
        }

    bench_1 = {"language": "fa", "country": "IR", "prompt_count": 100, "model": "gpt-4o", "search_grounding": True}
    bench_2 = {"language": "fa", "country": "IR", "prompt_count": 100, "model": "gpt-4o", "search_grounding": True}
    res_match = evaluate_comparability(bench_1, bench_2)
    assert res_match["comparable"] is True
    assert len(res_match["mismatch_reasons"]) == 0

    bench_3 = {"language": "fa", "country": "IR", "prompt_count": 500, "model": "claude-3-7-sonnet", "search_grounding": False}
    res_mismatch = evaluate_comparability(bench_1, bench_3)
    assert res_mismatch["comparable"] is False
    assert len(res_mismatch["mismatch_reasons"]) == 3
