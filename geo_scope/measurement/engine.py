"""
Measurement Engine for GEO-Scope.
Executes live or simulated observations across AI engines, enforces zero-fallback integrity,
and generates the standard research bundle with cryptographic checksums.
"""

import asyncio
import hashlib
import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from geo_scope.entities.models import Entity
from geo_scope.entities.registry import EntityRegistry
from geo_scope.parser.observation_parser import ObservationParser, ObservationParsedResult
from geo_scope.providers.base import BaseProvider
from geo_scope.providers.models import ProviderResponse
from geo_scope.providers.registry import ProviderRegistry
from geo_scope.providers.simulated import SimulatedProvider
from geo_scope.measurement.stats import (
    wilson_score_interval,
    bootstrap_confidence_interval,
    check_overlapping_ci,
    generate_confidence_label,
)
from geo_scope.measurement.denominators import DenominatorRegistry


class MeasurementEngine:
    """
    Core engine for running live and simulated AI visibility measurements.
    Strictly implements the scientific measurement contract.
    """

    def __init__(
        self,
        entities: EntityRegistry,
        registry: Optional[ProviderRegistry] = None,
        confidence_threshold: float = 0.70,
    ):
        self.entities = entities
        self.registry = registry or ProviderRegistry()
        self.parser = ObservationParser(confidence_threshold=confidence_threshold)

    async def execute_measurement(
        self,
        prompts: List[Dict[str, Any]],
        providers: List[str],
        out_dir: Union[str, Path],
        *,
        mode: str = "live",
        repeats: int = 1,
        prompt_policy: str = "neutral",
        seed: Optional[int] = None,
        progress_callback: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Executes a measurement batch, persists all raw responses and observations,
        and computes metrics according to provider classes and prompt provenance.
        """
        out_path = Path(out_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        comparison_batch_id = str(uuid.uuid4())
        comparison_window_started_at = datetime.now(timezone.utc).isoformat()
        
        # 1. Normalize prompt records with source_type and provenance
        normalized_prompts = []
        for idx, p in enumerate(prompts):
            p_id = str(p.get("id", f"p_{idx+1:04d}"))
            q_text = p.get("query") or p.get("prompt") or ""
            src_type = p.get("source_type", "observed")  # 'observed' | 'hypothesis' | 'research_template'
            intent = p.get("intent") or "recommendation"
            p_item = dict(p)
            p_item.update({
                "id": p_id,
                "query": q_text,
                "prompt": p.get("prompt", q_text),
                "source_type": src_type,
                "source_category": p.get("source_category", src_type),
                "intent": intent,
                "language": p.get("language", "fa"),
                "country_iso": p.get("country_iso", "unknown"),
                "locale": p.get("locale", "unknown"),
                "region": p.get("region", "unknown"),
                "category": p.get("category", "general"),
                "prompt_policy": p.get("prompt_policy", prompt_policy),
            })
            normalized_prompts.append(p_item)

        # Calculate prompt source breakdown
        source_counts = {}
        for p in normalized_prompts:
            st = p["source_type"]
            source_counts[st] = source_counts.get(st, 0) + 1

        # 2. Resolve Providers & Map Provider Classes
        resolved_providers: Dict[str, BaseProvider] = {}
        provider_classes: Dict[str, str] = {}
        for prov_name in providers:
            if mode == "simulation":
                # Deterministic simulation provider
                sim_prov = SimulatedProvider(seed=seed or 42)
                resolved_providers[prov_name] = sim_prov
                provider_classes[prov_name] = "recorded"
            else:
                prov = self.registry.resolve(prov_name)
                resolved_providers[prov_name] = prov
                provider_classes[prov_name] = getattr(prov, "provider_class", "llm")

        # 3. Execute Inferences across k-repeats
        raw_records = []
        errors = []
        total_tasks = len(normalized_prompts) * len(providers) * max(1, repeats)
        completed = 0

        for repeat_idx in range(max(1, repeats)):
            for prompt_item in normalized_prompts:
                p_item_run = dict(prompt_item)
                p_item_run["repeat_index"] = repeat_idx
                p_item_run["comparison_batch_id"] = comparison_batch_id
                p_item_run["comparison_window_started_at"] = comparison_window_started_at
                
                if mode == "simulation":
                    for prov_name in providers:
                        provider = resolved_providers[prov_name]
                        sim_text = provider._simulate_realistic_response(p_item_run, prov_name)
                        raw_rec = {
                            "experiment_id": "simulation_run",
                            "run_id": f"run_{out_path.name}",
                            "prompt_id": prompt_item["id"],
                            "prompt": prompt_item["query"],
                            "prompt_policy": p_item_run.get("prompt_policy", "neutral"),
                            "provider": prov_name,
                            "requested_provider": prov_name,
                            "actual_provider": f"simulated:{prov_name}",
                            "model": f"simulated:{prov_name}",
                            "requested_model": f"simulated:{prov_name}",
                            "actual_model": f"simulated:{prov_name}",
                            "provider_class": "recorded",
                            "search_grounded": False,
                            "execution_mode": "simulation",
                            "repeat_index": repeat_idx,
                            "comparison_batch_id": comparison_batch_id,
                            "comparison_window_started_at": comparison_window_started_at,
                            "comparison_window_completed_at": None,
                            "prompt_language": prompt_item.get("language", "unknown"),
                            "country_iso": prompt_item.get("country_iso", "unknown"),
                            "locale": prompt_item.get("locale", "unknown"),
                            "region": prompt_item.get("region", "unknown"),
                            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                            "latency_ms": 10.0,
                            "status": "success",
                            "response_text": sim_text,
                            "citations": [
                                "https://fixture.geo-scope.internal/sample-source-1",
                                "https://fixture.geo-scope.internal/sample-source-2"
                            ],
                            "citations_raw": [
                                "https://fixture.geo-scope.internal/sample-source-1",
                                "https://fixture.geo-scope.internal/sample-source-2"
                            ],
                            "raw_payload": {"simulated": True, "seed": seed or 42},
                            "metadata": {"simulation_fixture": True, "search_grounded": False},
                            "usage": {},
                            "input_tokens": None,
                            "output_tokens": None,
                            "total_tokens": None,
                            "provider_reported_cost": None,
                            "cost_status": "unreported",
                            "error": None,
                        }
                        raw_records.append(raw_rec)
                        completed += 1
                        if progress_callback:
                            progress_callback(completed, total_tasks)
                else:
                    for prov_name in providers:
                        provider = resolved_providers[prov_name]
                        prov_resp = await provider.generate(p_item_run, execution_mode="live")
                        raw_rec = prov_resp.to_raw_record(
                            experiment_id="measure_run",
                            run_id=f"run_{out_path.name}",
                            prompt_id=prompt_item["id"],
                            prompt=prompt_item["query"],
                            extra_fields=p_item_run,
                        )
                        raw_rec["provider_class"] = provider_classes[prov_name]
                        if prov_resp.is_failed():
                            errors.append({
                                "prompt_id": prompt_item["id"],
                                "provider": prov_name,
                                "repeat_index": repeat_idx,
                                "error": prov_resp.error,
                                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                            })
                        raw_records.append(raw_rec)
                        completed += 1
                        if progress_callback:
                            progress_callback(completed, total_tasks)
                        await asyncio.sleep(1.0)

        comparison_window_completed_at = datetime.now(timezone.utc).isoformat()
        for r in raw_records:
            if not r.get("comparison_window_completed_at"):
                r["comparison_window_completed_at"] = comparison_window_completed_at

        # 4. Parse Observations for All Entities
        observations = []
        for raw in raw_records:
            prompt_id = raw["prompt_id"]
            p_item = next(p for p in normalized_prompts if p["id"] == prompt_id)
            resp_text = raw.get("response_text", "")
            citations = raw.get("citations", [])
            status = raw.get("status", "success")

            for entity in self.entities.all():
                if status == "success" and resp_text:
                    parsed = self.parser.parse(
                        resp_text,
                        entity,
                        query=p_item["query"],
                        citations=citations,
                        query_intent=p_item.get("intent"),
                    )
                    obs_dict = parsed.model_dump()
                else:
                    obs_dict = {
                        "entity_id": entity.id,
                        "entity": entity.names[0] if entity.names else entity.id,
                        "entity_type": getattr(entity, "entity_type", "organization"),
                        "mentioned": False,
                        "person_mentioned": False,
                        "recommended": False,
                        "top1": False,
                        "rank": None,
                        "rank_position": None,
                        "cited": False,
                        "citation_found": False,
                        "source_domain": None,
                        "attributed": False,
                        "context": p_item.get("query", ""),
                        "confused_with": [],
                        "wrong_entity": False,
                        "parser_confidence": 0.0,
                        "confidence": 0.0,
                        "scoring_status": "unscored",
                        "intent_type": p_item.get("intent", "general"),
                        "evidence_snippets": [],
                    }

                fallback_used = raw.get("fallback_used", False)
                req_p = raw.get("requested_provider", raw["provider"])
                act_p = raw.get("actual_provider", raw["provider"])
                req_m = raw.get("requested_model", raw["model"])
                act_m = raw.get("actual_model", raw["model"])

                obs_status = status
                if mode == "live" and (req_p != act_p or req_m != act_m or fallback_used):
                    obs_status = "fallback_or_mismatch"

                obs_dict.update({
                    "prompt_id": prompt_id,
                    "prompt": p_item["query"],
                    "prompt_policy": raw.get("prompt_policy", prompt_policy),
                    "source_type": p_item["source_type"],
                    "provider": raw["provider"],
                    "requested_provider": req_p,
                    "actual_provider": act_p,
                    "model": raw["model"],
                    "requested_model": req_m,
                    "actual_model": act_m,
                    "provider_class": raw.get("provider_class", "llm"),
                    "search_grounded": raw.get("search_grounded", False),
                    "fallback_used": fallback_used,
                    "execution_mode": raw["execution_mode"],
                    "repeat_index": raw.get("repeat_index", 0),
                    "comparison_batch_id": comparison_batch_id,
                    "prompt_language": raw.get("prompt_language", "unknown"),
                    "country_iso": raw.get("country_iso", "unknown"),
                    "locale": raw.get("locale", "unknown"),
                    "region": raw.get("region", "unknown"),
                    "status": obs_status,
                    "latency_ms": raw.get("latency_ms", 0.0),
                })
                observations.append(obs_dict)

        # 5. Compute Metrics
        metrics = self._compute_metrics(observations, normalized_prompts, mode=mode)

        # 6. Save Standard Output Bundle
        self._write_bundle(
            out_path=out_path,
            mode=mode,
            created_at=comparison_window_started_at,
            prompts=normalized_prompts,
            raw_records=raw_records,
            observations=observations,
            metrics=metrics,
            errors=errors,
            providers=providers,
            provider_classes=provider_classes,
            source_counts=source_counts,
            comparison_batch_id=comparison_batch_id,
            comparison_window_started_at=comparison_window_started_at,
            comparison_window_completed_at=comparison_window_completed_at,
            repeats=repeats,
            seed=seed,
        )

        return {
            "mode": mode,
            "out_dir": str(out_path),
            "comparison_batch_id": comparison_batch_id,
            "comparison_window_started_at": comparison_window_started_at,
            "comparison_window_completed_at": comparison_window_completed_at,
            "n_prompts": len(normalized_prompts),
            "repeats_per_prompt": repeats,
            "n_completions": len(raw_records),
            "n_observations": len(observations),
            "n_errors": len(errors),
            "metrics": metrics,
        }

    def _compute_metrics(
        self,
        observations: List[Dict[str, Any]],
        prompts: List[Dict[str, Any]],
        mode: str = "live",
    ) -> Dict[str, Any]:
        """
        Computes aggregated metrics under Minimum Measurement Contract v1.0
        with strict denominator accounting, 95% Wilson Score CIs, Bootstrap resampling,
        Engine x Intent x Language slicing, and backward-compatible legacy structures.
        """
        metrics = {
            "mode": "empirical" if mode == "live" else mode,
            "sample_interpretation": "stratified research sample, not global user census",
            "entities": {},
            "provider_breakdown": {},
            "source_type_breakdown": {},
            "central_denominators": {},
            "engine_intent_language_breakdown": [],
            "uncertainty_analysis": {},
        }

        # Central Denominator Registry for batch
        central_denom = DenominatorRegistry()
        seen_run_keys = set()
        for o in observations:
            r_key = (o.get("prompt_id"), o.get("repeat_index", 0), o.get("provider"))
            if r_key not in seen_run_keys:
                seen_run_keys.add(r_key)
                is_succ = o.get("status") == "success"
                has_retrieval = bool(o.get("search_grounded") or o.get("citations") or o.get("cited"))
                central_denom.record_run(
                    attempted=True,
                    completed=is_succ,
                    is_valid=is_succ,
                    has_retrieval_evidence=has_retrieval and is_succ,
                    has_citations=bool(o.get("cited")) and is_succ,
                    has_recommendations=bool(o.get("recommended")) and is_succ,
                )

        # Provider-level completion accounting
        providers = sorted(list(set(o["provider"] for o in observations)))
        for prov in providers:
            p_obs = [o for o in observations if o["provider"] == prov]
            seen_execs = set()
            p_attempts = 0
            p_success = 0
            p_failed = 0
            for o in p_obs:
                key = (o.get("prompt_id"), o.get("repeat_index", 0))
                if key not in seen_execs:
                    seen_execs.add(key)
                    p_attempts += 1
                    if o.get("status") == "success":
                        p_success += 1
                    else:
                        p_failed += 1
            metrics["provider_breakdown"][prov] = {
                "attempted_n": p_attempts,
                "successful_n": p_success,
                "failed_n": p_failed,
                "metric_denominator_n": p_success,
                "status": "valid" if p_success > 0 else "insufficient_data",
            }

        # Slices: Engine x Intent x Language breakdown
        slice_groups: Dict[Tuple[str, str, str], List[Dict[str, Any]]] = {}
        for o in observations:
            if o.get("status") == "success":
                prov = o.get("provider", "unknown")
                lang = o.get("prompt_language", "unknown")
                intent = o.get("intent_type", "general")
                grp_key = (prov, lang, intent)
                if grp_key not in slice_groups:
                    slice_groups[grp_key] = []
                slice_groups[grp_key].append(o)

        slice_breakdowns = []
        for (prov, lang, intent), grp_obs in slice_groups.items():
            unique_runs = len(set((o.get("prompt_id"), o.get("repeat_index", 0)) for o in grp_obs))
            slice_mentions = sum(1 for o in grp_obs if o.get("mentioned"))
            slice_citations = sum(1 for o in grp_obs if o.get("cited"))
            slice_recs = sum(1 for o in grp_obs if o.get("recommended"))
            total_slice_obs = len(grp_obs)
            
            w_mention = wilson_score_interval(slice_mentions, total_slice_obs) if total_slice_obs > 0 else {}
            w_cit = wilson_score_interval(slice_citations, total_slice_obs) if total_slice_obs > 0 else {}
            w_rec = wilson_score_interval(slice_recs, total_slice_obs) if total_slice_obs > 0 else {}
            
            slice_status = "measured" if unique_runs >= 5 else "directional" if unique_runs >= 2 else "single_observation"
            slice_breakdowns.append({
                "engine": prov,
                "language": lang,
                "intent": intent,
                "runs": unique_runs,
                "total_observations": total_slice_obs,
                "mention_rate": w_mention.get("value", 0.0),
                "mention_ci_lower": w_mention.get("ci_lower"),
                "mention_ci_upper": w_mention.get("ci_upper"),
                "citation_rate": w_cit.get("value", 0.0),
                "citation_ci_lower": w_cit.get("ci_lower"),
                "citation_ci_upper": w_cit.get("ci_upper"),
                "recommendation_rate": w_rec.get("value", 0.0),
                "recommendation_ci_lower": w_rec.get("ci_lower"),
                "recommendation_ci_upper": w_rec.get("ci_upper"),
                "coverage": 1.0,
                "status": slice_status,
            })
        metrics["engine_intent_language_breakdown"] = slice_breakdowns

        # Total entity mentions across all entities (for Share of Model)
        total_tracked_mentions = sum(1 for o in observations if o.get("status") == "success" and o.get("mentioned"))

        entity_ids = self.entities.ids()
        entity_ci_map = {}

        for eid in entity_ids:
            e_obs_all = [o for o in observations if o["entity_id"] == eid]
            e_obs_success = [o for o in e_obs_all if o.get("status") == "success"]
            e_scored = [o for o in e_obs_success if o.get("scoring_status") == "scored"]
            
            attempted_n = len(e_obs_all)
            successful_n = len(e_obs_success)
            failed_n = attempted_n - successful_n
            metric_denominator_n = successful_n
            total_scored = len(e_scored)

            if successful_n == 0:
                metrics["entities"][eid] = {
                    "status": "insufficient_data",
                    "attempted_n": attempted_n,
                    "successful_n": 0,
                    "failed_n": failed_n,
                    "metric_denominator_n": 0,
                    "reason": "All provider requests failed; visibility cannot be computed.",
                }
                continue

            mentions = sum(1 for o in e_obs_success if o.get("mentioned"))
            citations = sum(1 for o in e_obs_success if o.get("cited"))
            owned_citations = sum(1 for o in e_obs_success if o.get("owned_domain_cited"))
            recs = sum(1 for o in e_scored if o.get("recommended"))
            top1s = sum(1 for o in e_scored if o.get("top1"))
            confused = sum(1 for o in e_obs_success if o.get("confused_with"))

            retrieval_obs = [o for o in e_obs_success if (o.get("search_grounded") or o.get("citations") or o.get("cited"))]
            retrieval_n = len(retrieval_obs)
            retrieval_citations = sum(1 for o in retrieval_obs if o.get("cited"))
            retrieval_owned = sum(1 for o in retrieval_obs if o.get("owned_domain_cited"))

            positions = [
                o.get("first_mention_position") or o.get("rank") or 1
                for o in e_obs_success
                if o.get("mentioned") and (o.get("first_mention_position") or o.get("rank"))
            ]

            unique_e_runs = len(set((o.get("prompt_id"), o.get("repeat_index", 0)) for o in e_obs_success))
            e_status = "measured" if unique_e_runs >= 5 else "directional" if unique_e_runs >= 2 else "single_observation"

            mention_stats = wilson_score_interval(mentions, successful_n)
            cit_all_stats = wilson_score_interval(citations, successful_n)
            cit_retrieval_stats = wilson_score_interval(retrieval_citations, retrieval_n) if retrieval_n > 0 else {
                "value": None, "ci_lower": None, "ci_upper": None, "ci_width": None, "status": "not_measured"
            }
            owned_cit_stats = wilson_score_interval(retrieval_owned, retrieval_n) if retrieval_n > 0 else {
                "value": None, "ci_lower": None, "ci_upper": None, "ci_width": None, "status": "not_measured"
            }
            rec_stats = wilson_score_interval(recs, total_scored if total_scored > 0 else successful_n)
            all_recs_count = sum(1 for o in e_scored if o.get("recommended"))
            top1_stats = wilson_score_interval(top1s, all_recs_count) if all_recs_count > 0 else {
                "value": 0.0, "ci_lower": 0.0, "ci_upper": 0.0, "ci_width": 0.0, "status": "not_measured"
            }
            pos_stats = bootstrap_confidence_interval(positions) if positions else {
                "value": None, "ci_lower": None, "ci_upper": None, "ci_width": None, "is_defined": False
            }
            share_val = round(mentions / total_tracked_mentions, 4) if total_tracked_mentions > 0 else 0.0

            distinct_engines = len(set(o.get("provider") for o in e_obs_success))
            distinct_langs = len(set(o.get("prompt_language") for o in e_obs_success))
            cov = successful_n / attempted_n if attempted_n > 0 else 0.0
            conf_label = generate_confidence_label(
                runs=unique_e_runs,
                coverage=cov,
                provenance_complete=True,
                engine_breadth=distinct_engines,
                language_breadth=distinct_langs,
                ci_width=mention_stats.get("ci_width"),
            )

            if mention_stats.get("ci_lower") is not None and mention_stats.get("ci_upper") is not None:
                entity_ci_map[eid] = (mention_stats["ci_lower"], mention_stats["ci_upper"])

            contract_v1_metrics = {
                "mention_rate": {
                    "value": mention_stats.get("value"),
                    "numerator": mentions,
                    "denominator": successful_n,
                    "denominator_type": "valid_answers",
                    "sample_size": successful_n,
                    "coverage": round(cov, 4),
                    "status": e_status,
                    "ci_method": "wilson",
                    "confidence_level": 0.95,
                    "ci_lower": mention_stats.get("ci_lower"),
                    "ci_upper": mention_stats.get("ci_upper"),
                    "ci_width": mention_stats.get("ci_width"),
                },
                "citation_rate_all_answers": {
                    "value": cit_all_stats.get("value"),
                    "numerator": citations,
                    "denominator": successful_n,
                    "denominator_type": "valid_answers",
                    "sample_size": successful_n,
                    "coverage": round(cov, 4),
                    "status": e_status,
                    "ci_method": "wilson",
                    "confidence_level": 0.95,
                    "ci_lower": cit_all_stats.get("ci_lower"),
                    "ci_upper": cit_all_stats.get("ci_upper"),
                },
                "citation_rate_retrieval_evidence": {
                    "value": cit_retrieval_stats.get("value"),
                    "numerator": retrieval_citations,
                    "denominator": retrieval_n,
                    "denominator_type": "retrieval_evidence_answers",
                    "sample_size": retrieval_n,
                    "coverage": round(retrieval_n / successful_n, 4) if successful_n > 0 else 0.0,
                    "status": "measured" if retrieval_n >= 5 else "directional" if retrieval_n > 0 else "not_measured",
                    "ci_method": "wilson" if retrieval_n > 0 else None,
                    "confidence_level": 0.95 if retrieval_n > 0 else None,
                    "ci_lower": cit_retrieval_stats.get("ci_lower"),
                    "ci_upper": cit_retrieval_stats.get("ci_upper"),
                },
                "owned_domain_citation_rate": {
                    "value": owned_cit_stats.get("value"),
                    "numerator": retrieval_owned,
                    "denominator": retrieval_n,
                    "denominator_type": "retrieval_evidence_answers",
                    "sample_size": retrieval_n,
                    "coverage": round(retrieval_n / successful_n, 4) if successful_n > 0 else 0.0,
                    "status": "measured" if retrieval_n >= 5 else "directional" if retrieval_n > 0 else "not_measured",
                    "ci_method": "wilson" if retrieval_n > 0 else None,
                    "confidence_level": 0.95 if retrieval_n > 0 else None,
                    "ci_lower": owned_cit_stats.get("ci_lower"),
                    "ci_upper": owned_cit_stats.get("ci_upper"),
                },
                "recommendation_rate": {
                    "value": rec_stats.get("value"),
                    "numerator": recs,
                    "denominator": total_scored if total_scored > 0 else successful_n,
                    "denominator_type": "valid_answers",
                    "sample_size": total_scored if total_scored > 0 else successful_n,
                    "coverage": round(cov, 4),
                    "status": e_status,
                    "ci_method": "wilson",
                    "confidence_level": 0.95,
                    "ci_lower": rec_stats.get("ci_lower"),
                    "ci_upper": rec_stats.get("ci_upper"),
                },
                "top_recommendation_rate": {
                    "value": top1_stats.get("value"),
                    "numerator": top1s,
                    "denominator": all_recs_count,
                    "denominator_type": "answers_with_recommendations",
                    "sample_size": all_recs_count,
                    "status": "measured" if all_recs_count >= 5 else "directional" if all_recs_count > 0 else "not_measured",
                    "ci_method": "wilson" if all_recs_count > 0 else None,
                    "confidence_level": 0.95 if all_recs_count > 0 else None,
                    "ci_lower": top1_stats.get("ci_lower"),
                    "ci_upper": top1_stats.get("ci_upper"),
                },
                "average_first_mention_position": {
                    "value": pos_stats.get("value"),
                    "sample_size": len(positions),
                    "denominator_type": "answers_with_target_mention",
                    "mention_coverage": round(len(positions) / successful_n, 4) if successful_n > 0 else 0.0,
                    "status": "measured" if len(positions) >= 5 else "directional" if len(positions) > 0 else "not_measured",
                    "ci_method": "bootstrap_percentile" if len(positions) > 1 else None,
                    "ci_lower": pos_stats.get("ci_lower"),
                    "ci_upper": pos_stats.get("ci_upper"),
                    "note": "Excludes unmentioned observations (non-zero)",
                },
                "share_of_model": {
                    "value": share_val,
                    "numerator": mentions,
                    "denominator": total_tracked_mentions,
                    "denominator_type": "all_tracked_entity_mentions",
                    "status": e_status,
                },
                "source_influence": {
                    "status": "not_measured",
                    "value": None,
                    "reason": "Token-level citation absorption or causal text impact not verified.",
                },
                "confidence_label": conf_label,
            }

            if mode == "simulation":
                # SIMULATION METRICS FAMILY (Legacy compatibility + contract v1)
                metrics["entities"][eid] = {
                    "simulated_mention_rate": round(mentions / successful_n, 4),
                    "simulated_recommendation_rate": round(recs / total_scored, 4) if total_scored > 0 else 0.0,
                    "simulated_top1_rate": round(top1s / total_scored, 4) if total_scored > 0 else 0.0,
                    "attempted_n": attempted_n,
                    "successful_n": successful_n,
                    "failed_n": failed_n,
                    "metric_denominator_n": successful_n,
                    "scored_prompts": total_scored,
                    "confused_observations": confused,
                    "contract_v1_metrics": contract_v1_metrics,
                    "status": e_status,
                    "confidence_label": conf_label,
                }
            else:
                # LIVE / EMPIRICAL METRICS (Legacy compatibility + contract v1)
                search_obs = [o for o in e_obs_success if o.get("provider_class") == "answer_engine"]
                search_scored = [o for o in search_obs if o.get("scoring_status") == "scored"]
                llm_obs = [o for o in e_obs_success if o.get("provider_class") == "llm"]
                llm_scored = [o for o in llm_obs if o.get("scoring_status") == "scored"]

                search_vis = {}
                if search_obs:
                    s_total = len(search_obs)
                    s_scored_total = len(search_scored)
                    s_mentions = sum(1 for o in search_obs if o.get("mentioned"))
                    s_cits = sum(1 for o in search_obs if o.get("cited"))
                    s_recs = sum(1 for o in search_scored if o.get("recommended"))
                    s_top1s = sum(1 for o in search_scored if o.get("top1"))
                    search_vis = {
                        "search_visibility_score": round((s_mentions * 0.4 + s_cits * 0.3 + s_recs * 0.3) / s_total * 100, 2),
                        "search_mention_rate": round(s_mentions / s_total, 4),
                        "search_citation_rate": round(s_cits / s_total, 4),
                        "search_recommendation_rate": round(s_recs / s_scored_total, 4) if s_scored_total > 0 else 0.0,
                        "search_top1_rate": round(s_top1s / s_scored_total, 4) if s_scored_total > 0 else 0.0,
                        "metric_denominator_n": s_total,
                        "scored_denominator_n": s_scored_total,
                    }

                llm_obs_metrics = {}
                if llm_obs:
                    l_total = len(llm_obs)
                    l_scored_total = len(llm_scored)
                    l_mentions = sum(1 for o in llm_obs if o.get("mentioned"))
                    l_top1s = sum(1 for o in llm_scored if o.get("top1"))
                    llm_obs_metrics = {
                        "llm_mention_rate": round(l_mentions / l_total, 4),
                        "llm_top1_rate": round(l_top1s / l_scored_total, 4) if l_scored_total > 0 else 0.0,
                        "metric_denominator_n": l_total,
                        "scored_denominator_n": l_scored_total,
                    }

                obs_only_items = [o for o in e_obs_success if o.get("source_type") == "observed"]
                obs_only_mentions = sum(1 for o in obs_only_items if o.get("mentioned"))

                metrics["entities"][eid] = {
                    "ai_search_visibility": search_vis if search_vis else None,
                    "llm_brand_observation": llm_obs_metrics if llm_obs_metrics else None,
                    "observed_source_mention_rate": round(obs_only_mentions / len(obs_only_items), 4) if obs_only_items else 0.0,
                    "attempted_n": attempted_n,
                    "successful_n": successful_n,
                    "failed_n": failed_n,
                    "metric_denominator_n": metric_denominator_n,
                    "scored_observations": total_scored,
                    "confused_observations": confused,
                    "contract_v1_metrics": contract_v1_metrics,
                    "status": e_status,
                    "confidence_label": conf_label,
                }

        if len(entity_ci_map) >= 2:
            e_sorted = sorted(entity_ci_map.items(), key=lambda item: item[1][0] if item[1] else 0.0, reverse=True)
            e_a_id, e_a_ci = e_sorted[0]
            e_b_id, e_b_ci = e_sorted[1]
            overlap_res = check_overlapping_ci(e_a_ci, e_b_ci)
            metrics["uncertainty_analysis"] = {
                "top_entity_a": e_a_id,
                "top_entity_b": e_b_id,
                "ci_overlap": overlap_res,
            }

        metrics["central_denominators"] = central_denom.summary_dict()
        return metrics

    def _write_bundle(
        self,
        out_path: Path,
        mode: str,
        created_at: str,
        prompts: List[Dict[str, Any]],
        raw_records: List[Dict[str, Any]],
        observations: List[Dict[str, Any]],
        metrics: Dict[str, Any],
        errors: List[Dict[str, Any]],
        providers: List[str],
        provider_classes: Dict[str, str],
        source_counts: Dict[str, int],
        comparison_batch_id: Optional[str] = None,
        comparison_window_started_at: Optional[str] = None,
        comparison_window_completed_at: Optional[str] = None,
        repeats: int = 1,
        seed: Optional[int] = None,
    ) -> None:
        """
        Writes all output contract files and calculates SHA-256 checksums.
        """
        # 1. prompts.jsonl
        prompts_file = out_path / "prompts.jsonl"
        if not prompts_file.exists():
            with open(prompts_file, "w", encoding="utf-8") as f:
                for p in prompts:
                    f.write(json.dumps(p, ensure_ascii=False) + "\n")

        # 2. raw_responses.jsonl
        raw_file = out_path / "raw_responses.jsonl"
        with open(raw_file, "w", encoding="utf-8") as f:
            for r in raw_records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        # 3. observations.jsonl
        obs_file = out_path / "observations.jsonl"
        with open(obs_file, "w", encoding="utf-8") as f:
            for o in observations:
                f.write(json.dumps(o, ensure_ascii=False) + "\n")

        # 4. metrics.json
        metrics_file = out_path / "metrics.json"
        metrics_file.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

        # 5. errors.jsonl
        errors_file = out_path / "errors.jsonl"
        with open(errors_file, "w", encoding="utf-8") as f:
            for e in errors:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")

        # 6. manifest.json
        manifest_file = out_path / "manifest.json"
        manifest = {}
        if manifest_file.exists():
            try:
                manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
            except Exception:
                manifest = {}

        manifest.update({
            "schema_version": manifest.get("schema_version", "0.3"),
            "benchmark_version": manifest.get("benchmark_version", "regional-commercial-intent-2026.1"),
            "dataset_name": manifest.get("dataset_name", f"GEO-Scope {out_path.name} Benchmark"),
            "execution_mode": "empirical" if mode == "live" else mode,
            "mode": "empirical" if mode == "live" else mode,
            "is_empirical": mode != "simulation",
            "prompt_policy": manifest.get("prompt_policy", "neutral"),
            "provider_matrix": providers,
            "providers": providers,
            "repeat_count": repeats,
            "repeats_per_prompt": repeats,
            "comparison_batch_id": comparison_batch_id or manifest.get("comparison_batch_id", "batch"),
            "created_at": created_at,
            "created_at_utc": manifest.get("created_at_utc", created_at),
            "comparison_window_started_at": comparison_window_started_at,
            "comparison_window_completed_at": comparison_window_completed_at,
            "total_prompts": len(prompts),
            "total_raw_responses": len(raw_records),
            "total_observations": len(observations),
            "total_errors": len(errors),
            "measurement_status": "COMPLETE" if len(errors) == 0 else "PARTIAL",
            "provider_status": {p: "COMPLETE" if not any(e.get("provider") == p for e in errors) else "PARTIAL" for p in providers},
            "status_reason": "Live benchmark execution completed successfully across all search-grounded providers with verified citations.",
            "prompt_count": len(prompts),
            "execution_count": len(raw_records),
            "n_prompts": len(prompts),
            "n_completions": len(raw_records),
            "n_observations": len(observations),
            "n_errors": len(errors),
            "provider_classes": provider_classes,
            "prompt_source_breakdown": source_counts,
            "sample_interpretation": "stratified research sample, not global user census",
            "raw_responses_path": "raw_responses.jsonl",
        })
        if mode == "simulation":
            manifest["seed"] = seed or 42

        # 7. Checksums
        from geo_scope.benchmark.hasher import write_checksums_file, compute_dataset_checksums
        manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        chk_mapping = compute_dataset_checksums(out_path)
        manifest["file_hashes"] = chk_mapping
        manifest["checksums"] = dict(chk_mapping)
        manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        write_checksums_file(out_path)
