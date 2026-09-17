# Live Benchmark Execution & Cost Controller for GEO-Scope v1
import asyncio
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

from urllib.parse import urlparse

from geo_scope.benchmark.profile import BenchmarkProfile
from geo_scope.benchmark.models import (
    PromptRecord,
    ObservationRecord,
    CitationEvidenceRecord,
    BenchmarkMetrics,
    BenchmarkManifest,
)
from geo_scope.benchmark.builder import BenchmarkBuilder
from geo_scope.benchmark.hasher import compute_file_sha256
from geo_scope.engine.execution_mode import ExecutionMode
from geo_scope.engine.model_runner import ModelRunner
from geo_scope.engine.persistence import RawRunStore
from geo_scope.engine.query_generator import generate_prompt_dataset
from geo_scope.engine.query_loader import load_custom_prompts
from geo_scope.engine.feature_extractor import (
    parse_model_response,
    extract_citations_and_domains,
)
from geo_scope.providers.models import sanitize_sensitive_data
from geo_scope.providers.registry import registry
from geo_scope.benchmark.validator import ProviderValidator


def estimate_benchmark_cost(profile: BenchmarkProfile) -> Dict[str, Any]:
    """
    Calculates estimated inference cost, total API calls, and budget compliance.
    """
    prompt_count = min(profile.sampling.count, profile.cost_limits.max_prompts)
    provider_count = len(profile.providers)
    total_calls = prompt_count * provider_count

    # Cost table per 1k queries by provider
    cost_per_query = {
        "perplexity_sonar": 0.005,
        "gemini_grounding": 0.003,
        "openai_completion": 0.002,
        "claude_completion": 0.008,
        "ollama_local": 0.0,
        "keyless_wrapper": 0.0,
        "openrouter_free": 0.0,
    }

    total_cost = sum(cost_per_query.get(p, 0.004) * prompt_count for p in profile.providers)

    return {
        "benchmark_version": profile.benchmark_version,
        "dataset_name": profile.dataset_name,
        "execution_mode": profile.execution_mode,
        "prompt_count": prompt_count,
        "provider_count": provider_count,
        "total_inferences": total_calls,
        "estimated_cost_usd": round(total_cost, 4),
        "max_cost_limit_usd": profile.cost_limits.max_cost_usd,
        "within_budget": total_cost <= profile.cost_limits.max_cost_usd,
        "providers": profile.providers,
    }


class LiveBenchmarkRunner:
    """
    Executes live multi-provider benchmarks with cost limits, resume support,
    zero-secret persistence, and deterministic reproduction package building.
    """

    def __init__(self, profile: BenchmarkProfile, out_dir: str = "benchmark"):
        self.profile = profile
        self.out_dir = Path(out_dir)
        self.dataset_id = profile.dataset_name
        self.builder = BenchmarkBuilder(dataset_id=self.dataset_id)

    def run(
        self,
        resume: bool = False,
        dry_run: bool = False,
        validate_providers: bool = True,
        benchmark_mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        cost_est = estimate_benchmark_cost(self.profile)
        if dry_run or self.profile.cost_limits.dry_run:
            print("[Dry-Run] Cost estimation computed. Zero network calls performed.")
            return {
                "dry_run": True,
                "cost_estimate": cost_est,
                "status": "dry_run_completed",
            }

        bmk_mode = (benchmark_mode or getattr(self.profile, "benchmark_mode", "discovery")).lower()

        # 1. Generate / Load Stratified Prompts
        prompts = self._load_or_generate_prompts()
        brands = self._build_brands_list()
        providers_info = self._build_providers_list()

        # 2. Pre-Flight Provider Validation & Provenance Check
        provider_validation_manifest = None
        if self.profile.execution_mode == "live" and validate_providers:
            print(f"\n===========================================================================")
            print(f"Benchmark Mode: {bmk_mode.upper()}")
            print(f"===========================================================================")
            validator = ProviderValidator()
            validation_results = asyncio.run(validator.validate_all(self.profile.providers))

            # Display pre-flight status for each provider
            for p, res in validation_results.items():
                p_label = p.replace("_", " ").title()
                if res.is_valid():
                    print(f"\n{p_label}:\nnative")
                else:
                    if res.fallback_detected:
                        print(f"\n{p_label}:\nfallback -> {res.verified_model or 'surrogate model'}")
                    else:
                        print(f"\n{p_label}:\nfailed ({res.error})")

            print(f"===========================================================================\n")

            if bmk_mode == "strict":
                failed = [p for p, res in validation_results.items() if not res.is_valid()]
                if failed:
                    report_str = validator.format_report(validation_results)
                    print("\n" + report_str + "\n")
                    raise ValueError(
                        f"Strict benchmark integrity violation: Provider(s) {failed} failed native validation "
                        f"(fallback or model mismatch detected). Execution halted in STRICT mode."
                    )
            provider_validation_manifest = {p: res.to_manifest_dict() for p, res in validation_results.items()}

        # 3. Check for Resume State
        completed_keys = set()
        existing_obs = []
        existing_cits = []
        state_file = self.out_dir / f".{self.dataset_id}_partial.jsonl"

        if resume and state_file.exists():
            print(f"🔄 Resuming existing benchmark from '{state_file}'...")
            with open(state_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        rec = json.loads(line)
                        existing_obs.append(rec)
                        completed_keys.add((rec["prompt_id"], rec["provider_id"]))
            print(f"✓ Found {len(completed_keys)} previously completed observation records.")

        # 4. Execute Live Inferences
        mode = ExecutionMode.from_string(self.profile.execution_mode)
        runner = ModelRunner(mode=mode)
        new_obs = []
        new_cits = []
        cit_idx = len(existing_cits) + 1

        print(f"🚀 Starting Live Benchmark execution across {len(self.profile.providers)} providers in {bmk_mode.upper()} mode...")

        # Open partial state writer
        state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(state_file, "a", encoding="utf-8") as state_out:
            for p_idx, prompt in enumerate(prompts):
                pid = prompt["prompt_id"]
                p_text = prompt["text"]

                for prov_id in self.profile.providers:
                    if (pid, prov_id) in completed_keys:
                        continue

                    # Execute single live call
                    t0 = time.time()
                    try:
                        resp_item = asyncio.run(runner.execute_single(
                            query_item={"query": p_text, "intent": prompt.get("intent_stratum", "informational"), "niche": prompt["niche"]},
                            model=prov_id,
                        ))
                        latency_ms = round((time.time() - t0) * 1000, 2)
                        resp_text = resp_item.get("response_text", "")
                        status = "success" if resp_item.get("status") != "failed" else "failed"
                        prov_resp = resp_item.get("provider_response")
                    except Exception as e:
                        latency_ms = round((time.time() - t0) * 1000, 2)
                        resp_text = ""
                        status = "failed"
                        prov_resp = None

                    # Parse response features
                    parsed = parse_model_response(
                        query_item={"query": p_text, "intent": prompt.get("intent_stratum", "informational"), "niche": prompt["niche"]},
                        model_name=prov_id,
                        response_text=resp_text,
                    )

                    # Compute response SHA-256 hash
                    resp_hash = hashlib.sha256(resp_text.encode("utf-8")).hexdigest() if resp_text else None

                    # Sanitize raw evidence
                    raw_data = None
                    if prov_resp and hasattr(prov_resp, "raw"):
                        raw_data = sanitize_sensitive_data(prov_resp.raw)

                    # Extract Provenance Metadata
                    raw_meta = {}
                    if prov_resp:
                        if hasattr(prov_resp, "metadata") and isinstance(prov_resp.metadata, dict):
                            raw_meta.update(prov_resp.metadata.get("meta", {}))
                        if hasattr(prov_resp, "raw") and isinstance(prov_resp.raw, dict):
                            raw_meta.update(prov_resp.raw.get("meta", {}))

                    actual_model = raw_meta.get("actual_model") or (prov_resp.raw.get("model") if prov_resp and hasattr(prov_resp, "raw") and isinstance(prov_resp.raw, dict) else None) or (prov_resp.model if prov_resp else prov_id)
                    actual_provider = (prov_resp.raw.get("provider") if prov_resp and hasattr(prov_resp, "raw") and isinstance(prov_resp.raw, dict) else None) or (prov_resp.provider if prov_resp else prov_id)
                    fallback_active = bool(raw_meta.get("fallback_active", False))

                    from geo_scope.benchmark.validator import models_match
                    if not models_match(prov_id, actual_model):
                        fallback_active = True

                    if status != "success":
                        exec_class = "failed"
                    elif fallback_active:
                        exec_class = "fallback"
                    else:
                        exec_class = "native"

                    # In strict mode, fallback responses are classified as failed
                    if bmk_mode == "strict" and exec_class == "fallback":
                        status = "failed"
                        exec_class = "failed"

                    obs_rec = {
                        "observation_id": f"obs_{len(existing_obs) + len(new_obs) + 1:05d}",
                        "prompt_id": pid,
                        "provider_id": prov_id,
                        "model": prov_id,
                        "requested_provider": prov_id,
                        "requested_model": prov_id,
                        "actual_provider": actual_provider,
                        "actual_model": actual_model,
                        "fallback_active": fallback_active,
                        "execution_class": exec_class,
                        "execution_mode": self.profile.execution_mode,
                        "status": status,
                        "brand_mentioned": parsed.get("target_mentioned", False) if status == "success" else False,
                        "brand_rank": parsed.get("target_rank") if status == "success" else None,
                        "is_top1": parsed.get("target_is_top_1", False) if status == "success" else False,
                        "top1_brand": self.profile.sampling.target_brand if parsed.get("target_is_top_1") else (self.profile.sampling.competitors[0] if self.profile.sampling.competitors else None),
                        "mentioned_brands": parsed.get("mentioned_brands", []),
                        "competitor_ranks": parsed.get("competitor_ranks", {}),
                        "sentiment": parsed.get("sentiment", "neutral"),
                        "latency_ms": latency_ms,
                        "response_hash": resp_hash,
                        "response_snippet": resp_text[:200] if resp_text else None,
                        "raw_evidence": raw_data,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }

                    # Extract genuine citations from provider response and response text (no fabricated URLs)
                    extracted_sources = []
                    # 1. Check provider response citations (e.g. from search grounding)
                    if prov_resp and getattr(prov_resp, "citations", None):
                        for c_item in prov_resp.citations:
                            if isinstance(c_item, str) and c_item.startswith("http"):
                                domain = urlparse(c_item).netloc.lower()
                                if domain.startswith("www."):
                                    domain = domain[4:]
                                extracted_sources.append({"url": c_item, "domain": domain, "method": "grounding_metadata"})
                            elif isinstance(c_item, dict) and c_item.get("url"):
                                url_val = c_item["url"]
                                domain = c_item.get("domain") or urlparse(url_val).netloc.lower()
                                if domain.startswith("www."):
                                    domain = domain[4:]
                                extracted_sources.append({"url": url_val, "domain": domain, "method": "grounding_metadata"})

                    # 2. Check markdown / raw URLs extracted directly from generated text
                    _, text_sources = extract_citations_and_domains(resp_text)
                    for src in text_sources:
                        extracted_sources.append({"url": src["url"], "domain": src["domain"], "method": "text_extracted"})

                    # Deduplicate citations by URL for this observation
                    seen_urls = set()
                    pos = 1
                    for src in extracted_sources:
                        u = src["url"]
                        if u in seen_urls:
                            continue
                        seen_urls.add(u)
                        cit_rec = {
                            "citation_id": f"cit_{cit_idx:05d}",
                            "prompt_id": pid,
                            "provider_id": prov_id,
                            "citation_url": u,
                            "url": u,
                            "domain": src["domain"],
                            "brand": self.profile.sampling.target_brand,
                            "cited_for_brand": self.profile.sampling.target_brand,
                            "position": pos,
                            "rank_position": pos,
                            "extraction_method": src["method"],
                        }
                        new_cits.append(cit_rec)
                        cit_idx += 1
                        pos += 1

                    new_obs.append(obs_rec)
                    state_out.write(json.dumps(obs_rec, ensure_ascii=False) + "\n")
                    state_out.flush()

        all_obs = existing_obs + new_obs
        all_cits = existing_cits + new_cits

        # 4. Build Benchmark Package
        native_cnt = sum(1 for o in all_obs if o.get("execution_class") == "native")
        fallback_cnt = sum(1 for o in all_obs if o.get("execution_class") == "fallback")
        failed_cnt = sum(1 for o in all_obs if o.get("execution_class") == "failed" or o.get("status") != "success")

        provenance_data = {
            "validated": True,
            "fallbacks_recorded": True,
            "benchmark_mode": bmk_mode,
            "native_count": native_cnt,
            "fallback_count": fallback_cnt,
            "failed_count": failed_cnt,
        }

        pkg_path = self.builder.build_package(
            out_dir=self.out_dir,
            prompts=prompts,
            observations=all_obs,
            citations=all_cits,
            brands=brands,
            providers=providers_info,
            execution_mode=self.profile.execution_mode,
            benchmark_mode=bmk_mode,
            research_status=self.profile.research_status,
            description=self.profile.description or f"GEO-Scope Live Benchmark {self.dataset_id}",
            provider_validation=provider_validation_manifest,
            model_provenance=provenance_data,
        )

        # 5. Clean up partial state file
        if state_file.exists():
            try:
                state_file.unlink()
            except OSError:
                pass

        # 6. Generate Markdown Research Report
        report_path = self._generate_research_report(pkg_path, all_obs, all_cits, prompts, brands, bmk_mode)

        return {
            "success": True,
            "dataset_id": self.dataset_id,
            "dataset_path": str(pkg_path),
            "report_path": str(report_path),
            "total_prompts": len(prompts),
            "total_observations": len(all_obs),
            "execution_mode": self.profile.execution_mode,
            "benchmark_mode": bmk_mode,
            "research_status": self.profile.research_status,
            "model_provenance": provenance_data,
        }

    def _load_or_generate_prompts(self) -> List[Dict[str, Any]]:
        if self.profile.sampling.custom_prompts_file and os.path.exists(self.profile.sampling.custom_prompts_file):
            raw = load_custom_prompts(
                file_path=self.profile.sampling.custom_prompts_file,
                default_brand=self.profile.sampling.target_brand,
                default_competitors=self.profile.sampling.competitors,
                default_niche=self.profile.sampling.niche,
            )
        else:
            raw = generate_prompt_dataset(
                niche_key=self.profile.sampling.niche,
                target_brand=self.profile.sampling.target_brand,
                competitors=self.profile.sampling.competitors,
                language=self.profile.sampling.language,
                total_count=min(self.profile.sampling.count, self.profile.cost_limits.max_prompts),
                seed=42,
            )

        prompts = []
        for idx, p in enumerate(raw):
            diff = "medium"
            if idx % 5 == 0:
                diff = "high"
            elif idx % 3 == 0:
                diff = "low"

            prompts.append({
                "prompt_id": p.get("prompt_id") or p.get("id") or f"prompt_{idx+1:04d}",
                "text": p.get("text") or p.get("question") or p.get("query", ""),
                "question": p.get("question") or p.get("text") or p.get("query", ""),
                "source_type": p.get("source_type", "generated"),
                "source_reference": p.get("source_reference", "answerpath"),
                "intent": p.get("intent", "informational"),
                "intent_stratum": p.get("intent_stratum") or p.get("intent", "informational"),
                "category": p.get("category") or (self.profile.sampling.categories[idx % len(self.profile.sampling.categories)] if self.profile.sampling.categories else "software"),
                "language": p.get("language", "en"),
                "difficulty": p.get("difficulty", diff),
                "niche": p.get("niche", self.profile.sampling.niche),
                "target_brand": p.get("target_brand", self.profile.sampling.target_brand),
                "competitors": p.get("competitors", self.profile.sampling.competitors),
                "confidence": p.get("confidence", 1.0),
                "entities": p.get("entities", [self.profile.sampling.target_brand] + self.profile.sampling.competitors),
            })
        return prompts

    def _build_brands_list(self) -> List[Dict[str, Any]]:
        brands = [{"name": self.profile.sampling.target_brand, "is_target": True, "domain": f"{self.profile.sampling.target_brand.lower()}.com"}]
        for comp in self.profile.sampling.competitors:
            brands.append({"name": comp, "is_target": False, "domain": f"{comp.lower().replace(' ', '')}.com"})
        return brands

    def _build_providers_list(self) -> List[Dict[str, Any]]:
        p_list = []
        for pid in self.profile.providers:
            is_grounded = pid in ["perplexity_sonar", "gemini_grounding"]
            p_list.append({
                "id": pid,
                "name": pid.replace("_", " ").title(),
                "search_grounded": is_grounded,
                "model": self.profile.models.get(pid, pid),
            })
        return p_list

    def _generate_research_report(
        self,
        dataset_dir: Path,
        observations: List[Dict[str, Any]],
        citations: List[Dict[str, Any]],
        prompts: List[Dict[str, Any]],
        brands: List[Dict[str, Any]],
        benchmark_mode: str = "discovery",
    ) -> Path:
        reports_dir = Path("reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        report_file = reports_dir / f"{self.dataset_id}-report.md"

        metrics_file = dataset_dir / "metrics.json"
        metrics = json.loads(metrics_file.read_text(encoding="utf-8")) if metrics_file.exists() else {}

        native_obs = [o for o in observations if o.get("execution_class") == "native" and o.get("status") == "success"]
        fallback_obs = [o for o in observations if o.get("execution_class") == "fallback"]
        failed_obs = [o for o in observations if o.get("status") != "success" or o.get("execution_class") == "failed"]

        lines = [
            f"# GEO-Scope Public Research Report: {self.dataset_id}",
            "",
            "## 1. Executive Summary & Epistemic Positioning",
            f"- **Benchmark Version**: `{self.profile.benchmark_version}`",
            f"- **Benchmark Mode**: `{benchmark_mode.upper()}` (Official strict evaluation vs operational discovery)",
            f"- **Execution Mode**: `{self.profile.execution_mode}`",
            f"- **Research Status**: `{self.profile.research_status}`",
            f"- **Dataset Size**: {len(prompts)} prompts | {len(observations)} observations across {len(self.profile.providers)} providers",
            f"- **Execution Provenance**: {len(native_obs)} native observations | {len(fallback_obs)} fallback-routed observations | {len(failed_obs)} failed",
            "- **Core Epistemic Standard**: All reported metrics represent empirical multi-model observations and statistical associations. They do **not** claim to uncover internal proprietary AI ranking algorithms.",
            "",
            "## 2. Execution Provenance & Model Separation",
            "",
            "### A. Native Model Results",
            "Direct model executions verified to match requested upstream architecture:",
            "",
            "| Provider | Requested Model | Verified Actual Model | Observations | Avg Latency (ms) | Status |",
            "|----------|-----------------|-----------------------|--------------|------------------|--------|",
        ]

        # Group observations by provider/model
        native_grouped: Dict[str, List[Dict[str, Any]]] = {}
        for o in native_obs:
            key = (o.get("requested_provider", o.get("provider_id")), o.get("actual_model", o.get("model")))
            native_grouped.setdefault(str(key), []).append(o)

        if not native_grouped:
            lines.append("| None | - | - | 0 | - | No native model executions |")
        else:
            for k_str, obs_list in native_grouped.items():
                first = obs_list[0]
                req_p = first.get("requested_provider", first.get("provider_id"))
                req_m = first.get("requested_model", first.get("model"))
                act_m = first.get("actual_model", first.get("model"))
                lats = [o["latency_ms"] for o in obs_list if o.get("latency_ms") is not None]
                avg_lat = f"{sum(lats)/len(lats):.1f}" if lats else "-"
                lines.append(f"| {req_p} | {req_m} | {act_m} | {len(obs_list)} | {avg_lat} | `PASS (Native)` |")

        lines.extend([
            "",
            "### B. Fallback Routed Results",
            "Requests redirected to fallback or surrogate backends (never merged silently with native metrics):",
            "",
            "| Requested Provider/Model | Actual Routed Backend | Trigger Reason | Observations | Avg Latency (ms) | Status |",
            "|--------------------------|-----------------------|----------------|--------------|------------------|--------|",
        ])

        fallback_grouped: Dict[str, List[Dict[str, Any]]] = {}
        for o in fallback_obs:
            key = (o.get("requested_provider", o.get("provider_id")), o.get("actual_model", o.get("model")))
            fallback_grouped.setdefault(str(key), []).append(o)

        if not fallback_grouped:
            lines.append("| None | - | - | 0 | - | Zero fallback routing detected |")
        else:
            for k_str, obs_list in fallback_grouped.items():
                first = obs_list[0]
                req = f"{first.get('requested_provider', first.get('provider_id'))} ({first.get('requested_model', first.get('model'))})"
                act = f"{first.get('actual_provider', 'gateway')} ({first.get('actual_model', 'unknown')})"
                lats = [o["latency_ms"] for o in obs_list if o.get("latency_ms") is not None]
                avg_lat = f"{sum(lats)/len(lats):.1f}" if lats else "-"
                lines.append(f"| {req} | {act} | Upstream inactive / surrogate | {len(obs_list)} | {avg_lat} | `FALLBACK_RECORDED` |")

        lines.extend([
            "",
            "## 3. Question Provenance & Demand Stratification",
            "",
            "### A. Observed Question Results (Real User Demand)",
            "Measurements derived strictly from real recorded user queries and customer logs:",
            "",
            "| Brand | Observed Mention Rate | Observed Top-1 Rate | Sample Size | Demand Confidence |",
            "|-------|-----------------------|---------------------|-------------|-------------------|",
        ])

        obs_vis = metrics.get("observed_visibility", {})
        obs_brands = obs_vis.get("brands", {})
        obs_n = obs_vis.get("sample_size", 0)
        if not obs_brands or obs_n == 0:
            lines.append("| None | - | - | 0 | No observed questions in run |")
        else:
            for b_name, b_data in obs_brands.items():
                m_pct = f"{b_data.get('mention_rate', 0):.1f}%" if b_data.get('mention_rate') is not None else "N/A"
                t_pct = f"{b_data.get('top1_rate', 0):.1f}%" if b_data.get('top1_rate') is not None else "N/A"
                lines.append(f"| {b_name} | {m_pct} | {t_pct} | {obs_n} | High (`observed`) |")

        lines.extend([
            "",
            "### B. Generated Research Prompt Results (Exploration Templates)",
            "Measurements derived from structured exploration prompt templates (never conflated with real user demand):",
            "",
            "| Brand | Template Mention Rate | Template Top-1 Rate | Sample Size | Category |",
            "|-------|-----------------------|---------------------|-------------|----------|",
        ])

        gen_vis = metrics.get("generated_visibility", {})
        gen_brands = gen_vis.get("brands", {})
        gen_n = gen_vis.get("sample_size", 0)
        if not gen_brands or gen_n == 0:
            lines.append("| None | - | - | 0 | Zero generated templates |")
        else:
            for b_name, b_data in gen_brands.items():
                m_pct = f"{b_data.get('mention_rate', 0):.1f}%" if b_data.get('mention_rate') is not None else "N/A"
                t_pct = f"{b_data.get('top1_rate', 0):.1f}%" if b_data.get('top1_rate') is not None else "N/A"
                lines.append(f"| {b_name} | {m_pct} | {t_pct} | {gen_n} | Research Template (`generated`) |")

        lines.extend([
            "",
            "### C. Combined Operational Visibility",
            "Blended operational index across all valid evaluation queries:",
            "",
            "| Metric Dimension | Total Prompts | Observed Prompts | Generated Prompts | Source Reference |",
            "|------------------|---------------|------------------|-------------------|------------------|",
        ])

        q_prov = metrics.get("question_provenance", {})
        tot_p = metrics.get("total_prompts", len(prompts))
        obs_p = q_prov.get("observed_count", 0)
        gen_p = q_prov.get("generated_count", tot_p - obs_p)
        ref_s = q_prov.get("source_reference", "answerpath")
        lines.append(f"| Question Pool | {tot_p} | {obs_p} | {gen_p} | `{ref_s}` |")

        lines.extend([
            "",
            "## 4. Brand Visibility Performance (95% Bootstrap CIs)",
            "",
            "| Brand | Target | Share of Model | Mention Rate (95% CI) | Top-1 Rate (95% CI) | Avg Rank |",
            "|-------|--------|----------------|-----------------------|---------------------|----------|",
        ])

        for b in metrics.get("brands", []):
            m = b.get("mention_rate", {})
            t = b.get("top1_rate", {})
            som = b.get("share_of_model", {})
            m_str = f"{m['value']:.1f}% [{m.get('ci_lower', 0):.1f}%, {m.get('ci_upper', 0):.1f}%]" if m.get("value") is not None else "N/A"
            t_str = f"{t['value']:.1f}% [{t.get('ci_lower', 0):.1f}%, {t.get('ci_upper', 0):.1f}%]" if t.get("value") is not None else "N/A"
            som_str = f"{som['value']:.1f}%" if som.get("value") is not None else "N/A"
            ar_str = f"#{b['avg_rank']:.1f}" if b.get("avg_rank") is not None else "-"
            tgt = "★ Yes" if b.get("is_target") else "No"
            lines.append(f"| {b['brand']} | {tgt} | {som_str} | {m_str} | {t_str} | {ar_str} |")

        lines.extend([
            "",
            "## 4. Multi-Model Provider Analysis",
            "",
            "| Provider | Success Obs | Failed Obs | Target Mention Rate | Target Top-1 Rate | Avg Latency (ms) |",
            "|----------|-------------|------------|---------------------|-------------------|------------------|",
        ])

        for pid, pdata in metrics.get("providers", {}).items():
            tm = pdata.get("target_mention_rate", {})
            tt = pdata.get("target_top1_rate", {})
            tm_str = f"{tm['value']:.1f}% [{tm.get('ci_lower', 0):.1f}%, {tm.get('ci_upper', 0):.1f}%]" if tm.get("value") is not None else "N/A"
            tt_str = f"{tt['value']:.1f}% [{tt.get('ci_lower', 0):.1f}%, {tt.get('ci_upper', 0):.1f}%]" if tt.get("value") is not None else "N/A"
            lat_str = f"{pdata.get('mean_latency_ms', 0):.1f}" if pdata.get("mean_latency_ms") is not None else "-"
            lines.append(f"| {pid} | {pdata.get('successful_observations', 0)} | {pdata.get('failed_observations', 0)} | {tm_str} | {tt_str} | {lat_str} |")

        lines.extend([
            "",
            "## 5. Empirical Factor Associations (Prior vs. Observed)",
            "",
            "| Factor | Prior Weight | Observed Effect | 95% Confidence Interval | Status |",
            "|--------|--------------|-----------------|-------------------------|--------|",
        ])

        if metrics.get("factor_analysis"):
            for f in metrics["factor_analysis"].get("factors", []):
                ci = f.get("confidence_interval", [None, None])
                ci_str = f"[{ci[0]:.2f}, {ci[1]:.2f}]" if ci[0] is not None else "-"
                lines.append(f"| {f.get('factor_name', f.get('factor'))} | {f.get('prior_weight', 0):.2f} | {f.get('observed_effect', 0):.2f} | {ci_str} | `{f.get('status', 'observed_association')}` |")

        lines.extend([
            "",
            "## 6. Methodological Limitations & Research Transparency",
            "1. **Dynamic Routing & Fallbacks**: Programmatic gateways dynamically route models and may activate fallback surrogate models when specific upstream endpoints are offline. GEO-Scope captures explicit execution provenance to distinguish native vs fallback observations.",
            "2. **Requested vs Observed Identity**: Requested models represent experimental targets; observed models reflect the actual upstream generating backend. Official benchmarks evaluate native executions strictly.",
            "3. **Temporal Volatility**: Search grounding indexes and LLM model checkpoints update continuously; results represent observations strictly at the recorded timestamps.",
            "",
            "## 7. Reproduction Protocol",
            "```bash",
            f"geo-scope benchmark verify --dataset benchmark/{self.dataset_id}",
            f"geo-scope benchmark reproduce --dataset benchmark/{self.dataset_id}",
            "```",
        ])

        report_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return report_file
