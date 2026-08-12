"""
Tests for Algo Analyzer Module
"""

from geo_scope.engine.algo_analyzer import AlgoAnalyzer


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
