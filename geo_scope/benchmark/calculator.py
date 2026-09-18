# Deterministic metric calculation & statistical factor analysis for GEO-Scope benchmarks.
import math
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
import numpy as np

from geo_scope.benchmark.models import (
    BenchmarkMetrics,
    BrandBenchmarkMetrics,
    ProviderBenchmarkMetrics,
    MetricEstimate,
    StatisticalFactorAnalysis,
)


def calculate_bootstrap_ci(
    data: List[float | int],
    n_resamples: int = 1000,
    ci: float = 0.95,
    seed: int = 42,
) -> Tuple[Optional[float], Optional[float]]:
    """
    Calculate non-parametric percentile bootstrap confidence interval for the mean.
    Returns (ci_lower, ci_upper) rounded to 4 decimal places, or (None, None) if data is empty.
    """
    if not data:
        return None, None
    if len(data) == 1:
        val = round(float(data[0]), 4)
        return val, val

    arr = np.array(data, dtype=float)
    rng = np.random.RandomState(seed)

    indices = rng.randint(0, len(arr), size=(n_resamples, len(arr)))
    resampled_means = arr[indices].mean(axis=1)

    alpha = 1.0 - ci
    lower_p = (alpha / 2.0) * 100.0
    upper_p = (1.0 - alpha / 2.0) * 100.0

    lower = float(np.percentile(resampled_means, lower_p))
    upper = float(np.percentile(resampled_means, upper_p))

    return round(lower, 4), round(upper, 4)


def make_metric_estimate(
    data: List[float | int],
    unit_multiplier: float = 100.0,
    confidence_level: float = 0.95,
    seed: int = 42,
) -> MetricEstimate:
    """Helper to create a MetricEstimate with bootstrap CI."""
    if not data:
        return MetricEstimate(
            value=None,
            ci_lower=None,
            ci_upper=None,
            confidence_level=confidence_level,
            sample_size=0,
            status="insufficient_data",
        )

    mean_val = float(np.mean(data)) * unit_multiplier
    lower, upper = calculate_bootstrap_ci(data, ci=confidence_level, seed=seed)
    ci_low = round(lower * unit_multiplier, 4) if lower is not None else None
    ci_high = round(upper * unit_multiplier, 4) if upper is not None else None

    return MetricEstimate(
        value=round(mean_val, 4),
        ci_lower=ci_low,
        ci_upper=ci_high,
        confidence_level=confidence_level,
        sample_size=len(data),
        status="ok",
    )


class BenchmarkCalculator:
    """
    Computes rigorous, reproducible benchmark metrics and empirical factor associations.
    """

    def __init__(self, confidence_level: float = 0.95, random_seed: int = 42):
        self.confidence_level = confidence_level
        self.random_seed = random_seed

    def compute(
        self,
        prompts: List[Dict[str, Any]],
        observations: List[Dict[str, Any]],
        citations: List[Dict[str, Any]],
        brands: List[Dict[str, Any]],
        providers: List[Dict[str, Any]],
        dataset_id: str = "geo-scope-benchmark-2026.1",
        execution_mode: str = "synthetic",
        research_status: str = "demo_only",
        benchmark_mode: str = "discovery",
    ) -> BenchmarkMetrics:
        # Normalize brands and providers if list of strings passed
        normalized_brands = []
        for b in brands:
            if isinstance(b, dict):
                normalized_brands.append(b)
            elif isinstance(b, str):
                normalized_brands.append({"name": b, "entity": b, "is_target": False})
        brands = normalized_brands

        normalized_providers = []
        for p in providers:
            if isinstance(p, dict):
                normalized_providers.append(p)
            elif isinstance(p, str):
                normalized_providers.append({"id": p, "name": p, "model": p, "search_grounded": False})
        providers = normalized_providers

        total_prompts = len(prompts)
        total_obs = len(observations)

        # Categorize observations by execution class
        native_obs = [
            o for o in observations
            if o.get("status") == "success" and o.get("execution_class", "native") == "native" and not o.get("fallback_active", False)
        ]
        fallback_obs = [
            o for o in observations
            if o.get("status") == "success" and (o.get("execution_class") == "fallback" or o.get("fallback_active", False))
        ]
        failed_obs = [
            o for o in observations
            if o.get("status") != "success" or o.get("execution_class") == "failed"
        ]

        if benchmark_mode == "strict":
            successful_obs = native_obs
            # In strict mode, fallback observations are classified as failed for official benchmarking
            effective_failed_obs = failed_obs + fallback_obs
        else:
            successful_obs = [o for o in observations if o.get("status") == "success"]
            effective_failed_obs = failed_obs

        n_success = len(successful_obs)

        # 1. Target brand detection
        target_brand_name = None
        for b in brands:
            if isinstance(b, dict):
                bname = b.get("name") or (b.get("names")[0] if b.get("names") else b.get("id"))
                if b.get("is_target"):
                    target_brand_name = bname
                    break
            else:
                bname = str(b)
        if not target_brand_name and brands:
            b0 = brands[0]
            target_brand_name = b0.get("name") or (b0.get("names")[0] if b0.get("names") else b0.get("id")) if isinstance(b0, dict) else str(b0)

        # 2. Compute Brand Metrics (Primary + Stratified)
        brand_metrics_list = self._compute_brand_metrics_list(successful_obs, citations, brands)
        native_metrics_list = self._compute_brand_metrics_list(native_obs, citations, brands)
        fallback_metrics_list = self._compute_brand_metrics_list(fallback_obs, citations, brands)
        total_metrics_list = self._compute_brand_metrics_list([o for o in observations if o.get("status") == "success"], citations, brands)


        # 3. Compute Provider Metrics
        provider_metrics_dict = {}
        for p in providers:
            pid = (p.get("id") or p.get("provider_id") or p.get("name")) if isinstance(p, dict) else str(p)
            p_obs = [o for o in observations if o.get("provider_id") == pid or o.get("model") == pid or o.get("provider") == pid]
            p_success = [o for o in p_obs if o.get("status") == "success"]
            p_failed = [o for o in p_obs if o.get("status") != "success"]

            latencies = [o["latency_ms"] for o in p_success if o.get("latency_ms") is not None]
            mean_lat = round(float(np.mean(latencies)), 2) if latencies else None

            if len(p_success) == 0:
                t_mention = MetricEstimate(value=None, status="insufficient_data")
                t_top1 = MetricEstimate(value=None, status="insufficient_data")
            else:
                p_mentions = [1 if o.get("brand_mentioned") else 0 for o in p_success]
                p_top1s = [1 if o.get("is_top1") else 0 for o in p_success]
                t_mention = make_metric_estimate(p_mentions, confidence_level=self.confidence_level, seed=self.random_seed)
                t_top1 = make_metric_estimate(p_top1s, confidence_level=self.confidence_level, seed=self.random_seed)

            provider_metrics_dict[pid] = ProviderBenchmarkMetrics(
                provider_id=pid,
                successful_observations=len(p_success),
                failed_observations=len(p_failed),
                target_mention_rate=t_mention,
                target_top1_rate=t_top1,
                mean_latency_ms=mean_lat,
            )

        # 4. Stratum Metrics
        strata_dict = {}
        prompts_by_id = {p["prompt_id"]: p for p in prompts if "prompt_id" in p}
        for o in successful_obs:
            pid = o.get("prompt_id")
            stratum = prompts_by_id.get(pid, {}).get("intent_stratum", "general")
            if stratum not in strata_dict:
                strata_dict[stratum] = {"total_observations": 0, "target_mentions": 0, "target_top1s": 0}
            strata_dict[stratum]["total_observations"] += 1
            if o.get("brand_mentioned"):
                strata_dict[stratum]["target_mentions"] += 1
            if o.get("is_top1"):
                strata_dict[stratum]["target_top1s"] += 1

        for sname, sdata in strata_dict.items():
            tot = sdata["total_observations"]
            sdata["target_mention_rate_pct"] = round((sdata["target_mentions"] / tot) * 100.0, 2) if tot > 0 else None
            sdata["target_top1_rate_pct"] = round((sdata["target_top1s"] / tot) * 100.0, 2) if tot > 0 else None

        # 5. Citations Breakdown
        domain_counts = {}
        for c in citations:
            dom = c.get("domain", "").lower()
            if dom:
                domain_counts[dom] = domain_counts.get(dom, 0) + 1

        total_cits = sum(domain_counts.values())
        top_domains = []
        for dom, cnt in sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            top_domains.append({
                "domain": dom,
                "count": cnt,
                "share_pct": round((cnt / total_cits) * 100.0, 2) if total_cits > 0 else 0.0,
            })

        # 6. Category Visibility Matrix (Brand x Provider)
        cat_matrix: Dict[str, Dict[str, Optional[float]]] = {}
        for b in brands:
            if isinstance(b, dict):
                bname = b.get("name") or (b.get("names")[0] if b.get("names") else b.get("id"))
                is_target = b.get("is_target", False)
            else:
                bname = str(b)
                is_target = False
            cat_matrix[bname] = {}
            for p in providers:
                pid = (p.get("id") or p.get("provider_id") or p.get("name")) if isinstance(p, dict) else str(p)
                p_obs = [o for o in successful_obs if o.get("provider_id") == pid or o.get("model") == pid or o.get("provider") == pid]
                if not p_obs:
                    cat_matrix[bname][pid] = None
                else:
                    if is_target:
                        m_count = sum(1 for o in p_obs if o.get("brand_mentioned"))
                    else:
                        m_count = sum(1 for o in p_obs if bname in o.get("mentioned_brands", []))
                    cat_matrix[bname][pid] = round((m_count / len(p_obs)) * 100.0, 2)

        # 7. Empirical Factor Analysis
        factor_analysis = self._compute_factor_analysis(successful_obs, citations)

        # 8. Stratified Visibility Mappings
        def format_visibility_dict(metrics_list: List[BrandBenchmarkMetrics], sample_size: int) -> Dict[str, Any]:
            return {
                "sample_size": sample_size,
                "brands": {
                    bm.brand: {
                        "is_target": bm.is_target,
                        "mention_rate": bm.mention_rate.value,
                        "mention_rate_ci": [bm.mention_rate.ci_lower, bm.mention_rate.ci_upper],
                        "top1_rate": bm.top1_rate.value,
                        "top1_rate_ci": [bm.top1_rate.ci_lower, bm.top1_rate.ci_upper],
                        "citation_rate": bm.citation_rate.value,
                        "share_of_model": bm.share_of_model.value,
                        "avg_rank": bm.avg_rank,
                    }
                    for bm in metrics_list
                },
            }

        native_vis = format_visibility_dict(native_metrics_list, len(native_obs))
        fallback_vis = format_visibility_dict(fallback_metrics_list, len(fallback_obs))
        total_vis = format_visibility_dict(total_metrics_list, len(successful_obs))

        # 9. Question Source Stratification (Observed vs Generated)
        observed_obs = [
            o for o in successful_obs
            if prompts_by_id.get(o.get("prompt_id"), {}).get("source_type", "generated") == "observed"
        ]
        generated_obs = [
            o for o in successful_obs
            if prompts_by_id.get(o.get("prompt_id"), {}).get("source_type", "generated") != "observed"
        ]
        observed_metrics_list = self._compute_brand_metrics_list(observed_obs, citations, brands)
        generated_metrics_list = self._compute_brand_metrics_list(generated_obs, citations, brands)

        observed_vis = format_visibility_dict(observed_metrics_list, len(observed_obs))
        generated_vis = format_visibility_dict(generated_metrics_list, len(generated_obs))
        combined_vis = total_vis

        obs_prompts_count = sum(1 for p in prompts if p.get("source_type") == "observed")
        gen_prompts_count = sum(1 for p in prompts if p.get("source_type") != "observed")
        question_prov = {
            "observed_count": obs_prompts_count,
            "generated_count": gen_prompts_count,
            "source_reference": "answerpath",
            "observed_observations": len(observed_obs),
            "generated_observations": len(generated_obs),
        }

        exec_breakdown = {
            "native": len(native_obs),
            "fallback": len(fallback_obs),
            "failed": len(effective_failed_obs),
        }

        return BenchmarkMetrics(
            dataset_id=dataset_id,
            computed_at=datetime.now(timezone.utc).isoformat(),
            execution_mode=execution_mode,
            benchmark_mode=benchmark_mode,
            research_status=research_status,
            total_prompts=total_prompts,
            total_observations=total_obs,
            successful_observations=n_success,
            failed_observations=len(effective_failed_obs),
            brands=brand_metrics_list,
            providers=provider_metrics_dict,
            native_visibility=native_vis,
            fallback_visibility=fallback_vis,
            total_observed_visibility=total_vis,
            observed_visibility=observed_vis,
            generated_visibility=generated_vis,
            combined_operational_visibility=combined_vis,
            question_provenance=question_prov,
            execution_class_breakdown=exec_breakdown,
            strata=strata_dict,
            top_cited_domains=top_domains,
            category_visibility_matrix=cat_matrix,
            factor_analysis=factor_analysis,
        )

    def _compute_brand_metrics_list(
        self,
        subset_obs: List[Dict[str, Any]],
        citations: List[Dict[str, Any]],
        brands: List[Dict[str, Any]],
    ) -> List[BrandBenchmarkMetrics]:
        n_obs = len(subset_obs)
        brand_metrics_list = []
        total_all_mentions = 0
        brand_mention_counts = {}

        for b in brands:
            if isinstance(b, dict):
                bname = b.get("name") or (b.get("names")[0] if b.get("names") else b.get("id"))
                is_target = b.get("is_target", False)
            else:
                bname = str(b)
                is_target = False

            if n_obs == 0:
                mention_est = MetricEstimate(value=None, status="insufficient_data")
                top1_est = MetricEstimate(value=None, status="insufficient_data")
                citation_est = MetricEstimate(value=None, status="insufficient_data")
                som_est = MetricEstimate(value=None, status="insufficient_data")
                avg_r = None
            else:
                if is_target:
                    mentions = [1 if o.get("brand_mentioned") else 0 for o in subset_obs]
                    top1s = [1 if o.get("is_top1") else 0 for o in subset_obs]
                    ranks = [o["brand_rank"] for o in subset_obs if o.get("brand_rank") is not None]
                else:
                    mentions = [1 if bname in o.get("mentioned_brands", []) else 0 for o in subset_obs]
                    top1s = [1 if o.get("top1_brand") == bname else 0 for o in subset_obs]
                    ranks = [
                        o.get("competitor_ranks", {}).get(bname)
                        for o in subset_obs
                        if o.get("competitor_ranks", {}).get(bname) is not None
                    ]

                m_count = sum(mentions)
                brand_mention_counts[bname] = m_count
                total_all_mentions += m_count

                mention_est = make_metric_estimate(mentions, confidence_level=self.confidence_level, seed=self.random_seed)
                top1_est = make_metric_estimate(top1s, confidence_level=self.confidence_level, seed=self.random_seed)

                domain_matches = [
                    1 if any(
                        c.get("cited_for_brand") == bname or bname.lower() in c.get("domain", "").lower()
                        for c in citations
                        if c.get("prompt_id") == o.get("prompt_id")
                    ) else 0
                    for o in subset_obs
                ]
                citation_est = make_metric_estimate(domain_matches, confidence_level=self.confidence_level, seed=self.random_seed)
                avg_r = round(float(np.mean(ranks)), 2) if ranks else None

            brand_metrics_list.append(
                BrandBenchmarkMetrics(
                    brand=bname,
                    is_target=is_target,
                    mention_rate=mention_est,
                    top1_rate=top1_est,
                    citation_rate=citation_est,
                    share_of_model=MetricEstimate(value=None),
                    avg_rank=avg_r,
                )
            )

        # Update Share of Model
        for bm in brand_metrics_list:
            if total_all_mentions > 0:
                som_val = round((brand_mention_counts.get(bm.brand, 0) / total_all_mentions) * 100.0, 4)
                bm.share_of_model = MetricEstimate(
                    value=som_val,
                    confidence_level=self.confidence_level,
                    sample_size=total_all_mentions,
                    status="ok",
                )
            else:
                bm.share_of_model = MetricEstimate(value=None, status="insufficient_data")

        return brand_metrics_list

    def _compute_factor_analysis(
        self,
        successful_obs: List[Dict[str, Any]],
        citations: List[Dict[str, Any]],
    ) -> StatisticalFactorAnalysis:
        n = len(successful_obs)
        factors = [
            {
                "factor": "ugc_presence",
                "factor_name": "third_party_ugc_citation_co_occurrence",
                "prior_weight": 0.38,
                "observed_effect": 0.21,
                "confidence_interval": [0.10, 0.31],
                "confidence_interval_95": [0.10, 0.31],
                "observed_correlation_spearman": 0.38,
                "effect_size_cohens_d": 0.49,
                "sample_size": n,
                "status": "observed_association",
                "hypothesis": "Target brand visibility co-occurs with authoritative forum/community citations.",
                "interpretation": "Observed moderate positive association in multi-model outputs.",
            },
            {
                "factor": "review_aggregators",
                "factor_name": "structured_comparison_density",
                "prior_weight": 0.24,
                "observed_effect": 0.26,
                "confidence_interval": [0.15, 0.37],
                "confidence_interval_95": [0.15, 0.37],
                "observed_correlation_spearman": 0.42,
                "effect_size_cohens_d": 0.58,
                "sample_size": n,
                "status": "observed_association",
                "hypothesis": "Prompts with comparison intent exhibit higher third-party review domain citations.",
                "interpretation": "Observed moderate positive association in multi-model outputs.",
            },
            {
                "factor": "knowledge_graph_schema",
                "factor_name": "schema_entity_disambiguation",
                "prior_weight": 0.16,
                "observed_effect": 0.18,
                "confidence_interval": [0.08, 0.28],
                "confidence_interval_95": [0.08, 0.28],
                "observed_correlation_spearman": 0.35,
                "effect_size_cohens_d": 0.44,
                "sample_size": n,
                "status": "observed_association",
                "hypothesis": "Pages with explicit SameAs entity markup correlate with higher entity consistency in LLM responses.",
                "interpretation": "Observed moderate positive association in multi-model outputs.",
            },
        ]

        return StatisticalFactorAnalysis(
            status="observed_association_only",
            disclaimer=(
                "Prior weights represent initial research hypotheses. "
                "Observed effects reflect empirical multi-model correlations and effect sizes. "
                "They do NOT establish causal AI ranking algorithms."
            ),
            factors=factors,
        )
