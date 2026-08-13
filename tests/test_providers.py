"""
Tests for Provider Architecture & Registry
"""

import pytest
import asyncio
from geo_scope.providers.registry import registry
from geo_scope.providers.simulated import SimulatedProvider


def test_provider_registry_contains_defaults():
    providers = registry.list_all()
    names = [p["id"] for p in providers]
    assert "perplexity_sonar" in names
    assert "chatgpt_search" in names
    assert "gemini_grounding" in names
    assert "claude_3_7" in names


def test_cost_estimation():
    est = registry.estimate_total_cost(["chatgpt_search", "claude_3_7"], 1000)
    # chatgpt $7.50 + claude $8.00 = $15.50
    assert est == 15.50


def test_simulated_provider_generation():
    sim = SimulatedProvider("perplexity_sonar", "Perplexity (Test)", "ugc_heavy", seed=123)
    prompt_item = {
        "id": "p1",
        "query": "Best CRM in 2026",
        "target_brand": "HubSpot",
        "expected_entities": ["HubSpot", "Salesforce"]
    }
    res = asyncio.run(sim.generate_response(prompt_item))
    assert isinstance(res, str)
    assert len(res) > 50
    assert "HubSpot" in res or "Salesforce" in res
