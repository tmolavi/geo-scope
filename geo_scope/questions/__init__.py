"""Question discovery and prompt provenance package for GEO-Scope powered by AnswerPath GEO."""
from geo_scope.questions.models import DiscoveredQuestion, QuestionCluster, DiscoveryResult
from geo_scope.questions.answerpath_connector import AnswerPathConnector, extract_records
from geo_scope.questions.discovery import (
    discover_questions,
    prepare_benchmark_dataset,
    format_discovery_report,
)

__all__ = [
    "DiscoveredQuestion",
    "QuestionCluster",
    "DiscoveryResult",
    "AnswerPathConnector",
    "extract_records",
    "discover_questions",
    "prepare_benchmark_dataset",
    "format_discovery_report",
]
