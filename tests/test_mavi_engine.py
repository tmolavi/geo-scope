"""
Comprehensive Unit & Integration Tests for MAVI Measurement Engine v1.
Validates L1-L5 layers, SAGE evaluation, GEO-Scope L5 integration, partial scoring,
confidence calculation, provenance, configurable weights, and zero-fabrication guarantees.
"""

import os
import json
import pytest
import subprocess
import sys
from geo_scope.mavi import (
    MAVIEngine,
    MAVIReport,
    LayerWeights,
    SAGEEvaluator,
    GEOScopeEvaluator,
)
from geo_scope.mcp_server import handle_tool_call


SAMPLE_RICH_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>HubSpot CRM - Comprehensive Platform Overview</title>
    <meta name="description" content="HubSpot provides an enterprise-grade CRM software for inbound marketing and sales.">
    <link rel="canonical" href="https://www.hubspot.com/products/crm">
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "HubSpot CRM",
        "description": "Enterprise cloud CRM software",
        "sameAs": [
            "https://www.wikidata.org/wiki/Q5928236",
            "https://en.wikipedia.org/wiki/HubSpot",
            "https://www.linkedin.com/company/hubspot"
        ],
        "author": {
            "@type": "Organization",
            "name": "HubSpot, Inc."
        }
    }
    </script>
</head>
<body>
    <main>
        <h1>HubSpot CRM: The Complete 2026 Inbound Sales Platform</h1>
        <p>HubSpot CRM is a cloud-based sales and marketing acceleration platform that provides automated pipeline management for growth teams.</p>
        
        <h2>Key Platform Capabilities and Architecture</h2>
        <p>The platform enables real-time customer data synchronisation across marketing, sales, and customer service operations with minimal technical overhead.</p>
        <p>According to recent industry benchmarks, HubSpot reduces lead qualification time by 45% while increasing sales pipeline visibility by 68% across distributed teams.</p>
        
        <h2>Competitive Feature Comparison</h2>
        <table>
            <thead>
                <tr>
                    <th>Feature</th>
                    <th>HubSpot CRM</th>
                    <th>Competitor Legacy</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Setup Time</td>
                    <td>24 Hours</td>
                    <td>3 Months</td>
                </tr>
                <tr>
                    <td>API Webhook Limits</td>
                    <td>1,000,000 / day</td>
                    <td>50,000 / day</td>
                </tr>
                <tr>
                    <td>Starting Price</td>
                    <td>$50 / month</td>
                    <td>$150 / month</td>
                </tr>
            </tbody>
        </table>
        
        <h3>Enterprise Security & Integrations</h3>
        <p>HubSpot features SOC-2 Type II compliance and over 500 pre-built REST API connectors for modern enterprise stacks.</p>
    </main>
</body>
</html>
"""

SAMPLE_BLOCKED_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="robots" content="noindex, nofollow">
</head>
<body>
    <p>Private admin portal.</p>
</body>
</html>
"""

SAMPLE_EXPERIMENT_DATA = {
    "experiment_id": "EXP-MAVI-9999",
    "summary": {
        "execution_mode": "live",
        "total_ai_executions": 100,
        "successful_executions": 95,
        "failed_executions": 5,
        "overall_sov": 78.5,
        "overall_top1_rate": 45.0,
    },
    "share_of_model": {
        "by_model": {
            "perplexity_sonar": {"successful_queries": 25, "mention_rate_pct": 84.0, "top1_rate_pct": 52.0},
            "chatgpt_search": {"successful_queries": 25, "mention_rate_pct": 80.0, "top1_rate_pct": 48.0},
            "gemini_grounding": {"successful_queries": 25, "mention_rate_pct": 76.0, "top1_rate_pct": 40.0},
            "claude_3_7": {"successful_queries": 20, "mention_rate_pct": 74.0, "top1_rate_pct": 40.0},
        }
    },
    "citation_analytics": {"total_citations_analyzed": 140},
}


# =============================================================================
# 1. SAGE Evaluator Tests (L1, L2, L3, L4)
# =============================================================================

def test_sage_l1_technical_accessibility():
    sage = SAGEEvaluator(html_content=SAMPLE_RICH_HTML, url="https://www.hubspot.com/products/crm", http_status=200)
    l1 = sage.evaluate_l1_technical_accessibility(weight=0.15)

    assert l1.layer_id == "L1"
    assert l1.status == "measured"
    assert l1.provenance.source == "sage"
    assert l1.score is not None and l1.score >= 70.0
    assert l1.details["http_status"] == 200
    assert "text_to_html_ratio" in l1.details
    assert "word_count" in l1.details


def test_sage_l1_blocked_noindex():
    sage = SAGEEvaluator(html_content=SAMPLE_BLOCKED_HTML, url="http://internal.site/admin", http_status=403)
    l1 = sage.evaluate_l1_technical_accessibility(weight=0.15)

    assert l1.score is not None


def test_sage_l2_semantic_extractability():
    sage = SAGEEvaluator(html_content=SAMPLE_RICH_HTML, url="https://www.hubspot.com/products/crm")
    l2 = sage.evaluate_l2_semantic_extractability(weight=0.20)

    assert l2.layer_id == "L2"
    assert l2.status == "measured"
    assert l2.score is not None and l2.score >= 50.0
    assert "json_ld_blocks" in l2.details
    assert "entity_types" in l2.details


def test_sage_l3_entity_clarity():
    sage = SAGEEvaluator(html_content=SAMPLE_RICH_HTML, target_brand="HubSpot")
    l3 = sage.evaluate_l3_entity_clarity(weight=0.20)

    assert l3.layer_id == "L3"
    assert l3.status == "measured"
    assert l3.score is not None and l3.score >= 50.0
    assert "entity_types" in l3.details
    assert l3.details["target_brand"] == "HubSpot"


def test_sage_l4_citation_readiness():
    sage = SAGEEvaluator(html_content=SAMPLE_RICH_HTML)
    l4 = sage.evaluate_l4_citation_readiness(weight=0.20)

    assert l4.layer_id == "L4"
    assert l4.status == "measured"
    assert l4.score is not None and l4.score >= 50.0
    assert "chunk_count" in l4.details


# =============================================================================
# 2. GEOScope Evaluator Tests (L5 Observed AI Visibility)
# =============================================================================

def test_geoscope_l5_measured():
    l5 = GEOScopeEvaluator.evaluate_l5(experiment_data=SAMPLE_EXPERIMENT_DATA, target_brand="HubSpot", weight=0.25)

    assert l5.layer_id == "L5"
    assert l5.status == "measured"
    assert l5.score is not None
    assert l5.score > 60.0
    assert l5.provenance.source == "geo-scope"
    assert l5.provenance.evidence_count == 95
    assert l5.details["experiment_id"] == "EXP-MAVI-9999"


def test_geoscope_l5_missing_returns_not_measured_without_fabrication():
    l5 = GEOScopeEvaluator.evaluate_l5(experiment_data=None, target_brand="HubSpot", weight=0.25)

    assert l5.layer_id == "L5"
    assert l5.status == "not_measured"
    assert l5.score is None
    assert l5.provenance.evidence_count == 0


def test_geoscope_l5_zero_successful_observations():
    empty_exp = {
        "experiment_id": "EXP-FAILED",
        "summary": {"total_ai_executions": 5, "successful_executions": 0, "failed_executions": 5},
    }
    l5 = GEOScopeEvaluator.evaluate_l5(experiment_data=empty_exp, target_brand="HubSpot")

    assert l5.status == "insufficient_data"
    assert l5.score is None


# =============================================================================
# 3. MAVI Engine Core: Full 5-Layer Measurement
# =============================================================================

def test_mavi_engine_full_5_layers():
    engine = MAVIEngine()
    report = engine.measure(
        html_content=SAMPLE_RICH_HTML,
        url="https://www.hubspot.com/products/crm",
        target_brand="HubSpot",
        experiment_data=SAMPLE_EXPERIMENT_DATA,
    )

    assert isinstance(report, MAVIReport)
    assert report.measured_layers_count == 5
    assert report.total_layers_count == 5
    assert report.measurement_mode == "measured"
    assert report.mavi_score is not None
    assert 60.0 <= report.mavi_score <= 100.0
    assert report.confidence.confidence_level in ("High", "Medium")
    assert report.confidence.confidence_score >= 0.70

    # Verify all layers have provenance
    for lid in ["L1", "L2", "L3", "L4", "L5"]:
        layer = report.layers[lid]
        assert layer.status == "measured"
        assert layer.score is not None
        assert layer.provenance.source in ("sage", "geo-scope")
        assert layer.provenance.metric_version in ("1.0.0", "2.0.0")


# =============================================================================
# 4. Partial Scoring & Normalization (Missing L5)
# =============================================================================

def test_mavi_engine_partial_scoring_without_l5():
    engine = MAVIEngine()
    report = engine.measure(
        html_content=SAMPLE_RICH_HTML,
        url="https://www.hubspot.com/products/crm",
        target_brand="HubSpot",
        experiment_data=None,  # No L5
    )

    assert report.measured_layers_count == 4
    assert report.total_layers_count == 5
    assert report.measurement_mode == "partial_measured"
    assert report.layers["L5"].status == "not_measured"
    assert report.layers["L5"].score is None

    # Verify normalization basis
    assert "Normalized across 4/5 measured layers" in report.normalization_basis
    assert "active weight sum = 0.75" in report.normalization_basis
    assert report.mavi_score is not None
    assert 60.0 <= report.mavi_score <= 100.0


def test_mavi_engine_empty_input_returns_not_measured():
    engine = MAVIEngine()
    report = engine.measure(html_content=None, experiment_data=None)

    assert report.measured_layers_count == 0
    assert report.measurement_mode == "not_measured"
    assert report.mavi_score is None
    assert report.grade == "N/A"
    assert report.confidence.confidence_level == "Insufficient"


# =============================================================================
# 5. Configurable Weights & Provenance
# =============================================================================

def test_mavi_engine_configurable_weights():
    custom_weights = {
        "L1": 0.10,
        "L2": 0.10,
        "L3": 0.20,
        "L4": 0.20,
        "L5": 0.40,
    }
    engine = MAVIEngine(weights=custom_weights)
    assert engine.weights_provenance == "custom_configured"
    assert engine.weights.l5_observed_ai_visibility == 0.40

    report = engine.measure(
        html_content=SAMPLE_RICH_HTML,
        target_brand="HubSpot",
        experiment_data=SAMPLE_EXPERIMENT_DATA,
    )
    assert report.weights_provenance == "custom_configured"
    assert report.weights["L5"] == 0.40


# =============================================================================
# 6. Manual Override Mode
# =============================================================================

def test_mavi_engine_manual_override():
    engine = MAVIEngine()
    manual_input = {"L1": 85.0, "L2": 72.0, "L3": 90.0, "L4": 65.0, "L5": 80.0}
    report = engine.measure(manual_layers=manual_input)

    assert report.measurement_mode == "manual_override"
    assert report.mavi_score is not None
    for lid in ["L1", "L2", "L3", "L4", "L5"]:
        layer = report.layers[lid]
        assert layer.status == "manual_override"
        assert layer.provenance.source == "manual"
        assert "Manual override" in layer.findings[0] or "manually" in layer.findings[0]


# =============================================================================
# 7. CLI & MCP Tool Integration Tests
# =============================================================================

def test_cli_mavi_command(tmp_path):
    html_file = str(tmp_path / "page.html")
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(SAMPLE_RICH_HTML)

    res = subprocess.run(
        [sys.executable, "-m", "geo_scope.cli", "mavi", "--html", html_file, "--brand", "HubSpot"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0
    assert "MOLAVI AI VISIBILITY INDEX (MAVI) REPORT" in res.stdout
    assert "L1 Technical Accessibility" in res.stdout
    assert "L2 Semantic Extractability" in res.stdout
    assert "L3 Entity Clarity" in res.stdout
    assert "L4" in res.stdout and "Citation Readiness" in res.stdout


def test_cli_mavi_json_format(tmp_path):
    html_file = str(tmp_path / "page.html")
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(SAMPLE_RICH_HTML)

    res = subprocess.run(
        [sys.executable, "-m", "geo_scope.cli", "mavi", "--html", html_file, "--brand", "HubSpot", "--format", "json"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0
    data = json.loads(res.stdout)
    assert "mavi_score" in data
    assert "layers" in data
    assert "L1" in data["layers"]
    assert "confidence" in data


@pytest.mark.asyncio
async def test_mcp_measure_mavi_tool():
    args = {
        "html_content": SAMPLE_RICH_HTML,
        "url": "https://www.hubspot.com/products/crm",
        "brand": "HubSpot",
        "experiment_data": SAMPLE_EXPERIMENT_DATA,
    }
    result = await handle_tool_call("measure_mavi", args)

    assert "mavi_score" in result
    assert result["measured_layers_count"] == 5
    assert result["grade"] in ("A+", "A", "B", "C", "D")
    assert result["layers"]["L5"]["status"] == "measured"
