from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class BenchmarkExecutionMode(str, Enum):
    STRICT = "strict"
    DISCOVERY = "discovery"


class MetricEstimate(BaseModel):
    value: Optional[float] = None
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None
    confidence_level: float = 0.95
    sample_size: int = 0
    status: str = "ok"  # "ok" | "insufficient_data"


class BenchmarkManifest(BaseModel):
    version: str = "2026.1"
    benchmark_version: str = "2026.1-live"
    dataset_id: str
    dataset_name: Optional[str] = None
    created_at: str
    execution_mode: str = "live"  # "live" | "synthetic"
    benchmark_mode: str = "discovery"  # "strict" | "discovery"
    research_status: str = "experimental_observation"  # "experimental_observation" | "peer_review_ready" | "demo_only"
    description: str
    git_commit: Optional[str] = None
    parser_version: str = "1.0.0"
    providers: List[str] = Field(default_factory=list)
    models: List[str] = Field(default_factory=list)
    experiment_ids: List[str] = Field(default_factory=list)
    dataset_hash: Optional[str] = None
    counts: Dict[str, int] = Field(default_factory=dict)
    file_hashes: Dict[str, str] = Field(default_factory=dict)
    composite_dataset_hash: Optional[str] = None
    provider_validation: Optional[Dict[str, Any]] = None
    model_provenance: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {
            "validated": True,
            "fallbacks_recorded": True,
        }
    )
    question_provenance: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {
            "observed_count": 0,
            "generated_count": 0,
            "source_reference": "answerpath",
        }
    )


class PromptRecord(BaseModel):
    prompt_id: str
    text: str = ""
    question: Optional[str] = None
    source_type: str = "generated"  # "observed" | "generated"
    source_reference: str = "answerpath"  # "answerpath" | "user" | "search_console" | "custom"
    intent: Optional[str] = None
    intent_stratum: str = "informational"
    category: Optional[str] = "software"
    entities: List[str] = Field(default_factory=list)
    confidence: float = 1.0
    language: str = "en"
    difficulty: Optional[str] = "medium"  # "low" | "medium" | "high"
    niche: str = "crm_sales"
    target_brand: str = ""
    competitors: List[str] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        if not self.text and self.question:
            self.text = self.question
        elif not self.question and self.text:
            self.question = self.text
        if not self.entities and self.target_brand:
            self.entities = [self.target_brand] + [c for c in self.competitors if c != self.target_brand]


class ObservationRecord(BaseModel):
    observation_id: str
    prompt_id: str
    provider_id: str
    model: str
    requested_provider: Optional[str] = None
    requested_model: Optional[str] = None
    actual_provider: Optional[str] = None
    actual_model: Optional[str] = None
    fallback_active: bool = False
    execution_class: str = "native"  # "native" | "fallback" | "failed"
    execution_mode: str = "live"  # "live" | "synthetic"
    status: str = "success"  # "success" | "failed"
    brand_mentioned: bool = False
    brand_rank: Optional[int] = None
    is_top1: bool = False
    top1_brand: Optional[str] = None
    mentioned_brands: List[str] = Field(default_factory=list)
    competitor_ranks: Dict[str, int] = Field(default_factory=dict)
    sentiment: Optional[str] = "neutral"
    latency_ms: Optional[float] = None
    response_hash: Optional[str] = None
    response_snippet: Optional[str] = None
    raw_evidence: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    timestamp: str


class CitationEvidenceRecord(BaseModel):
    citation_id: str
    prompt_id: str
    provider_id: str
    citation_url: Optional[str] = None
    url: str
    domain: str
    brand: Optional[str] = None
    cited_for_brand: Optional[str] = None
    position: Optional[int] = None
    rank_position: Optional[int] = None
    extraction_method: str = "native_citations"  # "grounding_metadata" | "native_citations" | "parsed_anchor"


class BrandBenchmarkMetrics(BaseModel):
    brand: str
    is_target: bool = False
    mention_rate: MetricEstimate
    top1_rate: MetricEstimate
    citation_rate: MetricEstimate
    share_of_model: MetricEstimate
    avg_rank: Optional[float] = None


class ProviderBenchmarkMetrics(BaseModel):
    provider_id: str
    successful_observations: int = 0
    failed_observations: int = 0
    target_mention_rate: MetricEstimate
    target_top1_rate: MetricEstimate
    mean_latency_ms: Optional[float] = None


class FactorEffectEstimate(BaseModel):
    factor: str
    prior_weight: float
    observed_effect: Optional[float] = None
    confidence_interval: List[Optional[float]] = Field(default_factory=list)
    sample_size: int = 0
    status: str = "observed_association"


class StatisticalFactorAnalysis(BaseModel):
    status: str = "observed_association_only"
    disclaimer: str = (
        "Prior weights represent initial research hypotheses. "
        "Observed effects reflect empirical multi-model correlations and effect sizes. "
        "They do NOT establish causal AI ranking algorithms."
    )
    factors: List[Dict[str, Any]] = Field(default_factory=list)


class BenchmarkMetrics(BaseModel):
    dataset_id: str
    computed_at: str
    execution_mode: str = "live"
    benchmark_mode: str = "discovery"
    research_status: str = "experimental_observation"
    total_prompts: int = 0
    total_observations: int = 0
    successful_observations: int = 0
    failed_observations: int = 0
    brands: List[BrandBenchmarkMetrics] = Field(default_factory=list)
    providers: Dict[str, ProviderBenchmarkMetrics] = Field(default_factory=dict)
    native_visibility: Optional[Dict[str, Any]] = None
    fallback_visibility: Optional[Dict[str, Any]] = None
    total_observed_visibility: Optional[Dict[str, Any]] = None
    observed_visibility: Optional[Dict[str, Any]] = None
    generated_visibility: Optional[Dict[str, Any]] = None
    combined_operational_visibility: Optional[Dict[str, Any]] = None
    question_provenance: Optional[Dict[str, Any]] = None
    execution_class_breakdown: Dict[str, int] = Field(default_factory=dict)
    strata: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    top_cited_domains: List[Dict[str, Any]] = Field(default_factory=list)
    category_visibility_matrix: Dict[str, Dict[str, Optional[float]]] = Field(default_factory=dict)
    factor_analysis: Optional[StatisticalFactorAnalysis] = None
