"""
MAVI Engine Data Models, Weights Configuration, and Provenance Schemas.
Molavi AI Visibility Index (MAVI) v1.0
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


@dataclass
class LayerProvenance:
    source: str  # "sage" | "geo-scope" | "manual"
    metric_version: str = "1.0.0"
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    evidence_count: int = 0
    experiment_id: Optional[str] = None
    url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LayerResult:
    layer_id: str  # "L1", "L2", "L3", "L4", "L5"
    layer_name: str
    weight: float
    score: Optional[float]  # 0.0 - 100.0 or None if not_measured
    status: str  # "measured" | "not_measured" | "manual_override"
    provenance: LayerProvenance
    details: Dict[str, Any] = field(default_factory=dict)
    findings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LayerWeights:
    """
    Default methodology weights for MAVI v1.
    Labeled as methodology defaults (not claimed to be empirically fitted).
    """
    l1_technical_accessibility: float = 0.15
    l2_semantic_extractability: float = 0.20
    l3_entity_clarity: float = 0.20
    l4_citation_readiness: float = 0.20
    l5_observed_ai_visibility: float = 0.25

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
    mavi_score: Optional[float]  # Normalized score (0-100) or None
    raw_measured_score: Optional[float]
    max_possible_raw_score: float
    measured_layers_count: int
    total_layers_count: int
    normalization_basis: str
    measurement_mode: str  # "measured" | "partial_measured" | "manual_override"
    grade: str
    confidence: ConfidenceAssessment
    weights: Dict[str, float]
    weights_provenance: str  # "methodology_defaults_v1" | "custom_configured"
    layers: Dict[str, LayerResult]
    target_entity: str
    url: Optional[str]
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mavi_score": self.mavi_score,
            "raw_measured_score": self.raw_measured_score,
            "max_possible_raw_score": self.max_possible_raw_score,
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
        }
