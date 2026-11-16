"""
Event Annotation Service and Algorithm Timeline Registry for GEO-Scope.
Tracks major search engine algorithmic updates, AI model version shifts,
and SERP compositional changes to decouple systemic search volatility
from on-page content and brand optimization signals.

(c) 2026 Taqi Molavi — https://molavi.pro — MIT License
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union


@dataclass
class EventRecord:
    """Represents a discrete algorithmic, model, or SERP change event."""
    event_id: str
    title: str
    event_type: str  # "core_update" | "model_upgrade" | "serp_ui_change" | "crawler_policy"
    provider: str    # "google" | "openai" | "anthropic" | "perplexity" | "all"
    start_date: str  # ISO-8601 (e.g. "2026-11-10T00:00:00Z")
    end_date_estimated: Optional[str] = None  # ISO-8601 or None if ongoing/instantaneous
    status: str = "active"  # "active" | "completed" | "upcoming"
    description: str = ""
    source_url: str = ""
    affected_surfaces: List[str] = field(default_factory=lambda: ["organic", "ai_overviews"])
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EventRecord:
        return cls(**data)


CANONICAL_EVENTS: List[EventRecord] = [
    EventRecord(
        event_id="google_core_update_nov_2026",
        title="Google November 2026 Core Update",
        event_type="core_update",
        provider="google",
        start_date="2026-11-10T10:07:00Z",
        end_date_estimated="2026-11-24T23:59:59Z",
        status="active",
        description="Global core update rolling out over approximately two weeks across all languages and regions.",
        source_url="https://status.search.google.com/",
        affected_surfaces=["organic", "ai_overviews", "search_console"],
        metadata={"rollout_scope": "global", "languages": "all", "seasonality_overlap": "Q4_shopping"}
    ),
    EventRecord(
        event_id="google_gemini_4_hydrogen_search",
        title="Google Search Upgrade to Gemini 4 Hydrogen",
        event_type="model_upgrade",
        provider="google",
        start_date="2026-11-08T00:00:00Z",
        end_date_estimated=None,
        status="completed",
        description="Default search model upgraded to Gemini 4 Hydrogen, enabling deep Query Fan-Out, multimodal comparisons, and subtopic parallel retrieval.",
        source_url="https://blog.google/products-and-platforms/products/search/gemini-4-hydrogen-search-upgrade/",
        affected_surfaces=["ai_overviews", "ai_mode", "complex_queries"],
        metadata={"query_fan_out": True, "context_window": "1M_tokens"}
    ),
    EventRecord(
        event_id="openai_businesses_hub_beta",
        title="OpenAI Businesses in ChatGPT & Business Hub Beta",
        event_type="model_upgrade",
        provider="openai",
        start_date="2026-11-10T09:00:00Z",
        end_date_estimated=None,
        status="active",
        description="Verified business profiles, direct Shopify catalog synchronization, and in-chat business agent discovery in ChatGPT search.",
        source_url="https://openai.com",
        affected_surfaces=["chatgpt_search", "business_hub"],
        metadata={"market": "US_initial", "shopify_integration": True}
    ),
    EventRecord(
        event_id="openai_chatgpt_wallet",
        title="OpenAI ChatGPT Wallet Agentic Checkout",
        event_type="serp_ui_change",
        provider="openai",
        start_date="2026-11-13T12:00:00Z",
        end_date_estimated=None,
        status="active",
        description="Direct in-chat biometric authentication and transactional execution for product recommendations.",
        source_url="https://openai.com",
        affected_surfaces=["chatgpt_search", "agentic_commerce"],
        metadata={"payment_layer": True}
    ),
    EventRecord(
        event_id="sistrix_aio_commercial_surge",
        title="SISTRIX UK Telemetry: AIO Coverage Surpasses 80%",
        event_type="serp_ui_change",
        provider="google",
        start_date="2026-11-05T00:00:00Z",
        end_date_estimated=None,
        status="active",
        description="Measured acceleration of AI Overviews into commercial and retail intents, reaching 80.7% on UK Visibility Index keywords.",
        source_url="https://www.sistrix.com/blog/ai-overviews-climb-e-commerce-sites-now-exposed-uk-data/",
        affected_surfaces=["ai_overviews", "e_commerce"],
        metadata={"index_exposure": 0.807, "region": "UK"}
    ),
]


class EventAnnotationService:
    """Service for managing search update events and annotating measurement records."""

    def __init__(self, include_canonical: bool = True):
        self._events: Dict[str, EventRecord] = {}
        if include_canonical:
            for ev in CANONICAL_EVENTS:
                self.register_event(ev)

    def register_event(self, event: EventRecord) -> None:
        self._events[event.event_id] = event

    def get_event(self, event_id: str) -> Optional[EventRecord]:
        return self._events.get(event_id)

    def list_events(
        self,
        provider: Optional[str] = None,
        event_type: Optional[str] = None,
        active_only: bool = False,
    ) -> List[EventRecord]:
        results = list(self._events.values())
        if provider:
            results = [e for e in results if e.provider.lower() == provider.lower() or e.provider == "all"]
        if event_type:
            results = [e for e in results if e.event_type == event_type]
        if active_only:
            results = [e for e in results if e.status == "active"]
        return results

    @staticmethod
    def _parse_timestamp(ts: Union[str, datetime]) -> datetime:
        if isinstance(ts, datetime):
            if ts.tzinfo is None:
                return ts.replace(tzinfo=timezone.utc)
            return ts
        # Parse ISO string
        clean_ts = ts.replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(clean_ts)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            return datetime.now(timezone.utc)

    def get_active_events_at(
        self,
        timestamp: Optional[Union[str, datetime]] = None,
        provider: Optional[str] = None,
    ) -> List[EventRecord]:
        """Finds all events active at a specific timestamp."""
        check_dt = self._parse_timestamp(timestamp) if timestamp else datetime.now(timezone.utc)
        active: List[EventRecord] = []
        for ev in self._events.values():
            if provider and ev.provider.lower() != provider.lower() and ev.provider != "all":
                continue
            start_dt = self._parse_timestamp(ev.start_date)
            if check_dt < start_dt:
                continue
            if ev.end_date_estimated:
                end_dt = self._parse_timestamp(ev.end_date_estimated)
                if check_dt > end_dt:
                    continue
            elif ev.status == "completed" and (check_dt - start_dt).days > 30:
                # Historical completed events fade from active annotation after 30 days
                continue
            active.append(ev)
        return active

    def annotate_run_provenance(
        self,
        provenance_dict: Dict[str, Any],
        timestamp: Optional[Union[str, datetime]] = None,
        provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Injects algorithmic_regime and active_events into provenance metadata."""
        active = self.get_active_events_at(timestamp, provider=provider)
        enriched = dict(provenance_dict)
        enriched["algorithmic_regime"] = {
            "is_unstable_regime": any(e.event_type == "core_update" and e.status == "active" for e in active),
            "active_event_ids": [e.event_id for e in active],
            "active_event_count": len(active),
            "events_summary": [
                {"id": e.event_id, "title": e.title, "type": e.event_type, "status": e.status}
                for e in active
            ],
        }
        return enriched

    def to_json(self) -> str:
        return json.dumps([e.to_dict() for e in self._events.values()], indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> EventAnnotationService:
        service = cls(include_canonical=False)
        data = json.loads(json_str)
        for item in data:
            service.register_event(EventRecord.from_dict(item))
        return service
