"""
Tests for Feature Extractor Module
"""

from geo_scope.engine.feature_extractor import (
    extract_citations_and_domains,
    detect_brand_positions,
    analyze_content_structure,
    parse_model_response
)


def test_extract_citations():
    text = """
    Here are the citations:
    - [Reddit Sales Thread](https://reddit.com/r/sales/comments/123)
    - [G2 CRM Grid](https://www.g2.com/categories/crm)
    - https://forbes.com/advisor/crm
    """
    urls, sources = extract_citations_and_domains(text)
    assert len(urls) == 3
    domains = [s["domain"] for s in sources]
    assert "reddit.com" in domains
    assert "g2.com" in domains
    assert "forbes.com" in domains

    categories = [s["category"] for s in sources]
    assert "ugc_forums" in categories
    assert "review_aggregators" in categories
    assert "tech_media_pr" in categories


def test_detect_brand_positions():
    text = """
    Top choices:
    1. HubSpot - The absolute best CRM on the market.
    2. Salesforce - Complex enterprise tool.
    3. Zoho CRM - Good budget tool.
    """
    brands = ["HubSpot", "Salesforce", "Zoho CRM", "Pipedrive"]
    positions = detect_brand_positions(text, brands)

    assert positions["HubSpot"]["mentioned"] is True
    assert positions["HubSpot"]["rank"] == 1
    assert positions["HubSpot"]["is_top_1"] is True
    assert positions["HubSpot"]["sentiment"] == "positive"

    assert positions["Salesforce"]["mentioned"] is True
    assert positions["Salesforce"]["rank"] == 2

    assert positions["Pipedrive"]["mentioned"] is False


def test_content_structure_analysis():
    text = """
    | Solution | Score |
    | HubSpot  | 9.8   |
    - 45% increase in lead conversion
    - 2026 verified data
    """
    structure = analyze_content_structure(text)
    assert structure["has_table"] is True
    assert structure["has_bullets"] is True
    assert structure["has_statistics"] is True
    assert structure["structured_score"] >= 3
