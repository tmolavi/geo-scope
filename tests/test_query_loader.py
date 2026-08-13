"""
Tests for Query Loader (Bring Your Own Prompts)
"""

import os
import tempfile
from geo_scope.engine.query_loader import load_custom_prompts


def test_load_csv_prompts():
    csv_content = """query,intent,language
What is the best CRM software for startups?,commercial_direct,en
HubSpot vs Salesforce full review,comparative,en
How to solve pipeline leaks?,problem_solving,en
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(csv_content)
        temp_path = f.name

    try:
        prompts = load_custom_prompts(temp_path, default_brand="HubSpot", default_competitors=["Salesforce"])
        assert len(prompts) == 3
        assert prompts[0]["query"] == "What is the best CRM software for startups?"
        assert prompts[0]["intent"] == "commercial_direct"
        assert prompts[0]["target_brand"] == "HubSpot"
        assert "Salesforce" in prompts[0]["expected_entities"]
    finally:
        os.remove(temp_path)


def test_load_json_prompts():
    json_content = """[
        {"query": "Best project management software in 2026", "intent": "commercial_direct"},
        {"query": "ClickUp vs Asana for engineers", "intent": "comparative"}
    ]"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write(json_content)
        temp_path = f.name

    try:
        prompts = load_custom_prompts(temp_path, default_brand="ClickUp")
        assert len(prompts) == 2
        assert prompts[0]["query"] == "Best project management software in 2026"
    finally:
        os.remove(temp_path)


def test_load_txt_prompts():
    txt_content = """# Comment line
What is the best SEO tool in 2026?
Ahrefs vs SEMrush comparison
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(txt_content)
        temp_path = f.name

    try:
        prompts = load_custom_prompts(temp_path, default_brand="Ahrefs")
        assert len(prompts) == 2
        assert prompts[0]["query"] == "What is the best SEO tool in 2026?"
        assert prompts[1]["intent"] == "comparative"
    finally:
        os.remove(temp_path)
