"""
MAVI Measurement Engine v1.0
Orchestrates multi-layer AI visibility index (L1-L5), partial normalization, provenance, and confidence assessment.
"""

import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from geo_scope.mavi.models import (
    LayerResult,
    LayerProvenance,
    LayerWeights,
    ConfidenceAssessment,
    MAVIReport,
)
from geo_scope.mavi.sage_evaluator import SAGEEvaluator
from geo_scope.mavi.geoscope_evaluator import GEOScopeEvaluator


class MAVIEngine:
    """
    Molavi AI Visibility Index (MAVI) Engine.
    Transforms MAVI from a manual checklist into a deterministic, measured multi-layer index.
    """

    def __init__(self, weights: Optional[LayerWeights | Dict[str, float]] = None):
        if weights is None:
            self.weights = LayerWeights()
            self.weights_provenance = "methodology_defaults_v1"
        elif isinstance(weights, LayerWeights):
            self.weights = weights
            self.weights_provenance = "custom_configured"
        elif isinstance(weights, dict):
            self.weights = LayerWeights.from_dict(weights)
            self.weights_provenance = "custom_configured"
        else:
            self.weights = LayerWeights()
            self.weights_provenance = "methodology_defaults_v1"

    def measure(
        self,
        html_content: Optional[str] = None,
        url: Optional[str] = None,
        target_brand: Optional[str] = None,
        experiment_data: Optional[Dict[str, Any]] = None,
        manual_layers: Optional[Dict[str, float]] = None,
        http_status: int = 200,
    ) -> MAVIReport:
        """
        Executes multi-layer MAVI measurement.
        """
        layers: Dict[str, LayerResult] = {}
        target_entity = target_brand or "Target Entity"

        # Check if running in manual override mode
        if manual_layers:
            measurement_mode = "manual_override"
            for layer_id in ["L1", "L2", "L3", "L4", "L5"]:
                name_map = {
                    "L1": "Technical Accessibility",
                    "L2": "Semantic Extractability",
                    "L3": "Entity Clarity",
                    "L4": "Citation Readiness",
                    "L5": "Observed AI Visibility",
                }
                val = manual_layers.get(layer_id)
                status = "manual_override" if val is not None else "not_measured"
                layers[layer_id] = LayerResult(
                    layer_id=layer_id,
                    layer_name=name_map[layer_id],
                    weight=self.weights.get_weight(layer_id),
                    score=round(float(val), 1) if val is not None else None,
                    status=status,
                    provenance=LayerProvenance(
                        source="manual",
                        metric_version="1.0.0",
                        evidence_count=1 if val is not None else 0,
                    ),
                    details={"mode": "manual_override_debug"},
                    findings=["Score manually supplied via manual override mode (not derived from audit measurements)."],
                )
        else:
            measurement_mode = "measured"
            # 1. Evaluate SAGE Layers L1-L4 from HTML or URL
            if html_content or url:
                sage = SAGEEvaluator(html_content=html_content, url=url, target_brand=target_brand, http_status=http_status)
                layers["L1"] = sage.evaluate_l1_technical_accessibility(weight=self.weights.l1_technical_accessibility)
                layers["L2"] = sage.evaluate_l2_semantic_extractability(weight=self.weights.l2_semantic_extractability)
                layers["L3"] = sage.evaluate_l3_entity_clarity(weight=self.weights.l3_entity_clarity)
                layers["L4"] = sage.evaluate_l4_citation_readiness(weight=self.weights.l4_citation_readiness)
            else:
                for lid, lname, w in [
                    ("L1", "Technical Accessibility", self.weights.l1_technical_accessibility),
                    ("L2", "Semantic Extractability", self.weights.l2_semantic_extractability),
                    ("L3", "Entity Clarity", self.weights.l3_entity_clarity),
                    ("L4", "Retrieval / Citation Readiness", self.weights.l4_citation_readiness),
                ]:
                    layers[lid] = LayerResult(
                        layer_id=lid,
                        layer_name=lname,
                        weight=w,
                        score=None,
                        status="not_measured",
                        provenance=LayerProvenance(source="sage", metric_version="2.0.0", evidence_count=0),
                        details={"reason": "No HTML content or URL supplied for SAGE audit"},
                        findings=[f"{lid} {lname} not measured (supply HTML or URL to measure)."],
                    )

            # 2. Evaluate Layer 5 from GEO-Scope experiment data
            layers["L5"] = GEOScopeEvaluator.evaluate_l5(
                experiment_data=experiment_data,
                target_brand=target_brand,
                weight=self.weights.l5_observed_ai_visibility,
            )

        # 3. Compute Partial Scoring and Normalization
        active_layers = [
            l for l in layers.values()
            if l.status in ("measured", "measured_synthetic", "manual_override") and l.score is not None
        ]
        measured_count = len(active_layers)
        total_layers = len(layers)

        if measured_count == 0:
            mavi_score = None
            raw_measured = None
            max_possible_raw = 0.0
            norm_basis = "No layers were measured; MAVI score undefined."
            grade = "N/A"
            final_mode = "not_measured"
        else:
            raw_measured = round(sum(l.score * l.weight for l in active_layers), 2)
            active_weights_sum = sum(l.weight for l in active_layers)
            max_possible_raw = round(active_weights_sum * 100.0, 1)

            if active_weights_sum > 0:
                normalized = round((raw_measured / active_weights_sum), 1)
            else:
                normalized = 0.0

            mavi_score = normalized
            if measurement_mode == "manual_override":
                final_mode = "manual_override"
                norm_basis = f"Manual override score across {measured_count}/{total_layers} layers"
            elif layers.get("L5") and layers["L5"].status == "measured_synthetic":
                final_mode = "measured_synthetic"
                norm_basis = f"Normalized across {measured_count}/{total_layers} layers (includes synthetic L5)"
            elif measured_count < total_layers:
                final_mode = "partial_measured"
                active_names = [l.layer_id for l in active_layers]
                norm_basis = f"Normalized across {measured_count}/{total_layers} measured layers ({', '.join(active_names)}); active weight sum = {active_weights_sum:.2f}"
            else:
                final_mode = "measured"
                norm_basis = "Complete 5-layer measurement index (100% layer coverage)"

            grade = (
                "A+" if mavi_score >= 85
                else "A" if mavi_score >= 70
                else "B" if mavi_score >= 55
                else "C" if mavi_score >= 40
                else "D"
            )

        # 4. Assess Measurement Confidence
        confidence = self._calculate_confidence(layers, measured_count, total_layers)

        return MAVIReport(
            mavi_score=mavi_score,
            raw_measured_score=raw_measured,
            max_possible_raw_score=max_possible_raw,
            measured_layers_count=measured_count,
            total_layers_count=total_layers,
            normalization_basis=norm_basis,
            measurement_mode=final_mode,
            grade=grade,
            confidence=confidence,
            weights=self.weights.to_dict(),
            weights_provenance=self.weights_provenance,
            layers=layers,
            target_entity=target_entity,
            url=url,
        )

    def _calculate_confidence(
        self,
        layers: Dict[str, LayerResult],
        measured_count: int,
        total_layers: int,
    ) -> ConfidenceAssessment:
        """
        Calculates MAVI confidence score from empirical data completeness and source validity.
        """
        factors: Dict[str, Any] = {
            "measured_layers_count": measured_count,
            "total_layers": total_layers,
            "freshness_days": 0,
        }

        l5 = layers.get("L5")
        l5_source_type = l5.source_type if l5 else "not_measured"
        l5_obs = (l5.provenance.successful_observations or l5.provenance.evidence_count) if l5 else 0

        factors["l5_source_type"] = l5_source_type
        factors["l5_successful_observations"] = l5_obs

        if measured_count == 5 and l5_source_type == "observed_live" and l5_obs >= 10:
            level = "High"
            score = 0.95
        elif measured_count >= 4 and l5_source_type in ("observed_live", "not_measured"):
            level = "Medium"
            score = 0.75 if l5_source_type == "observed_live" else 0.65
        elif measured_count >= 4 and l5_source_type == "synthetic":
            level = "Medium"
            score = 0.60
            factors["synthetic_l5_penalty"] = "Confidence reduced due to simulation-based L5."
        elif measured_count >= 2:
            level = "Low"
            score = 0.40
        else:
            level = "Insufficient"
            score = 0.0

        return ConfidenceAssessment(
            confidence_level=level,
            confidence_score=score,
            factors=factors,
        )

    def format_human_readable(self, report: MAVIReport) -> str:
        """
        Formats MAVIReport into a clean human-readable diagnostic report.
        """
        lines = []
        score_str = f"{report.mavi_score}/100" if report.mavi_score is not None else "N/A (Not Measured)"
        lines.append("=" * 75)
        lines.append("⟠ MOLAVI AI VISIBILITY INDEX (MAVI) REPORT v1.0")
        lines.append("=" * 75)
        lines.append(f"Target Entity      : {report.target_entity}")
        if report.url:
            lines.append(f"Target URL         : {report.url}")
        lines.append(f"MAVI Score         : {score_str} (Grade: {report.grade})")
        lines.append(f"Confidence Level   : {report.confidence.confidence_level} ({int(report.confidence.confidence_score * 100)}%)")
        lines.append(f"Measurement Mode   : {report.measurement_mode.upper()}")
        lines.append(f"Layers Measured    : {report.measured_layers_count}/{report.total_layers_count}")
        lines.append(f"Normalization Basis: {report.normalization_basis}")
        lines.append("-" * 75)
        lines.append("📊 LAYER-BY-LAYER MEASUREMENT BREAKDOWN:")
        lines.append("-" * 75)

        for lid in ["L1", "L2", "L3", "L4", "L5"]:
            layer = report.layers.get(lid)
            if not layer:
                continue
            status_tag = f"[{layer.status.upper()}]"
            score_display = f"{layer.score:.1f}/100 (Weight: {int(layer.weight * 100)}%)" if layer.score is not None else f"N/A (Weight: {int(layer.weight * 100)}%)"
            lines.append(f"• {layer.layer_id} {layer.layer_name:<28} : {score_display:<22} {status_tag}")
            lines.append(f"  Source: {layer.provenance.source} (v{layer.provenance.metric_version}) | Evidence: {layer.provenance.evidence_count} items")
            for f in layer.findings[:2]:
                lines.append(f"  → {f}")
            lines.append("")

        l5 = report.layers.get("L5")
        if l5 and l5.status == "measured" and l5.score is not None:
            lines.append("-" * 75)
            lines.append("🤖 Observed AI Visibility Evidence:")
            lines.append(f"  - Providers Evaluated   : {l5.details.get('providers_count', 0)} engines")
            lines.append(f"  - Successful Observations: {l5.details.get('successful_observations', 0)}")
            lines.append(f"  - Experiment Reference  : {l5.details.get('experiment_id', 'N/A')}")
            lines.append(f"  - Share of Model (SoM)  : {l5.details.get('overall_sov_pct')}%")
            lines.append(f"  - Top-1 Pick Rate       : {l5.details.get('overall_top1_rate_pct')}%")

        lines.append("=" * 75)
        return "\n".join(lines)
