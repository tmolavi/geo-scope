"""
Unit and Integration Tests for EventAnnotationService & Algorithm Timeline Registry.
Validates:
  - Canonical event registration (Nov 2026 Core Update, Gemini 4 Hydrogen, OpenAI Hub/Wallet)
  - Date filtering and active event detection
  - Provider and event type filtering
  - MetricRecord and run provenance metadata enrichment with algorithmic_regime
  - JSON serialization and deserialization
"""

from datetime import datetime, timezone
import json
import pytest

from geo_scope.measurement.timeline import (
    EventRecord,
    EventAnnotationService,
    CANONICAL_EVENTS,
)
from geo_scope.measurement.denominators import MetricRecord


def test_canonical_events_loaded():
    service = EventAnnotationService(include_canonical=True)
    events = service.list_events()
    assert len(events) >= 5

    core_up = service.get_event("google_core_update_nov_2026")
    assert core_up is not None
    assert core_up.provider == "google"
    assert core_up.event_type == "core_update"
    assert core_up.status == "active"
    assert "https://status.search.google.com/" in core_up.source_url


def test_active_events_at_specific_timestamp():
    service = EventAnnotationService(include_canonical=True)
    
    # Check Nov 12, 2026 (during November Core Update)
    active_nov12 = service.get_active_events_at("2026-11-12T12:00:00Z")
    active_ids = [e.event_id for e in active_nov12]
    assert "google_core_update_nov_2026" in active_ids
    assert "google_gemini_4_hydrogen_search" in active_ids

    # Check Nov 01, 2026 (before Nov Core Update started on Nov 10)
    active_nov01 = service.get_active_events_at("2026-11-01T12:00:00Z")
    nov01_ids = [e.event_id for e in active_nov01]
    assert "google_core_update_nov_2026" not in nov01_ids


def test_provider_filter():
    service = EventAnnotationService(include_canonical=True)
    google_events = service.list_events(provider="google")
    assert all(e.provider == "google" or e.provider == "all" for e in google_events)
    assert any(e.event_id == "google_core_update_nov_2026" for e in google_events)

    openai_events = service.list_events(provider="openai")
    assert any(e.event_id == "openai_businesses_hub_beta" for e in openai_events)


def test_annotate_run_provenance():
    service = EventAnnotationService(include_canonical=True)
    base_prov = {
        "execution_mode": "live",
        "model": "google_search",
        "benchmark_id": "bench_test_01",
    }
    enriched = service.annotate_run_provenance(base_prov, timestamp="2026-11-15T00:00:00Z")
    assert "algorithmic_regime" in enriched
    regime = enriched["algorithmic_regime"]
    assert regime["is_unstable_regime"] is True
    assert "google_core_update_nov_2026" in regime["active_event_ids"]
    assert regime["active_event_count"] >= 1


def test_metric_record_with_algorithmic_regime():
    record = MetricRecord(
        metric="citation_rate",
        value=0.75,
        numerator=3,
        denominator=4,
        denominator_type="answers_with_any_citation",
        sample_size=4,
        algorithmic_regime={"is_unstable_regime": True, "active_event": "google_core_update_nov_2026"},
    )
    d = record.to_dict()
    assert d["algorithmic_regime"]["is_unstable_regime"] is True


def test_json_roundtrip():
    service = EventAnnotationService(include_canonical=True)
    json_str = service.to_json()
    reloaded = EventAnnotationService.from_json(json_str)
    assert len(reloaded.list_events()) == len(service.list_events())
    assert reloaded.get_event("google_core_update_nov_2026") is not None
