"""
Tests for Shareable Experiment Report Generator
"""

import os
import shutil
import tempfile
from geo_scope.engine.report_generator import generate_experiment_artifacts


def test_generate_experiment_artifacts():
    temp_dir = tempfile.mkdtemp()
    try:
        mock_analysis = {
            "summary": {
                "total_queries_tested": 10,
                "total_ai_executions": 40,
                "target_brand": "HubSpot",
                "overall_sov": 75.0,
                "overall_top1_rate": 45.0,
                "best_performing_model": "perplexity_sonar",
                "weakest_performing_model": "claude_3_7"
            },
            "share_of_model": {
                "by_model": {
                    "perplexity_sonar": {"mention_rate_pct": 80.0, "top1_rate_pct": 50.0, "avg_rank": 1.2}
                }
            },
            "citation_analytics": {
                "top_cited_domains": [{"domain": "reddit.com", "count": 12}]
            },
            "algorithmic_factors": {"global_average_weights": {"ugc_community": 32.0}},
            "competitor_matrix": [
                {"brand": "HubSpot", "mention_rate_pct": 75.0, "top1_rate_pct": 45.0, "is_target": True},
                {"brand": "Salesforce", "mention_rate_pct": 60.0, "top1_rate_pct": 30.0, "is_target": False}
            ]
        }

        mock_parsed = [
            {
                "query_id": "q1",
                "model": "perplexity_sonar",
                "intent": "commercial_direct",
                "language": "en",
                "target_brand": "HubSpot",
                "target_mentioned": True,
                "target_rank": 1,
                "target_is_top_1": True,
                "target_sentiment": "positive",
                "citation_count": 2,
                "response_length": 400
            }
        ]

        mock_prompts = [{"id": "q1", "query": "Best CRM?", "intent": "commercial_direct"}]

        artifacts = generate_experiment_artifacts(mock_analysis, mock_parsed, mock_prompts, out_dir=temp_dir, experiment_id="EXP-TEST-001")

        assert os.path.exists(artifacts["summary_md"])
        assert os.path.exists(artifacts["report_html"])
        assert os.path.exists(artifacts["experiment_json"])
        assert os.path.exists(artifacts["queries_csv"])
        assert os.path.exists(artifacts["citations_csv"])

        with open(artifacts["summary_md"], "r", encoding="utf-8") as f:
            md = f.read()
            assert "EXP-TEST-001" in md
            assert "HubSpot" in md
            assert "75.0%" in md

    finally:
        shutil.rmtree(temp_dir)
