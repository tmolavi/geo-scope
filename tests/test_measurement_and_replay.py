"""
Tests for MeasurementEngine and ReplayEngine integrity.
"""

import hashlib
import json
import pytest
from pathlib import Path

from geo_scope.entities.registry import EntityRegistry
from geo_scope.measurement.engine import MeasurementEngine
from geo_scope.measurement.replay import ReplayEngine
from geo_scope.providers.base import BaseProvider
from geo_scope.providers.models import ProviderResponse
from geo_scope.providers.registry import ProviderRegistry


class MockFailingProvider(BaseProvider):
    def __init__(self, name="mock_fail"):
        super().__init__(name=name, display_name="Failing Provider", bias_description="Fails always")
        self.provider_class = "answer_engine"

    async def generate_response(self, prompt_item):
        raise RuntimeError("Simulated Gateway Timeout 504")

    async def generate(self, prompt_item, execution_mode="live") -> ProviderResponse:
        return ProviderResponse(
            provider=self.name,
            model="failing-model",
            status="failed",
            error={"code": "API_TIMEOUT", "message": "Simulated Gateway Timeout 504"},
            execution_mode=execution_mode,
            provider_class=self.provider_class,
        )


def test_measurement_simulation_bundle(tmp_path):
    entities = EntityRegistry.from_list([
        {"id": "inten", "names": ["Inten", "اینتن"], "people": ["تقی مولوی"], "domains": ["inten.asia"]},
        {"id": "web24", "names": ["Web24", "وب24"], "people": ["رضا شیرازی"], "domains": ["web24.ir"]},
    ])
    engine = MeasurementEngine(entities=entities)

    prompts = [
        {"id": "p1", "query": "بهترین شرکت سئو در ایران", "source_type": "observed", "intent": "recommendation"},
        {"id": "p2", "query": "تقی مولوی کیست؟", "source_type": "observed", "intent": "informational"},
    ]

    out_dir = tmp_path / "sim_run"
    import asyncio
    res = asyncio.run(engine.execute_measurement(
        prompts=prompts,
        providers=["perplexity_sonar", "gemini_grounding"],
        out_dir=out_dir,
        mode="simulation",
        seed=42,
    ))

    assert (out_dir / "manifest.json").exists()
    assert (out_dir / "prompts.jsonl").exists()
    assert (out_dir / "raw_responses.jsonl").exists()
    assert (out_dir / "observations.jsonl").exists()
    assert (out_dir / "metrics.json").exists()
    assert (out_dir / "errors.jsonl").exists()
    assert (out_dir / "checksums.sha256").exists()

    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["mode"] == "simulation"
    assert manifest["n_prompts"] == 2
    assert manifest["n_completions"] == 4

    metrics = json.loads((out_dir / "metrics.json").read_text(encoding="utf-8"))
    assert metrics["mode"] == "simulation"
    assert "simulated_mention_rate" in metrics["entities"]["inten"]


def test_live_measurement_zero_fallback(tmp_path):
    entities = EntityRegistry.from_list([
        {"id": "inten", "names": ["Inten", "اینتن"], "domains": ["inten.asia"]},
    ])
    custom_reg = ProviderRegistry()
    custom_reg.register(MockFailingProvider(name="mock_fail"))

    engine = MeasurementEngine(entities=entities, registry=custom_reg)
    prompts = [{"id": "p1", "query": "بهترین شرکت سئو", "source_type": "observed", "intent": "recommendation"}]

    out_dir = tmp_path / "live_fail_run"
    import asyncio
    res = asyncio.run(engine.execute_measurement(
        prompts=prompts,
        providers=["mock_fail"],
        out_dir=out_dir,
        mode="live",
    ))

    # Verification of zero fallback: errors must be explicitly recorded
    assert res["n_errors"] == 1
    errors_lines = (out_dir / "errors.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(errors_lines) == 1
    err_data = json.loads(errors_lines[0])
    assert err_data["error"]["code"] == "API_TIMEOUT"
    assert "Simulated Gateway Timeout" in err_data["error"]["message"]

    # Raw response must record status: failed, NOT simulated text
    raw_lines = (out_dir / "raw_responses.jsonl").read_text(encoding="utf-8").strip().splitlines()
    raw_obj = json.loads(raw_lines[0])
    assert raw_obj["status"] == "failed"
    assert raw_obj["response_text"] == ""


def test_deterministic_replay(tmp_path):
    entities = EntityRegistry.from_list([
        {"id": "inten", "names": ["Inten", "اینتن"], "people": ["تقی مولوی"], "domains": ["inten.asia"]},
        {"id": "web24", "names": ["Web24", "وب24"], "people": ["رضا شیرازی"], "domains": ["web24.ir"]},
    ])
    engine = MeasurementEngine(entities=entities)

    prompts = [
        {"id": "p1", "query": "بهترین شرکت سئو در ایران", "source_type": "observed", "intent": "recommendation"},
    ]

    sim_dir = tmp_path / "sim_source"
    import asyncio
    asyncio.run(engine.execute_measurement(
        prompts=prompts,
        providers=["perplexity_sonar"],
        out_dir=sim_dir,
        mode="simulation",
        seed=42,
    ))

    # Now replay offline
    replay_dir = tmp_path / "replayed"
    replayer = ReplayEngine(entities=entities)
    rep_res = replayer.replay(input_path=sim_dir, out_dir=replay_dir)

    assert rep_res["mode"] == "replay"
    assert rep_res["n_completions"] == 1
    assert (replay_dir / "checksums.sha256").exists()

    # Check that checksums verification passes on replayed directory
    from geo_scope.benchmark.hasher import verify_dataset_checksums
    chk_res = verify_dataset_checksums(replay_dir)
    assert chk_res["valid"] is True
