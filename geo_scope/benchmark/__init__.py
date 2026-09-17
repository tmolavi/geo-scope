"""
GEO-Scope Public Benchmark & Evidence Dataset Module.
"""

from geo_scope.benchmark.models import (
    BenchmarkManifest,
    PromptRecord,
    ObservationRecord,
    CitationEvidenceRecord,
    BrandBenchmarkMetrics,
    ProviderBenchmarkMetrics,
    BenchmarkMetrics,
    MetricEstimate,
    StatisticalFactorAnalysis,
)
from geo_scope.benchmark.hasher import (
    compute_file_sha256,
    compute_dataset_checksums,
    compute_composite_hash,
    write_checksums_file,
    verify_dataset_checksums,
)
from geo_scope.benchmark.calculator import BenchmarkCalculator, calculate_bootstrap_ci
from geo_scope.benchmark.builder import BenchmarkBuilder
from geo_scope.benchmark.reproducer import BenchmarkReproducer

__all__ = [
    "BenchmarkManifest",
    "PromptRecord",
    "ObservationRecord",
    "CitationEvidenceRecord",
    "BrandBenchmarkMetrics",
    "ProviderBenchmarkMetrics",
    "BenchmarkMetrics",
    "MetricEstimate",
    "StatisticalFactorAnalysis",
    "compute_file_sha256",
    "compute_dataset_checksums",
    "compute_composite_hash",
    "write_checksums_file",
    "verify_dataset_checksums",
    "BenchmarkCalculator",
    "calculate_bootstrap_ci",
    "BenchmarkBuilder",
    "BenchmarkReproducer",
]
