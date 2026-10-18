"""
Unit tests for MAVI Layer Decoupling & Sensitivity Analysis (geo_scope/mavi/).
Validates:
  - Strict decoupling: Readiness (L1-L4) vs Observed Visibility (L5)
  - Invariant: mavi_composite is strictly None when L5 is not measured
  - Missing data status accounting (not_measured, insufficient_data)
  - Sensitivity analysis output
"""

import pytest
from geo_scope.mavi import MAVIEngine, MAVIReport, LayerWeights


def test_mavi_decoupling_without_l5():
    engine = MAVIEngine()
    # Provide manual layers for L1-L4 only, leaving L5 unmeasured
    manual_layers = {
        "L1": 80.0,
        "L2": 75.0,
        "L3": 70.0,
        "L4": 65.0,
    }
    report = engine.measure(manual_layers=manual_layers, target_brand="TestCorp")

    assert isinstance(report, MAVIReport)
    # Readiness score must be computed
    assert report.readiness_score is not None
    assert 70.0 <= report.readiness_score <= 75.0

    # L5 must be not_measured
    assert report.layers["L5"].status == "not_measured"
    assert report.observed_visibility is not None
    assert report.observed_visibility["status"] == "not_measured"

    # Core Invariant: Composite MAVI must be None when L5 is unmeasured
    assert report.mavi_composite is None
    assert report.composite_reason == "Live empirical visibility has not been measured."


def test_mavi_decoupling_with_l5_measured():
    engine = MAVIEngine()
    # Provide all 5 layers
    manual_layers = {
        "L1": 80.0,
        "L2": 75.0,
        "L3": 70.0,
        "L4": 65.0,
        "L5": 60.0,
    }
    report = engine.measure(manual_layers=manual_layers, target_brand="TestCorp")

    assert report.readiness_score is not None
    assert report.layers["L5"].status == "manual_override"
    assert report.observed_visibility["status"] == "manual_override"
    # When L5 is measured, composite MAVI is defined
    assert report.mavi_composite is not None
    assert 65.0 <= report.mavi_composite <= 75.0
    assert report.composite_reason is None


def test_mavi_sensitivity_analysis():
    engine = MAVIEngine()
    manual_layers = {
        "L1": 80.0,
        "L2": 75.0,
        "L3": 70.0,
        "L4": 65.0,
        "L5": 60.0,
    }
    report = engine.measure(manual_layers=manual_layers, target_brand="TestCorp")
    
    sens = engine.sensitivity_analysis(report, delta=0.10)
    assert sens["base_composite"] == report.mavi_composite
    assert "empirical_heavy" in sens["scenarios"]
    assert "readiness_heavy" in sens["scenarios"]
    assert len(sens["stability_range"]) == 2
    assert sens["stability_range"][0] <= sens["stability_range"][1]


def test_mavi_sensitivity_analysis_unmeasured_l5():
    engine = MAVIEngine()
    manual_layers = {"L1": 80.0, "L2": 70.0}
    report = engine.measure(manual_layers=manual_layers, target_brand="TestCorp")
    
    sens = engine.sensitivity_analysis(report, delta=0.10)
    assert sens["status"] == "not_applicable"
    assert "Composite score is null" in sens["reason"]
