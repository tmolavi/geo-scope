"""
Tests for Provider Classification and Metric Family Separation.
"""

import pytest
from geo_scope.entities.models import Entity
from geo_scope.entities.registry import EntityRegistry
from geo_scope.measurement.engine import MeasurementEngine
from geo_scope.providers.perplexity_provider import PerplexityProvider
from geo_scope.providers.gemini_provider import GeminiProvider
from geo_scope.providers.hamzad_provider import HamzadProvider


def test_provider_classes():
    perp = PerplexityProvider()
    assert perp.provider_class == "answer_engine"

    gem = GeminiProvider()
    assert gem.provider_class == "answer_engine"

    hamzad_search = HamzadProvider(search_grounded=True)
    assert hamzad_search.provider_class == "answer_engine"

    hamzad_raw = HamzadProvider(target_provider="claude", search_grounded=False)
    assert hamzad_raw.provider_class == "llm"


def test_metric_family_separation():
    entities = EntityRegistry.from_list([
        {"id": "inten", "names": ["Inten", "اینتن"], "domains": ["inten.asia"]},
        {"id": "web24", "names": ["Web24", "وب24"], "domains": ["web24.ir"]},
    ])
    engine = MeasurementEngine(entities=entities)

    prompts = [
        {"id": "p1", "query": "بهترین شرکت سئو", "source_type": "observed", "intent": "recommendation"},
        {"id": "p2", "query": "خدمات وب ۲۴", "source_type": "observed", "intent": "informational"},
    ]

    # Observations simulating answer_engine vs llm
    observations = [
        # Answer Engine observation with citation and ranking
        {
            "prompt_id": "p1",
            "prompt": "بهترین شرکت سئو",
            "entity_id": "inten",
            "source_type": "observed",
            "provider": "perplexity_sonar",
            "model": "sonar",
            "provider_class": "answer_engine",
            "execution_mode": "live",
            "status": "success",
            "mentioned": True,
            "person_mentioned": False,
            "recommended": True,
            "top1": True,
            "rank": 1,
            "cited": True,
            "attributed": True,
            "confused_with": [],
            "wrong_entity": False,
            "parser_confidence": 0.95,
            "scoring_status": "scored",
            "intent_type": "recommendation",
            "evidence_snippets": [],
        },
        # LLM observation (no grounding/search citations)
        {
            "prompt_id": "p1",
            "prompt": "بهترین شرکت سئو",
            "entity_id": "inten",
            "source_type": "observed",
            "provider": "gpt-4o",
            "model": "gpt-4o",
            "provider_class": "llm",
            "execution_mode": "live",
            "status": "success",
            "mentioned": True,
            "person_mentioned": False,
            "recommended": True,
            "top1": True,
            "rank": 1,
            "cited": False,
            "attributed": False,
            "confused_with": [],
            "wrong_entity": False,
            "parser_confidence": 0.90,
            "scoring_status": "scored",
            "intent_type": "recommendation",
            "evidence_snippets": [],
        },
    ]

    metrics = engine._compute_metrics(observations, prompts, mode="live")
    inten_metrics = metrics["entities"]["inten"]

    # AI Search Visibility should exist and have search_visibility_score
    assert inten_metrics["ai_search_visibility"] is not None
    assert "search_visibility_score" in inten_metrics["ai_search_visibility"]
    assert inten_metrics["ai_search_visibility"]["search_citation_rate"] == 1.0

    # LLM Brand Observation should exist
    assert inten_metrics["llm_brand_observation"] is not None
    assert inten_metrics["llm_brand_observation"]["llm_mention_rate"] == 1.0
