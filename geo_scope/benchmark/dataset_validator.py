# Quality and Security Validator for GEO-Scope Benchmark Dataset Releases
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from geo_scope.benchmark.hasher import verify_dataset_checksums


SECRET_PATTERNS = [
    re.compile(r"sk-[a-zA-Z0-9_-]{20,}", re.IGNORECASE),
    re.compile(r"ghp_[a-zA-Z0-9]{30,}", re.IGNORECASE),
    re.compile(r"Bearer\s+(?!\[REDACTED\])[a-zA-Z0-9_\-\.]{25,}", re.IGNORECASE),
    re.compile(r"HAMZAD_API_KEY\s*=\s*['\"][a-zA-Z0-9_\-]{10,}['\"]", re.IGNORECASE),
]


def validate_benchmark_dataset(dataset_dir: str | Path) -> Dict[str, Any]:
    path = Path(dataset_dir)
    if not path.is_dir():
        return {
            "status": "FAIL",
            "passed": False,
            "error": f"Directory not found: {path}",
            "checks": {},
        }

    checks: Dict[str, Dict[str, Any]] = {}

    # Check 1: Required files exist
    required_files = [
        "manifest.json",
        "prompts.jsonl",
        "raw_responses.jsonl",
        "observations.jsonl",
        "metrics.json",
        "checksums.sha256",
    ]
    missing_req = [f for f in required_files if not (path / f).exists()]
    has_entities = (path / "entities.json").exists() or (path / "brands.json").exists()
    if not has_entities:
        missing_req.append("entities.json / brands.json")

    checks["required_files"] = {
        "passed": len(missing_req) == 0,
        "detail": "All required files present" if len(missing_req) == 0 else f"Missing files: {', '.join(missing_req)}",
    }

    # Check 2: Checksum Verification
    chk_res = verify_dataset_checksums(path)
    checks["checksum_matches"] = {
        "passed": chk_res["valid"],
        "detail": f"{len(chk_res['verified_files'])} files verified intact" if chk_res["valid"] else f"Mismatches: {len(chk_res['mismatches'])}, Missing: {len(chk_res['missing_files'])}, Extra: {len(chk_res['extra_files'])}",
    }

    # Check 3: Prompts Validity
    prompts_file = path / "prompts.jsonl"
    prompts_valid = True
    prompt_count = 0
    prompt_err = None
    if prompts_file.exists():
        try:
            with open(prompts_file, "r", encoding="utf-8") as f:
                for idx, line in enumerate(f, 1):
                    if line.strip():
                        p = json.loads(line)
                        if not any(p.get(k) for k in ["prompt", "query", "question", "text", "prompt_text"]):
                            prompts_valid = False
                            prompt_err = f"Line {idx} missing prompt text"
                            break
                        prompt_count += 1
        except Exception as exc:
            prompts_valid = False
            prompt_err = str(exc)
    else:
        prompts_valid = False
        prompt_err = "prompts.jsonl missing"

    checks["prompts_valid"] = {
        "passed": prompts_valid and prompt_count > 0,
        "detail": f"{prompt_count} valid prompts loaded" if prompts_valid and prompt_count > 0 else f"Failed: {prompt_err}",
    }

    # Check 4: Raw Responses
    raw_file = path / "raw_responses.jsonl"
    raw_valid = True
    raw_count = 0
    raw_err = None
    if raw_file.exists():
        try:
            with open(raw_file, "r", encoding="utf-8") as f:
                for idx, line in enumerate(f, 1):
                    if line.strip():
                        r = json.loads(line)
                        if not r.get("provider") and not r.get("engine"):
                            raw_valid = False
                            raw_err = f"Line {idx} missing provider"
                            break
                        raw_count += 1
        except Exception as exc:
            raw_valid = False
            raw_err = str(exc)
    else:
        raw_valid = False
        raw_err = "raw_responses.jsonl missing"

    checks["raw_responses_exist"] = {
        "passed": raw_valid and raw_count > 0,
        "detail": f"{raw_count} raw responses stored" if raw_valid and raw_count > 0 else f"Failed: {raw_err}",
    }

    # Check 5: Observations & Provider Metadata
    obs_file = path / "observations.jsonl"
    obs_valid = True
    obs_count = 0
    obs_err = None
    if obs_file.exists():
        try:
            with open(obs_file, "r", encoding="utf-8") as f:
                for idx, line in enumerate(f, 1):
                    if line.strip():
                        o = json.loads(line)
                        if not o.get("provider") and not o.get("engine"):
                            obs_valid = False
                            obs_err = f"Line {idx} missing provider metadata"
                            break
                        obs_count += 1
        except Exception as exc:
            obs_valid = False
            obs_err = str(exc)
    else:
        obs_valid = False
        obs_err = "observations.jsonl missing"

    checks["observations_metadata"] = {
        "passed": obs_valid and obs_count > 0,
        "detail": f"{obs_count} observations verified with provider metadata" if obs_valid and obs_count > 0 else f"Failed: {obs_err}",
    }

    # Check 6: Secret Detection
    secrets_found = []
    for fpath in path.rglob("*"):
        if fpath.is_file() and fpath.suffix in [".json", ".jsonl", ".txt", ".md", ".sha256"]:
            try:
                content = fpath.read_text(encoding="utf-8", errors="ignore")
                for pat in SECRET_PATTERNS:
                    m = pat.search(content)
                    if m:
                        secrets_found.append(f"{fpath.relative_to(path).as_posix()}: matched pattern {pat.pattern}")
            except Exception:
                pass

    checks["no_secrets_detected"] = {
        "passed": len(secrets_found) == 0,
        "detail": "Zero secrets or unredacted credentials detected" if len(secrets_found) == 0 else f"Potential secrets: {'; '.join(secrets_found)}",
    }

    # Check 7: Scientific Measurement Integrity (Live vs Simulation Isolation)
    manifest_file = path / "manifest.json"
    is_live_or_empirical = False
    m_data = {}
    if manifest_file.exists():
        try:
            m_data = json.loads(manifest_file.read_text(encoding="utf-8"))
            m_mode = m_data.get("mode") or m_data.get("execution_mode", "")
            is_live_or_empirical = m_mode in ("live", "empirical") or m_data.get("is_empirical") is True or "live" in str(m_data.get("execution_class", ""))
        except Exception:
            pass

    simulation_contamination = []
    if is_live_or_empirical and obs_file.exists():
        try:
            with open(obs_file, "r", encoding="utf-8") as f:
                for idx, line in enumerate(f, 1):
                    if line.strip():
                        o = json.loads(line)
                        if (
                            o.get("mode") == "simulation"
                            or o.get("execution_mode") == "simulation"
                            or o.get("execution_class") == "simulation"
                            or o.get("synthetic") is True
                        ):
                            simulation_contamination.append(f"Observation line {idx} marked simulation/synthetic in live release")
                            if len(simulation_contamination) >= 5:
                                break
        except Exception as exc:
            simulation_contamination.append(str(exc))

    checks["live_measurement_integrity"] = {
        "passed": len(simulation_contamination) == 0,
        "detail": "Zero simulation/synthetic contamination in empirical release" if len(simulation_contamination) == 0 else f"Contamination detected: {'; '.join(simulation_contamination)}",
    }

    # Check 8: Benchmark Repeat Protocol (Enforced for Empirical Protocols)
    repeat_valid = True
    repeat_detail = "Repeat count not required for this dataset tier"
    if is_live_or_empirical and "repeat_count" in m_data:
        rep_count = m_data.get("repeat_count", 1)
        if rep_count < 5:
            repeat_valid = False
            repeat_detail = f"Empirical release requires repeat_count >= 5 (found: {rep_count})"
        else:
            repeat_detail = f"Repeat protocol satisfied (repeat_count={rep_count} >= 5 with measurement window)"

    checks["repeat_protocol_integrity"] = {
        "passed": repeat_valid,
        "detail": repeat_detail,
    }

    all_passed = all(c["passed"] for c in checks.values())
    status = "PASS" if all_passed else "FAIL"

    return {
        "dataset_dir": str(path),
        "status": status,
        "passed": all_passed,
        "checks": checks,
    }


def format_validation_report(result: Dict[str, Any]) -> str:
    lines = [
        "=" * 70,
        f"GEO-Scope Dataset Quality Validation: {result['dataset_dir']}",
        f"Overall Status: {result['status']}",
        "=" * 70,
    ]
    for check_name, info in result["checks"].items():
        icon = "✓" if info["passed"] else "✗"
        label = check_name.replace("_", " ").title()
        lines.append(f"{icon} {label:<32}: {info['detail']}")
    lines.append("=" * 70)
    return "\n".join(lines)
