# Benchmark Profile loader and validator for GEO-Scope v1
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


class SamplingConfig(BaseModel):
    niche: str = "crm_sales"
    entities: List[str] = Field(default_factory=list)
    target_brand: Optional[str] = None
    competitors: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=lambda: ["crm", "sales_automation", "pipeline_management"])
    count: int = 30
    language: str = "both"
    difficulty_mix: Dict[str, float] = Field(default_factory=lambda: {"low": 0.2, "medium": 0.6, "high": 0.2})
    custom_prompts_file: Optional[str] = None

    def get_entities(self) -> List[str]:
        if self.entities:
            return list(self.entities)
        ents = []
        if self.target_brand:
            ents.append(self.target_brand)
        for c in self.competitors:
            if c not in ents:
                ents.append(c)
        return ents or ["Brand"]


class CostLimits(BaseModel):
    max_prompts: int = 100
    max_cost_usd: float = 10.0
    dry_run: bool = False


class BenchmarkProfile(BaseModel):
    benchmark_version: str = "2026.1-live"
    dataset_name: str = "geo-scope-live-2026.1"
    execution_mode: str = "live"  # "live" | "synthetic"
    research_status: str = "experimental_observation"  # "experimental_observation" | "demo_only"
    providers: List[str] = Field(default_factory=lambda: ["perplexity_sonar", "gemini_grounding", "openai_completion", "claude_completion"])
    models: Dict[str, str] = Field(default_factory=dict)
    sampling: SamplingConfig = Field(default_factory=SamplingConfig)
    cost_limits: CostLimits = Field(default_factory=CostLimits)
    methodology_version: str = "1.0.0"
    description: Optional[str] = None

    @classmethod
    def from_file(cls, filepath: str | Path) -> "BenchmarkProfile":
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Benchmark profile not found: {path}")

        raw_text = path.read_text(encoding="utf-8")
        if path.suffix.lower() in [".yaml", ".yml"]:
            if HAS_YAML:
                data = yaml.safe_load(raw_text)
            else:
                # Basic line parser fallback
                data = json.loads(raw_text) if raw_text.strip().startswith("{") else {}
        else:
            data = json.loads(raw_text)

        # Enforce mode rules
        mode = data.get("execution_mode", "live").lower()
        if mode == "synthetic":
            data["research_status"] = "demo_only"
        elif mode == "live" and data.get("research_status") == "demo_only":
            data["research_status"] = "experimental_observation"

        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
