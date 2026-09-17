"""Tests for GEO-Scope + AnswerPath GEO integration and Question Provenance."""
import json
import pytest
from pathlib import Path

from geo_scope.benchmark.models import (
    PromptRecord,
    BenchmarkManifest,
    BenchmarkMetrics,
    ObservationRecord,
)
from geo_scope.questions.models import DiscoveredQuestion, DiscoveryResult, QuestionCluster
from geo_scope.questions.answerpath_connector import (
    AnswerPathConnector,
    classify_intent,
    resolve_stage,
    generate_research_prompts,
    extract_records,
)
from geo_scope.questions.discovery import (
    discover_questions,
    prepare_benchmark_dataset,
    format_discovery_report,
)
from geo_scope.benchmark.calculator import BenchmarkCalculator
from geo_scope.benchmark.builder import BenchmarkBuilder


def test_prompt_record_question_provenance():
    p = PromptRecord(
        prompt_id="PRM-001",
        question="best GEO agency in Iran",
        source_type="observed",
        source_reference="answerpath:observed",
        intent="commercial",
        category="GEO",
        target_brand="GeoPro",
        competitors=["GeoMax"],
        confidence=0.95,
    )
    assert p.text == "best GEO agency in Iran"
    assert p.question == "best GEO agency in Iran"
    assert p.source_type == "observed"
    assert p.source_reference == "answerpath:observed"
    assert "GeoPro" in p.entities
    assert "GeoMax" in p.entities
    assert p.confidence == 0.95


def test_answerpath_intent_classification():
    assert classify_intent("What is GEO optimization?") == "learn"
    assert classify_intent("قیمت خدمات سئو و GEO چقدر است؟") == "buy"
    assert classify_intent("Compare GeoPro vs GeoMax for startups") == "compare"
    assert classify_intent("آیا شرکت الف معتبر و قابل اعتماد است؟") == "trust"
    assert classify_intent("حل مشکل دیده نشدن سایت در هوش مصنوعی") == "solve"


def test_answerpath_question_extraction(tmp_path):
    # Create sample JSON and CSV export files
    json_file = tmp_path / "chat_export.json"
    json_data = [
        {"role": "user", "content": "How do I choose the best GEO agency?"},
        {"role": "assistant", "content": "Here are some tips..."},
        {"role": "customer", "message": "What is the pricing for enterprise GEO?"},
    ]
    json_file.write_text(json.dumps(json_data), encoding="utf-8")

    csv_file = tmp_path / "queries.csv"
    csv_file.write_text("role,query\nuser,Compare HubSpot vs Salesforce\ncustomer,Is GeoPro reliable?\n", encoding="utf-8")

    records = extract_records(json_file)
    assert len(records) == 2
    assert "How do I choose the best GEO agency?" in [r[0] for r in records]

    csv_records = extract_records(csv_file)
    assert len(csv_records) == 2
    assert "Compare HubSpot vs Salesforce" in [r[0] for r in csv_records]


def test_discover_questions_mode_1(tmp_path):
    # Create sample log
    log_file = tmp_path / "user_logs.txt"
    log_file.write_text("Best CRM for startups\nWhat is the price of CRM software?\nBest CRM for startups\n", encoding="utf-8")

    res = discover_questions(
        topic="CRM Software",
        input_paths=[str(log_file)],
        include_generated=True,
        threshold=0.85,
        target_brand="HubSpot",
        competitors=["Salesforce"],
    )

    assert isinstance(res, DiscoveryResult)
    assert res.topic == "CRM Software"
    assert res.observed_count >= 2
    assert res.generated_count == 10
    assert res.total_discovered == res.observed_count + res.generated_count

    # Check intent distribution
    assert "buy" in res.intent_distribution or "learn" in res.intent_distribution

    # Check report formatting
    report = format_discovery_report(res)
    assert "AnswerPath GEO Question Discovery Report" in report
    assert "Observed User Questions" in report
    assert "Generated Research Prompts" in report


def test_prepare_benchmark_dataset_mode_2(tmp_path):
    log_file = tmp_path / "customer_logs.json"
    log_data = [{"role": "user", "text": "Best GEO agency for B2B brands"}]
    log_file.write_text(json.dumps(log_data), encoding="utf-8")

    out_dir = str(tmp_path / "benchmarks")
    res = prepare_benchmark_dataset(
        topic="GEO Agency",
        observed_inputs=[str(log_file)],
        include_default_generated=True,
        brand="GeoPro",
        competitors=["GeoMax"],
        out_dir=out_dir,
        dataset_id="test-prepared-2026.1",
    )

    pkg_dir = Path(res["directory"])
    assert pkg_dir.exists()
    assert (pkg_dir / "prompts" / "observed.jsonl").exists()
    assert (pkg_dir / "prompts" / "generated.jsonl").exists()
    assert (pkg_dir / "prompts.jsonl").exists()
    assert (pkg_dir / "manifest.json").exists()
    assert (pkg_dir / "provenance.json").exists()

    # Read manifest and verify counts
    with open(pkg_dir / "manifest.json") as f:
        m = json.load(f)
    assert m["counts"]["observed_prompts"] == 1
    assert m["counts"]["generated_prompts"] == 10
    assert m["question_provenance"]["observed_count"] == 1
    assert m["question_provenance"]["generated_count"] == 10

    # Read provenance.json
    with open(pkg_dir / "provenance.json") as f:
        prov = json.load(f)
    assert prov["question_provenance"]["source_reference"] == "answerpath"
    assert prov["question_provenance"]["observed_count"] == 1


def test_benchmark_calculator_demand_stratification():
    brands = [{"name": "HubSpot", "domain": "hubspot.com", "is_target": True}]
    providers = [{"id": "gemini-2.5-flash"}]

    prompts = [
        {"prompt_id": "PRM-OBS-1", "source_type": "observed", "intent_stratum": "commercial_direct"},
        {"prompt_id": "PRM-GEN-1", "source_type": "generated", "intent_stratum": "informational"},
    ]

    obs = [
        {
            "observation_id": "OBS-1",
            "prompt_id": "PRM-OBS-1",
            "provider_id": "gemini-2.5-flash",
            "model": "gemini-2.5-flash",
            "status": "success",
            "brand_mentioned": True,
            "is_top1": True,
            "top1_brand": "HubSpot",
            "mentioned_brands": ["HubSpot"],
            "execution_class": "native",
            "latency_ms": 300,
        },
        {
            "observation_id": "OBS-2",
            "prompt_id": "PRM-GEN-1",
            "provider_id": "gemini-2.5-flash",
            "model": "gemini-2.5-flash",
            "status": "success",
            "brand_mentioned": False,
            "is_top1": False,
            "top1_brand": None,
            "mentioned_brands": [],
            "execution_class": "native",
            "latency_ms": 350,
        },
    ]

    calc = BenchmarkCalculator()
    metrics = calc.compute(
        prompts=prompts,
        observations=obs,
        citations=[],
        brands=brands,
        providers=providers,
        benchmark_mode="discovery",
    )

    assert metrics.question_provenance["observed_count"] == 1
    assert metrics.question_provenance["generated_count"] == 1

    # Observed question visibility (HubSpot mentioned in 100% of observed queries)
    assert metrics.observed_visibility["sample_size"] == 1
    assert metrics.observed_visibility["brands"]["HubSpot"]["mention_rate"] == 100.0

    # Generated template visibility (HubSpot mentioned in 0% of generated queries)
    assert metrics.generated_visibility["sample_size"] == 1
    assert metrics.generated_visibility["brands"]["HubSpot"]["mention_rate"] == 0.0

    # Total / Combined visibility (50%)
    assert metrics.total_observed_visibility["sample_size"] == 2
    assert metrics.total_observed_visibility["brands"]["HubSpot"]["mention_rate"] == 50.0
