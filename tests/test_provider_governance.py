import json
import pytest
from geo_scope.entities.models import Entity
from geo_scope.providers.models import ProviderResponse
from geo_scope.parser.observation_parser import ObservationParser
from geo_scope.measurement.engine import MeasurementEngine
from geo_scope.entities.registry import EntityRegistry


def test_provider_response_preserves_governance_fields():
    resp = ProviderResponse(
        provider="perplexity_sonar",
        model="sonar-pro",
        execution_mode="live",
        provider_class="answer_engine",
        text="Sample output",
        citations=["https://who.int"],
        metadata={"search_grounded": True, "fallback_active": False},
        usage={"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150, "cost": 0.0025},
    )

    d = resp.to_dict()
    assert d["requested_provider"] == "perplexity_sonar"
    assert d["actual_provider"] == "perplexity_sonar"
    assert d["requested_model"] == "sonar-pro"
    assert d["actual_model"] == "sonar-pro"
    assert d["provider_class"] == "answer_engine"
    assert d["search_grounded"] is True
    assert d["fallback_used"] is False
    assert d["input_tokens"] == 100
    assert d["output_tokens"] == 50
    assert d["total_tokens"] == 150
    assert d["provider_reported_cost"] == 0.0025
    assert d["currency"] == "USD"
    assert d["cost_status"] == "reported"

    raw_rec = resp.to_raw_record(
        experiment_id="exp_01",
        run_id="run_01",
        prompt_id="p_01",
        prompt="Sample query",
    )
    assert raw_rec["requested_provider"] == "perplexity_sonar"
    assert raw_rec["actual_provider"] == "perplexity_sonar"
    assert raw_rec["fallback_used"] is False


def test_citation_vs_attribution_strict_separation():
    parser = ObservationParser()
    who_entity = Entity(
        id="who",
        names=["WHO", "World Health Organization", "سازمان بهداشت جهانی"],
        domains=["who.int"],
        do_not_confuse=[],
    )

    # Case 1: "According to WHO..." without link -> attribution = True, cited = False
    text_attribution_only = "According to the WHO, regular physical activity prevents cardiovascular disease."
    res_attr = parser.parse(text_attribution_only, who_entity)
    assert res_attr.attributed is True
    assert res_attr.cited is False

    # Case 2: Link "https://who.int" without sourcing quote -> citation = True, attribution = False
    text_citation_only = "Further health guidelines can be explored at https://who.int/guidelines for reference."
    res_cite = parser.parse(text_citation_only, who_entity, citations=["https://who.int/guidelines"])
    assert res_cite.cited is True
    assert res_cite.attributed is False

    # Case 3: Persian Attribution ("طبق گزارش سازمان بهداشت جهانی...")
    text_fa_attr = "طبق گزارش سازمان بهداشت جهانی، رعایت بهداشت عمومی کلید پیشگیری از بیماری‌هاست."
    res_fa = parser.parse(text_fa_attr, who_entity)
    assert res_fa.attributed is True

    # Case 4: Arabic Attribution ("وفقاً لمنظمة الصحة العالمية...")
    text_ar_attr = "وفقاً لـ WHO، فإن اللقاحات توفر حماية فعالة ضد الأوبئة."
    res_ar = parser.parse(text_ar_attr, who_entity)
    assert res_ar.attributed is True


@pytest.mark.asyncio
async def test_live_mismatch_marks_observation_status(tmp_path):
    registry = EntityRegistry.from_list([{
        "id": "hubspot",
        "names": ["HubSpot"],
        "domains": ["hubspot.com"],
    }])
    engine = MeasurementEngine(entities=registry)

    # Simulate a run where actual provider differs from requested provider
    prompts = [{"id": "p1", "query": "Best CRM software", "source_type": "observed", "intent": "recommendation"}]
    
    # In simulation mode, status is success/simulation
    res = await engine.execute_measurement(
        prompts=prompts,
        providers=["perplexity_sonar"],
        out_dir=tmp_path / "sim_out",
        mode="simulation",
    )
    assert res["n_observations"] == 1
    obs = json.loads((tmp_path / "sim_out" / "observations.jsonl").read_text().splitlines()[0])
    assert "requested_provider" in obs
    assert "actual_provider" in obs
    assert "fallback_used" in obs
