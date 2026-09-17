"""Data models for AnswerPath GEO question discovery, clustering, and provenance."""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class DiscoveredQuestion:
    prompt_id: str
    question: str
    source: str
    source_type: str  # "observed" | "generated"
    source_reference: str = "answerpath"
    intent: str = "discover"
    stage: str = "awareness"
    category: str = "GEO"
    entities: List[str] = field(default_factory=list)
    confidence: float = 1.0
    frequency: int = 1
    cluster: int = -1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt_id": self.prompt_id,
            "question": self.question,
            "text": self.question,
            "source": self.source,
            "source_type": self.source_type,
            "source_reference": self.source_reference,
            "intent": self.intent,
            "stage": self.stage,
            "category": self.category,
            "entities": self.entities,
            "confidence": self.confidence,
            "frequency": self.frequency,
            "cluster": self.cluster,
        }

    def to_prompt_record_dict(
        self,
        target_brand: str = "",
        competitors: Optional[List[str]] = None,
        language: str = "en",
        niche: str = "GEO",
    ) -> Dict[str, Any]:
        all_comps = competitors or []
        all_entities = list(dict.fromkeys(self.entities + ([target_brand] if target_brand else []) + all_comps))
        return {
            "prompt_id": self.prompt_id,
            "text": self.question,
            "question": self.question,
            "source_type": self.source_type,
            "source_reference": self.source_reference,
            "intent": self.intent,
            "intent_stratum": self._map_to_stratum(self.intent),
            "category": self.category or niche,
            "entities": all_entities,
            "confidence": self.confidence,
            "language": language,
            "difficulty": "medium",
            "niche": niche,
            "target_brand": target_brand,
            "competitors": all_comps,
        }

    @staticmethod
    def _map_to_stratum(intent: str) -> str:
        mapping = {
            "buy": "commercial_direct",
            "compare": "comparative",
            "trust": "reputation_reviews",
            "solve": "problem_solving",
            "learn": "informational",
            "discover": "informational",
        }
        return mapping.get(intent.lower(), "informational")


@dataclass
class QuestionCluster:
    cluster_id: int
    representative_question: str
    size: int
    intent: str
    source_types: List[str]
    questions: List[DiscoveredQuestion] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cluster_id": self.cluster_id,
            "representative_question": self.representative_question,
            "size": self.size,
            "intent": self.intent,
            "source_types": self.source_types,
            "questions": [q.to_dict() for q in self.questions],
        }


@dataclass
class DiscoveryResult:
    topic: str
    total_discovered: int
    observed_count: int
    generated_count: int
    clusters_count: int
    intent_distribution: Dict[str, int]
    questions: List[DiscoveredQuestion] = field(default_factory=list)
    clusters: List[QuestionCluster] = field(default_factory=list)
    recommended_prompts: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "total_discovered": self.total_discovered,
            "observed_count": self.observed_count,
            "generated_count": self.generated_count,
            "clusters_count": self.clusters_count,
            "intent_distribution": self.intent_distribution,
            "questions": [q.to_dict() for q in self.questions],
            "clusters": [c.to_dict() for c in self.clusters],
            "recommended_prompts": self.recommended_prompts,
        }
