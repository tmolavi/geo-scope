"""
History Tracker & Feedback Loop Module
Tracks historical benchmark snapshots and computes before/after progression deltas.
"""

import os
import json
import time
from typing import Dict, Any, List, Optional

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "benchmark_history.json")


def save_benchmark_snapshot(analysis_results: Dict[str, Any], niche: str, brand: str, prompt_count: int) -> Dict[str, Any]:
    """
    Saves an execution snapshot to the persistent history log and computes progression deltas.
    """
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    history = load_all_history()

    snapshot_id = f"snap_{int(time.time())}"
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    current_summary = analysis_results.get("summary", {})
    current_sov = current_summary.get("overall_sov", 0.0)
    current_top1 = current_summary.get("overall_top1_rate", 0.0)

    # Find previous snapshot for the same brand and niche to compute delta
    previous_runs = [h for h in history if h.get("brand", "").lower() == brand.lower() and h.get("niche") == niche]
    
    delta_sov = 0.0
    delta_top1 = 0.0
    is_first_run = True

    if previous_runs:
        is_first_run = False
        last_run = previous_runs[-1]
        delta_sov = round(current_sov - last_run.get("overall_sov", 0.0), 1)
        delta_top1 = round(current_top1 - last_run.get("overall_top1_rate", 0.0), 1)

    record = {
        "id": snapshot_id,
        "timestamp": timestamp,
        "brand": brand,
        "niche": niche,
        "prompt_count": prompt_count,
        "overall_sov": current_sov,
        "overall_top1_rate": current_top1,
        "best_model": current_summary.get("best_performing_model", "N/A"),
        "delta_sov": delta_sov,
        "delta_top1": delta_top1,
        "is_first_run": is_first_run,
        "factors_summary": analysis_results.get("algorithmic_factors", {}).get("global_average_weights", {})
    }

    history.append(record)
    # Keep last 50 snapshots
    history = history[-50:]

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    return record


def load_all_history() -> List[Dict[str, Any]]:
    """
    Loads all historical audit snapshots.
    """
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def get_brand_progression(brand: str, niche: str) -> List[Dict[str, Any]]:
    """
    Returns time-series progression snapshots for a specific brand.
    """
    history = load_all_history()
    return [h for h in history if h.get("brand", "").lower() == brand.lower() and h.get("niche") == niche]
