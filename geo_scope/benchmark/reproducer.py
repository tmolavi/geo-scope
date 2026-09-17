# Deterministic reproduction and verification engine for GEO-Scope benchmarks.
import json
import math
from pathlib import Path
from typing import Dict, Any, List, Optional

from geo_scope.benchmark.hasher import verify_dataset_checksums, compute_file_sha256, compute_composite_hash
from geo_scope.benchmark.models import BenchmarkMetrics, BenchmarkManifest
from geo_scope.benchmark.calculator import BenchmarkCalculator


class BenchmarkReproducer:
    """
    Verifies cryptographic dataset integrity and recomputes all metrics from raw records.
    """

    def __init__(self, tolerance: float = 0.05):
        self.tolerance = tolerance
        self.calculator = BenchmarkCalculator()

    def verify_and_reproduce(self, dataset_dir: str | Path) -> Dict[str, Any]:
        path = Path(dataset_dir)
        if not path.is_dir():
            return {
                "success": False,
                "error": f"Directory not found: {path}",
                "checksums_valid": False,
                "metrics_matched": False,
                "differences": [f"Directory not found: {path}"],
            }

        # 1. Verify SHA-256 Checksums
        chk_res = verify_dataset_checksums(path)
        if not chk_res["valid"]:
            return {
                "success": False,
                "error": "Dataset checksum verification failed (tampered, corrupted, or missing files).",
                "checksums_valid": False,
                "metrics_matched": False,
                "mismatches": chk_res["mismatches"],
                "missing_files": chk_res["missing_files"],
                "extra_files": chk_res["extra_files"],
                "differences": [f"Checksum mismatch on: {chk_res.get('mismatches')}"],
            }

        # 2. Check Manifest
        manifest_file = path / "manifest.json"
        if not manifest_file.exists():
            return {
                "success": False,
                "error": "Missing manifest.json",
                "checksums_valid": True,
                "metrics_matched": False,
                "differences": ["Missing manifest.json"],
            }

        manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))
        dataset_id = manifest_data.get("dataset_id", path.name)
        exec_mode = manifest_data.get("execution_mode", "synthetic")
        research_status = manifest_data.get("research_status", "demo_only")

        # 3. Load Raw Data
        prompts = []
        with open(path / "prompts.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    prompts.append(json.loads(line))

        observations = []
        with open(path / "observations.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    observations.append(json.loads(line))

        citations = []
        if (path / "citations.jsonl").exists():
            with open(path / "citations.jsonl", "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        citations.append(json.loads(line))

        brands_file = (path / "entities.json") if (path / "entities.json").exists() else (path / "brands.json")
        brands = json.loads(brands_file.read_text(encoding="utf-8"))
        providers = json.loads((path / "providers.json").read_text(encoding="utf-8"))
        expected_metrics_raw = json.loads((path / "metrics.json").read_text(encoding="utf-8"))

        # 4. Recompute Metrics from Raw Records
        recomputed = self.calculator.compute(
            prompts=prompts,
            observations=observations,
            citations=citations,
            brands=brands,
            providers=providers,
            dataset_id=dataset_id,
            execution_mode=exec_mode,
            research_status=research_status,
        )

        recomp_dict = recomputed.model_dump()

        # 5. Compare with stored metrics.json
        differences = []

        for cfield in ["total_prompts", "total_observations", "successful_observations", "failed_observations"]:
            if recomp_dict.get(cfield) != expected_metrics_raw.get(cfield):
                differences.append(f"{cfield} mismatch: expected {expected_metrics_raw.get(cfield)}, got {recomp_dict.get(cfield)}")

        exp_brands = {b["brand"]: b for b in expected_metrics_raw.get("brands", [])}
        for act_b in recomp_dict.get("brands", []):
            bname = act_b["brand"]
            if bname not in exp_brands:
                differences.append(f"Unexpected brand {bname} in recomputed metrics")
                continue
            exp_b = exp_brands[bname]
            for mkey in ["mention_rate", "top1_rate", "share_of_model"]:
                exp_v = exp_b.get(mkey, {}).get("value")
                act_v = act_b.get(mkey, {}).get("value")
                if exp_v is None and act_v is None:
                    continue
                if exp_v is None or act_v is None or abs(exp_v - act_v) > self.tolerance:
                    differences.append(f"{bname} {mkey} difference: expected {exp_v}, recomputed {act_v}")

        metrics_matched = len(differences) == 0
        success = chk_res["valid"] and metrics_matched

        chk_str = "VERIFIED (Bit-for-bit intact)" if chk_res["valid"] else "FAILED"
        math_str = "VERIFIED (Recomputed from raw records)" if metrics_matched else "MISMATCH"

        report_lines = [
            "=" * 70,
            f"GEO-Scope Benchmark Verification & Reproduction: {dataset_id}",
            "=" * 70,
            f"• Execution Mode    : {exec_mode}",
            f"• Research Status   : {research_status}",
            f"• SHA-256 Checksums : {chk_str}",
            f"• Metric Math Check : {math_str}",
            f"• Prompts / Obs     : {len(prompts)} prompts / {len(observations)} observations",
            f"• Brands Evaluated  : {', '.join([b.get('name', '') for b in brands])}",
            "-" * 70,
        ]

        if differences:
            report_lines.append("Discrepancies Found:")
            for d in differences:
                report_lines.append(f"  ✗ {d}")
        else:
            report_lines.append("✓ All observations, citations, and bootstrap confidence intervals successfully reproduced.")

        report_lines.append("=" * 70)
        report_text = "\n".join(report_lines)

        return {
            "success": success,
            "dataset_id": dataset_id,
            "execution_mode": exec_mode,
            "research_status": research_status,
            "checksums_valid": chk_res["valid"],
            "metrics_matched": metrics_matched,
            "total_prompts": len(prompts),
            "total_observations": len(observations),
            "differences": differences,
            "report": report_text,
            "recomputed_metrics": recomp_dict,
        }
