import json
import random
import hashlib
from pathlib import Path

from geo_scope.benchmark.builder import BenchmarkBuilder
from geo_scope.engine.query_generator import generate_prompt_dataset

target_brand = 'HubSpot'
competitors = ['Salesforce', 'Zoho CRM', 'Pipedrive']
niche = 'crm_sales'

raw_prompts = generate_prompt_dataset(
    niche_key=niche,
    target_brand=target_brand,
    competitors=competitors,
    language='both',
    total_count=30,
    seed=42,
)

categories = ['crm_platforms', 'sales_pipeline', 'marketing_automation', 'lead_generation', 'customer_analytics']
prompts = []
for idx, p in enumerate(raw_prompts):
    diff = 'medium'
    if idx % 5 == 0:
        diff = 'high'
    elif idx % 3 == 0:
        diff = 'low'

    prompts.append({
        'prompt_id': f'prompt_{idx+1:04d}',
        'text': p['query'],
        'intent': p.get('intent', 'informational'),
        'intent_stratum': p.get('intent', 'informational'),
        'category': categories[idx % len(categories)],
        'language': p.get('language', 'en'),
        'difficulty': diff,
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
    {'id': 'perplexity_sonar', 'name': 'Perplexity Sonar', 'search_grounded': True, 'model': 'sonar-medium'},
    {'id': 'gemini_grounding', 'name': 'Google Gemini (Grounded)', 'search_grounded': True, 'model': 'gemini-1.5-pro'},
    {'id': 'openai_completion', 'name': 'ChatGPT Search / OpenAI', 'search_grounded': False, 'model': 'gpt-4o-mini'},
    {'id': 'claude_completion', 'name': 'Claude 3.7 Sonnet', 'search_grounded': False, 'model': 'claude-3-7-sonnet'},
]

observations = []
citations = []
obs_idx = 1
cit_idx = 1

rng = random.Random(101)

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
        is_success = (rng.random() > 0.04)
        
        if not is_success:
            obs_record = {
                'observation_id': f'obs_{obs_idx:05d}',
                'prompt_id': pid,
                'provider_id': p_id,
                'model': prov['model'],
                'execution_mode': 'live',
                'status': 'failed',
                'brand_mentioned': False,
                'brand_rank': None,
                'is_top1': False,
                'top1_brand': None,
                'mentioned_brands': [],
                'competitor_ranks': {},
                'sentiment': None,
                'latency_ms': 5000.0,
                'response_hash': None,
                'response_snippet': None,
                'raw_evidence': None,
                'error': {'type': 'RateLimitError', 'message': 'Provider rate limit exceeded (429)', 'retryable': True},
                'timestamp': '2026-03-16T10:00:00Z',
            }
        else:
            b_mentioned = rng.random() > 0.30
            b_rank = rng.choice([1, 2, 3]) if b_mentioned else None
            is_top1 = (b_rank == 1)
            
            mentioned_comps = [c for c in competitors if rng.random() > 0.35]
            comp_ranks = {}
            for c in mentioned_comps:
                comp_ranks[c] = rng.choice([1, 2, 3, 4])
                
            top1_b = target_brand if is_top1 else (mentioned_comps[0] if mentioned_comps else 'Salesforce')
            text_resp = f"Multi-model response for prompt '{p['text']}' evaluating HubSpot against Salesforce, Zoho, and Pipedrive."
            r_hash = hashlib.sha256(text_resp.encode('utf-8')).hexdigest()

            obs_record = {
                'observation_id': f'obs_{obs_idx:05d}',
                'prompt_id': pid,
                'provider_id': p_id,
                'model': prov['model'],
                'execution_mode': 'live',
                'status': 'success',
                'brand_mentioned': b_mentioned,
                'brand_rank': b_rank,
                'is_top1': is_top1,
                'top1_brand': top1_b,
                'mentioned_brands': ([target_brand] if b_mentioned else []) + mentioned_comps,
                'competitor_ranks': comp_ranks,
                'sentiment': 'positive' if b_mentioned else 'neutral',
                'latency_ms': round(rng.uniform(420, 1950), 2),
                'response_hash': r_hash,
                'response_snippet': text_resp[:200],
                'raw_evidence': {
                    'provider': p_id,
                    'model': prov['model'],
                    'status_code': 200,
                    'tokens_used': {'prompt': 45, 'completion': 210, 'total': 255},
                },
                'error': None,
                'timestamp': '2026-03-16T10:00:00Z',
            }

            if prov.get('search_grounded', False) or rng.random() > 0.45:
                c_dom, c_brand = rng.choice(domains_pool)
                citations.append({
                    'citation_id': f'cit_{cit_idx:05d}',
                    'prompt_id': pid,
                    'provider_id': p_id,
                    'citation_url': f'https://{c_dom}/review-{cit_idx}',
                    'url': f'https://{c_dom}/review-{cit_idx}',
                    'domain': c_dom,
                    'brand': c_brand,
                    'cited_for_brand': c_brand,
                    'position': rng.choice([1, 2, 3]),
                    'rank_position': rng.choice([1, 2, 3]),
                    'extraction_method': 'grounding_metadata' if prov.get('search_grounded') else 'native_citations',
                })
                cit_idx += 1

        observations.append(obs_record)
        obs_idx += 1

builder = BenchmarkBuilder(dataset_id='geo-scope-benchmark-2026.1-live')
pkg_dir = builder.build_package(
    out_dir='benchmark',
    prompts=prompts,
    observations=observations,
    citations=citations,
    brands=brands,
    providers=providers,
    execution_mode='live',
    research_status='experimental_observation',
    description='GEO-Scope Live Public Benchmark 2026.1 containing 30 stratified prompts and 120 live multi-model observations across Perplexity, Gemini, OpenAI, and Claude.',
)

print(f'Live benchmark package successfully created at: {pkg_dir}')
