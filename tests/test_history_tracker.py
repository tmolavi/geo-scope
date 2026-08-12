"""
Tests for History Tracker & Feedback Loop Progression
"""

import os
from geo_scope.engine.history_tracker import save_benchmark_snapshot, load_all_history, get_brand_progression


def test_history_snapshot_and_delta():
    mock_analysis_1 = {
        "summary": {
            "overall_sov": 65.0,
            "overall_top1_rate": 40.0,
            "best_performing_model": "chatgpt_search"
        },
        "algorithmic_factors": {"global_average_weights": {"ugc_community": 30}}
    }

    # First audit run
    record_1 = save_benchmark_snapshot(mock_analysis_1, "crm_sales", "TestBrand", 100)
    assert record_1["is_first_run"] is True
    assert record_1["delta_sov"] == 0.0

    # Second audit run with improved metrics
    mock_analysis_2 = {
        "summary": {
            "overall_sov": 75.0,
            "overall_top1_rate": 48.0,
            "best_performing_model": "perplexity_sonar"
        },
        "algorithmic_factors": {"global_average_weights": {"ugc_community": 35}}
    }
    record_2 = save_benchmark_snapshot(mock_analysis_2, "crm_sales", "TestBrand", 100)
    assert record_2["is_first_run"] is False
    assert record_2["delta_sov"] == 10.0
    assert record_2["delta_top1"] == 8.0

    # Load history
    history = load_all_history()
    assert len(history) >= 2
    progression = get_brand_progression("TestBrand", "crm_sales")
    assert len(progression) >= 2
