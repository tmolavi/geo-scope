# Cryptographic hashing & integrity verification for GEO-Scope benchmark datasets.
import hashlib
import os
from pathlib import Path
from typing import Dict, Any, List, Optional


def compute_bytes_sha256(data: bytes) -> str:
    """Compute SHA-256 hex digest for byte sequence."""
    return hashlib.sha256(data).hexdigest()


def compute_file_sha256(filepath: str | Path) -> str:
    """Compute SHA-256 hex digest for a file on disk."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_dataset_checksums(dataset_dir: str | Path) -> Dict[str, str]:
    """
    Compute SHA-256 for all relevant files in dataset_dir (excluding checksums.sha256).
    Returns mapping of relative_filename -> sha256_hex.
    """
    dataset_path = Path(dataset_dir)
    checksums = {}
    for item in sorted(dataset_path.iterdir()):
        if item.is_file() and item.name != "checksums.sha256" and not item.name.startswith("."):
            checksums[item.name] = compute_file_sha256(item)
    return checksums


def compute_composite_hash(file_hashes: Dict[str, str]) -> str:
    """
    Compute a single deterministic SHA-256 hash representing the composite state
    of all files in the dataset.
    """
    canonical_lines = [f"{fname}:{file_hashes[fname]}" for fname in sorted(file_hashes.keys())]
    payload = "\n".join(canonical_lines).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def write_checksums_file(dataset_dir: str | Path, checksums: Optional[Dict[str, str]] = None) -> Path:
    """
    Write standard checksums.sha256 file into dataset_dir.
    Format: <sha256_hex>  <filename>
    """
    dataset_path = Path(dataset_dir)
    if checksums is None:
        checksums = compute_dataset_checksums(dataset_path)

    out_file = dataset_path / "checksums.sha256"
    lines = [f"{h}  {fname}" for fname, h in sorted(checksums.items())]
    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_file


def verify_dataset_checksums(dataset_dir: str | Path) -> Dict[str, Any]:
    """
    Verify all files in dataset_dir against its checksums.sha256.
    Detects bit-level modifications, missing files, or unauthorized additions.
    """
    dataset_path = Path(dataset_dir)
    checksums_file = dataset_path / "checksums.sha256"

    if not checksums_file.exists():
        return {
            "valid": False,
            "error": "Missing checksums.sha256 file",
            "verified_files": [],
            "mismatches": [],
            "missing_files": [],
            "extra_files": [],
        }

    expected_hashes = {}
    for line in checksums_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            expected_hash, fname = parts[0], parts[1].strip()
            expected_hashes[fname] = expected_hash

    actual_files = {
        item.name: item
        for item in dataset_path.iterdir()
        if item.is_file() and item.name != "checksums.sha256" and not item.name.startswith(".")
    }

    verified_files = []
    mismatches = []
    missing_files = []

    for fname, exp_hash in expected_hashes.items():
        if fname not in actual_files:
            missing_files.append(fname)
        else:
            act_hash = compute_file_sha256(actual_files[fname])
            if act_hash == exp_hash:
                verified_files.append(fname)
            else:
                mismatches.append({"file": fname, "expected": exp_hash, "actual": act_hash})

    extra_files = [fname for fname in actual_files if fname not in expected_hashes]

    is_valid = len(mismatches) == 0 and len(missing_files) == 0 and len(extra_files) == 0

    return {
        "valid": is_valid,
        "verified_files": verified_files,
        "mismatches": mismatches,
        "missing_files": missing_files,
        "extra_files": extra_files,
        "total_files": len(expected_hashes),
    }
