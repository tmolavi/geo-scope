#!/usr/bin/env python3
"""
Command Line Interface for GEO-Scope Platform
Supports:
  - geo-scope demo (5-Minute Quickstart Demo)
  - geo-scope run --mode live --providers perplexity,gemini (Real Provider Benchmark)
  - geo-scope run --mode simulation (Deterministic Baseline)
  - geo-scope providers (Provider Availability & Diagnostic)
  - geo-scope serve (Interactive Web Dashboard)
  - geo-scope mcp (Model Context Protocol Server)
"""

import argparse
import asyncio
import os
import sys
import json
from datetime import datetime, timezone

from geo_scope.engine.execution_mode import ExecutionMode
from geo_scope.engine.persistence import RawRunStore
from geo_scope.engine.query_generator import generate_prompt_dataset
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
    print("GEO-Scope Synthetic Benchmark")
    print("Execution mode: SIMULATION")
    print("Results are synthetic and must not be interpreted as real provider behavior.")
    print("🎯 Target Brand   : HubSpot   |   📂 Niche: CRM SaaS   |   🔢 Sample Prompts: 10")
    print("=" * 75)

    prompts = generate_prompt_dataset(
        niche_key="crm_sales",
        target_brand="HubSpot",
        competitors=["Salesforce", "Zoho CRM", "Pipedrive"],
        language="both",
        total_count=10,
    )

    runner = ModelRunner(mode=ExecutionMode.SIMULATION)
    models = ["perplexity_sonar", "chatgpt_search", "gemini_grounding", "claude_3_7"]
    print(
        f"\n[1/3] Running multi-model inference across {len(models)} AI engines ({len(prompts) * len(models)} calls)..."
    )

    responses = asyncio.run(runner.execute_batch(prompts, models=models))
    print("✓ Inference completed.")

    print("\n[2/3] Extracting brand mentions, ranks, and citation graph...")
    parsed = []
    for r in responses:
        item = parse_model_response(r["query_item"], r["model"], r["response_text"], r.get("provenance"))
        item["full_response_text"] = r["response_text"]
        item["query_text"] = r["query_item"]["query"]
        parsed.append(item)

    print("\n[3/3] Computing visibility metrics & generating report...")
    analyzer = AlgoAnalyzer(parsed, "HubSpot", ["Salesforce", "Zoho CRM", "Pipedrive"])
    analysis = analyzer.compute_full_analysis()

    # Save artifacts
    out_dir = "results"
    artifacts = generate_experiment_artifacts(analysis, parsed, prompts, out_dir=out_dir)

    print("\n" + "=" * 75)
    print("📊 DEMO EXPERIMENTAL BENCHMARK SUMMARY")
    print("=" * 75)
    print(f"• Target Brand Mention Rate (Share of Model) : {analysis['summary']['overall_sov']}%")
    print(f"• Top-1 Primary Recommendation Rate : {analysis['summary']['overall_top1_rate']}%")
    print(f"• Top Performing AI Engine          : {analysis['summary']['best_performing_model']}")
    print(f"• Lowest Performing AI Engine       : {analysis['summary']['weakest_performing_model']}")
    print("-" * 75)
    print("🤖 Model Breakdown:")
    for m, st in analysis["share_of_model"]["by_model"].items():
        print(
            f"  - {m:<20}: Mention Rate: {st['mention_rate_pct']}% | Top-1: {st['top1_rate_pct']}% | Avg Rank: #{st['avg_rank']}"
        )
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
    print('   geo-scope run --brand "Your Brand" --prompts my_prompts.csv\n')


def run_benchmark_cmd(args):
    if args.demo:
        run_demo_cmd()
        return

    started_at = datetime.now(timezone.utc).isoformat()
    os.makedirs(args.out, exist_ok=True)
    brand = args.brand.strip() if args.brand else "My Brand"
    comps = (
        [c.strip() for c in args.competitors.split(",") if c.strip()]
        if args.competitors
        else ["Competitor A", "Competitor B"]
    )

    # Resolve execution mode
    mode = ExecutionMode.from_string(args.mode)

    # 1. Load Prompts
    if args.prompts:
        print(f"\n[1/4] Loading custom user prompts from '{args.prompts}'...")
        prompts = load_custom_prompts(
            file_path=args.prompts, default_brand=brand, default_competitors=comps, default_niche=args.niche
        )
        print(f"✓ Loaded {len(prompts)} custom prompts.")
    else:
        print(f"\n[1/4] Synthesizing {args.count} structured prompts across 5 intent strata...")
        prompts = generate_prompt_dataset(
            niche_key=args.niche,
            target_brand=brand,
            competitors=comps,
            language=args.lang,
            total_count=args.count,
            seed=args.seed,
        )
        print(f"✓ Synthesized {len(prompts)} prompts.")

    # Determine provider selection
    provider_arg = args.providers or args.models
    if provider_arg:
        target_providers = [m.strip() for m in provider_arg.split(",") if m.strip()]
    else:
        if mode == ExecutionMode.LIVE:
            target_providers = ["perplexity_sonar", "openai_completion", "gemini_grounding", "claude_completion"]
        else:
            target_providers = ["perplexity_sonar", "chatgpt_search", "gemini_grounding", "claude_3_7"]

    # Initialize durable raw run store
    exp_id = f"EXP-{int(datetime.now(timezone.utc).timestamp())}"
    run_store = RawRunStore(base_dir=os.path.join(args.out, "runs"), experiment_id=exp_id)

    runner = ModelRunner(mode=mode, seed=args.seed, run_store=run_store, experiment_id=exp_id)
    if not args.responses:
        runner.validate_models(target_providers)

    # Print Mode Banners
    print("\n" + "=" * 75)
    if mode == ExecutionMode.LIVE:
        print("GEO-Scope Live Benchmark")
        print("Execution mode: LIVE")
        print("Synthetic fallback: DISABLED")
    else:
        print("GEO-Scope Synthetic Benchmark")
        print("Execution mode: SIMULATION")
        print("Results are synthetic and must not be interpreted as real provider behavior.")

    print(f"🎯 Target Brand  : {brand}")
    print(f"👥 Competitors   : {', '.join(comps)}")
    print(f"🔢 Total Prompts : {len(prompts)} ({len(prompts) * len(target_providers)} total inferences)")
    print(f"🤖 Providers     : {', '.join(target_providers)}")
    print(f"📦 Experiment ID : {exp_id}")
    print(f"📁 Raw Storage   : {run_store.run_dir}")
    print("=" * 75)

    if args.dry_run:
        print("\n🔍 Dry-run complete. Exiting without executing inferences.")
        return

    # 2. Inferences
    print(f"\n[2/4] Executing batch inference across {len(target_providers)} AI engines...")

    def progress(done, total):
        pct = int((done / total) * 100)
        print(f"\rProgress: [{done}/{total}] {pct}% completed...", end="", flush=True)

    if args.responses:
        from geo_scope.engine.response_import import load_responses

        raw_responses = load_responses(args.responses)
        brands = {r["query_item"]["target_brand"] for r in raw_responses}
        if brands != {brand}:
            raise ValueError("Imported target_brand must match --brand in every response")
        prompts = list({r["query_item"]["id"]: r["query_item"] for r in raw_responses}.values())
        comps = sorted({entity for q in prompts for entity in q["expected_entities"] if entity != brand})
        target_providers = sorted({r["model"] for r in raw_responses})
    else:
        raw_responses = asyncio.run(runner.execute_batch(prompts, models=target_providers, progress_callback=progress))
    print("\n✓ Inferences completed.")

    # 3. Extraction
    print("\n[3/4] Parsing brand mentions, rankings, and citation graphs...")
    parsed = []
    failed_counts = {}
    for item in raw_responses:
        q_item = item["query_item"]
        model = item["model"]
        text = item["response_text"]
        p_record = parse_model_response(q_item, model, text, item.get("provenance"))
        p_record["full_response_text"] = text
        p_record["query_text"] = q_item["query"]
        if item.get("status") == "failed":
            failed_counts[model] = failed_counts.get(model, 0) + 1
        parsed.append(p_record)
    print(f"✓ Processed {len(parsed)} model outputs.")

    # Expose failures clearly if any occurred
    if failed_counts:
        print("\n" + "!" * 75)
        print("⚠️ PROVIDER FAILURE REPORT (Zero Silent Fallback)")
        print("!" * 75)
        for model, count in failed_counts.items():
            sample_err = next((r.get("error") for r in raw_responses if r["model"] == model and r.get("error")), {})
            reason = sample_err.get("message", "Unknown provider error")
            print(f"Provider: {model}")
            print(f"Mode: {mode.value.upper()}")
            print(f"Status: FAILED ({count}/{len(prompts)} calls failed)")
            print(f"Reason: {reason}")
            print("Simulation fallback: disabled")
            print("-" * 75)

    # 4. Statistical Analysis & Report Generation
    print("\n[4/4] Computing visibility metrics & building portable reports...")
    analyzer = AlgoAnalyzer(parsed, brand, comps)
    analysis = analyzer.compute_full_analysis()
    delta_record = save_benchmark_snapshot(analysis, args.niche, brand, len(prompts))
    analysis["playbook"] = generate_geo_playbook(analysis, delta_info=delta_record)

    finished_at = datetime.now(timezone.utc).isoformat()

    # Create reproducible manifest
    provider_meta = {p_name: getattr(registry.get(p_name), "get_metadata", lambda: {})() for p_name in target_providers}
    run_store.create_manifest(
        execution_mode=mode.value,
        providers=provider_meta,
        models={p_name: getattr(registry.get(p_name), "model", p_name) for p_name in target_providers},
        prompts=prompts,
        started_at=started_at,
        finished_at=finished_at,
        configuration={"niche": args.niche, "brand": brand, "competitors": comps, "seed": args.seed},
    )

    artifacts = generate_experiment_artifacts(analysis, parsed, prompts, out_dir=args.out, experiment_id=exp_id)

    print("\n" + "=" * 75)
    print("📊 EXECUTIVE BENCHMARK RESULTS")
    print("=" * 75)
    print(f"• Execution Mode                            : {mode.value.upper()}")
    print(f"• Successful Inferences                     : {analysis['summary']['successful_executions']}/{analysis['summary']['total_ai_executions']}")
    if analysis['summary']['failed_executions'] > 0:
        print(f"• Failed Inferences (Excluded from SOV)     : {analysis['summary']['failed_executions']}")
    
    sov_str = f"{analysis['summary']['overall_sov']}%" if analysis['summary']['overall_sov'] is not None else "N/A"
    top1_str = f"{analysis['summary']['overall_top1_rate']}%" if analysis['summary']['overall_top1_rate'] is not None else "N/A"
    print(f"• Target Brand Mention Rate (Share of Model): {sov_str}")
    print(f"• Top-1 Recommendation Rate                 : {top1_str}")
    print(f"• Top Performing AI Engine                  : {analysis['summary']['best_performing_model']}")
    print(f"• Weakest Performing AI Engine              : {analysis['summary']['weakest_performing_model']}")
    if analysis['summary'].get('reason'):
        print(f"• Reason                                    : {analysis['summary']['reason']}")
    print("-" * 75)
    print("🏆 Competitor Matrix:")
    for c in analysis["competitor_matrix"]:
        is_t = "(Target Brand)" if c["is_target"] else "(Competitor)"
        m_rate_str = f"{c['mention_rate_pct']}%" if c['mention_rate_pct'] is not None else "N/A"
        t_rate_str = f"{c['top1_rate_pct']}%" if c['top1_rate_pct'] is not None else "N/A"
        print(f"  - {c['brand']:<15} : Mention Rate: {m_rate_str} | Top-1: {t_rate_str} {is_t}")
    print("=" * 75)
    print(f"\n📁 Portable Reports written to '{args.out}/':")
    print(f"  📄 Human-Readable Summary : {artifacts['summary_md']}")
    print(f"  🌐 Standalone HTML Report : {artifacts['report_html']}")
    print(f"  📦 Experiment Metadata    : {artifacts['experiment_json']}")
    print(f"  📊 Queries CSV Breakdown  : {artifacts['queries_csv']}")
    print(f"  🔗 Citations Graph CSV    : {artifacts['citations_csv']}")
    print(f"  📜 Run Manifest           : {run_store.manifest_path}")
    print(f"  🗄️ Raw Evidence JSONL     : {run_store.raw_dir}/")
    print("=" * 75 + "\n")


def serve_dashboard_cmd(args):
    import uvicorn

    print(f"🚀 Starting GEO-Scope Web Dashboard on http://{args.host}:{args.port}")
    uvicorn.run("geo_scope.server:app", host=args.host, port=args.port, reload=args.reload)


def mavi_cmd(args):
    from geo_scope.mavi import MAVIEngine
    import urllib.request
    import urllib.error

    html_content = ""
    http_status = 200

    if args.html and os.path.exists(args.html):
        with open(args.html, "r", encoding="utf-8") as f:
            html_content = f.read()
    elif args.url:
        try:
            req = urllib.request.Request(
                args.url,
                headers={"User-Agent": "GEO-Scope-MAVI/1.0 (+https://molavi.pro/)"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                http_status = resp.status
                html_content = resp.read().decode("utf-8", errors="ignore")
        except urllib.error.HTTPError as e:
            http_status = e.code
            html_content = e.read().decode("utf-8", errors="ignore")
        except Exception as e:
            http_status = 0
            print(f"⚠️ Warning: Failed to fetch URL '{args.url}': {e}", file=sys.stderr)

    experiment_data = None
    if args.experiment and os.path.exists(args.experiment):
        with open(args.experiment, "r", encoding="utf-8") as f:
            experiment_data = json.load(f)

    custom_weights = None
    if args.weights:
        if os.path.exists(args.weights):
            with open(args.weights, "r", encoding="utf-8") as f:
                custom_weights = json.load(f)
        else:
            try:
                custom_weights = json.loads(args.weights)
            except Exception:
                pass

    manual_layers = None
    if args.manual:
        try:
            manual_layers = json.loads(args.manual)
        except Exception as e:
            print(f"⚠️ Failed to parse --manual JSON: {e}", file=sys.stderr)

    engine = MAVIEngine(weights=custom_weights)
    report = engine.measure(
        html_content=html_content if html_content else None,
        url=args.url,
        target_brand=args.brand,
        experiment_data=experiment_data,
        manual_layers=manual_layers,
        http_status=http_status,
    )

    if args.format == "json":
        out_str = json.dumps(report.to_dict(), ensure_ascii=False, indent=2)
        print(out_str)
    else:
        out_str = engine.format_human_readable(report)
        print(out_str)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(json.dumps(report.to_dict(), ensure_ascii=False, indent=2) if args.out.endswith(".json") else out_str)
        print(f"\n💾 MAVI report written to '{args.out}'")


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")
    parser = argparse.ArgumentParser(
        prog="geo-scope",
        description="GEO-Scope: Generative Engine Optimization (GEO) & AI Algorithm Reverse-Engineering CLI",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: demo
    subparsers.add_parser("demo", help="Run 5-minute quickstart demo experiment")

    # Command: run
    run_parser = subparsers.add_parser("run", help="Run an AI visibility benchmark experiment")
    run_parser.add_argument("--demo", action="store_true", help="Run quick demo benchmark")
    run_parser.add_argument("--brand", type=str, default="HubSpot", help="Target Brand Name")
    run_parser.add_argument(
        "--competitors", type=str, default="Salesforce,Zoho CRM,Pipedrive", help="Comma-separated competitors list"
    )
    run_parser.add_argument(
        "--prompts", type=str, default=None, help="Path to custom prompts file (.csv, .json, .txt, .yaml)"
    )
    run_parser.add_argument("--niche", type=str, default="crm_sales", help="Industry preset key")
    run_parser.add_argument(
        "--count", type=int, default=50, help="Total prompts count when generating synthetically (default: 50)"
    )
    run_parser.add_argument("--lang", type=str, default="both", choices=["fa", "en", "both"], help="Query language")
    run_parser.add_argument("--out", type=str, default="results", help="Output directory for reports")
    run_parser.add_argument(
        "--dry-run", action="store_true", help="Simulate prompt loading and cost without calling models"
    )

    run_parser.add_argument(
        "--mode",
        choices=["live", "simulation", "simulate"],
        default="simulation",
        help="Explicit execution mode: live or simulation (default: simulation)",
    )
    run_parser.add_argument(
        "--providers",
        type=str,
        default=None,
        help="Comma-separated provider IDs (e.g. perplexity,gemini,openai,anthropic)",
    )
    run_parser.add_argument(
        "--models",
        type=str,
        default=None,
        help="Alias for --providers",
    )
    run_parser.add_argument("--seed", type=int, default=42, help="Dataset and simulation seed")
    run_parser.add_argument("--responses", help="Analyze a saved raw_responses.json without API access")

    # Command: mavi
    mavi_parser = subparsers.add_parser(
        "mavi", help="Measure Molavi AI Visibility Index (MAVI) across L1-L5 layers"
    )
    mavi_parser.add_argument("--url", type=str, default=None, help="Target URL to audit")
    mavi_parser.add_argument("--html", type=str, default=None, help="Path to HTML file to audit (SAGE L1-L4)")
    mavi_parser.add_argument("--brand", type=str, default="Target Entity", help="Target Brand / Entity name")
    mavi_parser.add_argument(
        "--experiment", type=str, default=None, help="Path to experiment.json for L5 Observed Visibility"
    )
    mavi_parser.add_argument(
        "--weights", type=str, default=None, help="JSON string or path to custom layer weights"
    )
    mavi_parser.add_argument(
        "--manual", type=str, default=None, help="JSON string for manual layer overrides (e.g. '{\"L1\": 85, \"L2\": 70}')"
    )
    mavi_parser.add_argument(
        "--format", type=str, default="text", choices=["text", "json"], help="Output format (text or json)"
    )
    mavi_parser.add_argument("--out", type=str, default=None, help="Output file path to save report")

    # Command: providers
    prov_parser = subparsers.add_parser("providers", help="List available providers and configuration status")
    prov_parser.add_argument("--json", action="store_true", help="Output raw JSON instead of aligned table")

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

    if args.command == "providers":
        if getattr(args, "json", False):
            print(json.dumps(registry.list_all(), ensure_ascii=False, indent=2))
        else:
            print(registry.format_availability_table())
    elif args.command == "demo":
        run_demo_cmd()
    elif args.command == "run":
        try:
            run_benchmark_cmd(args)
        except (ValueError, RuntimeError, OSError) as exc:
            parser.exit(2, f"Error: {exc}\n")
    elif args.command == "mavi":
        mavi_cmd(args)
    elif args.command == "serve":
        serve_dashboard_cmd(args)
    elif args.command == "mcp":
        from geo_scope.mcp_server import main as mcp_main

        mcp_main()
    elif args.command == "generate":
        prompts = generate_prompt_dataset(
            niche_key=args.niche, target_brand=args.brand, language=args.lang, total_count=args.count
        )
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(prompts, f, ensure_ascii=False, indent=2)
        print(f"✓ Generated {len(prompts)} prompts and saved to {args.out}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
