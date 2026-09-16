"""
Raw Response Persistence & Experiment Run Store.
Provides durable, appendable JSONL storage for auditability, reproducibility, and experiment manifests.
"""

import os
import json
import hashlib
import subprocess
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from geo_scope.providers.models import sanitize_sensitive_data


def get_git_commit() -> str:
    """Returns the current git HEAD commit SHA, or 'unknown' if not in a git tree."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2.0,
            check=False,
        )
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return "unknown"


def compute_dataset_hash(prompts: List[Dict[str, Any]]) -> str:
    """Computes a deterministic SHA-256 hash of prompt contents."""
    simplified = [
        {
            "id": p.get("id"),
            "query": p.get("query"),
            "target_brand": p.get("target_brand"),
            "expected_entities": sorted(p.get("expected_entities", [])),
        }
        for p in sorted(prompts, key=lambda x: str(x.get("id", "")))
    ]
    raw = json.dumps(simplified, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class RawRunStore:
    """
    Durable experiment run store.
    Persists:
      - manifest.json
      - prompts.jsonl
      - raw/<provider>.jsonl
    """

    def __init__(self, base_dir: str = "runs", experiment_id: Optional[str] = None):
        self.experiment_id = experiment_id or f"EXP-{int(datetime.now(timezone.utc).timestamp())}"
        self.run_dir = os.path.join(base_dir, self.experiment_id)
        self.raw_dir = os.path.join(self.run_dir, "raw")
        os.makedirs(self.raw_dir, exist_ok=True)
        self.prompts_path = os.path.join(self.run_dir, "prompts.jsonl")
        self.manifest_path = os.path.join(self.run_dir, "manifest.json")

    def append_raw_record(self, record: Dict[str, Any]):
        """
        Appends a sanitized raw invocation record to raw/<provider>.jsonl.
        """
        sanitized = sanitize_sensitive_data(record)
        provider = sanitized.get("provider", "unknown").replace("/", "_").replace(":", "_")
        provider_file = os.path.join(self.raw_dir, f"{provider}.jsonl")
        line = json.dumps(sanitized, ensure_ascii=False) + "\n"
        with open(provider_file, "a", encoding="utf-8") as f:
            f.write(line)

    def save_prompts(self, prompts: List[Dict[str, Any]]):
        """
        Persists the list of prompt objects to prompts.jsonl.
        """
        with open(self.prompts_path, "w", encoding="utf-8") as f:
            for p in prompts:
                f.write(json.dumps(p, ensure_ascii=False) + "\n")

    def create_manifest(
        self,
        execution_mode: str,
        providers: Dict[str, Any],
        models: Dict[str, str],
        prompts: List[Dict[str, Any]],
        started_at: str,
        finished_at: str,
        configuration: Optional[Dict[str, Any]] = None,
        parser_version: str = "1.0.0",
    ) -> Dict[str, Any]:
        """
        Creates and saves the reproducible experiment manifest.
        Guarantees that no API keys or secrets are written.
        """
        manifest = {
            "experiment_id": self.experiment_id,
            "geo_scope_version": "1.0.0",
            "git_commit": get_git_commit(),
            "execution_mode": execution_mode,
            "started_at": started_at,
            "finished_at": finished_at,
            "providers": sanitize_sensitive_data(providers),
            "models": sanitize_sensitive_data(models),
            "prompt_dataset_hash": compute_dataset_hash(prompts),
            "total_prompts": len(prompts),
            "parser_version": parser_version,
            "configuration": sanitize_sensitive_data(configuration or {}),
        }
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        return manifest
