"""SAGE Audit Adapter for MAVI Layers L1, L2, L3, L4.

Maps structured outputs from SAGE Core (`sage-audit`) into canonical MAVI LayerResult models.
Does NOT independently parse HTML or reimplement duplicate SEO/GEO analysis.

(c) 2026 Taqi Molavi — https://molavi.pro — MIT License
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

try:
    import sage_audit
    from sage_audit import SageAuditor, SageConfig
    from sage_audit.models import AuditReport, PillarReport
    SAGE_AVAILABLE = True
except ImportError:  # pragma: no cover
    SAGE_AVAILABLE = False
    SageAuditor = None
    SageConfig = None
    AuditReport = None
    PillarReport = None

from geo_scope.mavi.models import LayerProvenance, LayerResult

logger = logging.getLogger("geo_scope.mavi.sage_evaluator")

MAVI_METHODOLOGY_VERSION = "MAVI v1.0"


class SAGEEvaluator:
    """Adapter mapping structured SAGE audit reports to canonical MAVI Layers L1-L4."""

    def __init__(
        self,
        html_content: Optional[str] = None,
        url: Optional[str] = None,
        target_brand: Optional[str] = None,
        http_status: int = 200,
        sage_report: Optional[Any] = None,
    ):
        self.html = html_content or ""
        self.url = url or ""
        self.target_brand = (target_brand or "").strip()
        self.http_status = http_status
        self.sage_report = sage_report

        if self.sage_report is None and (self.html or self.url):
            self._execute_sage_audit()

    def _execute_sage_audit(self) -> None:
        """Executes SAGE Core audit to produce structured 3-pillar report."""
        if not SAGE_AVAILABLE:
            logger.warning("sage-audit package is not installed; SAGE evaluation will return unmeasured layers.")
            return

        try:
            cfg = SageConfig(embedding_backend="hashing")
            auditor = SageAuditor(config=cfg)
            if self.html:
                target_url = self.url or "https://example.local/"
                self.sage_report = auditor.audit_html(self.html, url=target_url)
            elif self.url:
                self.sage_report = auditor.audit(self.url)
        except Exception as exc:
            logger.error("SAGE audit invocation failed: %s", exc, exc_info=True)
            self.sage_report = None

    def _get_pillar(self, pillar_name: str) -> Optional[Any]:
        """Retrieves a pillar report (SEO, AEO, or GEO) from sage_report."""
        if self.sage_report is None:
            return None
        if hasattr(self.sage_report, pillar_name):
            return getattr(self.sage_report, pillar_name)
        if isinstance(self.sage_report, dict):
            return self.sage_report.get(pillar_name)
        return None

    def evaluate_l1_technical_accessibility(self, weight: float = 0.15) -> LayerResult:
        """L1 Technical Accessibility: Mapped from SAGE Pillar 1 (Technical SEO)."""
        seo = self._get_pillar("seo")
        if seo is None:
            return self._unmeasured_layer("L1", "Technical Accessibility", weight)

        score = round(float(getattr(seo, "score", 0.0) if hasattr(seo, "score") else seo.get("score", 0.0)), 1)
        metrics = getattr(seo, "metrics", {}) if hasattr(seo, "metrics") else seo.get("metrics", {})
        findings_objs = getattr(seo, "findings", []) if hasattr(seo, "findings") else seo.get("findings", [])

        findings_text = []
        for f in findings_objs[:5]:
            msg = getattr(f, "title", str(f)) if hasattr(f, "title") else (f.get("title") or f.get("message", str(f)))
            findings_text.append(msg)

        contributors = [
            {
                "signal": "technical_seo_baseline",
                "impact": round(score * 0.40, 1),
                "description": f"SAGE Technical SEO audit baseline score: {score}/100",
            },
            {
                "signal": "dom_cleanliness",
                "impact": round(min(30.0, metrics.get("text_to_code_ratio", 0.0) * 300.0), 1),
                "description": f"Text to HTML ratio: {metrics.get('text_to_code_ratio', 0.0):.2%}",
            },
            {
                "signal": "word_count_substance",
                "impact": round(min(30.0, (metrics.get("word_count", 0) / 500.0) * 30.0), 1),
                "description": f"Content word count: {metrics.get('word_count', 0)} words",
            },
        ]

        return LayerResult(
            layer_id="L1",
            layer_name="Technical Accessibility",
            weight=weight,
            score=score,
            status="measured",
            provenance=LayerProvenance(
                source="sage",
                metric_version="2.0.0",
                evidence_count=len(findings_objs),
                url=self.url or None,
            ),
            contributors=contributors,
            details={
                "http_status": self.http_status,
                "text_to_html_ratio": metrics.get("text_to_code_ratio", 0.0),
                "word_count": metrics.get("word_count", 0),
                "raw_metrics": metrics,
            },
            findings=findings_text or ["Technical SEO verified by SAGE."],
        )

    def evaluate_l2_semantic_extractability(self, weight: float = 0.20) -> LayerResult:
        """L2 Semantic Extractability: Mapped from SAGE Pillar 2 (AEO Structure)."""
        aeo = self._get_pillar("aeo")
        if aeo is None:
            return self._unmeasured_layer("L2", "Semantic Extractability", weight)

        score = round(float(getattr(aeo, "score", 0.0) if hasattr(aeo, "score") else aeo.get("score", 0.0)), 1)
        metrics = getattr(aeo, "metrics", {}) if hasattr(aeo, "metrics") else aeo.get("metrics", {})
        findings_objs = getattr(aeo, "findings", []) if hasattr(aeo, "findings") else aeo.get("findings", [])

        findings_text = []
        for f in findings_objs[:5]:
            msg = getattr(f, "title", str(f)) if hasattr(f, "title") else (f.get("title") or f.get("message", str(f)))
            findings_text.append(msg)

        contributors = [
            {
                "signal": "aeo_structure_baseline",
                "impact": round(score * 0.50, 1),
                "description": f"SAGE AEO structure and extractability score: {score}/100",
            },
            {
                "signal": "schema_entity_depth",
                "impact": round(min(25.0, metrics.get("json_ld_blocks", 0) * 12.5), 1),
                "description": f"JSON-LD structured blocks: {metrics.get('json_ld_blocks', 0)}",
            },
            {
                "signal": "entity_types_coverage",
                "impact": round(min(25.0, len(metrics.get("entity_types", [])) * 10.0), 1),
                "description": f"Identified schema entities: {', '.join(metrics.get('entity_types', [])) or 'None'}",
            },
        ]

        return LayerResult(
            layer_id="L2",
            layer_name="Semantic Extractability",
            weight=weight,
            score=score,
            status="measured",
            provenance=LayerProvenance(
                source="sage",
                metric_version="2.0.0",
                evidence_count=len(findings_objs),
                url=self.url or None,
            ),
            contributors=contributors,
            details={
                "json_ld_blocks": metrics.get("json_ld_blocks", 0),
                "entity_types": metrics.get("entity_types", []),
                "raw_metrics": metrics,
            },
            findings=findings_text or ["Semantic extractability verified by SAGE."],
        )

    def evaluate_l3_entity_clarity(self, weight: float = 0.20) -> LayerResult:
        """L3 Entity Clarity: Mapped from SAGE Pillar 2 (Entity Graph Analysis)."""
        aeo = self._get_pillar("aeo")
        if aeo is None:
            return self._unmeasured_layer("L3", "Entity Clarity", weight)

        metrics = getattr(aeo, "metrics", {}) if hasattr(aeo, "metrics") else aeo.get("metrics", {})
        findings_objs = getattr(aeo, "findings", []) if hasattr(aeo, "findings") else aeo.get("findings", [])
        entity_types = metrics.get("entity_types", [])

        # Filter entity-specific findings
        entity_findings = []
        for f in findings_objs:
            check_id = getattr(f, "check_id", "") if hasattr(f, "check_id") else f.get("check_id", "")
            if "entity" in check_id or "jsonld" in check_id or "schema" in check_id or "brand" in check_id:
                msg = getattr(f, "title", str(f)) if hasattr(f, "title") else (f.get("title") or f.get("message", str(f)))
                entity_findings.append(msg)

        score = round(float(getattr(aeo, "score", 0.0) if hasattr(aeo, "score") else aeo.get("score", 0.0)), 1)

        contributors = [
            {
                "signal": "entity_graph_completeness",
                "impact": round(score * 0.40, 1),
                "description": f"Entity graph score: {score}/100",
            },
            {
                "signal": "core_entity_presence",
                "impact": 30.0 if any(t in ("Organization", "Person", "Product", "SoftwareApplication") for t in entity_types) else 10.0,
                "description": f"Core entity types: {', '.join(entity_types) or 'None'}",
            },
            {
                "signal": "brand_disambiguation",
                "impact": 30.0 if self.target_brand else 15.0,
                "description": f"Target entity disambiguation: {self.target_brand or 'Generic'}",
            },
        ]

        return LayerResult(
            layer_id="L3",
            layer_name="Entity Clarity",
            weight=weight,
            score=score,
            status="measured",
            provenance=LayerProvenance(
                source="sage",
                metric_version="2.0.0",
                evidence_count=len(entity_findings) or len(findings_objs),
                url=self.url or None,
            ),
            contributors=contributors,
            details={
                "entity_types": entity_types,
                "target_brand": self.target_brand,
                "raw_metrics": metrics,
            },
            findings=entity_findings or ["Entity clarity verified by SAGE."],
        )

    def evaluate_l4_citation_readiness(self, weight: float = 0.20) -> LayerResult:
        """L4 Retrieval / Citation Readiness: Mapped from SAGE Pillar 3 (GEO & CSP)."""
        geo = self._get_pillar("geo")
        if geo is None:
            return self._unmeasured_layer("L4", "Retrieval / Citation Readiness", weight)

        metrics = getattr(geo, "metrics", {}) if hasattr(geo, "metrics") else geo.get("metrics", {})
        csp_val = metrics.get("citation_survival_proxy")
        score = round(float(csp_val) if csp_val is not None else float(getattr(geo, "score", 0.0) if hasattr(geo, "score") else geo.get("score", 0.0)), 1)
        findings_objs = getattr(geo, "findings", []) if hasattr(geo, "findings") else geo.get("findings", [])

        findings_text = []
        for f in findings_objs[:5]:
            msg = getattr(f, "title", str(f)) if hasattr(f, "title") else (f.get("title") or f.get("message", str(f)))
            findings_text.append(msg)

        contributors = [
            {
                "signal": "citation_survival_proxy",
                "impact": round(score * 0.60, 1),
                "description": f"SAGE Citation Survival Proxy (CSP): {score}/100 (E4 Heuristic Proxy)",
            },
            {
                "signal": "rag_chunk_count",
                "impact": round(min(20.0, metrics.get("chunk_count", 0) * 4.0), 1),
                "description": f"Extracted semantic chunks: {metrics.get('chunk_count', 0)}",
            },
            {
                "signal": "query_coverage",
                "impact": round(min(20.0, len(metrics.get("queries", [])) * 5.0), 1),
                "description": f"Generated synthetic queries: {len(metrics.get('queries', []))}",
            },
        ]

        return LayerResult(
            layer_id="L4",
            layer_name="Retrieval / Citation Readiness",
            weight=weight,
            score=score,
            status="measured",
            provenance=LayerProvenance(
                source="sage",
                metric_version="2.0.0",
                evidence_count=len(findings_objs),
                url=self.url or None,
            ),
            contributors=contributors,
            details={
                "citation_survival_proxy": csp_val,
                "chunk_count": metrics.get("chunk_count", 0),
                "methodology_status": "diagnostic_heuristic_proxy",
                "raw_metrics": metrics,
            },
            findings=findings_text or ["Citation readiness diagnostic verified by SAGE."],
        )

    def _unmeasured_layer(self, layer_id: str, layer_name: str, weight: float) -> LayerResult:
        """Helper returning a standard unmeasured LayerResult."""
        return LayerResult(
            layer_id=layer_id,
            layer_name=layer_name,
            weight=weight,
            score=None,
            status="not_measured",
            provenance=LayerProvenance(
                source="sage",
                metric_version="2.0.0",
                evidence_count=0,
                url=self.url or None,
            ),
            details={"reason": "No SAGE report available to measure this layer."},
            findings=[f"{layer_id} {layer_name} not measured (provide HTML or URL to measure via SAGE)."],
        )

