"""
Golden Parser Evaluation Framework for GEO-Scope.
Evaluates the deterministic ObservationParser against human-labeled golden datasets.
Produces granular precision, recall, F1, accuracy, and support metrics per field, language, and category.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from geo_scope.entities.registry import EntityRegistry
from geo_scope.parser.observation_parser import ObservationParser, ObservationParsedResult


def calculate_binary_metrics(actual_list: List[bool], expected_list: List[bool]) -> Dict[str, Any]:
    """Calculates precision, recall, f1, accuracy, and support for binary labels."""
    tp = sum(1 for a, e in zip(actual_list, expected_list) if a and e)
    fp = sum(1 for a, e in zip(actual_list, expected_list) if a and not e)
    fn = sum(1 for a, e in zip(actual_list, expected_list) if not a and e)
    tn = sum(1 for a, e in zip(actual_list, expected_list) if not a and not e)
    total = len(actual_list)

    precision = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 1.0
    recall = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 1.0
    f1 = round(2 * precision * recall / (precision + recall), 4) if (precision + recall) > 0 else 1.0
    accuracy = round((tp + tn) / total, 4) if total > 0 else 1.0

    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "accuracy": accuracy,
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": tn,
        "support": sum(1 for e in expected_list if e),
        "total_evaluated": total,
    }


def evaluate_golden_set(
    golden_set_dir: Union[str, Path],
    output_file: Optional[Union[str, Path]] = None,
    entities_file: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """
    Evaluates ObservationParser against a golden dataset directory.
    Expects 'golden_dataset.jsonl' and 'entities.json' in golden_set_dir.
    """
    base_dir = Path(golden_set_dir)
    if base_dir.is_dir():
        if (base_dir / "golden_examples.jsonl").exists():
            dataset_path = base_dir / "golden_examples.jsonl"
        else:
            dataset_path = base_dir / "golden_dataset.jsonl"
    else:
        dataset_path = base_dir
    
    if entities_file:
        ent_path = Path(entities_file)
    elif base_dir.is_dir() and (base_dir / "entities.json").exists():
        ent_path = base_dir / "entities.json"
    else:
        ent_path = Path("benchmark/golden_sets/v1/entities.json")

    if not dataset_path.is_file():
        raise FileNotFoundError(f"Golden dataset file not found: {dataset_path}")
    if not ent_path.is_file():
        raise FileNotFoundError(f"Entities file not found: {ent_path}")

    registry = EntityRegistry.load_from_file(ent_path)
    parser = ObservationParser()

    records: List[Dict[str, Any]] = []
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    # Field trackers
    fields = ["mentioned", "recommended", "cited", "attributed", "wrong_entity"]
    actuals: Dict[str, List[bool]] = {f: [] for f in fields}
    expecteds: Dict[str, List[bool]] = {f: [] for f in fields}

    # Rank and intent trackers
    rank_matches = 0
    rank_total = 0
    intent_matches = 0
    intent_total = 0

    # Per-language tracking
    by_lang: Dict[str, Dict[str, List[bool]]] = {}
    by_lang_expected: Dict[str, Dict[str, List[bool]]] = {}

    mismatches: List[Dict[str, Any]] = []

    for item in records:
        gid = item.get("id") or item.get("golden_id", "unknown")
        query = item.get("query", "")
        resp_text = item.get("response") or item.get("response_text", "")
        ent_id = item.get("entity_id", "")
        exp = item.get("expected", {})
        meta = item.get("metadata", {})
        lang = item.get("language") or meta.get("language", "unknown")

        entity = registry.get(ent_id)
        if not entity:
            raise ValueError(f"Golden record {gid} references unknown entity_id '{ent_id}'")

        # Run parser
        res: ObservationParsedResult = parser.parse(resp_text, entity, query=query)

        # Track per field
        field_mismatch = {}
        for f in fields:
            act_val = getattr(res, f, False)
            exp_val = exp.get(f, False)
            actuals[f].append(bool(act_val))
            expecteds[f].append(bool(exp_val))

            if lang not in by_lang:
                by_lang[lang] = {fld: [] for fld in fields}
                by_lang_expected[lang] = {fld: [] for fld in fields}
            by_lang[lang][f].append(bool(act_val))
            by_lang_expected[lang][f].append(bool(exp_val))

            if act_val != exp_val:
                field_mismatch[f] = {"expected": exp_val, "actual": act_val}

        # Check rank
        exp_rank = exp.get("rank")
        act_rank = res.rank
        if exp_rank is not None or act_rank is not None:
            rank_total += 1
            if exp_rank == act_rank:
                rank_matches += 1
            else:
                field_mismatch["rank"] = {"expected": exp_rank, "actual": act_rank}

        # Check intent
        exp_intent = item.get("intent_type") or exp.get("intent_type")
        if exp_intent:
            intent_total += 1
            if exp_intent == res.intent_type:
                intent_matches += 1
            else:
                field_mismatch["intent_type"] = {"expected": exp_intent, "actual": res.intent_type}

        if field_mismatch:
            mismatches.append({
                "golden_id": gid,
                "entity_id": ent_id,
                "language": lang,
                "mismatches": field_mismatch,
                "query": query,
                "response_snippet": resp_text[:120] + "..." if len(resp_text) > 120 else resp_text,
            })

    # Aggregate global metrics
    field_metrics = {f: calculate_binary_metrics(actuals[f], expecteds[f]) for f in fields}
    
    rank_accuracy = round(rank_matches / rank_total, 4) if rank_total > 0 else 1.0
    intent_accuracy = round(intent_matches / intent_total, 4) if intent_total > 0 else 1.0

    # Language breakdown
    lang_metrics = {}
    for l_code, l_acts in by_lang.items():
        lang_metrics[l_code] = {
            f: calculate_binary_metrics(l_acts[f], by_lang_expected[l_code][f])
            for f in fields
        }

    evaluated_entities = sorted(list(set(r.get("entity_id") for r in records if r.get("entity_id"))))
    evaluated_languages = sorted(list(by_lang.keys()))

    report = {
        "dataset": str(dataset_path),
        "dataset_size": len(records),
        "total_records": len(records),
        "languages": evaluated_languages,
        "entities": evaluated_entities,
        "fields_evaluated": fields,
        "total_mismatches": len(mismatches),
        "overall_accuracy": round((len(records) - len(mismatches)) / len(records), 4) if records else 1.0,
        "metrics_by_field": field_metrics,
        "rank_evaluation": {
            "evaluated_count": rank_total,
            "exact_matches": rank_matches,
            "rank_accuracy": rank_accuracy,
        },
        "intent_evaluation": {
            "evaluated_count": intent_total,
            "exact_matches": intent_matches,
            "intent_accuracy": intent_accuracy,
        },
        "metrics_by_language": lang_metrics,
        "confidence_notes": [
            "Entity resolution employs Unicode NFKC normalization, Persian/Arabic letter normalization, ZWNJ stripping, and continuous unspaced matching.",
            "Attribution is strictly separated from citation: attribution requires explicit sourcing prose while citation requires domain/URL presence.",
            "Homonym collisions (e.g., poet vs founder, market vs company) are filtered via negative constraints.",
        ],
        "limitations": [
            "Evaluation scores reflect the specific composition and balance of this versioned golden set.",
            "Open-ended natural language variation outside tested patterns may exhibit different precision/recall characteristics.",
            "Heuristic intent classification serves exploratory categorization rather than definitive user intent parsing.",
        ],
        "warning": "Evaluation results depend on the composition of the golden dataset.",
        "mismatches": mismatches,
    }

    if output_file:
        out_p = Path(output_file)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    return report
