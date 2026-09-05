"""
Tests for CLI Command Execution
"""

import subprocess
import sys
import os


def test_cli_help():
    res = subprocess.run([sys.executable, "-m", "geo_scope.cli", "--help"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "geo-scope" in res.stdout
    assert "demo" in res.stdout
    assert "run" in res.stdout


def test_cli_demo_execution():
    res = subprocess.run([sys.executable, "-m", "geo_scope.cli", "demo"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "DEMO EXPERIMENTAL BENCHMARK SUMMARY" in res.stdout
    assert "Share of Model" in res.stdout


def test_cli_custom_prompts_run(tmp_path):
    dataset_path = str(tmp_path / "prompts.txt")
    with open(dataset_path, "w", encoding="utf-8") as f:
        f.write("What CRM is suitable for a small team?\n")
    out_dir = str(tmp_path / "results")
    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "geo_scope.cli",
            "run",
            "--brand",
            "HubSpot",
            "--prompts",
            dataset_path,
            "--out",
            out_dir,
        ],
        capture_output=True,
        text=True,
    )

    assert res.returncode == 0
    assert "EXECUTIVE BENCHMARK RESULTS" in res.stdout
    assert os.path.exists(os.path.join(out_dir, "summary.md"))
    assert os.path.exists(os.path.join(out_dir, "report.html"))
