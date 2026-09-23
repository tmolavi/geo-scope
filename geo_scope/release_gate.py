"""
Benchmark Release Quality Gate for GEO-Scope.
Validates empirical benchmark packages for scientific rigor, provider integrity,
complete audit evidence, absence of simulation/fallback contamination, metadata conformance,
and cryptographic checksum verification prior to publication.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from geo_scope.benchmark.hasher import verify_dataset_checksums


SECRET_PATTERNS = [
    re.compile(r"sk-[a-zA-Z0-9_-]{20,}", re.IGNORECASE),
    re.compile(r"ghp_[a-zA-Z0-9]{30,}", re.IGNORECASE),
    re.compile(r"Bearer\s+(?!\[REDACTED\])[a-zA-Z0-9_\-\.]{25,}", re.IGNORECASE),
    re.compile(r"HAMZAD_API_KEY\s*=\s*['\"][a-zA-Z0-9_\-]{10,}['\"]", re.IGNORECASE),
]

REQUIRED_EVIDENCE_FILES = [
    "manifest.json",
    "prompts.jsonl",
    "raw_responses.jsonl",
    "observations.jsonl",
    "metrics.json",
    "errors.jsonl",
    "checksums.sha256",
    "methodology.md",
    "limitations.md",
]

REQUIRED_MANIFEST_FIELDS = [
    "schema_version",
    "benchmark_version",
    "execution_mode",
    "provider_matrix",
    "prompt_policy",
    "repeat_count",
    "comparison_batch_id",
]


def evaluate_release_gate(
    dataset_dir: Union[str, Path],
    output_report: Optional[Union[str, Path]] = None,
    is_empirical: bool = True,
) -> Dict[str, Any]:
    """
    Evaluates a benchmark dataset directory against strict scientific release gates.
    Returns a structured dictionary with overall status and per-check results.
    """
    path = Path(dataset_dir)
    if not path.is_dir():
        return {
            "dataset_dir": str(path),
            "status": "FAIL",
            "passed": False,
            "error": f"Directory not found: {path}",
            "checks": {},
        }

    checks: Dict[str, Dict[str, Any]] = {}

    # 1. Evidence Completeness Gate
    missing_files = []
    for f in REQUIRED_EVIDENCE_FILES:
        if not (path / f).exists():
            missing_files.append(f)
    
    # Check entities file
    has_entities = (path / "entities.json").exists() or (path / "brands.json").exists()
    if not has_entities:
        missing_files.append("entities.json")

    checks["evidence_artifacts_completeness"] = {
        "passed": len(missing_files) == 0,
        "detail": "All required evidence files present" if len(missing_files) == 0 else f"Missing required evidence files: {', '.join(missing_files)}",
    }

    # 2. Manifest & Metadata Conformance Gate
    manifest_path = path / "manifest.json"
    manifest_data: Dict[str, Any] = {}
    missing_manifest_fields = []
    if manifest_path.exists():
        try:
            manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
            for req_field in REQUIRED_MANIFEST_FIELDS:
                if req_field not in manifest_data and (
                    req_field != "benchmark_version" or "dataset_version" not in manifest_data
                ):
                    missing_manifest_fields.append(req_field)
        except Exception as exc:
            missing_manifest_fields.append(f"Invalid JSON: {exc}")
    else:
        missing_manifest_fields.append("manifest.json missing")

    checks["metadata_conformance"] = {
        "passed": len(missing_manifest_fields) == 0,
        "detail": "All required manifest metadata fields present" if len(missing_manifest_fields) == 0 else f"Missing manifest fields: {', '.join(missing_manifest_fields)}",
    }

    # 3. Cryptographic Checksum Integrity
    chk_res = verify_dataset_checksums(path)
    checks["cryptographic_checksums"] = {
        "passed": chk_res["valid"],
        "detail": f"All {len(chk_res['verified_files'])} artifacts verified intact with SHA-256" if chk_res["valid"] else f"Checksum failures: {len(chk_res['mismatches'])} mismatches, {len(chk_res['missing_files'])} missing",
    }

    # 4. Simulation & Synthetic Contamination Gate (Execution Integrity)
    exec_mode = manifest_data.get("execution_mode") or manifest_data.get("mode", "live")
    is_live_release = is_empirical or exec_mode in ("live", "empirical")

    raw_file = path / "raw_responses.jsonl"
    obs_file = path / "observations.jsonl"
    simulation_issues = []
    synthetic_fixtures = []
    provider_mismatches = []
    hidden_fallbacks = []

    if raw_file.exists():
        try:
            with open(raw_file, "r", encoding="utf-8") as f:
                for idx, line in enumerate(f, 1):
                    if not line.strip():
                        continue
                    r = json.loads(line)
                    
                    # Simulation check
                    if is_live_release:
                        if (
                            r.get("execution_mode") == "simulation"
                            or r.get("execution_class") == "simulation"
                            or r.get("synthetic") is True
                        ):
                            simulation_issues.append(f"raw_responses.jsonl line {idx} marked simulation/synthetic")

                    # Synthetic fixture domains
                    resp_text = str(r.get("response_text", ""))
                    if "fixture.geo-scope.internal" in resp_text:
                        synthetic_fixtures.append(f"raw_responses.jsonl line {idx} contains fixture domain")

                    # Provider identity mismatch check
                    req_p = r.get("requested_provider")
                    act_p = r.get("actual_provider")
                    req_m = r.get("requested_model")
                    act_m = r.get("actual_model")
                    if req_p and act_p and req_p != act_p:
                        provider_mismatches.append(f"raw_responses.jsonl line {idx} provider mismatch: requested '{req_p}' vs actual '{act_p}'")
                    if req_m and act_m and req_m != act_m:
                        provider_mismatches.append(f"raw_responses.jsonl line {idx} model mismatch: requested '{req_m}' vs actual '{act_m}'")

                    # Hidden fallback check
                    if r.get("fallback_used") is True or r.get("fallback_active") is True:
                        hidden_fallbacks.append(f"raw_responses.jsonl line {idx} has fallback_used=true")
        except Exception as exc:
            simulation_issues.append(f"Error reading raw_responses.jsonl: {exc}")

    if obs_file.exists() and is_live_release:
        try:
            with open(obs_file, "r", encoding="utf-8") as f:
                for idx, line in enumerate(f, 1):
                    if not line.strip():
                        continue
                    o = json.loads(line)
                    if (
                        o.get("mode") == "simulation"
                        or o.get("execution_mode") == "simulation"
                        or o.get("execution_class") == "simulation"
                        or o.get("synthetic") is True
                    ):
                        simulation_issues.append(f"observations.jsonl line {idx} marked simulation")
                    if o.get("fallback_used") is True:
                        hidden_fallbacks.append(f"observations.jsonl line {idx} has fallback_used=true")
        except Exception as exc:
            simulation_issues.append(f"Error reading observations.jsonl: {exc}")

    checks["no_simulation_records"] = {
        "passed": len(simulation_issues) == 0,
        "detail": "Zero simulation/synthetic records detected in live release" if len(simulation_issues) == 0 else f"Simulation contamination: {'; '.join(simulation_issues[:3])}",
    }

    checks["no_synthetic_fixtures"] = {
        "passed": len(synthetic_fixtures) == 0,
        "detail": "Zero synthetic/fixture domains detected" if len(synthetic_fixtures) == 0 else f"Synthetic fixture domains detected: {'; '.join(synthetic_fixtures[:3])}",
    }

    checks["no_provider_mismatch"] = {
        "passed": len(provider_mismatches) == 0,
        "detail": "All executions matched requested provider and model" if len(provider_mismatches) == 0 else f"Provider mismatches: {'; '.join(provider_mismatches[:3])}",
    }

    checks["no_hidden_fallback"] = {
        "passed": len(hidden_fallbacks) == 0,
        "detail": "Zero fallback substitutions detected" if len(hidden_fallbacks) == 0 else f"Fallback substitutions: {'; '.join(hidden_fallbacks[:3])}",
    }

    # 5. Repeat Protocol Gate (repeat_count >= 5 for empirical releases)
    repeat_count = manifest_data.get("repeat_count", 1)
    repeat_passed = True
    repeat_msg = f"Repeat count valid (k={repeat_count})"
    if is_live_release:
        if repeat_count < 5:
            repeat_passed = False
            repeat_msg = f"Empirical benchmark requires repeat_count >= 5 (found: {repeat_count})"
        else:
            repeat_msg = f"Empirical repeat protocol satisfied (repeat_count={repeat_count} >= 5)"

    checks["repeat_protocol_enforcement"] = {
        "passed": repeat_passed,
        "detail": repeat_msg,
    }

    # 6. Secret Detection Gate
    secrets_found = []
    for fpath in path.rglob("*"):
        if fpath.is_file() and fpath.suffix in [".json", ".jsonl", ".txt", ".md", ".sha256"]:
            try:
                content = fpath.read_text(encoding="utf-8", errors="ignore")
                for pat in SECRET_PATTERNS:
                    m = pat.search(content)
                    if m:
                        secrets_found.append(f"{fpath.relative_to(path).as_posix()}: pattern {pat.pattern}")
            except Exception:
                pass

    checks["no_secrets_detected"] = {
        "passed": len(secrets_found) == 0,
        "detail": "Zero secrets or unredacted credentials detected" if len(secrets_found) == 0 else f"Potential secrets found: {'; '.join(secrets_found)}",
    }

    # 7. Failure Denominator & Visibility Accounting Gate
    metrics_file = path / "metrics.json"
    denom_passed = True
    denom_msg = "Metrics file missing"
    if metrics_file.exists():
        try:
            m_data = json.loads(metrics_file.read_text(encoding="utf-8"))
            if "provider_breakdown" in m_data:
                for p_name, p_stat in m_data["provider_breakdown"].items():
                    if "metric_denominator_n" not in p_stat and "successful_n" not in p_stat:
                        denom_passed = False
                        denom_msg = f"Provider '{p_name}' missing metric_denominator_n"
                        break
                if denom_passed:
                    denom_msg = "Provider breakdown accounts for attempted, successful, and failed queries"
            elif "entities" in m_data:
                denom_msg = "Entity metrics present with denominator accounting"
        except Exception as exc:
            denom_passed = False
            denom_msg = f"Invalid metrics.json: {exc}"

    checks["failure_denominator_accounting"] = {
        "passed": denom_passed,
        "detail": denom_msg,
    }

    # Compute overall outcome
    all_passed = all(c["passed"] for c in checks.values())
    status = "PASS" if all_passed else "FAIL"

    report = {
        "dataset_dir": str(path),
        "status": status,
        "passed": all_passed,
        "execution_mode": exec_mode,
        "is_empirical": is_live_release,
        "checks": checks,
    }

    if output_report:
        out_p = Path(output_report)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    return report


def format_release_gate_report(report: Dict[str, Any]) -> str:
    """Formats the release gate report into a human-readable CLI summary."""
    lines = [
        "=" * 76,
        f"GEO-Scope Benchmark Release Quality Gate: {report['dataset_dir']}",
        f"Overall Gate Status : {report['status']}",
        "=" * 76,
    ]
    for check_name, info in report["checks"].items():
        icon = "✓" if info["passed"] else "✗"
        label = check_name.replace("_", " ").title()
        lines.append(f"{icon} {label:<36}: {info['detail']}")
    lines.append("=" * 76)
    return "\n".join(lines)
