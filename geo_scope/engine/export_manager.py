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
        "query_id", "model", "intent", "language", "target_brand",
        "target_mentioned", "target_rank", "target_is_top_1", "target_sentiment",
        "citation_count", "response_length"
    ]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for r in records:
        writer.writerow({
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
            "response_length": r.get("response_length", 0)
        })
        
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
            writer.writerow({
                "query_id": q_id,
                "model": m_name,
                "domain": cite.get("domain"),
                "category": cite.get("category"),
                "url": cite.get("url")
            })
            
    return output.getvalue()


def export_full_json(analysis_results: Dict[str, Any], raw_prompts: List[Dict[str, Any]]) -> str:
    """
    Exports full analysis and prompt metadata to JSON.
    """
    payload = {
        "analysis": analysis_results,
        "sample_prompts": raw_prompts[:50]
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)
