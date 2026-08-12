"""
Tests for Algo Analyzer Module with Realistic LLM Mocks
"""

import pytest
from geo_scope.engine.algo_analyzer import AlgoAnalyzer
from geo_scope.engine.feature_extractor import parse_model_response


def test_algo_analyzer_computation():
    mock_records = [
        {
            "query_id": "qry_0001",
            "model": "perplexity_sonar",
            "intent": "commercial_direct",
            "language": "en",
            "target_brand": "HubSpot",
            "target_mentioned": True,
            "target_rank": 1,
            "target_is_top_1": True,
            "target_sentiment": "positive",
            "all_brands_stats": {"HubSpot": {"mentioned": True, "is_top_1": True, "sentiment": "positive"}},
            "citations": [{"domain": "reddit.com", "category": "ugc_forums"}],
            "response_length": 500
        },
        {
            "query_id": "qry_0002",
            "model": "perplexity_sonar",
            "intent": "comparative",
            "language": "en",
            "target_brand": "HubSpot",
            "target_mentioned": False,
            "target_rank": 0,
            "target_is_top_1": False,
            "target_sentiment": "neutral",
            "all_brands_stats": {"HubSpot": {"mentioned": False, "is_top_1": False, "sentiment": "neutral"}},
            "citations": [{"domain": "g2.com", "category": "review_aggregators"}],
            "response_length": 450
        }
    ]

    analyzer = AlgoAnalyzer(mock_records, "HubSpot", ["Salesforce", "Zoho CRM"])
    analysis = analyzer.compute_full_analysis()

    assert "summary" in analysis
    assert analysis["summary"]["total_ai_executions"] == 2
    assert analysis["summary"]["overall_sov"] == 50.0
    assert "algorithmic_factors" in analysis
    assert "citation_analytics" in analysis


def test_mock_llm_multi_model_scenarios():
    """
    Simulates varied synthetic responses across ChatGPT Search, Perplexity, Gemini, and Claude.
    """
    prompt = {
        "id": "mock_001",
        "query": "Best CRM software in 2026",
        "intent": "commercial_direct",
        "language": "en",
        "target_brand": "HubSpot",
        "expected_entities": ["HubSpot", "Salesforce", "Zoho CRM"]
    }

    # Perplexity mock: High Reddit citations
    pplx_text = """
    Based on community recommendations:
    1. **HubSpot**: Highly regarded by startup founders for easy setup.
    2. **Salesforce**: Enterprise choice.
    
    Sources:
    - [Reddit Discussion](https://reddit.com/r/sales/crm_post)
    - [G2 CRM Grid](https://g2.com/categories/crm)
    """

    # ChatGPT Search mock: High PR media citations
    chatgpt_text = """
    Leading CRM tools in 2026:
    1. **Salesforce**: Market leader.
    2. **HubSpot**: Best for inbound sales.
    
    References:
    - [TechCrunch Enterprise Review](https://techcrunch.com/2026/crm)
    - [Forbes Advisor](https://forbes.com/best-crm)
    """

    # Claude mock: Detailed technical review
    claude_text = """
    Comprehensive evaluation:
    1. **HubSpot**: Balanced ROI and strong API ecosystem.
    2. **Zoho CRM**: Cost effective.
    
    Citations:
    - [Wikipedia Article](https://wikipedia.org/wiki/HubSpot)
    """

    pplx_parsed = parse_model_response(prompt, "perplexity_sonar", pplx_text)
    gpt_parsed = parse_model_response(prompt, "chatgpt_search", chatgpt_text)
    claude_parsed = parse_model_response(prompt, "claude_3_7", claude_text)

    records = [pplx_parsed, gpt_parsed, claude_parsed]
    analyzer = AlgoAnalyzer(records, "HubSpot", ["Salesforce", "Zoho CRM"])
    analysis = analyzer.compute_full_analysis()

    # HubSpot is mentioned in all 3 responses
    assert analysis["summary"]["overall_sov"] == 100.0
    # HubSpot is #1 in Perplexity and Claude, #2 in ChatGPT
    assert analysis["summary"]["overall_top1_rate"] == round((2 / 3) * 100, 1)
    assert len(analysis["citation_analytics"]["top_cited_domains"]) >= 3
