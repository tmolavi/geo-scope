#!/usr/bin/env python3
"""
Command Line Interface for GEO-Scope Platform
"""

import argparse
import asyncio
import os
import sys
import json
import uvicorn

from geo_scope.engine.query_generator import generate_prompt_dataset, INDUSTRY_PRESETS
from geo_scope.engine.model_runner import ModelRunner
from geo_scope.engine.feature_extractor import parse_model_response
from geo_scope.engine.algo_analyzer import AlgoAnalyzer
from geo_scope.engine.strategy_builder import generate_geo_playbook
from geo_scope.engine.export_manager import export_records_to_csv, export_citations_to_csv, export_full_json


def run_benchmark_cmd(args):
    os.makedirs(args.out, exist_ok=True)
    comps = [c.strip() for c in args.competitors.split(",") if c.strip()] if args.competitors else None

    print("\n" + "=" * 70)
    print("⟠ GEO-Scope: Generative Engine Optimization Benchmark")
    print(f"🎯 Target Brand: {args.brand}")
    print(f"📂 Industry Niche: {args.niche}")
    print(f"🔢 Total Prompts: {args.count}")
    print(f"🌐 Language: {args.lang}")
    print("=" * 70)

    # 1. Prompts
    print(f"\n[1/4] Generating {args.count} structured prompts across 5 intent categories...")
    prompts = generate_prompt_dataset(
        niche_key=args.niche,
        target_brand=args.brand,
        competitors=comps,
        language=args.lang,
        total_count=args.count
    )
    print(f"✓ Successfully synthesized {len(prompts)} prompts.")

    # 2. Inferences
    models = ["perplexity_sonar", "chatgpt_search", "gemini_grounding", "claude_3_7"]
    print(f"\n[2/4] Executing batch inference across {len(models)} AI models ({len(prompts) * len(models)} total inferences)...")
    runner = ModelRunner()

    def progress(done, total):
        pct = int((done / total) * 100)
        print(f"\rProgress: [{done}/{total}] {pct}% completed...", end="", flush=True)

    raw_responses = asyncio.run(runner.execute_batch(prompts, models=models, progress_callback=progress))
    print("\n✓ Inferences completed.")

    # 3. Extraction
    print(f"\n[3/4] Parsing brand rankings and citation graphs...")
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

    # 4. Statistical reverse-engineering
    print(f"\n[4/4] Reverse-engineering algorithm weights & computing Share of Model...")
    preset = INDUSTRY_PRESETS.get(args.niche, INDUSTRY_PRESETS["crm_sales"])
    final_comps = comps if comps else preset["competitors"]
    analyzer = AlgoAnalyzer(parsed, args.brand, final_comps)
    analysis = analyzer.compute_full_analysis()
    playbook = generate_geo_playbook(analysis)

    # Export
    csv_records = export_records_to_csv(parsed)
    csv_citations = export_citations_to_csv(parsed)
    json_full = export_full_json(analysis, prompts)

    queries_file = os.path.join(args.out, "benchmark_queries.csv")
    citations_file = os.path.join(args.out, "citations_graph.csv")
    report_file = os.path.join(args.out, "geo_intelligence_report.json")

    with open(queries_file, "w", encoding="utf-8") as f:
        f.write(csv_records)
    with open(citations_file, "w", encoding="utf-8") as f:
        f.write(csv_citations)
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(json_full)

    print("\n" + "=" * 70)
    print("📊 EXECUTIVE BENCHMARK RESULTS")
    print("=" * 70)
    print(f"• Target Brand Share of Model (SoM): {analysis['summary']['overall_sov']}%")
    print(f"• Top-1 Primary Recommendation Rate: {analysis['summary']['overall_top1_rate']}%")
    print(f"• Best Performing Model: {analysis['summary']['best_performing_model']}")
    print(f"• Weakest Performing Model: {analysis['summary']['weakest_performing_model']}")
    print("\n📁 Artifacts written to:")
    print(f"  - {queries_file}")
    print(f"  - {citations_file}")
    print(f"  - {report_file}")
    print("=" * 70 + "\n")


def serve_dashboard_cmd(args):
    print(f"🚀 Starting GEO-Scope Web Dashboard on http://{args.host}:{args.port}")
    uvicorn.run("geo_scope.server:app", host=args.host, port=args.port, reload=args.reload)


def main():
    parser = argparse.ArgumentParser(
        prog="geo-scope",
        description="GEO-Scope: Generative Engine Optimization (GEO) & AI Algorithm Reverse-Engineering CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: run
    run_parser = subparsers.add_parser("run", help="Run 1,000 queries AI benchmark")
    run_parser.add_argument("--niche", type=str, default="crm_sales", help="Industry preset key")
    run_parser.add_argument("--brand", type=str, default="HubSpot", help="Target Brand Name")
    run_parser.add_argument("--competitors", type=str, default="", help="Comma-separated competitors list")
    run_parser.add_argument("--count", type=int, default=1000, help="Total prompts count (default: 1000)")
    run_parser.add_argument("--lang", type=str, default="both", choices=["fa", "en", "both"], help="Query language")
    run_parser.add_argument("--out", type=str, default="output", help="Output directory")

    # Command: serve
    serve_parser = subparsers.add_parser("serve", help="Start the interactive Web Dashboard & API server")
    serve_parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address (default: 0.0.0.0)")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port number (default: 8000)")
    serve_parser.add_argument("--reload", action="store_true", help="Enable auto-reload")

    # Command: generate
    gen_parser = subparsers.add_parser("generate", help="Generate prompt datasets without running inference")
    gen_parser.add_argument("--niche", type=str, default="crm_sales", help="Industry preset key")
    gen_parser.add_argument("--brand", type=str, default="HubSpot", help="Target Brand Name")
    gen_parser.add_argument("--count", type=int, default=1000, help="Total prompts count")
    gen_parser.add_argument("--lang", type=str, default="both", choices=["fa", "en", "both"], help="Language")
    gen_parser.add_argument("--out", type=str, default="prompts.json", help="Output JSON path")

    # Command: mcp
    mcp_parser = subparsers.add_parser("mcp", help="Start MCP (Model Context Protocol) Server for Claude Desktop & Cursor")

    args = parser.parse_args()

    if args.command == "run":
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
