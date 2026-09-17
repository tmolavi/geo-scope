import os
import json
from pathlib import Path
import random

from geo_scope.benchmark.builder import BenchmarkBuilder
from geo_scope.engine.query_generator import generate_prompt_dataset

target_brand = 'HubSpot'
competitors = ['Salesforce', 'Zoho CRM', 'Pipedrive']
niche = 'crm_sales'

prompts_raw = generate_prompt_dataset(
    niche_key=niche,
    target_brand=target_brand,
    competitors=competitors,
    language='both',
    total_count=30,
    seed=42,
)

prompts = []
for idx, p in enumerate(prompts_raw):
    prompts.append({
        'prompt_id': f'prompt_{idx+1:03d}',
        'text': p['query'],
        'intent_stratum': p.get('intent', 'informational'),
        'language': p.get('language', 'en'),
        'niche': niche,
        'target_brand': target_brand,
        'competitors': competitors,
    })

brands = [
    {'name': 'HubSpot', 'is_target': True, 'domain': 'hubspot.com'},
    {'name': 'Salesforce', 'is_target': False, 'domain': 'salesforce.com'},
    {'name': 'Zoho CRM', 'is_target': False, 'domain': 'zoho.com'},
    {'name': 'Pipedrive', 'is_target': False, 'domain': 'pipedrive.com'},
]

providers = [
    {'id': 'perplexity_sonar', 'name': 'Perplexity Sonar', 'search_grounded': True},
    {'id': 'openai_completion', 'name': 'ChatGPT Search / OpenAI', 'search_grounded': False},
    {'id': 'gemini_grounding', 'name': 'Google Gemini (Grounded)', 'search_grounded': True},
    {'id': 'claude_completion', 'name': 'Claude 3.7 Sonnet', 'search_grounded': False},
]

observations = []
citations = []
obs_idx = 1
cit_idx = 1

rng = random.Random(42)

domains_pool = [
    ('g2.com', 'Salesforce'),
    ('capterra.com', 'HubSpot'),
    ('trustradius.com', 'Zoho CRM'),
    ('reddit.com', 'Pipedrive'),
    ('hubspot.com', 'HubSpot'),
    ('salesforce.com', 'Salesforce'),
    ('techradar.com', 'HubSpot'),
    ('forbes.com', 'Salesforce'),
]

for p in prompts:
    pid = p['prompt_id']
    for prov in providers:
        p_id = prov['id']
        b_mentioned = rng.random() > 0.35
        b_rank = rng.choice([1, 2, 3]) if b_mentioned else None
        is_top1 = (b_rank == 1)
        
        mentioned_comps = [c for c in competitors if rng.random() > 0.4]
        comp_ranks = {}
        for c in mentioned_comps:
            comp_ranks[c] = rng.choice([1, 2, 3, 4])
            
        top1_b = target_brand if is_top1 else (mentioned_comps[0] if mentioned_comps else 'Salesforce')

        obs_record = {
            'observation_id': f'obs_{obs_idx:04d}',
            'prompt_id': pid,
            'provider_id': p_id,
            'model': p_id,
            'execution_mode': 'synthetic',
            'status': 'success',
            'brand_mentioned': b_mentioned,
            'brand_rank': b_rank,
            'is_top1': is_top1,
            'top1_brand': top1_b,
            'mentioned_brands': ([target_brand] if b_mentioned else []) + mentioned_comps,
            'competitor_ranks': comp_ranks,
            'sentiment': 'positive' if b_mentioned else 'neutral',
            'latency_ms': round(rng.uniform(350, 1800), 2),
            'response_snippet': "Summary comparison evaluating HubSpot and competitors.",
            'timestamp': '2026-03-15T12:00:00Z',
        }
        observations.append(obs_record)
        obs_idx += 1

        if prov.get('search_grounded', False) or rng.random() > 0.5:
            c_dom, c_brand = rng.choice(domains_pool)
            citations.append({
                'citation_id': f'cit_{cit_idx:04d}',
                'prompt_id': pid,
                'provider_id': p_id,
                'domain': c_dom,
                'url': f'https://{c_dom}/article-{cit_idx}',
                'rank_position': rng.choice([1, 2, 3]),
                'cited_for_brand': c_brand,
            })
            cit_idx += 1

builder = BenchmarkBuilder(dataset_id='geo-scope-benchmark-2026.1')
pkg_dir = builder.build_package(
    out_dir='benchmark',
    prompts=prompts,
    observations=observations,
    citations=citations,
    brands=brands,
    providers=providers,
    execution_mode='synthetic',
    research_status='demo_only',
    description='GEO-Scope Reference Benchmark 2026.1 containing 30 prompts across CRM/Sales SaaS and 120 multi-model observations.',
)

print(f'Benchmark package successfully created at: {pkg_dir}')
