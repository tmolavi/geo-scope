"""
GEO-Scope Public Research Integrity Test Suite.

Verifies the 6 foundational empirical measurement guarantees:
1. Demo / Simulation output contains strictly simulated metrics and cannot masquerade as live.
2. Live provider failures strictly record errors and NEVER silently fall back to simulation.
3. Person mentions are strictly distinguished from brand mentions.
4. Homonyms and negative collision terms (do_not_confuse) do not create false-positive brand mentions.
5. Informational / entity-lookup queries are marked unscored for recommendation/rank metrics.
6. Offline replay produces deterministic, cryptographically verifiable evidence bundles.
"""

import asyncio
import json
import pytest
from pathlib import Path

from geo_scope.entities.models import Entity
from geo_scope.entities.registry import EntityRegistry
from geo_scope.measurement.engine import MeasurementEngine
from geo_scope.measurement.replay import ReplayEngine
from geo_scope.parser.observation_parser import ObservationParser, classify_query_intent
from geo_scope.benchmark.hasher import verify_dataset_checksums
from geo_scope.providers.base import BaseProvider
from geo_scope.providers.models import ProviderResponse
from geo_scope.providers.registry import ProviderRegistry


class MockLiveFailingProvider(BaseProvider):
    """Simulates a real API provider failure (500/504)."""
    def __init__(self, name="mock_fail_api"):
        super().__init__(name=name, display_name="Mock Failing API", bias_description="Always fails")
        self.provider_class = "answer_engine"

    async def generate_response(self, prompt_item):
        raise TimeoutError("Live Provider Timeout")

    async def generate(self, prompt_item, execution_mode="live") -> ProviderResponse:
        return ProviderResponse(
            provider=self.name,
            model="mock-failing-model",
            status="failed",
            error={"code": "TIMEOUT_504", "message": "Live Gateway Timeout: Upstream endpoint did not respond"},
            execution_mode=execution_mode,
            provider_class=self.provider_class,
        )


def test_1_demo_cannot_generate_live_metrics(tmp_path):
    """Guarantee 1: Demo / simulation generates simulated_* metrics with clear simulation metadata."""
    entities = EntityRegistry.from_list([
        {"id": "brand_a", "names": ["BrandA", "برند آ"], "domains": ["branda.com"]},
    ])
    engine = MeasurementEngine(entities=entities)
    prompts = [
        {"id": "q1", "query": "بهترین برند کدام است؟", "source_type": "hypothesis", "intent": "recommendation"}
    ]

    out_dir = tmp_path / "demo_run"
    res = asyncio.run(engine.execute_measurement(
        prompts=prompts,
        providers=["perplexity_sonar"],
        out_dir=out_dir,
        mode="simulation",
        seed=100,
    ))

    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["mode"] == "simulation"

    metrics = json.loads((out_dir / "metrics.json").read_text(encoding="utf-8"))
    assert metrics["mode"] == "simulation"
    assert "simulated_mention_rate" in metrics["entities"]["brand_a"]
    assert "simulated_recommendation_rate" in metrics["entities"]["brand_a"]
    # Verify no raw live metrics masquerading
    assert "observed_mention_rate" not in metrics["entities"]["brand_a"]


def test_2_live_failures_never_fallback_to_simulation(tmp_path):
    """Guarantee 2: Live measurement failure never generates synthetic responses."""
    entities = EntityRegistry.from_list([
        {"id": "brand_a", "names": ["BrandA", "برند آ"], "domains": ["branda.com"]},
    ])
    reg = ProviderRegistry()
    reg.register(MockLiveFailingProvider(name="mock_fail_api"))

    engine = MeasurementEngine(entities=entities, registry=reg)
    prompts = [
        {"id": "q1", "query": "بهترین برند", "source_type": "observed", "intent": "recommendation"}
    ]

    out_dir = tmp_path / "live_strict_failure"
    res = asyncio.run(engine.execute_measurement(
        prompts=prompts,
        providers=["mock_fail_api"],
        out_dir=out_dir,
        mode="live",
    ))

    # Error must be explicitly tracked
    assert res["n_errors"] == 1
    error_lines = (out_dir / "errors.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(error_lines) == 1
    err_obj = json.loads(error_lines[0])
    assert err_obj["error"]["code"] == "TIMEOUT_504"

    # Raw response must be marked failed with zero synthetic content
    raw_lines = (out_dir / "raw_responses.jsonl").read_text(encoding="utf-8").strip().splitlines()
    raw_obj = json.loads(raw_lines[0])
    assert raw_obj["status"] == "failed"
    assert raw_obj["response_text"] == ""
    assert raw_obj["execution_mode"] == "live"


def test_3_person_mention_does_not_count_as_brand_mention():
    """Guarantee 3: Mentioning a founder or spokesperson does not count as brand mention."""
    parser = ObservationParser()
    entity = Entity(
        id="inten",
        names=["Inten", "اینتن"],
        people=["Taghi Molavi", "تقی مولوی"],
        domains=["inten.asia"],
    )

    response_text = "تقی مولوی یکی از پژوهشگران و سخنرانان حوزه وب است."
    obs = parser.parse(response_text, entity, query="تقی مولوی")

    assert obs.person_mentioned is True
    assert obs.mentioned is False
    assert obs.recommended is False
    assert obs.top1 is False


def test_4_negative_homonyms_do_not_create_false_positives():
    """Guarantee 4: Homonyms and collision phrases are excluded and flagged in confused_with."""
    parser = ObservationParser()
    entity = Entity(
        id="novin",
        names=["Novin", "نوین"],
        domains=["novin.com"],
        do_not_confuse=["بانک اقتصاد نوین", "نوین چرم", "بیمه نوین"],
    )

    response_text = "برای افتتاح حساب قرض‌الحسنه می‌توانید به شعب بانک اقتصاد نوین مراجعه نمایید."
    obs = parser.parse(response_text, entity, query="بانک های فعال")

    assert obs.mentioned is False
    assert "بانک اقتصاد نوین" in obs.confused_with


def test_5_informational_queries_are_unscored():
    """Guarantee 5: Informational entity lookups yield scoring_status='unscored' for recommendation metrics."""
    parser = ObservationParser()
    entity = Entity(
        id="inten",
        names=["Inten", "اینتن"],
        domains=["inten.asia"],
    )

    info_query = "تاریخچه شرکت اینتن چیست؟"
    assert classify_query_intent(info_query) == "informational"

    response_text = "شرکت اینتن در زمینه طراحی سایت و سئو در دهه ۹۰ خورشیدی تاسیس شد."
    obs = parser.parse(response_text, entity, query=info_query)

    assert obs.mentioned is True
    assert obs.scoring_status == "unscored"
    assert obs.recommended is False
    assert obs.top1 is False
    assert obs.rank is None


def test_6_replay_produces_deterministic_matching_checksums(tmp_path):
    """Guarantee 6: Deterministic offline replay re-computes observations and produces valid SHA-256 package."""
    entities = EntityRegistry.from_list([
        {"id": "web24", "names": ["Web24", "وب24"], "domains": ["web24.ir"]},
        {"id": "novin", "names": ["Novin", "نوین"], "domains": ["novin.com"]},
    ])
    engine = MeasurementEngine(entities=entities)
    prompts = [
        {"id": "q1", "query": "بهترین شرکت های سئو کدامند؟", "source_type": "observed", "intent": "recommendation"},
        {"id": "q2", "query": "مقایسه وب ۲۴ و نوین", "source_type": "observed", "intent": "comparative"},
    ]

    source_dir = tmp_path / "source_run"
    asyncio.run(engine.execute_measurement(
        prompts=prompts,
        providers=["perplexity_sonar"],
        out_dir=source_dir,
        mode="simulation",
        seed=42,
    ))

    # Replay 1
    replay_dir_1 = tmp_path / "replay_run_1"
    replayer = ReplayEngine(entities=entities)
    res_1 = replayer.replay(input_path=source_dir, out_dir=replay_dir_1)

    # Replay 2 (same input)
    replay_dir_2 = tmp_path / "replay_run_2"
    res_2 = replayer.replay(input_path=source_dir, out_dir=replay_dir_2)

    # Verify cryptographic integrity of both replay outputs
    chk_1 = verify_dataset_checksums(replay_dir_1)
    chk_2 = verify_dataset_checksums(replay_dir_2)

    assert chk_1["valid"] is True
    assert chk_2["valid"] is True

    # Check that observations and metrics match exactly between replay 1 and replay 2
    obs_1 = (replay_dir_1 / "observations.jsonl").read_text(encoding="utf-8")
    obs_2 = (replay_dir_2 / "observations.jsonl").read_text(encoding="utf-8")
    assert obs_1 == obs_2

    met_1 = json.loads((replay_dir_1 / "metrics.json").read_text(encoding="utf-8"))
    met_2 = json.loads((replay_dir_2 / "metrics.json").read_text(encoding="utf-8"))
    assert met_1["entities"] == met_2["entities"]
