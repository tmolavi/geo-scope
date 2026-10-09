"""
Unit tests for Query Fan-Out Brand Introduction Evaluation & Classification.
Verifies all frozen scientific definitions, edge cases, zero-denominator handling,
and raw evidence linkages.
"""

import json
from pathlib import Path
import pytest

from geo_scope.benchmark.query_fanout import (
    BrandSourceClass,
    BrandObservation,
    classify_brand,
    evaluate_brand_presence,
    compute_fanout_metrics,
    text_contains_brand,
    citations_contain_brand,
)
from geo_scope.benchmark.models import ObservationRecord
from geo_scope.parser.observation_parser import ObservationParsedResult


def test_user_named_brand_is_not_classified_as_engine_introduced():
    """
    Test: A brand mentioned by the user in the initial prompt MUST be classified
    as USER_NAMED, even if it subsequently appears in engine-generated queries.
    """
    prompt = "Why should I choose HubSpot over competitors for our startup?"
    queries = [
        "HubSpot pricing and plan comparison 2026",
        "best CRM alternatives to HubSpot",
    ]
    retrieved = [
        {"title": "HubSpot Features", "snippet": "Overview", "url": "https://hubspot.com"},
    ]

    source_class, q_ref, r_ref = classify_brand(
        brand_name="HubSpot",
        user_prompt=prompt,
        generated_queries=queries,
        retrieved_metadata=retrieved,
        aliases=["hubspot"],
        domains=["hubspot.com"],
    )

    assert source_class == BrandSourceClass.USER_NAMED
    assert source_class != BrandSourceClass.ENGINE_QUERY_INTRODUCED
    assert q_ref is None
    assert r_ref is None


def test_query_introduced_brand_classification():
    """
    Test: A brand absent from the user prompt but present in an engine search query
    MUST be classified as ENGINE_QUERY_INTRODUCED with a valid query reference.
    """
    prompt = "What is the best CRM software for growing startups?"
    queries = [
        "top CRM software 2026 features",
        "HubSpot small business pricing and reviews",
    ]
    retrieved = [
        {"title": "HubSpot Reviews", "snippet": "Great tool", "url": "https://hubspot.com/reviews"},
    ]

    source_class, q_ref, r_ref = classify_brand(
        brand_name="HubSpot",
        user_prompt=prompt,
        generated_queries=queries,
        retrieved_metadata=retrieved,
        aliases=["hubspot"],
        domains=["hubspot.com"],
    )

    assert source_class == BrandSourceClass.ENGINE_QUERY_INTRODUCED
    assert q_ref is not None
    assert "query_2" in q_ref
    assert "HubSpot" in q_ref
    assert r_ref is None


def test_retrieved_only_classification():
    """
    Test: A brand absent from both user prompt and generated search queries,
    but present in retrieved results metadata, MUST be classified as RETRIEVED_ONLY.
    """
    prompt = "What is the best CRM software for growing startups?"
    queries = [
        "top CRM software 2026 features",
        "best customer relationship tools",
    ]
    retrieved = [
        {
            "title": "Top 10 CRM Systems in 2026",
            "snippet": "In this guide we compare Salesforce, Zoho, and other platforms.",
            "url": "https://techradar.com/best-crm",
        }
    ]

    source_class, q_ref, r_ref = classify_brand(
        brand_name="Salesforce",
        user_prompt=prompt,
        generated_queries=queries,
        retrieved_metadata=retrieved,
        aliases=["salesforce"],
        domains=["salesforce.com"],
    )

    assert source_class == BrandSourceClass.RETRIEVED_ONLY
    assert q_ref is None
    assert r_ref is not None
    assert "doc_1" in r_ref
    assert "techradar.com" in r_ref


def test_not_retrieved_classification():
    """
    Test: A brand absent from user prompt, generated queries, and retrieved items
    MUST be classified as NOT_RETRIEVED.
    """
    prompt = "What is the best CRM software for growing startups?"
    queries = ["top CRM software 2026 features"]
    retrieved = [{"title": "CRM Guide", "snippet": "CRM overview", "url": "https://example.com"}]

    source_class, q_ref, r_ref = classify_brand(
        brand_name="Pipedrive",
        user_prompt=prompt,
        generated_queries=queries,
        retrieved_metadata=retrieved,
        aliases=["pipedrive"],
        domains=["pipedrive.com"],
    )

    assert source_class == BrandSourceClass.NOT_RETRIEVED
    assert q_ref is None
    assert r_ref is None


def test_mention_citation_separation():
    """
    Test: Mention in final answer text and citation in sources MUST remain strictly separate.
    """
    brand = "Asana"
    domains = ["asana.com"]

    # Case 1: Mentioned in prose, but no citation link
    ans_1 = "We recommend **Asana** for agile task tracking across teams."
    cits_1 = ["https://techcrunch.com/project-management-roundup"]
    m1, c1 = evaluate_brand_presence(brand, ans_1, cits_1, domains=domains)
    assert m1 is True
    assert c1 is False

    # Case 2: Cited in URL, but brand name not in prose text
    ans_2 = "For general work tracking, several enterprise platforms provide good features."
    cits_2 = ["https://asana.com/product/features"]
    m2, c2 = evaluate_brand_presence(brand, ans_2, cits_2, domains=domains)
    assert m2 is False
    assert c2 is True

    # Case 3: Both mentioned and cited
    ans_3 = "Top pick is **Asana**."
    cits_3 = ["https://asana.com/overview"]
    m3, c3 = evaluate_brand_presence(brand, ans_3, cits_3, domains=domains)
    assert m3 is True
    assert c3 is True

    # Case 4: Neither
    ans_4 = "We recommend another solution entirely."
    cits_4 = ["https://example.com/software"]
    m4, c4 = evaluate_brand_presence(brand, ans_4, cits_4, domains=domains)
    assert m4 is False
    assert c4 is False


def test_entity_alias_and_boundary_handling():
    """
    Test: Brand alias matching correctly handles acronyms/variants without false substring hits.
    """
    # GCP alias for Google Cloud
    assert text_contains_brand("deploying containers on GCP", "Google Cloud", aliases=["gcp", "google cloud"])
    assert text_contains_brand("comparing AWS vs Azure vs GCP", "Google Cloud", aliases=["gcp"])

    # Substring boundary check: 'kit' should not match 'kitchen'
    assert not text_contains_brand("the kitchen appliance store", "Kit", aliases=["kit"])
    assert text_contains_brand("subscribe with Kit newsletter", "Kit", aliases=["kit"])

    # Word boundary check: 'asana' should not match 'asan' or 'hasana'
    assert not text_contains_brand("in iran asan pardakht is popular", "Asana", aliases=["asana"])
    assert text_contains_brand("try Asana for sprints", "Asana", aliases=["asana"])


def test_zero_denominator_explicit_handling():
    """
    Test: When zero observations occur in denominator, ratios must handle division
    by zero explicitly without returning arbitrary numbers or converting infinity to a fake multiplier.
    """
    # 0 retrieved-only items
    obs_empty_ro = [
        BrandObservation(
            conversation_id="conv_1",
            prompt_id="prm_1",
            engine="test",
            model="test",
            brand="BrandA",
            brand_source_class=BrandSourceClass.ENGINE_QUERY_INTRODUCED,
            final_answer_mentioned=True,
            final_answer_cited=False,
            raw_evidence_reference="raw/test.json",
        )
    ]
    metrics = compute_fanout_metrics(obs_empty_ro)
    assert metrics.retrieved_only_count == 0
    assert metrics.retrieved_only_mention_rate is None
    assert metrics.mention_rate_ratio is None  # Handled cleanly, not 999 or infinity

    # Retrieved-only items exist, but 0 mentions (mention rate = 0.0)
    obs_zero_mention_ro = [
        BrandObservation(
            conversation_id="conv_1",
            prompt_id="prm_1",
            engine="test",
            model="test",
            brand="BrandA",
            brand_source_class=BrandSourceClass.ENGINE_QUERY_INTRODUCED,
            final_answer_mentioned=True,
            final_answer_cited=False,
            raw_evidence_reference="raw/test.json",
        ),
        BrandObservation(
            conversation_id="conv_1",
            prompt_id="prm_1",
            engine="test",
            model="test",
            brand="BrandB",
            brand_source_class=BrandSourceClass.RETRIEVED_ONLY,
            final_answer_mentioned=False,
            final_answer_cited=False,
            raw_evidence_reference="raw/test.json",
        ),
    ]
    metrics2 = compute_fanout_metrics(obs_zero_mention_ro)
    assert metrics2.engine_introduced_mention_rate == 1.0
    assert metrics2.retrieved_only_mention_rate == 0.0
    # Must NOT convert division by zero to arbitrary number!
    assert metrics2.mention_rate_ratio is None


def test_raw_evidence_linkage():
    """
    Test: Every observation record in the benchmark dataset has a valid, existing
    raw evidence file, and the referenced generated queries or retrieval sources match.
    """
    repo_root = Path(__file__).resolve().parent.parent
    b_dir = repo_root / "benchmarks" / "query-fanout-brand-introduction"
    obs_file = b_dir / "observations.csv"

    assert obs_file.exists(), "observations.csv must exist in benchmark directory"

    import csv
    with open(obs_file, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    assert len(reader) >= 100, f"Expected at least 100 brand observations, got {len(reader)}"

    # Check a sample of 15 records
    import random
    random.seed(123)
    sample = random.sample(reader, 15)

    for row in sample:
        raw_ref = row["raw_evidence_reference"]
        raw_path = b_dir / raw_ref
        assert raw_path.exists(), f"Raw file {raw_path} must exist"

        with open(raw_path, "r", encoding="utf-8") as rf:
            raw_data = json.load(rf)

        assert raw_data["conversation_id"] == row["conversation_id"]
        assert raw_data["prompt_id"] == row["prompt_id"]
        assert len(raw_data["generated_search_queries"]) > 0
        assert len(raw_data["retrieved_results"]) > 0

        # If ENGINE_QUERY_INTRODUCED, generated query reference must point to an actual query in raw_data
        if row["brand_source_class"] == "ENGINE_QUERY_INTRODUCED":
            q_ref = row["generated_query_reference"]
            assert q_ref, "ENGINE_QUERY_INTRODUCED must have generated_query_reference"
            assert any(row["brand"].lower() in q.lower() for q in raw_data["generated_search_queries"])


def test_experimental_fields_in_observation_models():
    """
    Test: Experimental query fan-out entity tracing fields exist in ObservationRecord
    and ObservationParsedResult and default to empty lists.
    """
    obs_rec = ObservationRecord(
        observation_id="obs_001",
        prompt_id="prm_001",
        provider_id="gemini",
        model="gemini-2.5-flash",
        timestamp="2026-10-09T00:00:00Z",
    )
    assert hasattr(obs_rec, "query_introduced_entities")
    assert hasattr(obs_rec, "retrieved_entities")
    assert hasattr(obs_rec, "answer_mentioned_entities")
    assert hasattr(obs_rec, "answer_cited_entities")
    assert obs_rec.query_introduced_entities == []

    parsed_res = ObservationParsedResult(
        entity_id="hubspot",
        entity="HubSpot",
    )
    assert hasattr(parsed_res, "query_introduced_entities")
    assert hasattr(parsed_res, "retrieved_entities")
    assert hasattr(parsed_res, "answer_mentioned_entities")
    assert hasattr(parsed_res, "answer_cited_entities")
    assert parsed_res.query_introduced_entities == []
