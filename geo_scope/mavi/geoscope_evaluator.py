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
        mode = summary.get("execution_mode", "unknown")

        # Zero-success check: If 0 successful observations, do not fabricate score
        if successful_executions == 0:
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
                    experiment_id=exp_id,
                ),
                details={
                    "experiment_id": exp_id,
                    "execution_mode": mode,
                    "successful_observations": 0,
                    "failed_observations": failed_executions,
                    "reason": "no successful provider observations",
                },
                findings=[f"Experiment {exp_id} had 0 successful observations across AI engines."],
            )

        overall_sov = summary.get("overall_sov")
        overall_top1 = summary.get("overall_top1_rate")
        by_model = sov_data.get("by_model", {})

        # Calculate composite observed visibility score (0-100)
        # Component weights within L5:
        # - Mention Rate / SoM: 50%
        # - Top-1 Pick Rate: 35%
        # - Provider Coverage / Consistency: 15%
        sov_val = float(overall_sov if overall_sov is not None else 0.0)
        top1_val = float(overall_top1 if overall_top1 is not None else 0.0)

        # Provider coverage: active engines with >0 mentions vs tested engines
        active_providers = len([m for m, st in by_model.items() if st.get("successful_queries", 0) > 0])
        mentioned_providers = len([m for m, st in by_model.items() if (st.get("mention_rate_pct") or 0) > 0])
        provider_coverage_pct = (mentioned_providers / max(active_providers, 1)) * 100.0

        score_val = round((sov_val * 0.50) + (top1_val * 0.35) + (provider_coverage_pct * 0.15), 1)

        findings = [
            f"Observed in {successful_executions} successful inference runs across {active_providers} AI engines",
            f"Target Brand Mention Rate (Share of Model): {sov_val}%",
            f"Top-1 Recommendation Pick Rate: {top1_val}%",
            f"Multi-Model Provider Coverage: {provider_coverage_pct:.0f}% ({mentioned_providers}/{active_providers} engines)",
        ]

        return LayerResult(
            layer_id="L5",
            layer_name="Observed AI Visibility",
            weight=weight,
            score=score_val,
            status="measured",
            provenance=LayerProvenance(
                source="geo-scope",
                metric_version="1.0.0",
                evidence_count=successful_executions,
                experiment_id=exp_id,
            ),
            details={
                "experiment_id": exp_id,
                "execution_mode": mode,
                "successful_observations": successful_executions,
                "failed_observations": failed_executions,
                "providers_count": active_providers,
                "overall_sov_pct": overall_sov,
                "overall_top1_rate_pct": overall_top1,
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
