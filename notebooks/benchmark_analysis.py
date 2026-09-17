#!/usr/bin/env python3
# Reproducible Benchmark Analysis Script for GEO-Scope Public Benchmark Datasets.
# Can be run directly or imported into Jupyter Notebook.

import json
from pathlib import Path
import pandas as pd
import numpy as np

from geo_scope.benchmark.reproducer import BenchmarkReproducer
from geo_scope.benchmark.hasher import verify_dataset_checksums


def analyze_benchmark(dataset_dir: str = 'benchmark/geo-scope-benchmark-2026.1'):
    path = Path(dataset_dir)
    print('=' * 80)
    print(f'GEO-Scope Public Benchmark Analysis: {path.name}')
    print('=' * 80)

    # 1. Cryptographic Integrity Check
    chk = verify_dataset_checksums(path)
    if not chk['valid']:
        print(f'❌ Checksum verification failed: {chk}')
        return
    print(f'✓ SHA-256 Checksums Verified ({chk["total_files"]} files intact)')

    # 2. Reproduction Check
    reproducer = BenchmarkReproducer()
    repro_res = reproducer.verify_and_reproduce(path)
    if not repro_res['success']:
        print('❌ Metric reproduction failed:')
        for d in repro_res.get('differences', []):
            print(f'  - {d}')
        return
    print('✓ Benchmark Metrics Recomputed & Verified')

    # 3. Load Datasets into Pandas DataFrames
    prompts_df = pd.read_json(path / 'prompts.jsonl', lines=True)
    obs_df = pd.read_json(path / 'observations.jsonl', lines=True)
    cits_df = pd.read_json(path / 'citations.jsonl', lines=True) if (path / 'citations.jsonl').exists() else pd.DataFrame()
    metrics = json.loads((path / 'metrics.json').read_text(encoding='utf-8'))

    print('\n' + '-' * 80)
    print('📊 SUMMARY OVERVIEW')
    print('-' * 80)
    print(f'• Execution Mode      : {metrics["execution_mode"]}')
    print(f'• Research Status     : {metrics["research_status"]}')
    print(f'• Total Prompts       : {metrics["total_prompts"]}')
    print(f'• Total Observations  : {metrics["total_observations"]}')
    print(f'• Success / Failed    : {metrics["successful_observations"]} / {metrics["failed_observations"]}')

    print('\n' + '-' * 80)
    print('🏆 BRAND PERFORMANCE & 95% BOOTSTRAP CONFIDENCE INTERVALS')
    print('-' * 80)
    brand_rows = []
    for b in metrics['brands']:
        m_est = b['mention_rate']
        t_est = b['top1_rate']
        som_est = b['share_of_model']
        brand_rows.append({
            'Brand': b['brand'],
            'Target': '★' if b['is_target'] else '',
            'Share of Model (%)': f"{som_est['value']:.1f}%" if som_est['value'] is not None else 'N/A',
            'Mention Rate (95% CI)': f"{m_est['value']:.1f}% [{m_est['ci_lower']:.1f}%, {m_est['ci_upper']:.1f}%]" if m_est['value'] is not None else 'N/A',
            'Top-1 Rate (95% CI)': f"{t_est['value']:.1f}% [{t_est['ci_lower']:.1f}%, {t_est['ci_upper']:.1f}%]" if t_est['value'] is not None else 'N/A',
            'Avg Rank': f"#{b['avg_rank']:.1f}" if b['avg_rank'] is not None else '-',
        })
    print(pd.DataFrame(brand_rows).to_string(index=False))

    print('\n' + '-' * 80)
    print('🤖 MULTI-MODEL PROVIDER PERFORMANCE')
    print('-' * 80)
    prov_rows = []
    for pid, pdata in metrics['providers'].items():
        tm = pdata['target_mention_rate']
        tt = pdata['target_top1_rate']
        prov_rows.append({
            'Provider': pid,
            'Success Obs': pdata['successful_observations'],
            'Failed Obs': pdata['failed_observations'],
            'Target Mention Rate': f"{tm['value']:.1f}% [{tm['ci_lower']:.1f}%, {tm['ci_upper']:.1f}%]" if tm['value'] is not None else 'N/A',
            'Target Top-1 Rate': f"{tt['value']:.1f}% [{tt['ci_lower']:.1f}%, {tt['ci_upper']:.1f}%]" if tt['value'] is not None else 'N/A',
            'Avg Latency (ms)': f"{pdata['mean_latency_ms']:.1f}" if pdata['mean_latency_ms'] is not None else '-',
        })
    print(pd.DataFrame(prov_rows).to_string(index=False))

    print('\n' + '-' * 80)
    print('🔗 TOP CITED DOMAINS')
    print('-' * 80)
    cits_rows = []
    for cd in metrics.get('top_cited_domains', [])[:5]:
        cits_rows.append({
            'Domain': cd['domain'],
            'Citations': cd['count'],
            'Citation Share': f"{cd['share_pct']:.1f}%",
        })
    if cits_rows:
        print(pd.DataFrame(cits_rows).to_string(index=False))
    else:
        print('No citations recorded in this run.')

    print('\n' + '-' * 80)
    print('📈 EMPIRICAL FACTOR ANALYSIS (OBSERVED ASSOCIATIONS ONLY)')
    print('-' * 80)
    if metrics.get('factor_analysis'):
        fa = metrics['factor_analysis']
        print(f'Disclaimer: {fa["disclaimer"]}\n')
        f_rows = []
        for f in fa.get('factors', []):
            ci = f.get('confidence_interval_95', [None, None])
            f_rows.append({
                'Factor Hypothesis': f['factor_name'],
                'Spearman r': f"{f.get('observed_correlation_spearman', 0):.2f}",
                '95% CI': f"[{ci[0]:.2f}, {ci[1]:.2f}]" if ci[0] is not None else '-',
                'Effect Size (d)': f"{f.get('effect_size_cohens_d', 0):.2f}",
                'Interpretation': f.get('interpretation', ''),
            })
        print(pd.DataFrame(f_rows).to_string(index=False))

    print('\n' + '=' * 80)
    print('✓ Analysis complete.')
    print('=' * 80)


if __name__ == '__main__':
    analyze_benchmark()
