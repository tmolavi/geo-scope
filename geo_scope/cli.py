#!/usr/bin/env python3
"""
Command Line Interface for GEO-Scope Platform
Supports:
  - geo-scope demo (5-Minute Quickstart Demo)
  - geo-scope run --prompts <file> (Bring Your Own Prompts)
  - geo-scope serve (Interactive Web Dashboard)
  - geo-scope mcp (Model Context Protocol Server)
"""

import argparse
import asyncio
import os
import sys
import json
import time

from geo_scope.engine.query_generator import generate_prompt_dataset, INDUSTRY_PRESETS
from geo_scope.engine.query_loader import load_custom_prompts
from geo_scope.engine.model_runner import ModelRunner
from geo_scope.engine.feature_extractor import parse_model_response
from geo_scope.engine.algo_analyzer import AlgoAnalyzer
from geo_scope.engine.strategy_builder import generate_geo_playbook
from geo_scope.engine.history_tracker import save_benchmark_snapshot
from geo_scope.engine.report_generator import generate_experiment_artifacts
from geo_scope.providers.registry import registry


def run_demo_cmd():
    """
    The 5-Minute WOW Demo experience.
    Runs a fast 10-prompt benchmark on HubSpot vs Salesforce using the simulated benchmark engine.
    """
    print("\n" + "=" * 75)
    print("⟠ GEO-Scope: 5-Minute Quickstart Demo Experiment")
    print("📋 Execution Mode : [SIMULATED BENCHMARK DEMO - Zero API Key Required]")
    print("🎯 Target Brand   : HubSpot   |   📂 Niche: CRM SaaS   |   🔢 Sample Prompts: 10")
    print("ℹ️ Note           : Demo uses calibrated baseline simulation. For live API calls, configure provider keys.")
    print("=" * 75)

    prompts = generate_prompt_dataset(
        niche_key="crm_sales",
        target_brand="HubSpot",
        competitors=["Salesforce", "Zoho CRM", "Pipedrive"],
        language="both",
        total_count=10
    )

    runner = ModelRunner()
    models = ["perplexity_sonar", "chatgpt_search", "gemini_grounding", "claude_3_7"]
    print(f"\n[1/3] Running multi-model inference across {len(models)} AI engines ({len(prompts) * len(models)} calls)...")

    responses = asyncio.run(runner.execute_batch(prompts, models=models))
    print("✓ Inference completed.")

    print("\n[2/3] Extracting brand mentions, ranks, and citation graph...")
    parsed = []
    for r in responses:
        item = parse_model_response(r["query_item"], r["model"], r["response_text"])
        item["full_response_text"] = r["response_text"]
        item["query_text"] = r["query_item"]["query"]
        parsed.append(item)

    print("\n[3/3] Reverse-engineering algorithm weights & generating report...")
    analyzer = AlgoAnalyzer(parsed, "HubSpot", ["Salesforce", "Zoho CRM", "Pipedrive"])
    analysis = analyzer.compute_full_analysis()

    # Save artifacts
    out_dir = "results"
    artifacts = generate_experiment_artifacts(analysis, parsed, prompts, out_dir=out_dir)

    print("\n" + "=" * 75)
    print("📊 DEMO EXPERIMENTAL BENCHMARK SUMMARY")
    print("=" * 75)
    print(f"• Target Brand Share of Model (SoM) : {analysis['summary']['overall_sov']}%")
    print(f"• Top-1 Primary Recommendation Rate : {analysis['summary']['overall_top1_rate']}%")
    print(f"• Top Performing AI Engine          : {analysis['summary']['best_performing_model']}")
    print(f"• Lowest Performing AI Engine       : {analysis['summary']['weakest_performing_model']}")
    print("-" * 75)
    print("🤖 Model Breakdown:")
    for m, st in analysis["share_of_model"]["by_model"].items():
        print(f"  - {m:<20}: Mention Rate: {st['mention_rate_pct']}% | Top-1: {st['top1_rate_pct']}% | Avg Rank: #{st['avg_rank']}")
    print("-" * 75)
    print("🏆 Competitor Matrix:")
    for c in analysis["competitor_matrix"]:
        is_t = "(Target Brand)" if c["is_target"] else "(Competitor)"
        print(f"  - {c['brand']:<15} : Mention Rate: {c['mention_rate_pct']}% | Top-1: {c['top1_rate_pct']}% {is_t}")
    print("=" * 75)
    print(f"\n📁 Portable Reports Generated in '{out_dir}/':")
    print(f"  📄 Human-Readable Summary : {artifacts['summary_md']}")
    print(f"  🌐 Standalone HTML Report : {artifacts['report_html']}")
    print(f"  📦 Experiment Metadata    : {artifacts['experiment_json']}")
    print(f"  📊 Queries CSV Breakdown  : {artifacts['queries_csv']}")
    print(f"  🔗 Citations Graph CSV    : {artifacts['citations_csv']}")
    print("\n✨ Ready to test your own brand? Run:")
    print("   geo-scope run --brand \"Your Brand\" --prompts my_prompts.csv\n")


def run_benchmark_cmd(args):
    if args.demo:
        run_demo_cmd()
        return

    os.makedirs(args.out, exist_ok=True)
    brand = args.brand.strip() if args.brand else "My Brand"
    comps = [c.strip() for c in args.competitors.split(",") if c.strip()] if args.competitors else ["Competitor A", "Competitor B"]

    # 1. Load Prompts
    if args.prompts:
        print(f"\n[1/4] Loading custom user prompts from '{args.prompts}'...")
        prompts = load_custom_prompts(
            file_path=args.prompts,
            default_brand=brand,
            default_competitors=comps,
            default_niche=args.niche
        )
        print(f"✓ Loaded {len(prompts)} custom prompts.")
    else:
        print(f"\n[1/4] Synthesizing {args.count} structured prompts across 5 intent strata...")
        prompts = generate_prompt_dataset(
            niche_key=args.niche,
            target_brand=brand,
            competitors=comps,
            language=args.lang,
            total_count=args.count
        )
        print(f"✓ Synthesized {len(prompts)} prompts.")

    # Cost Estimation & Dry Run Check
    models = ["perplexity_sonar", "chatgpt_search", "gemini_grounding", "claude_3_7"]
    est_cost = registry.estimate_total_cost(models, len(prompts))

    print("\n" + "=" * 75)
    print("⟠ GEO-Scope: Generative Engine Optimization Benchmark")
    print(f"🎯 Target Brand  : {brand}")
    print(f"👥 Competitors   : {', '.join(comps)}")
    print(f"🔢 Total Prompts : {len(prompts)} ({len(prompts) * len(models)} total inferences)")
    print(f"🤖 Models        : {', '.join(models)}")
    print(f"📋 Mode          : Simulated Benchmark Engine (Deterministic baseline heuristics)")
    print(f"💰 Estimated API Cost (if using live cloud APIs): ~${est_cost:.2f} USD")
    print("=" * 75)

    if args.dry_run:
        print("\n🔍 Dry-run complete. Exiting without executing inferences.")
        return

    # 2. Inferences
    print(f"\n[2/4] Executing batch inference across {len(models)} AI models...")
    runner = ModelRunner()

    def progress(done, total):
        pct = int((done / total) * 100)
        print(f"\rProgress: [{done}/{total}] {pct}% completed...", end="", flush=True)

    raw_responses = asyncio.run(runner.execute_batch(prompts, models=models, progress_callback=progress))
    print("\n✓ Inferences completed.")

    # 3. Extraction
    print(f"\n[3/4] Parsing brand mentions, rankings, and citation graphs...")
    parsed = []
    for item in raw_responses:
        q_item = item["query_item"]
        model = item["model"]
        text = item["response_text"]
        p_record = parse_model_response(q_item, model, text)
        p_record["full_response_text"] = text
        p_record["query_text"] = q_item["query"]
        parsed.append(p_record)
    print(f"✓ Processed {len(parsed)} model outputs.")

    # 4. Statistical Analysis & Report Generation
    print(f"\n[4/4] Reverse-engineering algorithm weights & building portable reports...")
    analyzer = AlgoAnalyzer(parsed, brand, comps)
    analysis = analyzer.compute_full_analysis()
    delta_record = save_benchmark_snapshot(analysis, args.niche, brand, len(prompts))
    playbook = generate_geo_playbook(analysis, delta_info=delta_record)

    artifacts = generate_experiment_artifacts(analysis, parsed, prompts, out_dir=args.out)

    print("\n" + "=" * 75)
    print("📊 EXECUTIVE BENCHMARK RESULTS")
    print("=" * 75)
    print(f"• Target Brand Share of Model (SoM) : {analysis['summary']['overall_sov']}%")
    print(f"• Top-1 Recommendation Rate         : {analysis['summary']['overall_top1_rate']}%")
    print(f"• Top Performing AI Engine          : {analysis['summary']['best_performing_model']}")
    print(f"• Weakest Performing AI Engine       : {analysis['summary']['weakest_performing_model']}")
    print("-" * 75)
    print("🏆 Competitor Matrix:")
    for c in analysis["competitor_matrix"]:
        is_t = "(Target Brand)" if c["is_target"] else "(Competitor)"
        print(f"  - {c['brand']:<15} : Mention Rate: {c['mention_rate_pct']}% | Top-1: {c['top1_rate_pct']}% {is_t}")
    print("=" * 75)
    print(f"\n📁 Portable Reports written to '{args.out}/':")
    print(f"  📄 Human-Readable Summary : {artifacts['summary_md']}")
    print(f"  🌐 Standalone HTML Report : {artifacts['report_html']}")
    print(f"  📦 Experiment Metadata    : {artifacts['experiment_json']}")
    print(f"  📊 Queries CSV Breakdown  : {artifacts['queries_csv']}")
    print(f"  🔗 Citations Graph CSV    : {artifacts['citations_csv']}")
    print("=" * 75 + "\n")


def serve_dashboard_cmd(args):
    import uvicorn
    print(f"🚀 Starting GEO-Scope Web Dashboard on http://{args.host}:{args.port}")
    uvicorn.run("geo_scope.server:app", host=args.host, port=args.port, reload=args.reload)


def main():
    parser = argparse.ArgumentParser(
        prog="geo-scope",
        description="GEO-Scope: Generative Engine Optimization (GEO) & AI Algorithm Reverse-Engineering CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: demo
    subparsers.add_parser("demo", help="Run 5-minute quickstart demo experiment")

    # Command: run
    run_parser = subparsers.add_parser("run", help="Run an AI visibility benchmark experiment")
    run_parser.add_argument("--demo", action="store_true", help="Run quick demo benchmark")
    run_parser.add_argument("--brand", type=str, default="HubSpot", help="Target Brand Name")
    run_parser.add_argument("--competitors", type=str, default="Salesforce,Zoho CRM,Pipedrive", help="Comma-separated competitors list")
    run_parser.add_argument("--prompts", type=str, default=None, help="Path to custom prompts file (.csv, .json, .txt, .yaml)")
    run_parser.add_argument("--niche", type=str, default="crm_sales", help="Industry preset key")
    run_parser.add_argument("--count", type=int, default=50, help="Total prompts count when generating synthetically (default: 50)")
    run_parser.add_argument("--lang", type=str, default="both", choices=["fa", "en", "both"], help="Query language")
    run_parser.add_argument("--out", type=str, default="results", help="Output directory for reports")
    run_parser.add_argument("--dry-run", action="store_true", help="Simulate prompt loading and cost without calling models")

    # Command: serve
    serve_parser = subparsers.add_parser("serve", help="Start the interactive Web Dashboard & API server")
    serve_parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address (default: 0.0.0.0)")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port number (default: 8000)")
    serve_parser.add_argument("--reload", action="store_true", help="Enable auto-reload")

    # Command: mcp
    subparsers.add_parser("mcp", help="Start MCP (Model Context Protocol) Server for Claude Desktop & Cursor")

    # Command: generate
    gen_parser = subparsers.add_parser("generate", help="Generate prompt datasets without running inference")
    gen_parser.add_argument("--niche", type=str, default="crm_sales", help="Industry preset key")
    gen_parser.add_argument("--brand", type=str, default="HubSpot", help="Target Brand Name")
    gen_parser.add_argument("--count", type=int, default=1000, help="Total prompts count")
    gen_parser.add_argument("--lang", type=str, default="both", choices=["fa", "en", "both"], help="Language")
    gen_parser.add_argument("--out", type=str, default="prompts.json", help="Output JSON path")

    args = parser.parse_args()

    if args.command == "demo":
        run_demo_cmd()
    elif args.command == "run":
        run_benchmark_cmd(args)
    elif args.command == "serve":
        serve_dashboard_cmd(args)
    elif args.command == "mcp":
        from geo_scope.mcp_server import main as mcp_main
        mcp_main()
    elif args.command == "generate":
        prompts = generate_prompt_dataset(
            niche_key=args.niche,
            target_brand=args.brand,
            language=args.lang,
            total_count=args.count
        )
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(prompts, f, ensure_ascii=False, indent=2)
        print(f"✓ Generated {len(prompts)} prompts and saved to {args.out}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
