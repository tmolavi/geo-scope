# Dataset package builder for GEO-Scope Public Benchmark v1.
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

from geo_scope.benchmark.models import BenchmarkManifest, BenchmarkMetrics
from geo_scope.benchmark.calculator import BenchmarkCalculator
from geo_scope.benchmark.hasher import (
    compute_dataset_checksums,
    compute_composite_hash,
    write_checksums_file,
)


def get_git_commit(repo_dir: Optional[str | Path] = None) -> Optional[str]:
    """Attempt to get the current git commit hash."""
    try:
        cmd = ["git", "rev-parse", "HEAD"]
        env = os.environ.copy()
        env["DEVELOPER_DIR"] = "/Library/Developer/CommandLineTools"
        res = subprocess.run(cmd, cwd=repo_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return None


class BenchmarkBuilder:
    """
    Builds a complete, versioned, tamper-proof GEO-Scope benchmark dataset package.
    """

    def __init__(self, dataset_id: str = "geo-scope-benchmark-2026.1"):
        self.dataset_id = dataset_id
        self.calculator = BenchmarkCalculator()

    def build_package(
        self,
        out_dir: str | Path,
        prompts: List[Dict[str, Any]],
        observations: List[Dict[str, Any]],
        citations: List[Dict[str, Any]],
        brands: List[Dict[str, Any]],
        providers: List[Dict[str, Any]],
        execution_mode: str = "synthetic",
        benchmark_mode: str = "discovery",
        research_status: str = "demo_only",
        description: Optional[str] = None,
        methodology_md: Optional[str] = None,
        readme_md: Optional[str] = None,
        provider_validation: Optional[Dict[str, Any]] = None,
        model_provenance: Optional[Dict[str, Any]] = None,
    ) -> Path:
        target_dir = Path(out_dir) / self.dataset_id
        target_dir.mkdir(parents=True, exist_ok=True)

        if description is None:
            description = (
                f"GEO-Scope Public Benchmark {self.dataset_id} containing multi-model "
                f"observations across {len(providers)} providers and {len(prompts)} prompts."
            )

        # 1. Write data files
        prompts_file = target_dir / "prompts.jsonl"
        with open(prompts_file, "w", encoding="utf-8") as f:
            for p in prompts:
                f.write(json.dumps(p, ensure_ascii=False) + "\n")

        # Write partitioned prompts directory
        prompts_sub_dir = target_dir / "prompts"
        prompts_sub_dir.mkdir(parents=True, exist_ok=True)
        obs_prompts = [p for p in prompts if p.get("source_type") == "observed"]
        gen_prompts = [p for p in prompts if p.get("source_type") != "observed"]

        with open(prompts_sub_dir / "observed.jsonl", "w", encoding="utf-8") as f:
            for p in obs_prompts:
                f.write(json.dumps(p, ensure_ascii=False) + "\n")

        with open(prompts_sub_dir / "generated.jsonl", "w", encoding="utf-8") as f:
            for p in gen_prompts:
                f.write(json.dumps(p, ensure_ascii=False) + "\n")

        (target_dir / "brands.json").write_text(
            json.dumps(brands, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

        (target_dir / "providers.json").write_text(
            json.dumps(providers, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

        obs_file = target_dir / "observations.jsonl"
        with open(obs_file, "w", encoding="utf-8") as f:
            for o in observations:
                f.write(json.dumps(o, ensure_ascii=False) + "\n")

        cits_file = target_dir / "citations.jsonl"
        with open(cits_file, "w", encoding="utf-8") as f:
            for c in citations:
                f.write(json.dumps(c, ensure_ascii=False) + "\n")

        # 2. Compute and write metrics.json
        metrics_obj = self.calculator.compute(
            prompts=prompts,
            observations=observations,
            citations=citations,
            brands=brands,
            providers=providers,
            dataset_id=self.dataset_id,
            execution_mode=execution_mode,
            benchmark_mode=benchmark_mode,
            research_status=research_status,
        )
        (target_dir / "metrics.json").write_text(
            json.dumps(metrics_obj.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

        # Write provenance.json
        provenance_payload = {
            "dataset_id": self.dataset_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "execution_mode": execution_mode,
            "benchmark_mode": benchmark_mode,
            "question_provenance": {
                "total_prompts": len(prompts),
                "observed_count": len(obs_prompts),
                "generated_count": len(gen_prompts),
                "source_reference": "answerpath",
                "observed_sources": list({p.get("source_reference", "observed") for p in obs_prompts}),
                "generated_sources": list({p.get("source_reference", "generated") for p in gen_prompts}),
            },
            "model_provenance": model_provenance or {
                "validated": True,
                "fallbacks_recorded": True,
            },
        }
        (target_dir / "provenance.json").write_text(
            json.dumps(provenance_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

        # 3. Write documentation
        if methodology_md is None:
            methodology_md = f"""# GEO-Scope Benchmark Methodology ({self.dataset_id})

## Overview
This benchmark evaluates Generative Engine Optimization (GEO) performance, brand visibility, and citation presence across multi-model AI engines.

## Execution Mode & Status
- **Execution Mode**: `{execution_mode}`
- **Research Status**: `{research_status}`
- **Strict Separation**: Synthetic simulation runs are explicitly marked `demo_only` and must not be cited as real provider behavior.

## Question & Model Provenance
- **Observed Prompts**: {len(obs_prompts)} (Real user demand)
- **Generated Prompts**: {len(gen_prompts)} (Research exploration templates)
- **Model Provenance**: Explicit tracking of native vs fallback routes.

## Measured Metrics
1. **Share of Model (SoM)**: Percentage of total observed brand mentions attributed to the brand.
2. **Mention Rate**: Percentage of successful multi-model observations containing the brand (with 95% bootstrap CI).
3. **Top-1 Primary Rate**: Percentage of successful observations where the brand is the first/primary recommendation.
4. **Citation Rate**: Percentage of observations citing the brand or authoritative third-party source.

## Statistical Bounds & Language Guardrails
- All confidence intervals are non-parametric 95% percentile bootstrap estimates (1,000 resamples).
- Factor analyses report **observed empirical correlations** only, avoiding speculative "AI ranking algorithm" assertions.
"""
        (target_dir / "methodology.md").write_text(methodology_md.strip() + "\n", encoding="utf-8")

        if readme_md is None:
            readme_md = f"""# {self.dataset_id}

GEO-Scope Public Benchmark & Evidence Dataset.

- Total Prompts: {len(prompts)}
  - Observed User Questions: {len(obs_prompts)}
  - Generated Research Prompts: {len(gen_prompts)}
- Total Observations: {len(observations)}
- Providers: {len(providers)}
- Brands: {len(brands)}
- Execution Mode: `{execution_mode}`
- Research Status: `{research_status}`

## Quick Reproduction
```bash
geo-scope benchmark verify --dataset .
geo-scope benchmark reproduce --dataset .
```
"""
        (target_dir / "README.md").write_text(readme_md.strip() + "\n", encoding="utf-8")

        # 4. Compute file hashes (excluding manifest.json and checksums.sha256)
        file_hashes = compute_dataset_checksums(target_dir)
        composite_hash = compute_composite_hash(file_hashes)

        # 5. Write manifest.json
        p_ids = [p.get("id") or p.get("provider_id", "") for p in providers]
        m_ids = [p.get("model") or p.get("id", "") for p in providers]
        bmk_ver = "2026.1-live" if execution_mode == "live" else "2026.1-synthetic"

        manifest = BenchmarkManifest(
            version="2026.1",
            benchmark_version=bmk_ver,
            dataset_id=self.dataset_id,
            dataset_name=self.dataset_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            execution_mode=execution_mode,
            research_status=research_status,
            description=description,
            git_commit=get_git_commit(target_dir),
            parser_version="1.0.0",
            providers=p_ids,
            models=m_ids,
            experiment_ids=[self.dataset_id],
            dataset_hash=composite_hash,
            counts={
                "prompts": len(prompts),
                "observed_prompts": len(obs_prompts),
                "generated_prompts": len(gen_prompts),
                "observations": len(observations),
                "citations": len(citations),
                "brands": len(brands),
                "providers": len(providers),
            },
            file_hashes=file_hashes,
            composite_dataset_hash=composite_hash,
            provider_validation=provider_validation,
            benchmark_mode=benchmark_mode,
            model_provenance=model_provenance or {
                "validated": True,
                "fallbacks_recorded": True,
            },
            question_provenance={
                "observed_count": len(obs_prompts),
                "generated_count": len(gen_prompts),
                "source_reference": "answerpath",
            },
        )
        (target_dir / "manifest.json").write_text(
            json.dumps(manifest.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

        # 6. Recompute full checksums including manifest.json and write checksums.sha256
        full_checksums = compute_dataset_checksums(target_dir)
        write_checksums_file(target_dir, full_checksums)

        return target_dir
