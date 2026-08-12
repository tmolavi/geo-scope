"""
Tests for FastAPI Server Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from geo_scope.server import app

client = TestClient(app)


def test_get_index():
    response = client.get("/")
    assert response.status_code == 200


def test_get_presets():
    response = client.get("/api/presets")
    assert response.status_code == 200
    data = response.json()
    assert "presets" in data
    assert "crm_sales" in data["presets"]
    assert "available_models" in data


def test_benchmark_status_and_results():
    status_res = client.get("/api/benchmark_status")
    assert status_res.status_code == 200
    
    results_res = client.get("/api/benchmark_results")
    assert results_res.status_code == 200
    data = results_res.json()
    assert "analysis" in data
    assert "playbook" in data


def test_prompts_endpoint():
    response = client.get("/api/prompts?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) <= 5
