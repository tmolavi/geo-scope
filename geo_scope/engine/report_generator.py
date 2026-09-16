"""
Shareable Experiment Report Generator
Builds portable Markdown, HTML, JSON, and CSV research artifacts.
"""

import os
import json
import time
from html import escape
from typing import Dict, Any, List
from geo_scope.engine.export_manager import export_records_to_csv, export_citations_to_csv


def generate_experiment_artifacts(
    analysis_results: Dict[str, Any],
    parsed_records: List[Dict[str, Any]],
    prompts: List[Dict[str, Any]],
    out_dir: str = "results",
    experiment_id: str = None,
) -> Dict[str, str]:
    """
    Generates all portable experiment artifacts inside out_dir.
    """
    os.makedirs(out_dir, exist_ok=True)
    exp_id = experiment_id or f"EXP-{int(time.time())}"
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

    summary = analysis_results.get("summary", {})
    sov_data = analysis_results.get("share_of_model", {})
    citations_data = analysis_results.get("citation_analytics", {})
    factors_data = analysis_results.get("algorithmic_factors", {})
    competitors = analysis_results.get("competitor_matrix", [])

    # Archive all inputs and outputs so parsing can be independently replayed.
    raw_records = [
        {
            "query_item": next((q for q in prompts if q.get("id") == r["query_id"]), {}),
            "model": r["model"],
            "response_text": r.get("full_response_text", ""),
            "provenance": r.get("provenance", {}),
        }
        for r in parsed_records
    ]
    for filename, data in (
        ("raw_responses.json", raw_records),
        ("parsed_records.json", parsed_records),
        ("prompts.json", prompts),
    ):
        with open(os.path.join(out_dir, filename), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # 1. Generate summary.md
    md_content = _build_markdown_summary(
        exp_id, timestamp, summary, sov_data, citations_data, factors_data, competitors
    )
    md_path = os.path.join(out_dir, "summary.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    # 2. Generate report.html (Standalone Portable)
    def html_safe(value):
        if isinstance(value, str):
            return escape(value, quote=True)
        if isinstance(value, dict):
            return {escape(str(k), quote=True): html_safe(v) for k, v in value.items()}
        if isinstance(value, list):
            return [html_safe(v) for v in value]
        return value

    html_content = _build_portable_html_report(
        exp_id, timestamp, *[html_safe(v) for v in (summary, sov_data, citations_data, factors_data, competitors)]
    )
    html_path = os.path.join(out_dir, "report.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # 3. Generate experiment.json (Full Reproducibility Metadata)
    exp_meta = {
        "experiment_id": exp_id,
        "timestamp_utc": timestamp,
        "framework": "GEO-Scope v1.0.0",
        "author_credit": "Taqi Molavi (https://molavi.pro/)",
        "repository": "https://github.com/tmolavi/geo-scope",
        "playbook": analysis_results.get("playbook", {}),
        "summary": summary,
        "share_of_model": sov_data,
        "citation_analytics": citations_data,
        "algorithmic_factors": factors_data,
        "competitor_matrix": competitors,
        "prompts": prompts,
        "records": parsed_records,
    }
    json_path = os.path.join(out_dir, "experiment.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(exp_meta, f, ensure_ascii=False, indent=2)

    # 4. Generate CSVs
    queries_csv = export_records_to_csv(parsed_records)
    queries_csv_path = os.path.join(out_dir, "queries.csv")
    with open(queries_csv_path, "w", encoding="utf-8") as f:
        f.write(queries_csv)

    citations_csv = export_citations_to_csv(parsed_records)
    citations_csv_path = os.path.join(out_dir, "citations.csv")
    with open(citations_csv_path, "w", encoding="utf-8") as f:
        f.write(citations_csv)

    return {
        "raw_responses_json": os.path.join(out_dir, "raw_responses.json"),
        "experiment_id": exp_id,
        "summary_md": md_path,
        "report_html": html_path,
        "experiment_json": json_path,
        "queries_csv": queries_csv_path,
        "citations_csv": citations_csv_path,
    }


def _build_markdown_summary(exp_id, timestamp, summary, sov, citations, factors, competitors):
    brand = summary.get("target_brand", "Target Brand")
    total_q = summary.get("total_queries_tested", 0)
    total_inf = summary.get("total_ai_executions", 0)
    overall_sov = summary.get("overall_sov")
    overall_sov_str = f"{overall_sov}%" if overall_sov is not None else "N/A"
    top1_rate = summary.get("overall_top1_rate")
    top1_rate_str = f"{top1_rate}%" if top1_rate is not None else "N/A"
    best_m = summary.get("best_performing_model", "N/A")

    lines = [
        f"# ⟠ GEO-Scope Experiment Report: `{exp_id}`",
        f"*Generated on {timestamp} using [GEO-Scope](https://github.com/tmolavi/geo-scope) by [Taqi Molavi](https://molavi.pro/)*\n",
        "## 📊 Executive Summary\n",
        f"- **Target Brand**: `{brand}`",
        f"- **Total Prompts Evaluated**: `{total_q}` ({total_inf} multi-model inferences)",
        f"- **Execution Mode**: `{summary.get('execution_mode', 'unknown')}`",
        f"- **Overall Mention Rate (Share of Model)**: **`{overall_sov_str}`**",
        f"- **Top-1 Recommendation Pick Rate**: **`{top1_rate_str}`**",
        f"- **Top Performing AI Engine**: `{best_m}`\n",
        "## 🤖 Model-by-Model Visibility Breakdown\n",
        "| AI Engine | Mention Rate (SoM %) | Top #1 Pick Rate (%) | Average List Rank |",
        "| :--- | :---: | :---: | :---: |",
    ]

    for provider_id, provenance in summary.get("provider_provenance", {}).items():
        lines.insert(
            10,
            f"- **Provider {provider_id}**: {provenance.get('response_kind', 'unknown')}; model {provenance.get('model_id', 'unknown')}",
        )
    by_model = sov.get("by_model", {})
    for m, st in by_model.items():
        m_rate = f"{st.get('mention_rate_pct')}%" if st.get('mention_rate_pct') is not None else "N/A"
        t_rate = f"{st.get('top1_rate_pct')}%" if st.get('top1_rate_pct') is not None else "N/A"
        lines.append(
            f"| **{m}** | {m_rate} | {t_rate} | {st.get('avg_rank') if st.get('avg_rank') is not None else 'N/A'} |"
        )

    lines.append("\n## 🏆 Competitor Share of Voice Matrix\n")
    lines.append(
        "| Brand Entity | Mention Rate (%) | Share of brand-response mentions (%) | Top-1 Recommendation Rate (%) | Status |"
    )
    lines.append("| :--- | :---: | :---: | :---: | :---: |")
    for c in competitors:
        is_t = "🎯 Target Brand" if c.get("is_target") else "Competitor"
        m_rate = f"{c.get('mention_rate_pct')}%" if c.get('mention_rate_pct') is not None else "N/A"
        sov_rate = f"{c.get('share_of_voice_pct')}%" if c.get('share_of_voice_pct') is not None else "N/A"
        t_rate = f"{c.get('top1_rate_pct')}%" if c.get('top1_rate_pct') is not None else "N/A"
        lines.append(
            f"| **{c.get('brand')}** | {m_rate} | {sov_rate} | {t_rate} | {is_t} |"
        )

    lines.append("\n## 🔗 Referenced Sources (see citation provenance)\n")
    lines.append("| Rank | Domain | Category | Citation Count |")
    lines.append("| :---: | :--- | :--- | :---: |")
    top_doms = citations.get("top_cited_domains", [])[:8]
    for idx, d in enumerate(top_doms, 1):
        lines.append(f"| #{idx} | `{d.get('domain')}` | Referenced URL | {d.get('count')} citations |")

    lines.append(
        "\nRanking-factor weights are labeled hypothesis priors, not fitted findings. Unknown ranks are excluded from average rank. Top-1 rate uses all responses as denominator. Referenced URLs alone do not prove web search.\n"
    )
    lines.append("\n---\n")
    lines.append(
        '> **Experimental Reproducibility Notice**: Results reflect the specific prompt matrix and experimental parameters evaluated. Reanalyze recorded responses using `geo-scope run --responses raw_responses.json --brand "'
        + brand
        + '" --prompts <file>`.'
    )

    return "\n".join(lines)


def _build_portable_html_report(exp_id, timestamp, summary, sov, citations, factors, competitors):
    brand = summary.get("target_brand", "Target Brand")
    overall_sov = summary.get("overall_sov")
    overall_sov_str = f"{overall_sov}%" if overall_sov is not None else "N/A"
    top1_rate = summary.get("overall_top1_rate")
    top1_rate_str = f"{top1_rate}%" if top1_rate is not None else "N/A"
    total_q = summary.get("total_queries_tested", 0)

    model_rows = ""
    for m, st in sov.get("by_model", {}).items():
        m_rate = f"{st.get('mention_rate_pct')}%" if st.get('mention_rate_pct') is not None else "N/A"
        t_rate = f"{st.get('top1_rate_pct')}%" if st.get('top1_rate_pct') is not None else "N/A"
        model_rows += f"""
        <tr>
            <td style="padding: 10px 14px; font-weight: bold; border-bottom: 1px solid #1e293b;">{m}</td>
            <td style="padding: 10px 14px; text-align: center; color: #818cf8; font-weight: bold; border-bottom: 1px solid #1e293b;">{m_rate}</td>
            <td style="padding: 10px 14px; text-align: center; color: #fbbf24; font-weight: bold; border-bottom: 1px solid #1e293b;">{t_rate}</td>
            <td style="padding: 10px 14px; text-align: center; color: #94a3b8; border-bottom: 1px solid #1e293b;">{st.get('avg_rank') if st.get('avg_rank') is not None else 'N/A'}</td>
        </tr>
        """

    comp_rows = ""
    for c in competitors:
        is_target_badge = (
            '<span style="background: rgba(99, 102, 241, 0.2); color: #a5b4fc; padding: 2px 8px; border-radius: 4px; font-size: 11px;">Target Brand</span>'
            if c.get("is_target")
            else '<span style="color: #64748b; font-size: 11px;">Competitor</span>'
        )
        m_rate = f"{c.get('mention_rate_pct')}%" if c.get('mention_rate_pct') is not None else "N/A"
        t_rate = f"{c.get('top1_rate_pct')}%" if c.get('top1_rate_pct') is not None else "N/A"
        comp_rows += f"""
        <tr>
            <td style="padding: 10px 14px; font-weight: bold; border-bottom: 1px solid #1e293b;">{c.get('brand')}</td>
            <td style="padding: 10px 14px; text-align: center; color: #818cf8; font-weight: bold; border-bottom: 1px solid #1e293b;">{m_rate}</td>
            <td style="padding: 10px 14px; text-align: center; color: #fbbf24; font-weight: bold; border-bottom: 1px solid #1e293b;">{t_rate}</td>
            <td style="padding: 10px 14px; text-align: center; border-bottom: 1px solid #1e293b;">{is_target_badge}</td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GEO-Scope Report: {exp_id}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #0b0f19;
            color: #f1f5f9;
            margin: 0;
            padding: 30px 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: #111827;
            border: 1px solid #1f2937;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }}
        .badge {{
            display: inline-block;
            background: rgba(99, 102, 241, 0.2);
            color: #a5b4fc;
            border: 1px solid rgba(99, 102, 241, 0.4);
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-family: monospace;
            font-weight: bold;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 25px 0;
        }}
        .kpi-card {{
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 18px;
        }}
        .kpi-title {{ font-size: 12px; color: #94a3b8; font-weight: 600; text-transform: uppercase; }}
        .kpi-val {{ font-size: 28px; font-weight: 800; color: #ffffff; margin-top: 5px; font-family: monospace; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 13px; }}
        th {{ background: #1e293b; color: #94a3b8; padding: 10px 14px; text-align: left; border-bottom: 2px solid #334155; font-size: 11px; text-transform: uppercase; }}
        a {{ color: #818cf8; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1f2937; padding-bottom: 20px;">
            <div>
                <span class="badge">⟠ GEO-SCOPE EXPERIMENT</span>
                <span class="badge" style="background: rgba(148, 163, 184, 0.2); color: #cbd5e1; border-color: rgba(148, 163, 184, 0.4);">MODE: {summary.get("execution_mode", "unknown")}</span>
                <h1 style="margin: 8px 0 0 0; font-size: 22px; color: #ffffff;">AI Visibility Audit: {brand}</h1>
                <p style="margin: 4px 0 0 0; font-size: 12px; color: #64748b;">ID: {exp_id} • {timestamp}</p>
            </div>
            <div>
                <a href="https://github.com/tmolavi/geo-scope" target="_blank" style="background: #4f46e5; color: white; padding: 8px 14px; border-radius: 8px; font-size: 12px; font-weight: bold;">View on GitHub ↗</a>
            </div>
        </div>

        <p>Scope: {summary.get('measurement_scope', 'Recorded response analysis')}. Factor weights are research priors. N/A means no explicit rank.</p>
        <p>Provider capabilities: {', '.join(str(k) + ': ' + str(v.get('response_kind', 'unknown')) for k, v in summary.get('provider_provenance', {}).items())}</p>
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Mention Rate (Share of Model)</div>
                <div class="kpi-val" style="color: #818cf8;">{overall_sov}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Top-1 Pick Rate</div>
                <div class="kpi-val" style="color: #fbbf24;">{top1_rate}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Total Prompts</div>
                <div class="kpi-val">{total_q}</div>
            </div>
        </div>

        <h3 style="color: #e2e8f0; font-size: 16px; margin-top: 30px;">🤖 Performance by AI Engine</h3>
        <table>
            <thead>
                <tr>
                    <th>AI Engine</th>
                    <th style="text-align: center;">Mention Rate (SoM)</th>
                    <th style="text-align: center;">Top #1 Recommendation</th>
                    <th style="text-align: center;">Average Rank</th>
                </tr>
            </thead>
            <tbody>
                {model_rows}
            </tbody>
        </table>

        <h3 style="color: #e2e8f0; font-size: 16px; margin-top: 30px;">🏆 Competitor Comparison Matrix</h3>
        <table>
            <thead>
                <tr>
                    <th>Brand Entity</th>
                    <th style="text-align: center;">Mention Rate</th>
                    <th style="text-align: center;">Top #1 Pick Rate</th>
                    <th style="text-align: center;">Status</th>
                </tr>
            </thead>
            <tbody>
                {comp_rows}
            </tbody>
        </table>

        <div style="margin-top: 35px; padding-top: 20px; border-top: 1px solid #1f2937; text-align: center; font-size: 12px; color: #64748b;">
            Generated by <a href="https://github.com/tmolavi/geo-scope">GEO-Scope</a> • Open Source Research by <a href="https://molavi.pro/">Taqi Molavi</a>
        </div>
    </div>
</body>
</html>"""
    return html
