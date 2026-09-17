#!/usr/bin/env python3
"""
Live Benchmark Execution Pipeline for GEO-Scope using Hamzad AI Gateway.
Executes real multi-model search and recommendation queries against Google Gemini,
Perplexity Sonar, OpenAI ChatGPT, and Anthropic Claude via Hamzad Gateway.

Security Guarantee:
- GEO-Scope stores ZERO provider API keys.
- All model keys and credentials remain isolated within Hamzad Gateway.
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path
import httpx

from geo_scope.benchmark.profile import BenchmarkProfile
from geo_scope.benchmark.runner import LiveBenchmarkRunner, estimate_benchmark_cost
from geo_scope.benchmark.hasher import verify_dataset_checksums
from geo_scope.benchmark.reproducer import BenchmarkReproducer
from geo_scope.providers.hamzad_provider import HamzadProvider


async def check_gateway_connectivity(gateway_url: str, timeout: float = 2.0) -> bool:
    """
    Checks whether the Hamzad AI Gateway endpoint is reachable.
    """
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout, connect=timeout)) as client:
            resp = await client.get(f"{gateway_url.rstrip('/')}/health")
            if resp.status_code < 500:
                return True
    except Exception:
        pass
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Run GEO-Scope Live AI Visibility Benchmark with real Hamzad Gateway executions."
    )
    parser.add_argument(
        "--profile",
        type=str,
        default="benchmark/profiles/geo-scope-ai-visibility-2026.1.yaml",
        help="Path to benchmark profile YAML/JSON file.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="benchmark/releases",
        help="Target output directory for the benchmark release package.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume an interrupted benchmark run from partial state.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Estimate costs and validate pipeline without performing network calls.",
    )
    parser.add_argument(
        "--check-connection",
        action="store_true",
        help="Test connectivity to Hamzad AI Gateway and exit.",
    )

    args = parser.parse_args()

    profile_path = Path(args.profile)
    if not profile_path.exists():
        print(f"❌ Error: Profile file '{profile_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    print(f"📖 Loading benchmark profile from '{profile_path}'...")
    profile = BenchmarkProfile.from_file(profile_path)

    # Validate live execution mode
    if profile.execution_mode != "live":
        print(f"⚠️ Notice: Profile specifies execution_mode='{profile.execution_mode}'.")

    cost_est = estimate_benchmark_cost(profile)
    print("\n--- Benchmark Cost & Execution Estimate ---")
    print(f"Dataset Name:       {cost_est['dataset_name']}")
    print(f"Execution Mode:     {cost_est['execution_mode']}")
    print(f"Prompt Count:       {cost_est['prompt_count']}")
    print(f"Provider Count:     {cost_est['provider_count']}")
    print(f"Total Inferences:   {cost_est['total_inferences']}")
    print(f"Estimated Cost:     ${cost_est['estimated_cost_usd']:.4f} USD")
    print(f"Budget Limit:       ${cost_est['max_cost_limit_usd']:.2f} USD")
    print(f"Within Budget:      {'✓ YES' if cost_est['within_budget'] else '❌ NO'}")
    print("-------------------------------------------\n")

    gateway_url = os.getenv("HAMZAD_GATEWAY_URL", "http://localhost:8000")
    print(f"🌐 Target Hamzad AI Gateway: {gateway_url}")

    if args.check_connection:
        print(f"🔍 Testing connection to Hamzad Gateway at {gateway_url}...")
        is_up = asyncio.run(check_gateway_connectivity(gateway_url))
        if is_up:
            print("✓ Hamzad Gateway is ONLINE and reachable.")
            sys.exit(0)
        else:
            print(f"❌ Could not connect to Hamzad Gateway at {gateway_url}.", file=sys.stderr)
            print("Ensure the Hamzad Gateway service is running and accessible.", file=sys.stderr)
            sys.exit(1)

    if args.dry_run or profile.cost_limits.dry_run:
        print("🔍 Dry-Run mode enabled. Initializing runner for pre-flight validation...")
        runner = LiveBenchmarkRunner(profile=profile, out_dir=args.output_dir)
        res = runner.run(dry_run=True)
        print("✓ Pre-flight dry-run completed successfully.")
        sys.exit(0)

    # Check connection before starting live execution
    is_up = asyncio.run(check_gateway_connectivity(gateway_url, timeout=3.0))
    if not is_up:
        print(
            f"⚠️ Warning: Hamzad Gateway at {gateway_url} appears offline or unreachable.\n"
            f"Live execution requires a running Hamzad Gateway.\n"
            f"Set HAMZAD_GATEWAY_URL to a valid endpoint or run with --dry-run for validation.",
            file=sys.stderr,
        )

    # Execute live benchmark
    print(f"🚀 Starting Live Benchmark execution for dataset '{profile.dataset_name}'...")
    runner = LiveBenchmarkRunner(profile=profile, out_dir=args.output_dir)
    result = runner.run(resume=args.resume, dry_run=False)

    if result.get("success"):
        pkg_path = Path(result["dataset_path"])
        print(f"\n🎉 Live benchmark package successfully generated at: {pkg_path}")

        # Checksum Verification
        chk = verify_dataset_checksums(pkg_path)
        print(f"🔒 Checksum verification: valid={chk['valid']}, mismatches={len(chk['mismatches'])}")

        # Metric Reproducibility Verification
        reproducer = BenchmarkReproducer(tolerance=0.01)
        rep = reproducer.verify_and_reproduce(pkg_path)
        print(f"📊 Reproduction check: success={rep['success']}, metrics_matched={rep['metrics_matched']}")
    else:
        print(f"❌ Benchmark run failed: {result}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
