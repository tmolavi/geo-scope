"""
Unit tests for GEO-Scope Statistical Layer (geo_scope/measurement/stats.py).
Validates:
  - 95% Wilson Score Intervals against known theoretical values
  - Edge cases: n=0, k=0, k=n, n=1
  - Bootstrap Resampling Confidence Intervals: deterministic seeds and sample distributions
  - Overlapping confidence interval detection and warning generation
  - Rule-based confidence labeling (insufficient, directional, moderate, strong)
"""

import pytest
from geo_scope.measurement.stats import (
    wilson_score_interval,
    bootstrap_confidence_interval,
    check_overlapping_ci,
    generate_confidence_label,
    get_z_score,
)


def test_wilson_score_interval_known_values():
    # 50 out of 100 -> p=0.5, Wilson 95% CI is approximately [0.4038, 0.5962]
    ci = wilson_score_interval(50, 100, confidence_level=0.95)
    assert ci["value"] == 0.50
    assert ci["ci_lower"] == pytest.approx(0.4038, abs=0.01)
    assert ci["ci_upper"] == pytest.approx(0.5962, abs=0.01)
    assert ci["is_defined"] is True
    assert ci["ci_method"] == "wilson"


def test_wilson_score_interval_extremes():
    # 0 out of 100 -> lower bound 0.0, upper bound > 0
    ci_zero = wilson_score_interval(0, 100, confidence_level=0.95)
    assert ci_zero["value"] == 0.0
    assert ci_zero["ci_lower"] == 0.0
    assert 0.0 < ci_zero["ci_upper"] < 0.05

    # 100 out of 100 -> upper bound 1.0, lower bound < 1
    ci_all = wilson_score_interval(100, 100, confidence_level=0.95)
    assert ci_all["value"] == 1.0
    assert ci_all["ci_upper"] == 1.0
    assert 0.95 < ci_all["ci_lower"] < 1.0


def test_wilson_score_interval_empty_sample():
    # n=0 total
    ci_empty = wilson_score_interval(0, 0, confidence_level=0.95)
    assert ci_empty["value"] == 0.0
    assert ci_empty["ci_lower"] is None
    assert ci_empty["ci_upper"] is None
    assert ci_empty["is_defined"] is False


def test_bootstrap_confidence_interval_deterministic():
    data = [1.0, 2.0, 1.0, 3.0, 2.0, 1.0, 2.0, 4.0, 2.0, 1.0]
    ci_1 = bootstrap_confidence_interval(data, n_resamples=500, random_seed=42)
    ci_2 = bootstrap_confidence_interval(data, n_resamples=500, random_seed=42)

    assert ci_1["is_defined"] is True
    assert ci_1["value"] == pytest.approx(1.9, abs=0.01)
    # Fully deterministic reproducibility with same seed
    assert ci_1["ci_lower"] == ci_2["ci_lower"]
    assert ci_1["ci_upper"] == ci_2["ci_upper"]
    assert ci_1["ci_lower"] < ci_1["value"] < ci_1["ci_upper"]


def test_bootstrap_confidence_interval_single_observation():
    data = [2.5]
    ci = bootstrap_confidence_interval(data, n_resamples=100, random_seed=42)
    assert ci["is_defined"] is True
    assert ci["value"] == 2.5
    assert ci["ci_lower"] == 2.5
    assert ci["ci_upper"] == 2.5


def test_bootstrap_confidence_interval_empty():
    ci = bootstrap_confidence_interval([])
    assert ci["is_defined"] is False
    assert ci["value"] is None


def test_check_overlapping_ci_detected():
    # Interval A: [0.30, 0.50]
    # Interval B: [0.45, 0.65] -> Overlap in [0.45, 0.50]
    res = check_overlapping_ci((0.30, 0.50), (0.45, 0.65))
    assert res["overlapping"] is True
    assert res["warning"] == "The observed difference is within the uncertainty range of this sample."
    assert res["overlap_range"] == [0.45, 0.50]


def test_check_overlapping_ci_separated():
    # Interval A: [0.10, 0.25]
    # Interval B: [0.55, 0.80] -> Disjoint
    res = check_overlapping_ci((0.10, 0.25), (0.55, 0.80))
    assert res["overlapping"] is False
    assert res["warning"] is None


def test_generate_confidence_label_rules():
    # Low runs -> directional or insufficient
    assert generate_confidence_label(runs=1) == "insufficient"
    assert generate_confidence_label(runs=3) == "directional"

    # Low coverage -> insufficient
    assert generate_confidence_label(runs=10, coverage=0.40) == "insufficient"

    # Unverified provenance -> insufficient
    assert generate_confidence_label(runs=10, coverage=1.0, provenance_complete=False) == "insufficient"

    # Wide confidence interval -> directional
    assert generate_confidence_label(runs=6, coverage=1.0, ci_width=0.45) == "directional"

    # Moderate conditions (runs >= 5, moderate width)
    assert generate_confidence_label(runs=6, coverage=0.90, engine_breadth=2, ci_width=0.18) == "moderate"

    # Strong conditions (runs >= 5, 3 engines, 2 languages, narrow width)
    assert generate_confidence_label(
        runs=10,
        coverage=1.0,
        provenance_complete=True,
        engine_breadth=3,
        language_breadth=2,
        ci_width=0.12,
    ) == "strong"
