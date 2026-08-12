"""
Tests for MCP Server Protocol & Tools
"""

import asyncio
from geo_scope.mcp_server import handle_tool_call, MCP_TOOLS


def test_mcp_tools_schema():
    tool_names = [t["name"] for t in MCP_TOOLS]
    assert "audit_ai_visibility" in tool_names
    assert "reverse_engineer_ranking_factors" in tool_names
    assert "generate_geo_playbook" in tool_names


def test_audit_ai_visibility_tool():
    res = asyncio.run(handle_tool_call("audit_ai_visibility", {
        "brand": "HubSpot",
        "niche": "crm_sales",
        "competitors": ["Salesforce", "Zoho CRM"],
        "prompt_count": 10
    }))
    assert "target_brand" in res
    assert res["target_brand"] == "HubSpot"
    assert "overall_share_of_model_pct" in res
    assert "top_1_recommendation_rate_pct" in res
    assert "best_performing_ai" in res


def test_reverse_engineer_tool():
    res = asyncio.run(handle_tool_call("reverse_engineer_ranking_factors", {
        "target_brand": "HubSpot",
        "niche": "crm_sales"
    }))
    assert "factor_weights_by_model" in res
    assert "global_average_weights" in res
