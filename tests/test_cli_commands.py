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


def test_cli_custom_prompts_run():
    dataset_path = os.path.join(os.path.dirname(__file__), "..", "datasets", "saas_crm.csv")
    out_dir = "/tmp/geo_test_cli_out"
    res = subprocess.run([
        sys.executable, "-m", "geo_scope.cli", "run",
        "--brand", "HubSpot",
        "--prompts", dataset_path,
        "--out", out_dir
    ], capture_output=True, text=True)

    assert res.returncode == 0
    assert "EXECUTIVE BENCHMARK RESULTS" in res.stdout
    assert os.path.exists(os.path.join(out_dir, "summary.md"))
    assert os.path.exists(os.path.join(out_dir, "report.html"))
