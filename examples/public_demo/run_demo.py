#!/usr/bin/env python3
"""
GEO-Scope Public Proof Demonstration Runner.
Demonstrates SHA-256 cryptographic verification and empirical metric recalculation offline.
"""
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

from geo_scope.benchmark.reproducer import BenchmarkReproducer

def main():
    demo_dir = Path(__file__).resolve().parent
    print("=" * 70)
    print("GEO-Scope Public Demo: Offline Benchmark Verification & Reproduction")
    print(f"Dataset Location: {demo_dir}")
    print("=" * 70)

    reproducer = BenchmarkReproducer()
    result = reproducer.verify_and_reproduce(demo_dir)

    print(result.get("report", ""))
    if result["success"]:
        print("\n✅ Verification Successful: 100% mathematical integrity confirmed.")
        sys.exit(0)
    else:
        print("\n❌ Verification Failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
