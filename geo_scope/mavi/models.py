"""MAVI Engine Data Models, Weights Configuration, and Provenance Schemas.
Molavi AI Visibility Index (MAVI) v1.0

(c) 2026 Taqi Molavi — https://molavi.pro — MIT License
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

MAVI_METHODOLOGY_VERSION: str = "MAVI v1.0"


@dataclass
class LayerProvenance:
    source: str = "sage"  # "sage" | "geo-scope" | "manual"
    source_engine: str = "sage-audit"
    metric_version: str = "2.0.0"
    methodology_version: str = "MAVI v1.0"
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    evidence_count: int = 0
    experiment_id: Optional[str] = None
    execution_mode: Optional[str] = None
    successful_observations: Optional[int] = None
    total_observations: Optional[int] = None
    providers: Optional[List[str]] = None
    url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LayerResult:
    layer_id: str  # "L1", "L2", "L3", "L4", "L5"
    layer_name: str
    weight: float
    score: Optional[float]  # 0.0 - 100.0 or None if not_measured
    status: str  # "measured" | "measured_synthetic" | "not_measured" | "insufficient_data" | "manual_override"
    provenance: LayerProvenance
    source_type: str = "not_measured"  # "observed_live" | "synthetic" | "not_measured" | "insufficient_data"
    methodology_status: str = "standard"
    contributors: List[Dict[str, Any]] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    findings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "layer_id": self.layer_id,
            "layer_name": self.layer_name,
            "weight": self.weight,
            "score": self.score,
            "status": self.status,
            "source_type": self.source_type,
            "methodology_status": self.methodology_status,
            "provenance": self.provenance.to_dict(),
            "contributors": self.contributors,
            "details": self.details,
            "findings": self.findings,
        }


@dataclass
class LayerWeights:
    """Default methodology weights for MAVI v1.

    Labeled as methodology defaults (not claimed to be empirically fitted).
    """
    l1_technical_accessibility: float = 0.15
    l2_semantic_extractability: float = 0.20
    l3_entity_clarity: float = 0.20
    l4_citation_readiness: float = 0.20
    l5_observed_ai_visibility: float = 0.25

    def __post_init__(self) -> None:
        for name, val in [
            ("L1", self.l1_technical_accessibility),
            ("L2", self.l2_semantic_extractability),
            ("L3", self.l3_entity_clarity),
            ("L4", self.l4_citation_readiness),
            ("L5", self.l5_observed_ai_visibility),
        ]:
            if val < 0:
                raise ValueError(f"Weight for {name} cannot be negative: {val}")
        total = (
            self.l1_technical_accessibility
            + self.l2_semantic_extractability
            + self.l3_entity_clarity
            + self.l4_citation_readiness
            + self.l5_observed_ai_visibility
        )
        if total <= 0:
            raise ValueError("Sum of layer weights must be greater than zero.")

    def get_weight(self, layer_id: str) -> float:
        mapping = {
            "L1": self.l1_technical_accessibility,
            "L2": self.l2_semantic_extractability,
            "L3": self.l3_entity_clarity,
            "L4": self.l4_citation_readiness,
            "L5": self.l5_observed_ai_visibility,
        }
        return mapping.get(layer_id, 0.0)

    def to_dict(self) -> Dict[str, float]:
        return {
            "L1": self.l1_technical_accessibility,
            "L2": self.l2_semantic_extractability,
            "L3": self.l3_entity_clarity,
            "L4": self.l4_citation_readiness,
            "L5": self.l5_observed_ai_visibility,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "LayerWeights":
        # Support both short ("L1") and long keys
        for k, v in data.items():
            if float(v) < 0:
                raise ValueError(f"Weight for {k} cannot be negative: {v}")
        l1 = data.get("L1", data.get("l1_technical_accessibility", 0.15))
        l2 = data.get("L2", data.get("l2_semantic_extractability", 0.20))
        l3 = data.get("L3", data.get("l3_entity_clarity", 0.20))
        l4 = data.get("L4", data.get("l4_citation_readiness", 0.20))
        l5 = data.get("L5", data.get("l5_observed_ai_visibility", 0.25))
        return cls(
            l1_technical_accessibility=float(l1),
            l2_semantic_extractability=float(l2),
            l3_entity_clarity=float(l3),
            l4_citation_readiness=float(l4),
            l5_observed_ai_visibility=float(l5),
        )


@dataclass
class ConfidenceAssessment:
    confidence_level: str  # "High" | "Medium" | "Low" | "Insufficient"
    confidence_score: float  # 0.0 - 1.0
    factors: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MAVIReport:
    mavi_methodology_version: str = "MAVI v1.0"
    mavi_score: Optional[float] = None  # Normalized score (0-100) or None
    raw_measured_score: Optional[float] = None
    max_possible_raw_score: float = 100.0
    max_score: float = 100.0
    measured_layers_count: int = 0
    total_layers_count: int = 5
    normalization_basis: str = ""
    measurement_mode: str = "measured"  # "measured" | "partial_measured" | "measured_synthetic" | "manual_override" | "not_measured"
    grade: str = "N/A"
    confidence: ConfidenceAssessment = field(default_factory=lambda: ConfidenceAssessment("Low", 0.0))
    weights: Dict[str, float] = field(default_factory=dict)
    weights_provenance: str = "methodology_defaults_v1"  # "methodology_defaults_v1" | "custom_configured"
    layers: Dict[str, LayerResult] = field(default_factory=dict)
    target_entity: str = "Target Entity"
    url: Optional[str] = None
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    limitations: List[str] = field(
        default_factory=lambda: [
            "L1-L4 represent deterministic page-level AI extractability and diagnostic proxies from SAGE.",
            "L4 Citation Survival Proxy (CSP) is a heuristic proxy (E4), not a calibrated empirical probability.",
            "L5 reflects observational visibility only when executed in LIVE mode with sufficient observations.",
            "Synthetic L5 results are simulation-based and non-observational.",
        ]
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mavi_methodology_version": self.mavi_methodology_version,
            "mavi_score": self.mavi_score,
            "raw_measured_score": self.raw_measured_score,
            "max_possible_raw_score": self.max_possible_raw_score,
            "max_score": self.max_score,
            "measured_layers_count": self.measured_layers_count,
            "total_layers_count": self.total_layers_count,
            "normalization_basis": self.normalization_basis,
            "measurement_mode": self.measurement_mode,
            "grade": self.grade,
            "confidence": self.confidence.to_dict(),
            "weights": self.weights,
            "weights_provenance": self.weights_provenance,
            "target_entity": self.target_entity,
            "url": self.url,
            "timestamp_utc": self.timestamp_utc,
            "layers": {k: v.to_dict() for k, v in self.layers.items()},
            "limitations": self.limitations,
        }

