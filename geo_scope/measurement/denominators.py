"""
Central Denominator Registry for GEO-Scope AI Visibility Measurement.
Guarantees unambiguous mathematical accounting:
  - Every metric has an explicit numerator and denominator
  - Denominator types are strictly categorized
  - Missing data is never coerced to zero
  - Sample size, coverage, and status are coupled with every result
"""

from typing import Dict, Any, Optional, Union
from pydantic import BaseModel, Field


class MetricRecord(BaseModel):
    """Standardized representation of a single visibility metric observation."""
    metric: str
    value: Optional[float] = None
    numerator: Optional[int] = None
    denominator: Optional[int] = None
    denominator_type: str
    sample_size: int
    coverage: float = 1.0
    status: str = "measured"  # "measured" | "directional" | "single_observation" | "not_measured" | "insufficient_data" | "provider_error" | "fixture_only"
    ci_method: Optional[str] = None
    confidence_level: Optional[float] = None
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None
    ci_width: Optional[float] = None
    confidence_label: Optional[str] = None
    disclaimer: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=False)


class DenominatorRegistry:
    """
    Central repository for tracking observation denominators across an execution batch or slice.
    """

    def __init__(self):
        self.attempted_runs: int = 0
        self.completed_runs: int = 0
        self.valid_answers: int = 0
        self.answers_with_retrieval_evidence: int = 0
        self.answers_with_any_citation: int = 0
        self.answers_with_recommendations: int = 0
        self.human_validated_answers: int = 0
        self.all_tracked_entity_mentions: int = 0

        # Per-entity counters: entity_id -> count
        self.entity_mentions: Dict[str, int] = {}
        self.entity_citations: Dict[str, int] = {}
        self.entity_owned_citations: Dict[str, int] = {}
        self.entity_recommendations: Dict[str, int] = {}
        self.entity_top1_recommendations: Dict[str, int] = {}
        self.entity_first_mention_positions: Dict[str, list] = {}

    def record_run(
        self,
        attempted: bool = True,
        completed: bool = True,
        is_valid: bool = True,
        has_retrieval_evidence: bool = False,
        has_citations: bool = False,
        has_recommendations: bool = False,
        is_human_validated: bool = False,
    ) -> None:
        """Records an engine run execution."""
        if attempted:
            self.attempted_runs += 1
        if completed:
            self.completed_runs += 1
        if is_valid:
            self.valid_answers += 1
        if has_retrieval_evidence:
            self.answers_with_retrieval_evidence += 1
        if has_citations:
            self.answers_with_any_citation += 1
        if has_recommendations:
            self.answers_with_recommendations += 1
        if is_human_validated:
            self.human_validated_answers += 1

    def record_entity_observation(
        self,
        entity_id: str,
        mentioned: bool = False,
        cited: bool = False,
        owned_domain_cited: bool = False,
        recommended: bool = False,
        top1_recommended: bool = False,
        first_mention_position: Optional[int] = None,
    ) -> None:
        """Records entity-specific detection flags."""
        if entity_id not in self.entity_mentions:
            self.entity_mentions[entity_id] = 0
            self.entity_citations[entity_id] = 0
            self.entity_owned_citations[entity_id] = 0
            self.entity_recommendations[entity_id] = 0
            self.entity_top1_recommendations[entity_id] = 0
            self.entity_first_mention_positions[entity_id] = []

        if mentioned:
            self.entity_mentions[entity_id] += 1
            self.all_tracked_entity_mentions += 1
            if first_mention_position is not None and first_mention_position > 0:
                self.entity_first_mention_positions[entity_id].append(first_mention_position)

        if cited:
            self.entity_citations[entity_id] += 1
        if owned_domain_cited:
            self.entity_owned_citations[entity_id] += 1
        if recommended:
            self.entity_recommendations[entity_id] += 1
        if top1_recommended:
            self.entity_top1_recommendations[entity_id] += 1

    def build_metric(
        self,
        metric_name: str,
        numerator: Optional[int],
        denominator: Optional[int],
        denominator_type: str,
        sample_size: int,
        coverage: float = 1.0,
        status: Optional[str] = None,
        ci_info: Optional[Dict[str, Any]] = None,
        disclaimer: Optional[str] = None,
    ) -> MetricRecord:
        """Constructs a standardized MetricRecord with complete provenance."""
        # Determine value
        if numerator is None or denominator is None or denominator == 0:
            val = None
        else:
            val = round(numerator / denominator, 4)

        # Determine status
        if status is None:
            if sample_size == 0 or denominator == 0:
                status = "not_measured"
            elif sample_size < 2:
                status = "single_observation"
            elif sample_size < 5:
                status = "directional"
            else:
                status = "measured"

        record = MetricRecord(
            metric=metric_name,
            value=val,
            numerator=numerator,
            denominator=denominator,
            denominator_type=denominator_type,
            sample_size=sample_size,
            coverage=round(coverage, 4),
            status=status,
            disclaimer=disclaimer,
        )

        if ci_info:
            record.ci_method = ci_info.get("ci_method")
            record.confidence_level = ci_info.get("confidence_level")
            record.ci_lower = ci_info.get("ci_lower")
            record.ci_upper = ci_info.get("ci_upper")
            record.ci_width = ci_info.get("ci_width")

        return record

    def summary_dict(self) -> Dict[str, Any]:
        """Returns the central denominator ledger."""
        return {
            "attempted_runs": self.attempted_runs,
            "completed_runs": self.completed_runs,
            "valid_answers": self.valid_answers,
            "answers_with_retrieval_evidence": self.answers_with_retrieval_evidence,
            "answers_with_any_citation": self.answers_with_any_citation,
            "answers_with_recommendations": self.answers_with_recommendations,
            "human_validated_answers": self.human_validated_answers,
            "all_tracked_entity_mentions": self.all_tracked_entity_mentions,
        }
