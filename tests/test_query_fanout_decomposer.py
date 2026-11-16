"""
Unit and Integration Tests for QueryFanOutDecomposer and AnswerPath integration.
Validates:
  - Detection of comparative, commercial, and informational intents
  - Generation of structured sub-queries with subtopics and source expectations
  - Multilingual decomposition (English and Persian)
  - FanOutDecompositionResult serialization
  - AnswerPathConnector.decompose_fanout integration
"""

import pytest

from geo_scope.questions.fanout import (
    SubQueryItem,
    FanOutDecompositionResult,
    QueryFanOutDecomposer,
)
from geo_scope.questions.answerpath_connector import AnswerPathConnector


def test_fanout_comparative_query_english():
    decomposer = QueryFanOutDecomposer()
    prompt = "Compare HubSpot vs Salesforce for enterprise B2B CRM in 2026"
    res = decomposer.decompose(prompt, parent_prompt_id="test_p1")

    assert res.parent_prompt_id == "test_p1"
    assert res.primary_intent == "comparative"
    assert res.language == "en"
    assert res.fan_out_ratio >= 3.0
    assert len(res.sub_queries) >= 3

    subtopics = [sq.subtopic for sq in res.sub_queries]
    assert "architecture_features" in subtopics
    assert "pricing_licensing" in subtopics
    assert "user_reviews_sentiment" in subtopics

    for sq in res.sub_queries:
        assert sq.sub_query_id.startswith("test_p1_sq")
        assert len(sq.expected_source_types) > 0


def test_fanout_persian_commercial_query():
    decomposer = QueryFanOutDecomposer()
    prompt = "بهترین نرم افزار حسابداری ابری و قیمت پکیج‌ها در سال ۱۴۰۵"
    res = decomposer.decompose(prompt)

    assert res.language == "fa"
    assert res.primary_intent == "commercial_direct"
    assert len(res.sub_queries) >= 3
    assert any("قیمت" in sq.sub_query_text or "تعرفه" in sq.sub_query_text for sq in res.sub_queries)


def test_fanout_serialization():
    decomposer = QueryFanOutDecomposer()
    res = decomposer.decompose("What is generative engine optimization?")
    d = res.to_dict()

    assert "parent_prompt_id" in d
    assert "sub_queries" in d
    assert d["decomposition_strategy"] == "gemini_hydrogen_fanout_v1"
    assert d["fan_out_ratio"] == float(len(d["sub_queries"]))


def test_answerpath_connector_fanout_integration():
    connector = AnswerPathConnector()
    res = connector.decompose_fanout(
        prompt="Compare Supabase vs Firebase for realtime mobile app",
        max_subqueries=3,
    )
    assert isinstance(res, FanOutDecompositionResult)
    assert len(res.sub_queries) == 3
    assert res.primary_intent == "comparative"
