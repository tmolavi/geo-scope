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
            normalized_prompts.append({
                "id": p_id,
                "query": q_text,
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
                
                for prov_name in providers:
                    provider = resolved_providers[prov_name]
                    
                    if mode == "simulation":
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
                    else:
                        # LIVE EXECUTION - Zero simulation fallback
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

                obs_dict.update({
                    "prompt_id": prompt_id,
                    "prompt": p_item["query"],
                    "prompt_policy": raw.get("prompt_policy", prompt_policy),
                    "source_type": p_item["source_type"],
                    "provider": raw["provider"],
                    "requested_provider": raw.get("requested_provider", raw["provider"]),
                    "actual_provider": raw.get("actual_provider", raw["provider"]),
                    "model": raw["model"],
                    "requested_model": raw.get("requested_model", raw["model"]),
                    "actual_model": raw.get("actual_model", raw["model"]),
                    "provider_class": raw.get("provider_class", "llm"),
                    "search_grounded": raw.get("search_grounded", False),
                    "execution_mode": raw["execution_mode"],
                    "repeat_index": raw.get("repeat_index", 0),
                    "comparison_batch_id": comparison_batch_id,
                    "prompt_language": raw.get("prompt_language", "unknown"),
                    "country_iso": raw.get("country_iso", "unknown"),
                    "locale": raw.get("locale", "unknown"),
                    "region": raw.get("region", "unknown"),
                    "status": status,
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
        Computes aggregated metrics with strict separation of metric families and failure denominators:
        - simulation: simulated_mention_rate, simulated_recommendation_rate, simulated_top1_rate
        - answer_engine: AI Search Visibility (search_mention_rate, search_citation_rate, search_top1_rate)
        - llm: LLM Brand Observation (llm_mention_rate, llm_top1_rate)
        Also provides filtering by prompt source_type and explicit failure accounting.
        """
        metrics = {
            "mode": mode,
            "sample_interpretation": "stratified research sample, not global user census",
            "entities": {},
            "provider_breakdown": {},
            "source_type_breakdown": {},
        }

        # Provider-level completion accounting
        providers = sorted(list(set(o["provider"] for o in observations)))
        for prov in providers:
            p_obs = [o for o in observations if o["provider"] == prov]
            # Deduplicate prompt/repeat level status
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

        entity_ids = self.entities.ids()
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

            # Base count calculations on successful completions only
            mentions = sum(1 for o in e_obs_success if o.get("mentioned"))
            citations = sum(1 for o in e_obs_success if o.get("cited"))
            recs = sum(1 for o in e_scored if o.get("recommended"))
            top1s = sum(1 for o in e_scored if o.get("top1"))
            confused = sum(1 for o in e_obs_success if o.get("confused_with"))

            if mode == "simulation":
                # SIMULATION METRICS FAMILY
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
                }
            else:
                # LIVE / EMPIRICAL METRICS
                search_obs = [o for o in e_obs_success if o.get("provider_class") == "answer_engine"]
                search_scored = [o for o in search_obs if o.get("scoring_status") == "scored"]
                llm_obs = [o for o in e_obs_success if o.get("provider_class") == "llm"]
                llm_scored = [o for o in llm_obs if o.get("scoring_status") == "scored"]

                # AI Search Visibility Family (answer_engine only)
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

                # LLM Brand Observation Family (llm only)
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

                # Observed prompts only subset
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
                }

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
        manifest = {
            "schema_version": "0.3",
            "mode": mode,
            "created_at": created_at,
            "comparison_batch_id": comparison_batch_id,
            "comparison_window_started_at": comparison_window_started_at,
            "comparison_window_completed_at": comparison_window_completed_at,
            "repeats_per_prompt": repeats,
            "prompt_count": len(prompts),
            "execution_count": len(raw_records),
            "n_prompts": len(prompts),
            "n_completions": len(raw_records),
            "n_observations": len(observations),
            "n_errors": len(errors),
            "providers": providers,
            "provider_classes": provider_classes,
            "prompt_source_breakdown": source_counts,
            "sample_interpretation": "stratified research sample, not global user census",
            "raw_responses_path": "raw_responses.jsonl",
        }
        if mode == "simulation":
            manifest["seed"] = seed or 42

        manifest_file = out_path / "manifest.json"
        manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

        # 7. checksums.sha256
        checksum_files = [
            "manifest.json",
            "prompts.jsonl",
            "raw_responses.jsonl",
            "observations.jsonl",
            "metrics.json",
            "errors.jsonl",
        ]
        checksums = {}
        for fname in checksum_files:
            target = out_path / fname
            if target.exists():
                h = hashlib.sha256(target.read_bytes()).hexdigest()
                checksums[fname] = h

        chk_file = out_path / "checksums.sha256"
        with open(chk_file, "w", encoding="utf-8") as f:
            for fname, chk in sorted(checksums.items()):
                f.write(f"{chk}  {fname}\n")
