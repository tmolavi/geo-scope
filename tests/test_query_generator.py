"""
Tests for Query Generator Module
"""

import pytest
from geo_scope.engine.query_generator import generate_prompt_dataset, INDUSTRY_PRESETS


def test_generate_prompts_count():
    count = 100
    dataset = generate_prompt_dataset(niche_key="crm_sales", total_count=count)
    assert len(dataset) == count
    assert dataset[0]["id"] == "qry_0001"
    assert "query" in dataset[0]
    assert "intent" in dataset[0]


def test_all_industry_presets_exist():
    for key in INDUSTRY_PRESETS:
        prompts = generate_prompt_dataset(niche_key=key, total_count=10)
        assert len(prompts) == 10
        assert prompts[0]["niche"] == key


def test_language_selection():
    fa_prompts = generate_prompt_dataset(language="fa", total_count=20)
    assert all(p["language"] == "fa" for p in fa_prompts)

    en_prompts = generate_prompt_dataset(language="en", total_count=20)
    assert all(p["language"] == "en" for p in en_prompts)
