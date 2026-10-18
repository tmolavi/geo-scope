"""
Export Manager Module
Exports benchmark datasets and reports into CSV, JSON, and Markdown formats.
"""

import csv
import io
import json
from typing import List, Dict, Any


def export_records_to_csv(records: List[Dict[str, Any]]) -> str:
    """
    Exports parsed query records into standard CSV format.
    """
    output = io.StringIO()
    fieldnames = [
        "query_id",
        "model",
        "intent",
        "language",
        "target_brand",
        "target_mentioned",
        "target_rank",
        "target_is_top_1",
        "target_sentiment",
        "execution_mode",
        "response_kind",
        "citation_basis",
        "target_mention_order",
        "citation_count",
        "response_length",
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for r in records:
        writer.writerow(
            {
                "execution_mode": r.get("provenance", {}).get("execution_mode", "unknown"),
                "response_kind": r.get("provenance", {}).get("response_kind", "unknown"),
                "citation_basis": r.get("citation_basis", "unknown"),
                "target_mention_order": r.get("target_mention_order"),
                "query_id": r.get("query_id"),
                "model": r.get("model"),
                "intent": r.get("intent"),
                "language": r.get("language"),
                "target_brand": r.get("target_brand"),
                "target_mentioned": "YES" if r.get("target_mentioned") else "NO",
                "target_rank": r.get("target_rank", 0),
                "target_is_top_1": "YES" if r.get("target_is_top_1") else "NO",
                "target_sentiment": r.get("target_sentiment", "neutral"),
                "citation_count": r.get("citation_count", 0),
                "response_length": r.get("response_length", 0),
            }
        )

    return output.getvalue()


def export_citations_to_csv(records: List[Dict[str, Any]]) -> str:
    """
    Exports all extracted citations and source domains into CSV.
    """
    output = io.StringIO()
    fieldnames = ["query_id", "model", "domain", "category", "url"]

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for r in records:
        q_id = r.get("query_id")
        m_name = r.get("model")
        for cite in r.get("citations", []):
            writer.writerow(
                {
                    "query_id": q_id,
                    "model": m_name,
                    "domain": cite.get("domain"),
                    "category": cite.get("category"),
                    "url": cite.get("url"),
                }
            )

    return output.getvalue()


def export_full_json(analysis_results: Dict[str, Any], raw_prompts: List[Dict[str, Any]]) -> str:
    """
    Exports full analysis and prompt metadata to JSON.
    """
    payload = {"analysis": analysis_results, "sample_prompts": raw_prompts[:50]}
    return json.dumps(payload, ensure_ascii=False, indent=2)


def export_contract_v1_metrics_to_csv(metrics_data: Dict[str, Any]) -> str:
    """
    Exports Minimum Measurement Contract v1.0 metrics into CSV with complete statistical uncertainty
    and denominator metadata.
    """
    output = io.StringIO()
    fieldnames = [
        "entity_id",
        "metric",
        "value",
        "numerator",
        "denominator",
        "denominator_type",
        "sample_size",
        "coverage",
        "status",
        "ci_method",
        "confidence_level",
        "ci_lower",
        "ci_upper",
        "confidence_label",
        "note",
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    entities = metrics_data.get("entities", {})
    for eid, edata in entities.items():
        v1_metrics = edata.get("contract_v1_metrics", {})
        conf_label = edata.get("confidence_label", "directional")
        for m_name, m_info in v1_metrics.items():
            if isinstance(m_info, dict):
                writer.writerow({
                    "entity_id": eid,
                    "metric": m_name,
                    "value": m_info.get("value"),
                    "numerator": m_info.get("numerator"),
                    "denominator": m_info.get("denominator"),
                    "denominator_type": m_info.get("denominator_type", ""),
                    "sample_size": m_info.get("sample_size", 0),
                    "coverage": m_info.get("coverage", 1.0),
                    "status": m_info.get("status", "measured"),
                    "ci_method": m_info.get("ci_method", ""),
                    "confidence_level": m_info.get("confidence_level", ""),
                    "ci_lower": m_info.get("ci_lower"),
                    "ci_upper": m_info.get("ci_upper"),
                    "confidence_label": conf_label,
                    "note": m_info.get("note", ""),
                })

    return output.getvalue()

