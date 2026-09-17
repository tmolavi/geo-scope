# Benchmark Data Models & Schemas for GEO-Scope v1
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
    dataset_id: str
    created_at: str
    execution_mode: str = "synthetic"  # "live" | "synthetic"
    research_status: str = "demo_only"  # "peer_review_ready" | "demo_only"
    description: str
    git_commit: Optional[str] = None
    parser_version: str = "1.0.0"
    counts: Dict[str, int] = Field(default_factory=dict)
    file_hashes: Dict[str, str] = Field(default_factory=dict)
    composite_dataset_hash: Optional[str] = None


class PromptRecord(BaseModel):
    prompt_id: str
    text: str
    intent_stratum: str
    language: str = "en"
    niche: str = "crm_sales"
    target_brand: str
    competitors: List[str] = Field(default_factory=list)


class ObservationRecord(BaseModel):
    observation_id: str
    prompt_id: str
    provider_id: str
    model: str
    execution_mode: str = "synthetic"  # "live" | "synthetic"
    status: str = "success"  # "success" | "failed"
    brand_mentioned: bool = False
    brand_rank: Optional[int] = None
    is_top1: bool = False
    sentiment: Optional[str] = "neutral"
    latency_ms: Optional[float] = None
    response_snippet: Optional[str] = None
    timestamp: str


class CitationEvidenceRecord(BaseModel):
    citation_id: str
    prompt_id: str
    provider_id: str
    domain: str
    url: str
    rank_position: Optional[int] = None
    cited_for_brand: Optional[str] = None


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


class StatisticalFactorAnalysis(BaseModel):
    status: str = "observed_association_only"
    disclaimer: str = (
        "Correlations and effect sizes represent empirical statistical associations "
        "in observed multi-model outputs. They do NOT establish causal AI ranking algorithms."
    )
    factors: List[Dict[str, Any]] = Field(default_factory=list)


class BenchmarkMetrics(BaseModel):
    dataset_id: str
    computed_at: str
    execution_mode: str = "synthetic"
    research_status: str = "demo_only"
    total_prompts: int = 0
    total_observations: int = 0
    successful_observations: int = 0
    failed_observations: int = 0
    brands: List[BrandBenchmarkMetrics] = Field(default_factory=list)
    providers: Dict[str, ProviderBenchmarkMetrics] = Field(default_factory=dict)
    strata: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    top_cited_domains: List[Dict[str, Any]] = Field(default_factory=list)
    factor_analysis: Optional[StatisticalFactorAnalysis] = None
