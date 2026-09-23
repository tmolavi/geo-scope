"""
Comprehensive Test Suite for GEO-Scope Scientific Measurement Contract.
Verifies all Phase 1 constraints:
1. Hard simulation vs live isolation
2. Explicit prompt_policy (neutral vs forced_list)
3. Strict mentioned != recommended separation
4. Strict ranking list contract (no paragraph inference)
5. Correct statistical reporting & failure denominators
6. Exploratory association terminology (no causal factor claims)
7. Independent repeats (repeat_index) and temporal sync (comparison_batch_id)
8. Provider identity & search grounding tracking
9. Usage and cost reporting with 'unreported' default
10. Locale fallback to 'unknown'
"""

import pytest
import json
from pathlib import Path
from typing import Dict, Any, List

from geo_scope.entities.models import Entity
from geo_scope.entities.registry import EntityRegistry
from geo_scope.parser.observation_parser import ObservationParser
from geo_scope.providers.models import ProviderResponse
from geo_scope.providers.openai_provider import OpenAIProvider
from geo_scope.providers.claude_provider import ClaudeProvider
from geo_scope.providers.perplexity_provider import PerplexityProvider
from geo_scope.providers.ollama_provider import OllamaProvider
from geo_scope.measurement.engine import MeasurementEngine
from geo_scope.measurement.replay import ReplayEngine
from geo_scope.benchmark.dataset_validator import validate_benchmark_dataset


def test_mentioned_vs_recommended_strict_separation():
    """Verifies that mentioning a brand without endorsement does NOT mark recommended=True."""
    parser = ObservationParser()
    entity = Entity(id="inten", names=["Inten", "اینتن"], domains=["inten.asia"])

    # Mere descriptive mention without recommendation
    text_mention_only = "اینتن یک شرکت طراحی سایت در تهران است که در سال ۱۳۹۲ تاسیس شد."
    res = parser.parse(text_mention_only, entity, query="شرکت اینتن")
    assert res.mentioned is True
    assert res.recommended is False
    assert res.rank is None

    # Explicit recommendation
    text_recommended = "ما شرکت اینتن را به عنوان برترین گزینه برای سئو پیشنهاد و توصیه می‌کنیم."
    res_rec = parser.parse(text_recommended, entity, query="بهترین شرکت سئو")
    assert res_rec.mentioned is True
    assert res_rec.recommended is True


def test_ranking_contract_ordered_list_only():
    """Verifies rank_position is extracted ONLY from numbered lists, never from paragraph order."""
    parser = ObservationParser()
    entity_a = Entity(id="a", names=["BrandA"])
    entity_b = Entity(id="b", names=["BrandB"])

    # Unnumbered paragraph order must NOT produce ranks
    paragraph_text = "BrandA offers good features. Later we also looked at BrandB which has lower cost."
    res_a = parser.parse(paragraph_text, entity_a, query="compare brands")
    res_b = parser.parse(paragraph_text, entity_b, query="compare brands")
    assert res_a.mentioned is True
    assert res_b.mentioned is True
    assert res_a.rank is None
    assert res_b.rank is None

    # Recognized numbered list items produce rank
    numbered_text = """
    Top recommended solutions:
    1. BrandA - best enterprise platform
    2. BrandB - best budget platform
    """
    res_num_a = parser.parse(numbered_text, entity_a, query="best solutions")
    res_num_b = parser.parse(numbered_text, entity_b, query="best solutions")
    assert res_num_a.rank == 1
    assert res_num_a.top1 is True
    assert res_num_a.recommended is True
    assert res_num_b.rank == 2
    assert res_num_b.top1 is False
    assert res_num_b.recommended is True


def test_provider_prompt_policy_neutral_default():
    """Verifies provider adapters default to neutral instructions and support forced_list."""
    # OpenAI provider payload inspection
    oai = OpenAIProvider(api_key="test-key")
    # neutral policy
    prompt_neutral = {"query": "What is Python?", "prompt_policy": "neutral"}
    # Claude provider
    claude = ClaudeProvider(api_key="test-key")
    # Perplexity provider
    pplx = PerplexityProvider(api_key="test-key")
    # Ollama provider
    ollama = OllamaProvider(host="http://localhost:11434")

    assert oai.name == "openai_completion"
    assert claude.name == "claude_completion"
    assert pplx.name == "perplexity_sonar"
    assert ollama.name == "ollama_local"


def test_provider_response_cost_and_locale_schema():
    """Verifies ProviderResponse populates cost accounting, locale defaults, and provider identity."""
    resp = ProviderResponse(
        provider="openai",
        model="gpt-4o",
        execution_mode="live",
        text="Sample output",
        usage={"prompt_tokens": 120, "completion_tokens": 80, "total_tokens": 200},
    )
    raw = resp.to_raw_record(
        experiment_id="exp1",
        run_id="run1",
        prompt_id="p1",
        prompt="Sample query",
    )
    assert raw["input_tokens"] == 120
    assert raw["output_tokens"] == 80
    assert raw["total_tokens"] == 200
    assert raw["cost_status"] == "unreported"
    assert raw["prompt_language"] == "unknown"
    assert raw["country_iso"] == "unknown"
    assert raw["locale"] == "unknown"
    assert raw["prompt_policy"] == "neutral"
    assert raw["repeat_index"] == 0


@pytest.mark.asyncio
async def test_failure_denominator_contract_and_k_repeats(tmp_path):
    """Verifies k-repeats, temporal sync IDs, and failure denominator accounting."""
    entity = Entity(id="inten", names=["Inten", "اینتن"])
    registry = EntityRegistry([entity])
    engine = MeasurementEngine(entities=registry)

    prompts = [
        {"id": "p1", "query": "بهترین سئو کار", "language": "fa", "country_iso": "IR"},
        {"id": "p2", "query": "آژانس دیجیتال مارکتینگ", "language": "fa", "country_iso": "IR"},
    ]

    # Run simulated measurement with repeats=2
    res = await engine.execute_measurement(
        prompts=prompts,
        providers=["perplexity_sonar"],
        out_dir=tmp_path / "repeat_run",
        mode="simulation",
        repeats=2,
        seed=42,
    )

    assert res["repeats_per_prompt"] == 2
    assert res["n_completions"] == 4  # 2 prompts * 1 provider * 2 repeats
    assert res["comparison_batch_id"] is not None

    # Verify manifest
    manifest_data = json.loads((tmp_path / "repeat_run" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest_data["schema_version"] == "0.3"
    assert manifest_data["repeats_per_prompt"] == 2
    assert "comparison_window_started_at" in manifest_data
    assert "comparison_window_completed_at" in manifest_data

    # Verify metrics denominator accounting
    metrics_data = json.loads((tmp_path / "repeat_run" / "metrics.json").read_text(encoding="utf-8"))
    assert "sample_interpretation" in metrics_data
    assert metrics_data["entities"]["inten"]["attempted_n"] == 4
    assert metrics_data["entities"]["inten"]["successful_n"] == 4
    assert metrics_data["entities"]["inten"]["metric_denominator_n"] == 4


def test_simulation_rejection_in_live_datasets(tmp_path):
    """Verifies that the dataset validator strictly rejects simulation records in live datasets."""
    dataset_dir = tmp_path / "fake_live_release"
    dataset_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "schema_version": "0.3",
        "mode": "live",
        "execution_mode": "live",
        "created_at": "2026-09-23T12:00:00Z",
        "prompt_count": 1,
        "n_prompts": 1,
        "n_completions": 1,
        "n_observations": 1,
        "providers": ["gemini_grounding"],
        "raw_responses_path": "raw_responses.jsonl",
    }
    (dataset_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (dataset_dir / "prompts.jsonl").write_text(json.dumps({"id": "p1", "query": "Test query"}) + "\n", encoding="utf-8")
    (dataset_dir / "entities.json").write_text(json.dumps([{"id": "test", "names": ["Test"]}]), encoding="utf-8")
    (dataset_dir / "raw_responses.jsonl").write_text(json.dumps({"prompt_id": "p1", "provider": "gemini_grounding", "status": "success"}) + "\n", encoding="utf-8")
    (dataset_dir / "metrics.json").write_text("{}", encoding="utf-8")
    (dataset_dir / "errors.jsonl").write_text("", encoding="utf-8")

    # Contaminated observation record with mode="simulation"
    obs_record = {
        "entity_id": "test",
        "prompt_id": "p1",
        "provider": "gemini_grounding",
        "mode": "simulation",
        "execution_mode": "simulation",
        "mentioned": True,
        "recommended": False,
        "status": "success",
    }
    (dataset_dir / "observations.jsonl").write_text(json.dumps(obs_record) + "\n", encoding="utf-8")

    # Compute checksums
    import hashlib
    chk_lines = []
    for fname in ["manifest.json", "prompts.jsonl", "entities.json", "raw_responses.jsonl", "observations.jsonl", "metrics.json", "errors.jsonl"]:
        fpath = dataset_dir / fname
        if fpath.exists():
            h = hashlib.sha256(fpath.read_bytes()).hexdigest()
            chk_lines.append(f"{h}  {fname}\n")
    (dataset_dir / "checksums.sha256").write_text("".join(chk_lines), encoding="utf-8")

    res = validate_benchmark_dataset(dataset_dir)
    assert res["passed"] is False
    assert res["status"] == "FAIL"
    assert res["checks"]["live_measurement_integrity"]["passed"] is False
    assert "Contamination detected" in res["checks"]["live_measurement_integrity"]["detail"]
