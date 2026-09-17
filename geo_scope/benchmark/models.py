# Benchmark Data Models & Schemas for GEO-Scope v1 (Live & Synthetic)
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


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


class PromptRecord(BaseModel):
    prompt_id: str
    text: str
    intent: Optional[str] = None
    intent_stratum: str = "informational"
    category: Optional[str] = "software"
    language: str = "en"
    difficulty: Optional[str] = "medium"  # "low" | "medium" | "high"
    niche: str = "crm_sales"
    target_brand: str
    competitors: List[str] = Field(default_factory=list)


class ObservationRecord(BaseModel):
    observation_id: str
    prompt_id: str
    provider_id: str
    model: str
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
    research_status: str = "experimental_observation"
    total_prompts: int = 0
    total_observations: int = 0
    successful_observations: int = 0
    failed_observations: int = 0
    brands: List[BrandBenchmarkMetrics] = Field(default_factory=list)
    providers: Dict[str, ProviderBenchmarkMetrics] = Field(default_factory=dict)
    strata: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    top_cited_domains: List[Dict[str, Any]] = Field(default_factory=list)
    factor_analysis: Optional[StatisticalFactorAnalysis] = None
