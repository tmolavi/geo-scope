"""
GEO-Scope: Generative Engine Optimization (GEO) & AI Visibility Reverse-Engineering Platform
An open-source scientific framework for reverse-engineering LLM ranking factors and citation algorithms.
"""

__version__ = "1.0.0"
__author__ = "GEO-Scope Community & Contributors"
__license__ = "MIT"

from geo_scope.engine.query_generator import generate_prompt_dataset, INDUSTRY_PRESETS
from geo_scope.engine.feature_extractor import parse_model_response, extract_citations_and_domains, detect_brand_positions
from geo_scope.engine.model_runner import ModelRunner
from geo_scope.engine.algo_analyzer import AlgoAnalyzer
from geo_scope.engine.strategy_builder import generate_geo_playbook

__all__ = [
    "__version__",
    "generate_prompt_dataset",
    "INDUSTRY_PRESETS",
    "parse_model_response",
    "extract_citations_and_domains",
    "detect_brand_positions",
    "ModelRunner",
    "AlgoAnalyzer",
    "generate_geo_playbook",
]
