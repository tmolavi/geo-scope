"""
GEO-Scope Evaluator for MAVI Layer L5 (Observed AI Visibility).
Extracts real, empirical brand visibility, top-1 rank, and citation presence from GEO-Scope benchmark experiments.
"""

from typing import Dict, Any, List, Optional
from geo_scope.mavi.models import LayerResult, LayerProvenance


class GEOScopeEvaluator:
    """
    Evaluates Layer 5 (Observed AI Visibility) from GEO-Scope live experiment results.
    Strict zero-fabrication contract: returns status='not_measured' and score=None if no valid benchmark observations exist.
    """

    @classmethod
    def evaluate_l5(
        cls,
        experiment_data: Optional[Dict[str, Any]] = None,
        target_brand: Optional[str] = None,
        weight: float = 0.25,
    ) -> LayerResult:
        """
        Extracts L5 Observed AI Visibility from an experiment analysis dictionary.
        """
        if not experiment_data:
            return LayerResult(
                layer_id="L5",
                layer_name="Observed AI Visibility",
                weight=weight,
                score=None,
                status="not_measured",
                provenance=LayerProvenance(
                    source="geo-scope",
                    metric_version="1.0.0",
                    evidence_count=0,
                ),
                details={"reason": "No experiment or live benchmark data provided"},
                findings=["L5 Observed AI Visibility has not been measured (run 'geo-scope run' or supply experiment data)."],
            )

        summary = experiment_data.get("summary", {})
        sov_data = experiment_data.get("share_of_model", {})
        citations_data = experiment_data.get("citation_analytics", {})

        total_ai_executions = summary.get("total_ai_executions", 0)
        successful_executions = summary.get("successful_executions", 0)
        failed_executions = summary.get("failed_executions", 0)
        exp_id = experiment_data.get("experiment_id") or summary.get("experiment_id") or "EXP-OBSERVED"
        mode = experiment_data.get("execution_mode") or summary.get("execution_mode", "unknown")

        # Zero-success check: If 0 successful observations, return insufficient_data
        if successful_executions == 0:
            return LayerResult(
                layer_id="L5",
                layer_name="Observed AI Visibility",
                weight=weight,
                score=None,
                status="insufficient_data",
                source_type="insufficient_data",
                methodology_status="insufficient_data",
                provenance=LayerProvenance(
                    source="geo-scope",
                    source_engine="geo-scope",
                    metric_version="1.0.0",
                    evidence_count=0,
                    experiment_id=exp_id,
                    execution_mode=mode,
                    successful_observations=0,
                    total_observations=total_ai_executions,
                ),
                details={
                    "experiment_id": exp_id,
                    "execution_mode": mode,
                    "successful_observations": 0,
                    "failed_observations": failed_executions,
                    "reason": "no successful provider observations",
                },
                findings=[f"Experiment {exp_id} had 0 successful observations across AI engines (insufficient data)."],
            )

        overall_sov = summary.get("overall_sov") or summary.get("target_brand_mention_rate") or 0.0
        overall_top1 = summary.get("overall_top1_rate") or summary.get("target_brand_top1_rate") or 0.0
        overall_citation = summary.get("overall_citation_rate") or 0.0
        by_model = sov_data.get("by_model", {})

        sov_val = float(overall_sov)
        top1_val = float(overall_top1)
        citation_val = float(overall_citation)

        mode_str = str(mode).lower()
        is_live = mode_str in ("live", "observed_live")
        source_type = "observed_live" if is_live else "synthetic"
        status = "measured" if is_live else "measured_synthetic"
        methodology_status = "observational_benchmark" if is_live else "non_observational"

        if by_model and citation_val == 0.0:
            active_providers = len([m for m, st in by_model.items() if st.get("successful_queries", 0) > 0])
            mentioned_providers = len([m for m, st in by_model.items() if (st.get("mention_rate_pct") or 0) > 0])
            provider_coverage_pct = (mentioned_providers / max(active_providers, 1)) * 100.0
            score_val = round((sov_val * 0.50) + (top1_val * 0.35) + (provider_coverage_pct * 0.15), 1)
        else:
            active_providers = len(experiment_data.get("providers", [])) or 1
            provider_coverage_pct = 100.0
            score_val = round((sov_val * 0.50) + (top1_val * 0.30) + (citation_val * 0.20), 1)

        contributors = [
            {
                "signal": "share_of_model_mentions",
                "impact": round(sov_val * 0.50, 1),
                "description": f"Brand mention rate across model responses: {sov_val:.1f}%",
            },
            {
                "signal": "top1_recommendation_rate",
                "impact": round(top1_val * 0.30, 1),
                "description": f"Top-1 primary recommendation frequency: {top1_val:.1f}%",
            },
            {
                "signal": "citation_absorption_rate",
                "impact": round(citation_val * 0.20, 1),
                "description": f"Domain citation inclusion rate: {citation_val:.1f}%",
            },
        ]

        findings = [
            f"Observed in {successful_executions} successful inference runs across {active_providers} AI engines ({source_type})",
            f"Target Brand Mention Rate (Share of Model): {sov_val:.1f}%",
            f"Top-1 Recommendation Pick Rate: {top1_val:.1f}%",
        ]

        return LayerResult(
            layer_id="L5",
            layer_name="Observed AI Visibility",
            weight=weight,
            score=score_val,
            status=status,
            source_type=source_type,
            methodology_status=methodology_status,
            provenance=LayerProvenance(
                source="geo-scope",
                source_engine="geo-scope",
                metric_version="1.0.0",
                evidence_count=successful_executions,
                experiment_id=exp_id,
                execution_mode=mode,
                successful_observations=successful_executions,
                total_observations=total_ai_executions,
                providers=experiment_data.get("providers"),
            ),
            contributors=contributors,
            details={
                "experiment_id": exp_id,
                "execution_mode": mode,
                "successful_observations": successful_executions,
                "failed_observations": failed_executions,
                "providers_count": active_providers,
                "overall_sov_pct": sov_val,
                "overall_top1_rate_pct": top1_val,
                "provider_coverage_pct": round(provider_coverage_pct, 1),
                "by_model_breakdown": {
                    m: {
                        "mention_rate_pct": st.get("mention_rate_pct"),
                        "top1_rate_pct": st.get("top1_rate_pct"),
                        "successful_queries": st.get("successful_queries"),
                    }
                    for m, st in by_model.items()
                },
            },
            findings=findings,
        )
