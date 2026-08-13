"""
Query Loader Module for Bring Your Own Prompts (BYOP)
Loads and standardizes custom user prompt datasets from CSV, JSON, TXT, and YAML files.
"""

import os
import csv
import json
from typing import List, Dict, Any, Optional


def load_custom_prompts(
    file_path: str,
    default_brand: str = "My Brand",
    default_competitors: Optional[List[str]] = None,
    default_niche: str = "custom_benchmark"
) -> List[Dict[str, Any]]:
    """
    Parses a user-supplied prompt dataset file into standard GEO-Scope prompt objects.
    Supports .csv, .json, .txt, .yaml/.yml formats.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Prompts file not found at: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    raw_prompts = []

    if ext == ".csv":
        raw_prompts = _load_from_csv(file_path)
    elif ext == ".json":
        raw_prompts = _load_from_json(file_path)
    elif ext in [".txt", ""]:
        raw_prompts = _load_from_txt(file_path)
    elif ext in [".yaml", ".yml"]:
        raw_prompts = _load_from_yaml(file_path)
    else:
        # Fallback to plain text
        raw_prompts = _load_from_txt(file_path)

    if not raw_prompts:
        raise ValueError(f"No valid prompts found in file: {file_path}")

    # Standardize metadata
    standardized = []
    comps = default_competitors or ["Competitor A", "Competitor B"]
    all_brands = [default_brand] + [c for c in comps if c != default_brand]

    for idx, item in enumerate(raw_prompts, 1):
        if isinstance(item, str):
            query_text = item.strip()
            intent = _infer_intent(query_text)
            lang = "fa" if any('\u0600' <= ch <= '\u06FF' for ch in query_text) else "en"
            standardized.append({
                "id": f"byop_{idx:04d}",
                "query": query_text,
                "intent": intent,
                "language": lang,
                "niche": default_niche,
                "target_brand": default_brand,
                "primary_subject": default_brand,
                "expected_entities": all_brands,
                "difficulty": "user_defined"
            })
        elif isinstance(item, dict):
            query_text = item.get("query") or item.get("prompt") or item.get("question") or item.get("text") or ""
            if not query_text:
                continue
            intent = item.get("intent") or _infer_intent(query_text)
            lang = item.get("language") or ("fa" if any('\u0600' <= ch <= '\u06FF' for ch in query_text) else "en")
            standardized.append({
                "id": item.get("id", f"byop_{idx:04d}"),
                "query": query_text.strip(),
                "intent": intent,
                "language": lang,
                "niche": item.get("niche", default_niche),
                "target_brand": item.get("target_brand", default_brand),
                "primary_subject": item.get("primary_subject", default_brand),
                "expected_entities": item.get("expected_entities", all_brands),
                "difficulty": item.get("difficulty", "user_defined")
            })

    return standardized


def _load_from_csv(path: str) -> List[Dict[str, Any]]:
    prompts = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        # Detect delimiter
        sample = f.read(2048)
        f.seek(0)
        delimiter = ","
        if "\t" in sample and "," not in sample:
            delimiter = "\t"
        elif ";" in sample and "," not in sample:
            delimiter = ";"

        reader = csv.DictReader(f, delimiter=delimiter)
        if reader.fieldnames:
            # Look for query column
            query_col = None
            for col in reader.fieldnames:
                if col.lower() in ["query", "prompt", "question", "text", "keyword", "search_term"]:
                    query_col = col
                    break
            if not query_col:
                query_col = reader.fieldnames[0]

            for row in reader:
                q = row.get(query_col, "").strip()
                if q:
                    prompts.append({
                        "query": q,
                        "intent": row.get("intent", "").strip(),
                        "language": row.get("language", "").strip(),
                        "niche": row.get("niche", "").strip()
                    })
        else:
            # Plain lines
            f.seek(0)
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    prompts.append(line)
    return prompts


def _load_from_json(path: str) -> List[Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        if "prompts" in data and isinstance(data["prompts"], list):
            return data["prompts"]
        elif "queries" in data and isinstance(data["queries"], list):
            return data["queries"]
    return []


def _load_from_txt(path: str) -> List[str]:
    prompts = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                prompts.append(line)
    return prompts


def _load_from_yaml(path: str) -> List[Any]:
    try:
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "prompts" in data:
            return data["prompts"]
    except ImportError:
        return _load_from_txt(path)
    return []


def _infer_intent(query: str) -> str:
    q = query.lower()
    if any(w in q for w in ["vs", "compare", "comparison", "alternative", "versus", "مقایسه", "تفاوت", "جایگزین"]):
        return "comparative"
    if any(w in q for w in ["how to", "how do", "fix", "solve", "guide", "tutorial", "چگونه", "چطور", "حل مشکل", "راهنما"]):
        return "problem_solving"
    if any(w in q for w in ["review", "scam", "complaint", "reddit", "trust", "is it good", "نظر", "معایب", "شکایت", "اعتبار"]):
        return "reputation_sentiment"
    if any(w in q for w in ["best", "top", "pricing", "cost", "cheap", "buy", "بهترین", "قیمت", "خرید", "برترین"]):
        return "commercial_direct"
    return "long_tail_niche"
