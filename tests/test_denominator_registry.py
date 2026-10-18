"""
Unit tests for GEO-Scope Central Denominator Registry (geo_scope/measurement/denominators.py).
Validates:
  - Strict denominator accounting across attempted, completed, and valid runs
  - Separation of All-Answers vs Retrieval-Evidence denominators
  - Standardized MetricRecord creation and schema validation
"""

import pytest
from geo_scope.measurement.denominators import DenominatorRegistry, MetricRecord


def test_denominator_registry_run_tracking():
    registry = DenominatorRegistry()
    
    # Run 1: Successful with retrieval evidence, citations, recommendations
    registry.record_run(attempted=True, completed=True, is_valid=True, has_retrieval_evidence=True, has_citations=True, has_recommendations=True)
    # Run 2: Successful without retrieval evidence (pure parametric answer)
    registry.record_run(attempted=True, completed=True, is_valid=True, has_retrieval_evidence=False, has_citations=False, has_recommendations=True)
    # Run 3: Failed execution (rate limited or network error)
    registry.record_run(attempted=True, completed=False, is_valid=False)

    summary = registry.summary_dict()
    assert summary["attempted_runs"] == 3
    assert summary["completed_runs"] == 2
    assert summary["valid_answers"] == 2
    assert summary["answers_with_retrieval_evidence"] == 1
    assert summary["answers_with_any_citation"] == 1
    assert summary["answers_with_recommendations"] == 2


def test_denominator_registry_entity_accounting():
    registry = DenominatorRegistry()
    registry.record_entity_observation(
        entity_id="inten",
        mentioned=True,
        cited=True,
        owned_domain_cited=True,
        recommended=True,
        top1_recommended=True,
        first_mention_position=1,
    )
    registry.record_entity_observation(
        entity_id="inten",
        mentioned=True,
        cited=False,
        owned_domain_cited=False,
        recommended=False,
        top1_recommended=False,
        first_mention_position=2,
    )

    assert registry.entity_mentions["inten"] == 2
    assert registry.entity_citations["inten"] == 1
    assert registry.entity_owned_citations["inten"] == 1
    assert registry.entity_recommendations["inten"] == 1
    assert registry.entity_top1_recommendations["inten"] == 1
    assert registry.entity_first_mention_positions["inten"] == [1, 2]
    assert registry.all_tracked_entity_mentions == 2


def test_build_metric_record():
    registry = DenominatorRegistry()
    rec = registry.build_metric(
        metric_name="owned_domain_citation_rate",
        numerator=5,
        denominator=10,
        denominator_type="retrieval_evidence_answers",
        sample_size=10,
        coverage=0.90,
        status="measured",
        ci_info={
            "ci_method": "wilson",
            "confidence_level": 0.95,
            "ci_lower": 0.2366,
            "ci_upper": 0.7634,
            "ci_width": 0.5268,
        },
    )

    assert isinstance(rec, MetricRecord)
    assert rec.metric == "owned_domain_citation_rate"
    assert rec.value == 0.50
    assert rec.numerator == 5
    assert rec.denominator == 10
    assert rec.denominator_type == "retrieval_evidence_answers"
    assert rec.sample_size == 10
    assert rec.coverage == 0.90
    assert rec.status == "measured"
    assert rec.ci_method == "wilson"
    assert rec.ci_lower == 0.2366
    assert rec.ci_upper == 0.7634


def test_build_metric_record_unmeasured():
    registry = DenominatorRegistry()
    rec = registry.build_metric(
        metric_name="source_influence",
        numerator=None,
        denominator=None,
        denominator_type="token_absorption_answers",
        sample_size=0,
        status="not_measured",
        disclaimer="Token-level citation absorption not verified.",
    )

    assert rec.value is None
    assert rec.status == "not_measured"
    assert rec.disclaimer == "Token-level citation absorption not verified."
