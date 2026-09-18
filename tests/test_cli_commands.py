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
    assert "measure" in res.stdout
    assert "replay" in res.stdout


def test_cli_demo_execution():
    res = subprocess.run([sys.executable, "-m", "geo_scope.cli", "demo"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "GEO-Scope Quickstart Demo (SIMULATION FIXTURE)" in res.stdout
    assert "Simulated Mention Rate" in res.stdout
    assert "DEMO SIMULATION METRICS SUMMARY" in res.stdout


def test_cli_measure_simulation_and_replay(tmp_path):
    measure_out = str(tmp_path / "measure_sim")
    replay_out = str(tmp_path / "replay_sim")

    # 1. Test measure in simulation mode
    res_m = subprocess.run(
        [
            sys.executable,
            "-m",
            "geo_scope.cli",
            "measure",
            "--entities",
            "entities/iran-seo-agencies.json",
            "--prompts",
            "examples/prompts/observed-sample.jsonl",
            "--mode",
            "simulation",
            "--out-dir",
            measure_out,
        ],
        capture_output=True,
        text=True,
    )
    assert res_m.returncode == 0
    assert "MEASUREMENT METRICS SUMMARY" in res_m.stdout
    assert os.path.exists(os.path.join(measure_out, "manifest.json"))
    assert os.path.exists(os.path.join(measure_out, "checksums.sha256"))

    # 2. Test replay command
    res_r = subprocess.run(
        [
            sys.executable,
            "-m",
            "geo_scope.cli",
            "replay",
            "--input",
            measure_out,
            "--entities",
            "entities/iran-seo-agencies.json",
            "--out-dir",
            replay_out,
        ],
        capture_output=True,
        text=True,
    )
    assert res_r.returncode == 0
    assert "REPLAY METRICS SUMMARY" in res_r.stdout
    assert os.path.exists(os.path.join(replay_out, "checksums.sha256"))


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
