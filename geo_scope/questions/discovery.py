"""
High-level discovery and benchmark preparation engine connecting AnswerPath GEO to GEO-Scope.
"""
from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

from geo_scope.questions.models import DiscoveryResult, DiscoveredQuestion
from geo_scope.questions.answerpath_connector import AnswerPathConnector, extract_records


def discover_questions(
    topic: str,
    input_paths: Optional[List[str]] = None,
    include_generated: bool = True,
    threshold: float = 0.88,
    category: str = "GEO",
    target_brand: str = "",
    competitors: Optional[List[str]] = None,
    entities: Optional[List[str]] = None,
) -> DiscoveryResult:
    """
    Mode 1: Research Discovery
    Discovers questions from owned input files/logs and/or template generators,
    clusters them by intent and similarity, and prepares candidate benchmark prompt sets.
    """
    inputs = []
    if input_paths:
        for p in input_paths:
            inputs.extend(extract_records(p))

    resolved_entities = entities or (([target_brand] if target_brand else []) + (competitors or []))
    connector = AnswerPathConnector(threshold=threshold)
    return connector.mine_questions(
        topic=topic,
        inputs=inputs,
        include_generated=include_generated,
        category=category,
        entities=resolved_entities,
    )


def prepare_benchmark_dataset(
    topic: str,
    observed_inputs: Optional[List[str]] = None,
    generated_inputs: Optional[List[str]] = None,
    include_default_generated: bool = True,
    brand: str = "My Brand",
    competitors: Optional[List[str]] = None,
    entities: Optional[List[str]] = None,
    out_dir: str = "benchmark",
    dataset_id: Optional[str] = None,
    category: str = "GEO",
    threshold: float = 0.88,
) -> Dict[str, Any]:
    """
    Mode 2: Official Benchmark Preparation
    Creates a versioned benchmark prompt package with separated observed vs generated files:
    benchmark/<dataset-id>/
      ├── prompts/
      │    ├── observed.jsonl
      │    └── generated.jsonl
      ├── prompts.jsonl
      ├── manifest.json
      └── provenance.json
    """
    now_str = datetime.now(timezone.utc).isoformat()
    if not dataset_id:
        slug = topic.lower().replace(" ", "-").replace("/", "-")
        dataset_id = f"geo-scope-benchmark-{slug}-2026.1"

    target_dir = Path(out_dir) / dataset_id
    prompts_dir = target_dir / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    # 1. Gather observed questions
    observed_rows = []
    if observed_inputs:
        for p in observed_inputs:
            observed_rows.extend(extract_records(p))

    # 2. Gather custom generated inputs
    gen_rows = []
    if generated_inputs:
        for p in generated_inputs:
            gen_rows.extend(extract_records(p))

    # 3. Mine with AnswerPathConnector
    connector = AnswerPathConnector(threshold=threshold)
    
    # Process observed questions
    res_obs = connector.mine_questions(
        topic=topic,
        inputs=observed_rows,
        include_generated=False,
        category=category,
        entities=[brand] + (competitors or []),
    )
    
    # Process generated questions (inputs + default generated if requested)
    res_gen = connector.mine_questions(
        topic=topic,
        inputs=gen_rows,
        include_generated=include_default_generated,
        category=category,
        entities=[brand] + (competitors or []),
    )

    # Format PromptRecord dicts
    observed_records = [
        q.to_prompt_record_dict(target_brand=brand, competitors=competitors, niche=category)
        for q in res_obs.questions
    ]
    generated_records = [
        q.to_prompt_record_dict(target_brand=brand, competitors=competitors, niche=category)
        for q in res_gen.questions
    ]
    all_prompts = observed_records + generated_records

    # 4. Write prompts/observed.jsonl
    obs_file = prompts_dir / "observed.jsonl"
    with open(obs_file, "w", encoding="utf-8") as f:
        for r in observed_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # 5. Write prompts/generated.jsonl
    gen_file = prompts_dir / "generated.jsonl"
    with open(gen_file, "w", encoding="utf-8") as f:
        for r in generated_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # 6. Write unified prompts.jsonl
    unified_file = target_dir / "prompts.jsonl"
    with open(unified_file, "w", encoding="utf-8") as f:
        for r in all_prompts:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # 7. Write provenance.json
    provenance_data = {
        "dataset_id": dataset_id,
        "topic": topic,
        "created_at": now_str,
        "question_provenance": {
            "total_prompts": len(all_prompts),
            "observed_count": len(observed_records),
            "generated_count": len(generated_records),
            "source_reference": "answerpath",
            "observed_sources": list({q.source for q in res_obs.questions}),
            "generated_sources": list({q.source for q in res_gen.questions}),
            "intent_distribution": {
                "observed": res_obs.intent_distribution,
                "generated": res_gen.intent_distribution,
            },
        },
    }
    prov_file = target_dir / "provenance.json"
    prov_file.write_text(json.dumps(provenance_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # 8. Write manifest.json
    manifest_data = {
        "version": "2026.1",
        "benchmark_version": "2026.1-live",
        "dataset_id": dataset_id,
        "created_at": now_str,
        "execution_mode": "live",
        "benchmark_mode": "discovery",
        "research_status": "peer_review_ready" if len(observed_records) > 0 else "demo_only",
        "description": f"Prepared benchmark prompt set for '{topic}' powered by AnswerPath GEO.",
        "counts": {
            "prompts": len(all_prompts),
            "observed_prompts": len(observed_records),
            "generated_prompts": len(generated_records),
            "brands": 1 + len(competitors or []),
        },
        "question_provenance": {
            "observed_count": len(observed_records),
            "generated_count": len(generated_records),
            "source_reference": "answerpath",
        },
    }
    man_file = target_dir / "manifest.json"
    man_file.write_text(json.dumps(manifest_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "dataset_id": dataset_id,
        "directory": str(target_dir),
        "total_prompts": len(all_prompts),
        "observed_count": len(observed_records),
        "generated_count": len(generated_records),
        "observed_file": str(obs_file),
        "generated_file": str(gen_file),
        "prompts_file": str(unified_file),
        "manifest_file": str(man_file),
        "provenance_file": str(prov_file),
    }


def format_discovery_report(result: DiscoveryResult) -> str:
    """Formats a human-readable terminal report for discovered questions and clusters."""
    lines = [
        "=" * 78,
        f"🔍 AnswerPath GEO Question Discovery Report: '{result.topic}'",
        "=" * 78,
        f"• Total Discovered Questions : {result.total_discovered}",
        f"  - Observed User Questions   : {result.observed_count} (Real demand)",
        f"  - Generated Research Prompts : {result.generated_count} (Exploration templates)",
        f"• Distinct Question Clusters : {result.clusters_count}",
        "-" * 78,
        "📊 Intent Distribution:",
    ]
    for intent, count in sorted(result.intent_distribution.items(), key=lambda x: x[1], reverse=True):
        pct = (count / result.total_discovered * 100) if result.total_discovered > 0 else 0
        lines.append(f"  - {intent:<15} : {count:3d} ({pct:5.1f}%)")

    lines.extend([
        "-" * 78,
        "💡 Top Recommended Benchmark Candidate Clusters:",
    ])
    for idx, c in enumerate(result.clusters[:10], 1):
        stypes = ", ".join(c.source_types)
        lines.append(f"  {idx:2d}. [{c.intent.upper()}] ({stypes}) (Freq: {c.size})")
        lines.append(f"      \"{c.representative_question}\"")

    lines.append("=" * 78)
    return "\n".join(lines)
