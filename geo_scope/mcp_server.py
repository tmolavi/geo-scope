"""
Model Context Protocol (MCP) Server for GEO-Scope
Enables Claude Desktop, Cursor, Antigravity, and AI Agents to run GEO audits & benchmarks directly.
"""

import sys
import json
import asyncio
from typing import Dict, Any, List

from geo_scope.engine.query_generator import generate_prompt_dataset
from geo_scope.engine.model_runner import ModelRunner
from geo_scope.engine.feature_extractor import parse_model_response
from geo_scope.engine.algo_analyzer import AlgoAnalyzer
from geo_scope.engine.strategy_builder import generate_geo_playbook


MCP_TOOLS = [
    {
        "name": "audit_ai_visibility",
        "description": "Audits a brand's visibility and Share of Model (SoM) across ChatGPT Search, Perplexity, Gemini, and Claude.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand": {"type": "string", "description": "Target brand name (e.g. HubSpot, Ahrefs, Notion)"},
                "niche": {"type": "string", "description": "Industry vertical (crm_sales, seo_marketing, project_management, ai_copywriting, ecommerce_platform)", "default": "crm_sales"},
                "competitors": {"type": "array", "items": {"type": "string"}, "description": "List of 2-5 major competitors"},
                "prompt_count": {"type": "integer", "description": "Number of evaluation queries (e.g. 50, 200, 1000)", "default": 50}
            },
            "required": ["brand"]
        }
    },
    {
        "name": "reverse_engineer_ranking_factors",
        "description": "Reverse engineers the algorithmic factor weights (Reddit UGC, G2 reviews, PR, Schema, Freshness) for a target niche.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "niche": {"type": "string", "description": "Industry vertical key", "default": "crm_sales"},
                "target_brand": {"type": "string", "description": "Brand to evaluate against factors"}
            },
            "required": ["target_brand"]
        }
    },
    {
        "name": "generate_geo_playbook",
        "description": "Generates a concrete, prioritized 5-pillar GEO optimization roadmap (BLUF method, tables, Reddit strategy, schema).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand": {"type": "string", "description": "Target brand name"},
                "niche": {"type": "string", "description": "Industry vertical", "default": "crm_sales"}
            },
            "required": ["brand"]
        }
    }
]


async def handle_tool_call(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    if name == "audit_ai_visibility":
        brand = arguments.get("brand")
        niche = arguments.get("niche", "crm_sales")
        comps = arguments.get("competitors", [])
        count = arguments.get("prompt_count", 50)

        prompts = generate_prompt_dataset(niche_key=niche, target_brand=brand, competitors=comps, total_count=count)
        runner = ModelRunner()
        responses = await runner.execute_batch(prompts)
        parsed = [parse_model_response(r["query_item"], r["model"], r["response_text"]) for r in responses]
        analyzer = AlgoAnalyzer(parsed, brand, comps)
        analysis = analyzer.compute_full_analysis()

        return {
            "target_brand": brand,
            "overall_share_of_model_pct": analysis["summary"]["overall_sov"],
            "top_1_recommendation_rate_pct": analysis["summary"]["overall_top1_rate"],
            "best_performing_ai": analysis["summary"]["best_performing_model"],
            "weakest_performing_ai": analysis["summary"]["weakest_performing_model"],
            "competitor_share_of_voice": analysis["competitor_matrix"][:4],
            "top_cited_sources": analysis["citation_analytics"]["top_cited_domains"][:5]
        }

    elif name == "reverse_engineer_ranking_factors":
        brand = arguments.get("target_brand")
        niche = arguments.get("niche", "crm_sales")
        prompts = generate_prompt_dataset(niche_key=niche, target_brand=brand, total_count=50)
        runner = ModelRunner()
        responses = await runner.execute_batch(prompts)
        parsed = [parse_model_response(r["query_item"], r["model"], r["response_text"]) for r in responses]
        analyzer = AlgoAnalyzer(parsed, brand, [])
        analysis = analyzer.compute_full_analysis()

        return {
            "factor_weights_by_model": analysis["algorithmic_factors"]["weights_by_model"],
            "global_average_weights": analysis["algorithmic_factors"]["global_average_weights"],
            "identified_strategic_gaps": analysis["strategic_gaps"]
        }

    elif name == "generate_geo_playbook":
        brand = arguments.get("brand")
        niche = arguments.get("niche", "crm_sales")
        prompts = generate_prompt_dataset(niche_key=niche, target_brand=brand, total_count=50)
        runner = ModelRunner()
        responses = await runner.execute_batch(prompts)
        parsed = [parse_model_response(r["query_item"], r["model"], r["response_text"]) for r in responses]
        analyzer = AlgoAnalyzer(parsed, brand, [])
        analysis = analyzer.compute_full_analysis()
        playbook = generate_geo_playbook(analysis)
        return playbook

    return {"error": f"Unknown tool: {name}"}


def main():
    """
    Standard JSON-RPC Stdio Server loop for MCP.
    """
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            method = req.get("method")
            msg_id = req.get("id")

            if method == "tools/list":
                res = {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": MCP_TOOLS}}
                sys.stdout.write(json.dumps(res) + "\n")
                sys.stdout.flush()

            elif method == "tools/call":
                params = req.get("params", {})
                tool_name = params.get("name")
                args = params.get("arguments", {})
                tool_result = asyncio.run(handle_tool_call(tool_name, args))
                res = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(tool_result, ensure_ascii=False, indent=2)}]
                    }
                }
                sys.stdout.write(json.dumps(res) + "\n")
                sys.stdout.flush()

            elif method == "initialize":
                res = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "geo-scope-mcp", "version": "1.0.0"}
                    }
                }
                sys.stdout.write(json.dumps(res) + "\n")
                sys.stdout.flush()
        except Exception as e:
            err_res = {"jsonrpc": "2.0", "id": req.get("id"), "error": {"code": -32603, "message": str(e)}}
            sys.stdout.write(json.dumps(err_res) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
