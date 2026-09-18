"""
Model Context Protocol (MCP) Server for GEO-Scope
Enables Claude Desktop, Cursor, Antigravity, and AI Agents to run GEO audits & benchmarks directly.
"""

import sys
import json
import asyncio
from typing import Dict, Any

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
                "niche": {
                    "type": "string",
                    "description": "Industry vertical (crm_sales, seo_marketing, project_management, ai_copywriting, ecommerce_platform)",
                    "default": "crm_sales",
                },
                "competitors": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of 2-5 major competitors",
                },
                "prompt_count": {
                    "type": "integer",
                    "description": "Number of evaluation queries (e.g. 50, 200, 1000)",
                    "default": 50,
                },
            },
            "required": ["brand"],
        },
    },
    {
        "name": "reverse_engineer_ranking_factors",
        "description": "Returns labeled platform-specific research priors (Reddit UGC, G2 reviews, PR, Schema, Freshness) for a target niche (does not fit proprietary neural weights).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "niche": {"type": "string", "description": "Industry vertical key", "default": "crm_sales"},
                "target_brand": {"type": "string", "description": "Brand to evaluate against factors"},
            },
            "required": ["target_brand"],
        },
    },
    {
        "name": "generate_geo_playbook",
        "description": "Generates a concrete, prioritized 5-pillar GEO optimization roadmap (BLUF method, tables, Reddit strategy, schema).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand": {"type": "string", "description": "Target brand name"},
                "niche": {"type": "string", "description": "Industry vertical", "default": "crm_sales"},
            },
            "required": ["brand"],
        },
    },
]


for tool in MCP_TOOLS:
    tool[
        "description"
    ] += " Defaults to seeded simulation. Select live and explicit providers for actual inference. Factor weights are research priors, not fitted findings."
    tool["inputSchema"]["properties"].update(
        {
            "mode": {"type": "string", "enum": ["simulate", "live"], "default": "simulate"},
            "models": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Provider IDs, e.g. ollama_local, openrouter_free, perplexity_sonar",
            },
            "seed": {"type": "integer", "default": 42},
        }
    )

MCP_TOOLS.append(
    {
        "name": "measure_mavi",
        "description": "Measures the Molavi AI Visibility Index (MAVI) across L1-L5 layers (Technical Accessibility, Semantic Extractability, Entity Clarity, Citation Readiness, Observed AI Visibility). Computes measured multi-layer scores with partial normalization and zero score fabrication.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Target webpage URL (e.g. https://example.com/product)"},
                "html_content": {"type": "string", "description": "Raw HTML content to audit via SAGE (L1-L4)"},
                "brand": {"type": "string", "description": "Target entity or brand name"},
                "experiment_data": {"type": "object", "description": "Exported GEO-Scope experiment analysis JSON for L5"},
                "custom_weights": {"type": "object", "description": "Custom weights dictionary for L1-L5"},
                "manual_layers": {"type": "object", "description": "Manual layer overrides (labeled as manual_override)"},
            },
        },
    }
)

MCP_TOOLS.append(
    {
        "name": "verify_benchmark",
        "description": "Verifies SHA-256 cryptographic integrity and bit-level authenticity of a GEO-Scope benchmark dataset.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "dataset_path": {"type": "string", "description": "Path to benchmark dataset directory"},
            },
            "required": ["dataset_path"],
        },
    }
)

MCP_TOOLS.append(
    {
        "name": "reproduce_benchmark",
        "description": "Cryptographically verifies a benchmark dataset and recomputes all metrics from raw observations.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "dataset_path": {"type": "string", "description": "Path to benchmark dataset directory"},
                "tolerance": {"type": "number", "description": "Numerical tolerance for float comparison", "default": 0.05},
            },
            "required": ["dataset_path"],
        },
    }
)


async def handle_tool_call(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    if name == "verify_benchmark":
        from geo_scope.benchmark.hasher import verify_dataset_checksums

        dataset_path = arguments.get("dataset_path")
        return verify_dataset_checksums(dataset_path)

    elif name == "reproduce_benchmark":
        from geo_scope.benchmark.reproducer import BenchmarkReproducer

        dataset_path = arguments.get("dataset_path")
        tolerance = float(arguments.get("tolerance", 0.05))
        reproducer = BenchmarkReproducer(tolerance=tolerance)
        return reproducer.verify_and_reproduce(dataset_path)

    elif name == "measure_mavi":
        from geo_scope.mavi import MAVIEngine

        engine = MAVIEngine(weights=arguments.get("custom_weights"))
        report = engine.measure(
            html_content=arguments.get("html_content"),
            url=arguments.get("url"),
            target_brand=arguments.get("brand"),
            experiment_data=arguments.get("experiment_data"),
            manual_layers=arguments.get("manual_layers"),
        )
        return report.to_dict()

    elif name == "audit_ai_visibility":
        brand = arguments.get("brand")
        niche = arguments.get("niche", "crm_sales")
        comps = arguments.get("competitors", [])
        count = arguments.get("prompt_count", 50)

        prompts = generate_prompt_dataset(
            niche_key=niche, target_brand=brand, competitors=comps, total_count=count, seed=arguments.get("seed", 42)
        )
        runner = ModelRunner(mode=arguments.get("mode", "simulate"), seed=arguments.get("seed", 42))
        responses = await runner.execute_batch(prompts, models=arguments.get("models"))
        parsed = [
            parse_model_response(r["query_item"], r["model"], r["response_text"], r.get("provenance"))
            for r in responses
        ]
        analyzer = AlgoAnalyzer(parsed, brand, comps)
        analysis = analyzer.compute_full_analysis()

        return {
            "execution_mode": analysis["summary"]["execution_mode"],
            "records": parsed,
            "target_brand": brand,
            "overall_share_of_model_pct": analysis["summary"]["overall_sov"],
            "top_1_recommendation_rate_pct": analysis["summary"]["overall_top1_rate"],
            "best_performing_ai": analysis["summary"]["best_performing_model"],
            "weakest_performing_ai": analysis["summary"]["weakest_performing_model"],
            "competitor_share_of_voice": analysis["competitor_matrix"][:4],
            "top_cited_sources": analysis["citation_analytics"]["top_cited_domains"][:5],
        }

    elif name == "reverse_engineer_ranking_factors":
        brand = arguments.get("target_brand")
        niche = arguments.get("niche", "crm_sales")
        prompts = generate_prompt_dataset(
            niche_key=niche, target_brand=brand, total_count=50, seed=arguments.get("seed", 42)
        )
        runner = ModelRunner(mode=arguments.get("mode", "simulate"), seed=arguments.get("seed", 42))
        responses = await runner.execute_batch(prompts, models=arguments.get("models"))
        parsed = [
            parse_model_response(r["query_item"], r["model"], r["response_text"], r.get("provenance"))
            for r in responses
        ]
        analyzer = AlgoAnalyzer(parsed, brand, [])
        analysis = analyzer.compute_full_analysis()

        return {
            "status": "hypothesis_prior_not_fitted",
            "factor_weights_by_model": analysis["algorithmic_factors"]["weights_by_model"],
            "global_average_weights": analysis["algorithmic_factors"]["global_average_weights"],
            "identified_strategic_gaps": analysis["strategic_gaps"],
        }

    elif name == "generate_geo_playbook":
        brand = arguments.get("brand")
        niche = arguments.get("niche", "crm_sales")
        prompts = generate_prompt_dataset(
            niche_key=niche, target_brand=brand, total_count=50, seed=arguments.get("seed", 42)
        )
        runner = ModelRunner(mode=arguments.get("mode", "simulate"), seed=arguments.get("seed", 42))
        responses = await runner.execute_batch(prompts, models=arguments.get("models"))
        parsed = [
            parse_model_response(r["query_item"], r["model"], r["response_text"], r.get("provenance"))
            for r in responses
        ]
        analyzer = AlgoAnalyzer(parsed, brand, [])
        analysis = analyzer.compute_full_analysis()
        playbook = generate_geo_playbook(analysis)
        return playbook

    return {"error": f"Unknown tool: {name}"}


def main():
    """
    Standard JSON-RPC Stdio Server loop for MCP.
    """
    req = {}
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
                    },
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
                        "serverInfo": {"name": "geo-scope-mcp", "version": "1.0.0"},
                    },
                }
                sys.stdout.write(json.dumps(res) + "\n")
                sys.stdout.flush()
        except Exception as e:
            err_res = {
                "jsonrpc": "2.0",
                "id": req.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Request failed ({type(e).__name__}); check provider configuration",
                },
            }
            sys.stdout.write(json.dumps(err_res) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
