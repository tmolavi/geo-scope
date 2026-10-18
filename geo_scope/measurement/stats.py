"""
Statistical Layer for GEO-Scope AI Visibility Measurement.
Implements:
  - Wilson Score Confidence Intervals (95%) for binomial rates
  - Bootstrap Resampling Confidence Intervals for continuous metrics & shares
  - Overlapping confidence interval detection & warnings
  - Rule-based confidence labeling (insufficient, directional, moderate, strong)
"""

import math
import random
from typing import Dict, Any, List, Optional, Tuple, Callable, Union


def get_z_score(confidence_level: float = 0.95) -> float:
    """
    Returns standard normal z-score for given two-tailed confidence level.
    Default 0.95 -> 1.959963984540054 (z = 1.96).
    """
    # Common quantiles table for exact precision without external scipy dependency
    known = {
        0.90: 1.6448536269514722,
        0.95: 1.959963984540054,
        0.98: 2.3263478740408408,
        0.99: 2.5758293035489004,
    }
    if confidence_level in known:
        return known[confidence_level]
    # Numerical approximation for arbitrary confidence levels
    p = 1.0 - (1.0 - confidence_level) / 2.0
    # Hastings approximation for probit
    t = math.sqrt(-2.0 * math.log(1.0 - p))
    c0, c1, c2 = 2.515517, 0.802853, 0.010328
    d1, d2, d3 = 1.432788, 0.189269, 0.001308
    return t - ((c2 * t + c1) * t + c0) / (((d3 * t + d2) * t + d1) * t + 1.0)


def wilson_score_interval(
    successes: int,
    total: int,
    confidence_level: float = 0.95,
) -> Dict[str, Any]:
    """
    Calculates the two-tailed Wilson score confidence interval for a binomial proportion.
    Handles n=0, k=0, and k=n with mathematical safety.

    Returns dict containing:
      - value: point estimate (k / n) or 0.0 if n=0
      - ci_method: "wilson"
      - confidence_level: float
      - ci_lower: float bounded in [0.0, 1.0]
      - ci_upper: float bounded in [0.0, 1.0]
      - ci_width: float
      - is_defined: bool (False if total == 0)
    """
    if total <= 0:
        return {
            "value": 0.0,
            "ci_method": "wilson",
            "confidence_level": confidence_level,
            "ci_lower": None,
            "ci_upper": None,
            "ci_width": None,
            "is_defined": False,
        }

    k = max(0, min(int(successes), int(total)))
    n = int(total)
    p_hat = k / n
    z = get_z_score(confidence_level)
    z_sq = z * z

    denom = 1.0 + z_sq / n
    center = (p_hat + (z_sq / (2.0 * n))) / denom
    spread = (z * math.sqrt((p_hat * (1.0 - p_hat) / n) + (z_sq / (4.0 * n * n)))) / denom

    ci_lower = max(0.0, round(center - spread, 4))
    ci_upper = min(1.0, round(center + spread, 4))

    return {
        "value": round(p_hat, 4),
        "ci_method": "wilson",
        "confidence_level": confidence_level,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "ci_width": round(ci_upper - ci_lower, 4),
        "is_defined": True,
    }


def bootstrap_confidence_interval(
    data: List[Union[int, float]],
    statistic_fn: Optional[Callable[[List[Union[int, float]]], float]] = None,
    n_resamples: int = 1000,
    confidence_level: float = 0.95,
    random_seed: int = 42,
) -> Dict[str, Any]:
    """
    Calculates a non-parametric percentile bootstrap confidence interval for arbitrary sample distributions.
    Deterministic via fixed random_seed.

    Returns dict containing:
      - value: sample statistic
      - ci_method: "bootstrap_percentile"
      - n_resamples: int
      - random_seed: int
      - confidence_level: float
      - ci_lower: float or None
      - ci_upper: float or None
      - ci_width: float or None
      - is_defined: bool
    """
    if not data or len(data) == 0:
        return {
            "value": None,
            "ci_method": "bootstrap_percentile",
            "n_resamples": n_resamples,
            "random_seed": random_seed,
            "confidence_level": confidence_level,
            "ci_lower": None,
            "ci_upper": None,
            "ci_width": None,
            "is_defined": False,
        }

    stat_fn = statistic_fn or (lambda x: sum(x) / len(x))
    point_val = round(stat_fn(data), 4)

    if len(data) == 1:
        return {
            "value": point_val,
            "ci_method": "bootstrap_percentile",
            "n_resamples": n_resamples,
            "random_seed": random_seed,
            "confidence_level": confidence_level,
            "ci_lower": point_val,
            "ci_upper": point_val,
            "ci_width": 0.0,
            "is_defined": True,
            "note": "single_observation_degenerate_ci",
        }

    rng = random.Random(random_seed)
    n = len(data)
    boot_stats = []

    for _ in range(n_resamples):
        resample = [data[rng.randint(0, n - 1)] for _ in range(n)]
        boot_stats.append(stat_fn(resample))

    boot_stats.sort()
    alpha = (1.0 - confidence_level) / 2.0
    lower_idx = int(math.floor(alpha * n_resamples))
    upper_idx = int(math.ceil((1.0 - alpha) * n_resamples)) - 1
    lower_idx = max(0, min(lower_idx, n_resamples - 1))
    upper_idx = max(0, min(upper_idx, n_resamples - 1))

    ci_lower = round(boot_stats[lower_idx], 4)
    ci_upper = round(boot_stats[upper_idx], 4)

    return {
        "value": point_val,
        "ci_method": "bootstrap_percentile",
        "n_resamples": n_resamples,
        "random_seed": random_seed,
        "confidence_level": confidence_level,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "ci_width": round(ci_upper - ci_lower, 4),
        "is_defined": True,
    }


def check_overlapping_ci(
    entity_a_ci: Union[Tuple[float, float], Dict[str, Any]],
    entity_b_ci: Union[Tuple[float, float], Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Checks if confidence intervals of two entities overlap.
    When overlapping, generates the mandatory scientific uncertainty warning.
    """
    def extract_bounds(val: Any) -> Tuple[Optional[float], Optional[float]]:
        if isinstance(val, dict):
            return val.get("ci_lower"), val.get("ci_upper")
        if isinstance(val, (list, tuple)) and len(val) >= 2:
            return float(val[0]), float(val[1])
        return None, None

    l_a, u_a = extract_bounds(entity_a_ci)
    l_b, u_b = extract_bounds(entity_b_ci)

    if l_a is None or u_a is None or l_b is None or u_b is None:
        return {
            "overlapping": False,
            "warning": None,
            "overlap_range": None,
        }

    overlap_lower = max(l_a, l_b)
    overlap_upper = min(u_a, u_b)
    is_overlap = overlap_lower <= overlap_upper

    if is_overlap:
        return {
            "overlapping": True,
            "warning": "The observed difference is within the uncertainty range of this sample.",
            "overlap_range": [round(overlap_lower, 4), round(overlap_upper, 4)],
        }
    return {
        "overlapping": False,
        "warning": None,
        "overlap_range": None,
    }


def generate_confidence_label(
    runs: int,
    coverage: float = 1.0,
    provenance_complete: bool = True,
    engine_breadth: int = 1,
    language_breadth: int = 1,
    human_validated: bool = False,
    ci_width: Optional[float] = None,
) -> str:
    """
    Computes rule-based confidence label for visibility metrics.
    Allowed outputs: 'insufficient', 'directional', 'moderate', 'strong'.
    Strictly forbids sensationalist terms like 'Guaranteed', 'Winner', or 'Dominant'.
    """
    if runs < 2 or coverage < 0.50 or not provenance_complete:
        return "insufficient"

    if runs < 5:
        return "directional"

    if ci_width is not None and ci_width > 0.40:
        return "directional"

    # Evaluates candidates for moderate vs strong
    if runs >= 5 and coverage >= 0.85:
        width_ok = (ci_width is None) or (ci_width <= 0.20)
        multi_engine = engine_breadth >= 3
        multi_lang_or_human = (language_breadth >= 2) or human_validated

        if width_ok and multi_engine and multi_lang_or_human:
            return "strong"
        return "moderate"

    return "directional"
