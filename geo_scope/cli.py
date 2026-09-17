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


def benchmark_cmd(args):
    from geo_scope.benchmark.builder import BenchmarkBuilder
    from geo_scope.benchmark.hasher import verify_dataset_checksums
    from geo_scope.benchmark.reproducer import BenchmarkReproducer
    from geo_scope.benchmark.profile import BenchmarkProfile
    from geo_scope.benchmark.runner import LiveBenchmarkRunner, estimate_benchmark_cost

    sub = getattr(args, "benchmark_action", None)
    if not sub:
        print("Usage: geo-scope benchmark [run|estimate-cost|verify|reproduce|export] [options]")
        return

    if sub == "run":
        profile_path = args.profile
        profile = BenchmarkProfile.from_file(profile_path)
        runner = LiveBenchmarkRunner(profile=profile, out_dir=getattr(args, "out", "benchmark"))
        benchmark_mode = getattr(args, "mode", None)
        res = runner.run(
            resume=getattr(args, "resume", False),
            dry_run=getattr(args, "dry_run", False),
            benchmark_mode=benchmark_mode,
        )
        if res.get("dry_run"):
            print("\n📊 Dry Run Cost Estimation:")
            print(json.dumps(res["cost_estimate"], indent=2))
        else:
            print(f"\n✓ Benchmark completed successfully!")
            print(f"📁 Dataset Package : {res['dataset_path']}")
            print(f"📄 Research Report : {res['report_path']}")

    elif sub == "estimate-cost":
        profile_path = args.profile
        profile = BenchmarkProfile.from_file(profile_path)
        est = estimate_benchmark_cost(profile)
        print("\n💰 Benchmark Cost Estimation:")
        print(f"• Benchmark Version : {est['benchmark_version']}")
        print(f"• Dataset Name      : {est['dataset_name']}")
        print(f"• Execution Mode    : {est['execution_mode']}")
        print(f"• Prompts Count     : {est['prompt_count']}")
        print(f"• Providers ({est['provider_count']})   : {', '.join(est['providers'])}")
        print(f"• Total Calls       : {est['total_inferences']}")
        print(f"• Estimated Cost    : ${est['estimated_cost_usd']:.4f} USD")
        print(f"• Budget Limit      : ${est['max_cost_limit_usd']:.2f} USD")
        print(f"• Within Budget     : {'✓ Yes' if est['within_budget'] else '✗ Exceeds budget'}")

    elif sub == "verify":
        dataset_path = args.dataset
        res = verify_dataset_checksums(dataset_path)
        if res["valid"]:
            print(f"✓ Checksum Verification PASSED: {res['total_files']} files verified intact in '{dataset_path}'")
        else:
            print(f"✗ Checksum Verification FAILED in '{dataset_path}':")
            for m in res.get("mismatches", []):
                print(f"  - Mismatch: {m['file']} (expected: {m['expected'][:10]}..., got: {m['actual'][:10]}...)")
            for mf in res.get("missing_files", []):
                print(f"  - Missing file: {mf}")
            for ef in res.get("extra_files", []):
                print(f"  - Extra unverified file: {ef}")
            sys.exit(1)

    elif sub == "reproduce":
        dataset_path = args.dataset
        reproducer = BenchmarkReproducer(tolerance=getattr(args, "tolerance", 0.05))
        res = reproducer.verify_and_reproduce(dataset_path)
        print(res["report"])
        if getattr(args, "out", None):
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(res, f, ensure_ascii=False, indent=2)
            print(f"Reproduction result saved to {args.out}")
        if not res["success"]:
            sys.exit(1)

    elif sub == "prepare":
        from geo_scope.questions.discovery import prepare_benchmark_dataset
        obs_inputs = getattr(args, "observed", []) or []
        if isinstance(obs_inputs, str):
            obs_inputs = [x.strip() for x in obs_inputs.split(",") if x.strip()]
        gen_inputs = getattr(args, "generated", []) or []
        if isinstance(gen_inputs, str):
            gen_inputs = [x.strip() for x in gen_inputs.split(",") if x.strip()]
        comps = (
            [c.strip() for c in args.competitors.split(",") if c.strip()]
            if getattr(args, "competitors", None)
            else ["Competitor A", "Competitor B"]
        )
        res = prepare_benchmark_dataset(
            topic=args.topic,
            observed_inputs=obs_inputs,
            generated_inputs=gen_inputs,
            include_default_generated=not getattr(args, "no_default_generated", False),
            brand=getattr(args, "brand", "My Brand"),
            competitors=comps,
            out_dir=getattr(args, "out", "benchmark"),
            dataset_id=getattr(args, "dataset_id", None),
            category=getattr(args, "category", "GEO"),
            threshold=getattr(args, "threshold", 0.88),
        )
        print(f"\n✓ Prepared versioned benchmark dataset in '{res['directory']}'")
        print(f"• Dataset ID        : {res['dataset_id']}")
        print(f"• Total Prompts     : {res['total_prompts']}")
        print(f"• Observed Prompts  : {res['observed_count']} (Real demand -> {res['observed_file']})")
        print(f"• Generated Prompts : {res['generated_count']} (Templates -> {res['generated_file']})")
        print(f"• Unified Prompts   : {res['prompts_file']}")
        print(f"• Manifest File     : {res['manifest_file']}")
        print(f"• Provenance File   : {res['provenance_file']}")

    elif sub == "export":
        out_dir = args.out
        dataset_id = args.dataset_id or "geo-scope-benchmark-2026.1"
        builder = BenchmarkBuilder(dataset_id=dataset_id)
        
        # Load experiment if provided
        exp_file = args.experiment
        if exp_file and os.path.exists(exp_file):
            with open(exp_file, "r", encoding="utf-8") as f:
                exp_data = json.load(f)
            prompts = exp_data.get("prompts", [])
            obs = exp_data.get("records", [])
            cits = exp_data.get("citations", [])
            brands = exp_data.get("brands", [])
            providers = exp_data.get("providers", [])
            exec_mode = exp_data.get("execution_mode", args.mode)
            res_status = exp_data.get("research_status", args.status)
        else:
            print(f"Error: Experiment file not found at '{exp_file}'", file=sys.stderr)
            sys.exit(1)

        pkg_path = builder.build_package(
            out_dir=out_dir,
            prompts=prompts,
            observations=obs,
            citations=cits,
            brands=brands,
            providers=providers,
            execution_mode=exec_mode,
            research_status=res_status,
        )
        print(f"✓ Benchmark dataset package exported to: {pkg_path}")

    elif sub == "providers-check":
        import asyncio
        from geo_scope.benchmark.validator import ProviderValidator
        gateway_url = getattr(args, "url", None) or os.getenv("HAMZAD_GATEWAY_URL", "https://api.molavi.pro")

        if getattr(args, "profile", None) and os.path.exists(args.profile):
            profile = BenchmarkProfile.from_file(args.profile)
            providers_to_check = profile.providers
        elif getattr(args, "providers", None):
            providers_to_check = [p.strip() for p in args.providers.split(",") if p.strip()]
        else:
            providers_to_check = ["gemini-2.5-flash", "gpt-4o", "claude-3-5-sonnet", "sonar-pro"]

        validator = ProviderValidator(gateway_url=gateway_url)
        results = asyncio.run(validator.validate_all(providers_to_check, prompt=getattr(args, "prompt", "Reply with exactly OK.")))

        if getattr(args, "json", False):
            print(json.dumps({p: res.to_manifest_dict() for p, res in results.items()}, indent=2))
        else:
            print(validator.format_report(results))


def prompts_cmd(args):
    """
    Question discovery, clustering, and candidate prompt generation powered by AnswerPath GEO.
    """
    action = getattr(args, "prompts_action", "discover")
    if action == "discover":
        from geo_scope.questions.discovery import discover_questions, format_discovery_report
        inputs = getattr(args, "input", []) or []
        if isinstance(inputs, str):
            inputs = [x.strip() for x in inputs.split(",") if x.strip()]
        comps = (
            [c.strip() for c in args.competitors.split(",") if c.strip()]
            if getattr(args, "competitors", None)
            else []
        )
        result = discover_questions(
            topic=args.topic,
            input_paths=inputs,
            include_generated=not getattr(args, "no_generated", False),
            threshold=getattr(args, "threshold", 0.88),
            category=getattr(args, "category", "GEO"),
            target_brand=getattr(args, "brand", ""),
            competitors=comps,
        )
        if getattr(args, "json", False):
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(format_discovery_report(result))

        if getattr(args, "out", None):
            out_p = Path(args.out)
            out_p.mkdir(parents=True, exist_ok=True)
            (out_p / "questions.json").write_text(json.dumps([q.to_dict() for q in result.questions], ensure_ascii=False, indent=2), encoding="utf-8")
            (out_p / "prompts.jsonl").write_text("\n".join(json.dumps(p, ensure_ascii=False) for p in result.recommended_prompts) + "\n", encoding="utf-8")
            print(f"\n📁 Discovered question artifacts written to '{args.out}/'")


def hamzad_cmd(args):
    """
    Validate Hamzad AI Gateway connectivity, authentication, and smoke inference.
    """
    from geo_scope.providers.hamzad_provider import HamzadProvider

    action = getattr(args, "hamzad_action", "check") or "check"
    if action == "check":
        gateway_url = (getattr(args, "url", None) or os.getenv("HAMZAD_GATEWAY_URL", "https://api.molavi.pro")).rstrip("/")
        api_key = os.getenv("HAMZAD_API_KEY") or os.getenv("HAMZAD_MASTER_API_KEY", "")
        project_id = os.getenv("HAMZAD_PROJECT_ID", "hamzad")

        print("\n" + "=" * 75)
        print("🌐 Hamzad AI Gateway Diagnostic & Smoke Check")
        print("=" * 75)
        print(f"• Gateway Endpoint : {gateway_url}")
        print(f"• Project ID       : {project_id}")
        print(f"• Authentication   : {'Configured (Bearer / Header)' if api_key else 'Public / Default Project'}")
        print("-" * 75)

        provider = HamzadProvider(gateway_url=gateway_url, project_id=project_id, api_key=api_key)

        # 1. Health check
        print("1. Testing Gateway Reachability & Health...")
        health = asyncio.run(provider.check_health())
        if health.get("ok"):
            print(f"   ✓ Reachable: {health.get('path')} (HTTP {health.get('status_code')})")
        else:
            print(f"   ❌ Health check failed: {health.get('error')}")

        # 2. Smoke inference
        print("\n2. Testing Model Inference (Smoke Query)...")
        prompt = getattr(args, "prompt", "Reply with exactly OK.")
        model = getattr(args, "model", "hamzad-fast")
        smoke = asyncio.run(provider.smoke_check(prompt=prompt, model=model))

        if smoke.get("ok"):
            print(f"   ✓ Inference Successful (HTTP 200)")
            print(f"   • Model     : {smoke.get('model')}")
            print(f"   • Provider  : {smoke.get('provider')}")
            print(f"   • Latency   : {smoke.get('latency_ms')} ms")
            print(f"   • Response  : {smoke.get('text')}")
        else:
            print(f"   ❌ Inference Failed: {smoke.get('error')}")

        print("=" * 75)
        if health.get("ok") and smoke.get("ok"):
            print("🎉 Hamzad AI Gateway is fully operational and ready for GEO-Scope benchmarks.\n")
        else:
            print("⚠️ Some checks failed. Verify network connectivity or configuration.\n")
            sys.exit(1)


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

    # Command: benchmark
    bmk_parser = subparsers.add_parser("benchmark", help="Public benchmark dataset verification, reproduction & export")
    bmk_subparsers = bmk_parser.add_subparsers(dest="benchmark_action", help="Benchmark action")

    # benchmark run
    run_bmk_p = bmk_subparsers.add_parser("run", help="Run a live or synthetic multi-provider benchmark from a profile YAML")
    run_bmk_p.add_argument("--profile", type=str, required=True, help="Path to benchmark profile YAML file")
    run_bmk_p.add_argument("--out", type=str, default="benchmark", help="Target output directory")
    run_bmk_p.add_argument("--resume", action="store_true", help="Resume interrupted benchmark execution")
    run_bmk_p.add_argument("--dry-run", action="store_true", help="Estimate cost and validate profile without executing calls")
    run_bmk_p.add_argument(
        "--mode",
        type=str,
        choices=["strict", "discovery"],
        default=None,
        help="Benchmark execution mode: strict (enforces zero-fallback) or discovery (accepts all with full provenance)",
    )

    # benchmark estimate-cost
    est_p = bmk_subparsers.add_parser("estimate-cost", help="Estimate API inference cost and call counts for a benchmark profile")
    est_p.add_argument("--profile", type=str, required=True, help="Path to benchmark profile YAML file")

    # benchmark verify
    verify_p = bmk_subparsers.add_parser("verify", help="Verify SHA-256 checksums of a benchmark dataset")
    verify_p.add_argument("--dataset", type=str, required=True, help="Path to benchmark dataset directory")

    # benchmark reproduce
    reproduce_p = bmk_subparsers.add_parser("reproduce", help="Verify checksums and recompute all metrics from raw observations")
    reproduce_p.add_argument("--dataset", type=str, required=True, help="Path to benchmark dataset directory")
    reproduce_p.add_argument("--tolerance", type=float, default=0.05, help="Numerical tolerance for float comparison")
    reproduce_p.add_argument("--out", type=str, default=None, help="Optional output JSON file for reproduction report")

    # benchmark export
    export_p = bmk_subparsers.add_parser("export", help="Export an experiment run to a benchmark dataset package")
    export_p.add_argument("--experiment", type=str, required=True, help="Path to experiment JSON file")
    export_p.add_argument("--out", type=str, default="benchmark", help="Target parent directory for benchmark package")
    export_p.add_argument("--dataset-id", type=str, default="geo-scope-benchmark-2026.1", help="Dataset identifier")
    export_p.add_argument("--mode", type=str, default="synthetic", choices=["live", "synthetic"], help="Execution mode")
    export_p.add_argument("--status", type=str, default="demo_only", choices=["peer_review_ready", "demo_only"], help="Research status")

    # benchmark providers-check
    prov_check_p = bmk_subparsers.add_parser("providers-check", help="Verify live provider routing, model identity & fallback integrity")
    prov_check_p.add_argument("--profile", type=str, default=None, help="Path to benchmark profile YAML file")
    prov_check_p.add_argument("--providers", type=str, default=None, help="Comma-separated providers to validate")
    prov_check_p.add_argument("--url", type=str, default=None, help="Override Hamzad Gateway URL")
    prov_check_p.add_argument("--prompt", type=str, default="Reply with exactly OK.", help="Validation prompt")
    prov_check_p.add_argument("--json", action="store_true", help="Output JSON results")

    # benchmark prepare
    prep_p = bmk_subparsers.add_parser("prepare", help="Prepare a versioned benchmark dataset with separated observed and generated prompts")
    prep_p.add_argument("--topic", type=str, required=True, help="Topic, niche, or product domain")
    prep_p.add_argument("--observed", action="append", default=[], help="Path to observed user queries / logs (.json, .jsonl, .csv, .zip, .txt)")
    prep_p.add_argument("--generated", action="append", default=[], help="Path to custom generated prompt files")
    prep_p.add_argument("--no-default-generated", action="store_true", help="Omit default AnswerPath template research prompts")
    prep_p.add_argument("--brand", type=str, default="My Brand", help="Target Brand Name")
    prep_p.add_argument("--competitors", type=str, default=None, help="Comma-separated competitors list")
    prep_p.add_argument("--category", type=str, default="GEO", help="Benchmark category name")
    prep_p.add_argument("--threshold", type=float, default=0.88, help="Clustering similarity threshold")
    prep_p.add_argument("--dataset-id", type=str, default=None, help="Custom dataset ID")
    prep_p.add_argument("--out", type=str, default="benchmark", help="Output directory")

    # Command: prompts
    prompts_parser = subparsers.add_parser("prompts", help="Question discovery, intent extraction, and prompt clustering via AnswerPath GEO")
    prompts_subparsers = prompts_parser.add_subparsers(dest="prompts_action", help="Prompts action")

    # prompts discover
    disc_p = prompts_subparsers.add_parser("discover", help="Discover user questions, cluster by intent, and generate candidate benchmark sets")
    disc_p.add_argument("topic", type=str, help="Topic, niche, or industry to mine questions for")
    disc_p.add_argument("--input", action="append", default=[], help="Owned export or log file/directory (.json, .jsonl, .csv, .zip, .txt)")
    disc_p.add_argument("--no-generated", action="store_true", help="Only mine observed questions (omit template generator)")
    disc_p.add_argument("--threshold", type=float, default=0.88, help="Deduplication and clustering similarity threshold (0.0-1.0)")
    disc_p.add_argument("--category", type=str, default="GEO", help="Domain category tag")
    disc_p.add_argument("--brand", type=str, default="", help="Target Brand Name")
    disc_p.add_argument("--competitors", type=str, default=None, help="Comma-separated competitors list")
    disc_p.add_argument("--out", type=str, default=None, help="Output directory to save questions.json and prompts.jsonl")
    disc_p.add_argument("--json", action="store_true", help="Output structured JSON instead of human-readable report")

    # Command: hamzad
    hamzad_parser = subparsers.add_parser("hamzad", help="Hamzad AI Gateway connectivity, authentication & smoke inference")
    hamzad_subparsers = hamzad_parser.add_subparsers(dest="hamzad_action", help="Hamzad action")

    # hamzad check
    hamzad_check_p = hamzad_subparsers.add_parser("check", help="Verify gateway health, authentication, and execute smoke query")
    hamzad_check_p.add_argument("--url", type=str, default=None, help="Override gateway URL (default: https://api.molavi.pro)")
    hamzad_check_p.add_argument("--model", type=str, default="hamzad-fast", help="Target model (default: hamzad-fast)")
    hamzad_check_p.add_argument("--prompt", type=str, default="Reply with exactly OK.", help="Smoke prompt")

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
    elif args.command == "benchmark":
        benchmark_cmd(args)
    elif args.command == "prompts":
        prompts_cmd(args)
    elif args.command == "hamzad":
        hamzad_cmd(args)
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

