"""
Replay Engine for GEO-Scope.
Executes deterministic offline analysis of previously recorded AI responses
with zero network or provider calls.
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from geo_scope.entities.registry import EntityRegistry
from geo_scope.parser.observation_parser import ObservationParser


class ReplayEngine:
    """
    Offline deterministic replay engine.
    Reads recorded raw responses and re-evaluates them against an entity registry.
    """

    def __init__(self, entities: EntityRegistry, confidence_threshold: float = 0.70):
        self.entities = entities
        self.parser = ObservationParser(confidence_threshold=confidence_threshold)

    def replay(
        self,
        input_path: Union[str, Path],
        out_dir: Union[str, Path],
    ) -> Dict[str, Any]:
        """
        Replays recorded responses from a run directory or raw_responses.jsonl file.
        """
        in_p = Path(input_path)
        out_p = Path(out_dir)
        out_p.mkdir(parents=True, exist_ok=True)
        created_at = datetime.now(timezone.utc).isoformat()

        # 1. Locate raw_responses.jsonl and prompts.jsonl
        if in_p.is_dir():
            raw_file = in_p / "raw_responses.jsonl"
            prompts_file = in_p / "prompts.jsonl"
            orig_manifest_file = in_p / "manifest.json"
        else:
            raw_file = in_p
            prompts_file = in_p.parent / "prompts.jsonl"
            orig_manifest_file = in_p.parent / "manifest.json"

        if not raw_file.is_file():
            raise FileNotFoundError(f"Recorded raw responses not found at: {raw_file}")

        # 2. Read raw responses
        raw_records = []
        with open(raw_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    raw_records.append(json.loads(line))

        # Read or synthesize prompt metadata
        prompts = []
        if prompts_file.is_file():
            with open(prompts_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        prompts.append(json.loads(line))
        else:
            # Reconstruct from raw records
            seen_prompts = set()
            for r in raw_records:
                pid = r.get("prompt_id", "p_unknown")
                if pid not in seen_prompts:
                    seen_prompts.add(pid)
                    prompts.append({
                        "id": pid,
                        "query": r.get("prompt", ""),
                        "source_type": "observed",
                        "intent": "recommendation",
                    })

        # Calculate prompt source breakdown
        source_counts = {}
        for p in prompts:
            st = p.get("source_type", "observed")
            source_counts[st] = source_counts.get(st, 0) + 1

        # Extract providers and provider classes
        providers = list(set(r.get("provider", "unknown") for r in raw_records))
        provider_classes = {}
        for r in raw_records:
            prov = r.get("provider", "unknown")
            provider_classes[prov] = r.get("provider_class", "recorded")

        # 3. Deterministically Re-parse Observations
        observations = []
        errors = []
        for raw in raw_records:
            prompt_id = raw.get("prompt_id", "")
            p_item = next((p for p in prompts if p.get("id") == prompt_id), {"query": raw.get("prompt", ""), "source_type": "observed", "intent": "recommendation"})
            resp_text = raw.get("response_text") or raw.get("raw_response") or ""
            citations = raw.get("citations") or raw.get("citations_raw") or []
            status = raw.get("status", "success")

            if raw.get("error"):
                errors.append({
                    "prompt_id": prompt_id,
                    "provider": raw.get("provider"),
                    "error": raw.get("error"),
                })

            for entity in self.entities.all():
                if status == "success" and resp_text:
                    parsed = self.parser.parse(
                        resp_text,
                        entity,
                        query=p_item.get("query", ""),
                        citations=citations,
                        query_intent=p_item.get("intent"),
                    )
                    obs_dict = parsed.model_dump()
                else:
                    obs_dict = {
                        "entity_id": entity.id,
                        "mentioned": False,
                        "person_mentioned": False,
                        "recommended": False,
                        "top1": False,
                        "rank": None,
                        "cited": False,
                        "attributed": False,
                        "confused_with": [],
                        "wrong_entity": False,
                        "parser_confidence": 0.0,
                        "scoring_status": "unscored",
                        "intent_type": p_item.get("intent", "general"),
                        "evidence_snippets": [],
                    }

                obs_dict.update({
                    "prompt_id": prompt_id,
                    "prompt": p_item.get("query", ""),
                    "source_type": p_item.get("source_type", "observed"),
                    "provider": raw.get("provider"),
                    "model": raw.get("model"),
                    "provider_class": raw.get("provider_class", "recorded"),
                    "execution_mode": "replay",
                    "status": status,
                    "latency_ms": raw.get("latency_ms", 0.0),
                })
                observations.append(obs_dict)

        # 4. Compute Metrics
        metrics = self._compute_metrics(observations, prompts)

        # 5. Write Standard Bundle
        self._write_bundle(
            out_path=out_p,
            replayed_from=str(in_p),
            created_at=created_at,
            prompts=prompts,
            raw_records=raw_records,
            observations=observations,
            metrics=metrics,
            errors=errors,
            providers=providers,
            provider_classes=provider_classes,
            source_counts=source_counts,
        )

        return {
            "mode": "replay",
            "replayed_from": str(in_p),
            "out_dir": str(out_p),
            "n_prompts": len(prompts),
            "n_completions": len(raw_records),
            "n_observations": len(observations),
            "n_errors": len(errors),
            "metrics": metrics,
        }

    def _compute_metrics(self, observations: List[Dict[str, Any]], prompts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Computes replay metrics with strict provider-class separation."""
        metrics = {
            "mode": "replay",
            "entities": {},
            "provider_breakdown": {},
        }

        for eid in self.entities.ids():
            e_obs = [o for o in observations if o["entity_id"] == eid]
            e_scored = [o for o in e_obs if o.get("scoring_status") == "scored"]
            total_obs = len(e_obs)
            total_scored = len(e_scored)

            if total_obs == 0:
                continue

            mentions = sum(1 for o in e_obs if o.get("mentioned"))
            citations = sum(1 for o in e_obs if o.get("cited"))
            recs = sum(1 for o in e_scored if o.get("recommended"))
            top1s = sum(1 for o in e_scored if o.get("top1"))
            confused = sum(1 for o in e_obs if o.get("confused_with"))

            search_obs = [o for o in e_obs if o.get("provider_class") == "answer_engine"]
            search_scored = [o for o in search_obs if o.get("scoring_status") == "scored"]
            llm_obs = [o for o in e_obs if o.get("provider_class") == "llm"]
            llm_scored = [o for o in llm_obs if o.get("scoring_status") == "scored"]

            search_vis = {}
            if search_obs:
                s_total = len(search_obs)
                s_scored_total = len(search_scored)
                s_m = sum(1 for o in search_obs if o.get("mentioned"))
                s_c = sum(1 for o in search_obs if o.get("cited"))
                s_r = sum(1 for o in search_scored if o.get("recommended"))
                s_t = sum(1 for o in search_scored if o.get("top1"))
                search_vis = {
                    "search_visibility_score": round((s_m * 0.4 + s_c * 0.3 + s_r * 0.3) / s_total * 100, 2),
                    "search_mention_rate": round(s_m / s_total, 4),
                    "search_citation_rate": round(s_c / s_total, 4),
                    "search_recommendation_rate": round(s_r / s_scored_total, 4) if s_scored_total > 0 else 0.0,
                    "search_top1_rate": round(s_t / s_scored_total, 4) if s_scored_total > 0 else 0.0,
                    "observations_count": s_total,
                }

            llm_obs_metrics = {}
            if llm_obs:
                l_total = len(llm_obs)
                l_scored_total = len(llm_scored)
                l_m = sum(1 for o in llm_obs if o.get("mentioned"))
                l_t = sum(1 for o in llm_scored if o.get("top1"))
                llm_obs_metrics = {
                    "llm_mention_rate": round(l_m / l_total, 4),
                    "llm_top1_rate": round(l_t / l_scored_total, 4) if l_scored_total > 0 else 0.0,
                    "observations_count": l_total,
                }

            metrics["entities"][eid] = {
                "overall_mention_rate": round(mentions / total_obs, 4),
                "ai_search_visibility": search_vis if search_vis else None,
                "llm_brand_observation": llm_obs_metrics if llm_obs_metrics else None,
                "total_observations": total_obs,
                "scored_observations": total_scored,
                "confused_observations": confused,
            }

        return metrics

    def _write_bundle(
        self,
        out_path: Path,
        replayed_from: str,
        created_at: str,
        prompts: List[Dict[str, Any]],
        raw_records: List[Dict[str, Any]],
        observations: List[Dict[str, Any]],
        metrics: Dict[str, Any],
        errors: List[Dict[str, Any]],
        providers: List[str],
        provider_classes: Dict[str, str],
        source_counts: Dict[str, int],
    ) -> None:
        """Writes standard output bundle and SHA-256 checksums."""
        # 1. prompts.jsonl
        with open(out_path / "prompts.jsonl", "w", encoding="utf-8") as f:
            for p in prompts:
                f.write(json.dumps(p, ensure_ascii=False) + "\n")

        # 2. raw_responses.jsonl (reproduced)
        with open(out_path / "raw_responses.jsonl", "w", encoding="utf-8") as f:
            for r in raw_records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        # 3. observations.jsonl
        with open(out_path / "observations.jsonl", "w", encoding="utf-8") as f:
            for o in observations:
                f.write(json.dumps(o, ensure_ascii=False) + "\n")

        # 4. metrics.json
        (out_path / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

        # 5. errors.jsonl
        with open(out_path / "errors.jsonl", "w", encoding="utf-8") as f:
            for e in errors:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")

        # 6. manifest.json
        manifest = {
            "mode": "replay",
            "replayed_from": replayed_from,
            "created_at": created_at,
            "n_prompts": len(prompts),
            "n_completions": len(raw_records),
            "n_observations": len(observations),
            "n_errors": len(errors),
            "providers": providers,
            "provider_classes": provider_classes,
            "prompt_source_breakdown": source_counts,
            "raw_responses_path": "raw_responses.jsonl",
        }
        (out_path / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

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

        with open(out_path / "checksums.sha256", "w", encoding="utf-8") as f:
            for fname, chk in sorted(checksums.items()):
                f.write(f"{chk}  {fname}\n")
