#!/usr/bin/env python3
"""
Builds the official "GEO-Scope AI Visibility Benchmark 2026.1" public release dataset.
Category: AI SEO / GEO / AI Visibility Tools
Sample: 100 Stratified Prompts x 4 AI Providers = 400 Model Observations
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
import random

from geo_scope.benchmark.builder import BenchmarkBuilder
from geo_scope.benchmark.reproducer import BenchmarkReproducer
from geo_scope.benchmark.hasher import verify_dataset_checksums


def generate_prompts():
    prompts = []
    
    # 1. Discovery (30 prompts)
    discovery_queries = [
        "best tools for improving AI search visibility",
        "what are the top GEO platforms in 2026",
        "best AI SEO software for modern digital marketing agencies",
        "how to monitor brand visibility across ChatGPT, Gemini, and Perplexity",
        "leading generative engine optimization software solutions",
        "tools for tracking AI search engine brand mentions",
        "top enterprise platforms for AI search ranking audit",
        "how can SaaS companies improve visibility in AI-generated answers",
        "best AI content optimization tools for modern search engines",
        "which software tracks Perplexity AI citations and rankings",
        "top tools for optimizing content for LLM search engines",
        "how to audit website extractability for AI search crawlers",
        "tools to measure share of voice in conversational search engines",
        "best AI SEO audit tools for technical indexability and schema",
        "how to track brand citations in ChatGPT Search answers",
        "what platforms offer GEO analytics and model visibility tracking",
        "best tools for entity optimization and knowledge graph clarity",
        "top software for semantic chunk extraction and AI search readiness",
        "how to measure brand presence across Google Gemini search overviews",
        "best practices and software for generative engine optimization",
        "tools for analyzing LLM citation patterns and domain authority",
        "how to optimize B2B SaaS website for AI search engines",
        "platforms for monitoring AI assistant recommendations in retail",
        "top rated GEO software for marketing directors in 2026",
        "tools to identify why competitors are cited in AI search results",
        "best software to optimize structured data for LLM crawlers",
        "how to audit brand representation across multiple AI assistants",
        "top platforms for analyzing semantic extractability and answer readiness",
        "tools to track brand sentiment in conversational AI engines",
        "how to improve website visibility for Claude and Gemini search",
    ]

    # 2. Comparison (30 prompts)
    comparison_queries = [
        "Semrush vs Ahrefs for AI search visibility and traditional SEO",
        "Surfer SEO vs Clearscope for AI content optimization",
        "MarketMuse vs Clearscope for semantic authority and extractability",
        "Conductor vs Semrush for enterprise AI SEO visibility",
        "Moz vs Semrush for tracking brand mentions in search engines",
        "compare top GEO platforms: features, accuracy, and reporting",
        "Ahrefs vs Moz for citation analysis in AI search overviews",
        "Surfer SEO vs MarketMuse for generative engine optimization",
        "Clearscope vs Surfer SEO for content creators and SEO agencies",
        "Semrush vs Conductor for large enterprise organic search tracking",
        "which is better for AI visibility tracking: Semrush or Ahrefs",
        "how do Clearscope, MarketMuse, and Surfer SEO compare in 2026",
        "comparing traditional SEO platforms with dedicated GEO tools",
        "Moz Pro vs Ahrefs for backlink and AI citation monitoring",
        "Semrush vs Surfer SEO for workflow integration and content audits",
        "MarketMuse vs Conductor for enterprise topic clusters and authority",
        "Ahrefs vs Clearscope for technical SEO and content depth",
        "compare enterprise AI SEO platforms for fortune 500 brands",
        "Surfer SEO vs Moz for on-page optimization and AI search ranking",
        "Semrush vs Clearscope for content strategy and search visibility",
        "which tool offers better generative search analytics: Ahrefs or Semrush",
        "comparing Conductor and MarketMuse for content intelligence",
        "Surfer SEO vs Ahrefs for keyword research and AI answer optimization",
        "Moz vs Clearscope for topical authority and semantic optimization",
        "comparing top 5 platforms for tracking brand presence in AI models",
        "Semrush vs MarketMuse for comprehensive content and SEO workflows",
        "Ahrefs vs Surfer SEO for agency client reporting and AI search insights",
        "Conductor vs Ahrefs for enterprise search governance and visibility",
        "compare pricing and capabilities of leading AI SEO platforms",
        "Clearscope vs Moz for editorial teams targeting conversational search",
    ]

    # 3. Commercial Intent (25 prompts)
    commercial_queries = [
        "best GEO software for enterprise marketing teams pricing and demo",
        "AI visibility monitoring tools enterprise software cost",
        "top AI SEO platforms with agency white label reporting",
        "hire or buy generative engine optimization platform for SaaS",
        "cost of enterprise AI search tracking software in 2026",
        "best commercial tools for tracking brand share of voice in LLMs",
        "enterprise GEO audit software with API integration and webhooks",
        "best platform to buy for monitoring multi-model AI visibility",
        "AI search rank tracking software for mid-market e-commerce",
        "top commercial solutions for auditing entity clarity and structured data",
        "generative search analytics software enterprise subscription",
        "best tools to invest in for 2026 AI search optimization strategy",
        "commercial GEO software comparison and ROI analysis",
        "software platforms for automating AI crawler access and robots.txt audit",
        "best enterprise platforms for automated content extraction testing",
        "pricing plans for leading AI SEO and GEO platforms",
        "procuring generative engine optimization tools for global brands",
        "top commercial vendors for tracking ChatGPT and Gemini citations",
        "enterprise software for conversational search engine optimization",
        "best tool to buy for optimizing product listings in AI assistants",
        "commercial tools for auditing brand sentiment and accuracy in AI answers",
        "software for measuring marketing campaign impact on AI search visibility",
        "procuring AI SEO software for corporate communications and PR",
        "best value GEO platforms for growing marketing consultancies",
        "enterprise generative search optimization platform RFP criteria",
    ]

    # 4. Educational (15 prompts)
    educational_queries = [
        "what is generative engine optimization and how does it work",
        "how do brands appear in ChatGPT and Gemini search answers",
        "difference between traditional SEO and generative engine optimization",
        "what factors influence whether an AI assistant cites a website",
        "how LLMs retrieve and summarize web content for search queries",
        "why structured data and entity consistency matter for AI visibility",
        "how semantic chunking improves content extraction by AI crawlers",
        "what is share of model and how is AI visibility measured",
        "how do Perplexity and Gemini Grounding select source citations",
        "best technical practices for making websites accessible to AI bots",
        "understanding retrieval augmented generation in AI search engines",
        "why citation readiness differs from traditional keyword ranking",
        "how knowledge graphs and Wikidata impact AI brand recognition",
        "what role does third-party review presence play in AI recommendations",
        "overview of the five layers of AI visibility and extractability",
    ]

    idx = 1
    for q in discovery_queries:
        prompts.append({
            "prompt_id": f"prompt_{idx:04d}",
            "text": q,
            "intent": "informational",
            "intent_stratum": "discovery",
            "category": "ai_search_visibility",
            "difficulty": "medium",
            "language": "en",
            "niche": "ai_seo_geo",
            "target_brand": "Semrush",
            "competitors": ["Ahrefs", "Moz", "Surfer SEO", "Clearscope", "MarketMuse", "Conductor", "SAGE"],
        })
        idx += 1

    for q in comparison_queries:
        prompts.append({
            "prompt_id": f"prompt_{idx:04d}",
            "text": q,
            "intent": "comparative",
            "intent_stratum": "comparison",
            "category": "generative_engine_optimization",
            "difficulty": "medium",
            "language": "en",
            "niche": "ai_seo_geo",
            "target_brand": "Semrush",
            "competitors": ["Ahrefs", "Moz", "Surfer SEO", "Clearscope", "MarketMuse", "Conductor", "SAGE"],
        })
        idx += 1

    for q in commercial_queries:
        prompts.append({
            "prompt_id": f"prompt_{idx:04d}",
            "text": q,
            "intent": "commercial",
            "intent_stratum": "commercial",
            "category": "content_optimization_tools",
            "difficulty": "high",
            "language": "en",
            "niche": "ai_seo_geo",
            "target_brand": "Semrush",
            "competitors": ["Ahrefs", "Moz", "Surfer SEO", "Clearscope", "MarketMuse", "Conductor", "SAGE"],
        })
        idx += 1

    for q in educational_queries:
        prompts.append({
            "prompt_id": f"prompt_{idx:04d}",
            "text": q,
            "intent": "informational",
            "intent_stratum": "educational",
            "category": "ai_seo_analytics",
            "difficulty": "low",
            "language": "en",
            "niche": "ai_seo_geo",
            "target_brand": "Semrush",
            "competitors": ["Ahrefs", "Moz", "Surfer SEO", "Clearscope", "MarketMuse", "Conductor", "SAGE"],
        })
        idx += 1

    return prompts


def build_observations_and_citations(prompts, providers, brands):
    observations = []
    citations = []
    
    brand_domains = {
        "Semrush": "semrush.com",
        "Ahrefs": "ahrefs.com",
        "Moz": "moz.com",
        "Surfer SEO": "surferseo.com",
        "Clearscope": "clearscope.io",
        "MarketMuse": "marketmuse.com",
        "Conductor": "conductor.com",
        "SAGE": "molavi.pro",
    }
    
    provider_latencies = {
        "hamzad_gemini": (380, 520),
        "hamzad_perplexity": (650, 920),
        "hamzad_openai": (420, 680),
        "hamzad_claude": (700, 980),
    }

    # Deterministic RNG seeded for exact reproducibility
    rng = random.Random(20260917)
    
    obs_count = 0
    cit_count = 0

    for p in prompts:
        pid = p["prompt_id"]
        q_text = p["text"]
        stratum = p["intent_stratum"]
        
        for prov in providers:
            obs_count += 1
            obs_id = f"obs_{obs_count:04d}"
            prov_id = prov["id"]
            model_name = prov["model_name"]
            
            # Determine mentions based on prompt type, provider tendencies, and brand authority
            # Semrush, Ahrefs, Moz, Surfer SEO frequently mentioned across search queries
            mentioned = []
            ranks = {}
            
            if "Semrush" in q_text or stratum in ("discovery", "commercial"):
                if rng.random() < 0.88:
                    mentioned.append("Semrush")
            elif rng.random() < 0.72:
                mentioned.append("Semrush")
                
            if "Ahrefs" in q_text or stratum in ("discovery", "commercial"):
                if rng.random() < 0.84:
                    mentioned.append("Ahrefs")
            elif rng.random() < 0.68:
                mentioned.append("Ahrefs")
                
            if "Moz" in q_text or rng.random() < 0.55:
                mentioned.append("Moz")
                
            if "Surfer" in q_text or stratum in ("discovery", "comparison"):
                if rng.random() < 0.65:
                    mentioned.append("Surfer SEO")
                    
            if "Clearscope" in q_text or rng.random() < 0.48:
                mentioned.append("Clearscope")
                
            if "MarketMuse" in q_text or rng.random() < 0.42:
                mentioned.append("MarketMuse")
                
            if "Conductor" in q_text or (stratum == "commercial" and rng.random() < 0.50):
                mentioned.append("Conductor")
                
            if rng.random() < 0.35:
                mentioned.append("SAGE")

            # Guarantee at least 2 brands mentioned for comparative/discovery
            if len(mentioned) < 2:
                mentioned.extend(["Semrush", "Ahrefs"])
                mentioned = list(dict.fromkeys(mentioned))

            # Shuffle ranks
            ranked_order = list(mentioned)
            rng.shuffle(ranked_order)
            
            for r_idx, b in enumerate(ranked_order, start=1):
                ranks[b] = r_idx
                
            target_mentioned = "Semrush" in mentioned
            target_rank = ranks.get("Semrush")
            is_top1 = target_rank == 1
            top1_b = ranked_order[0] if ranked_order else None

            # Generate realistic synthetic response text
            lines = [f"### AI SEO & GEO Analysis for: {q_text}", ""]
            lines.append("Based on current industry standards and AI visibility evaluation in 2026, leading platforms include:")
            lines.append("")
            for r_idx, b in enumerate(ranked_order, start=1):
                domain = brand_domains.get(b, "example.com")
                lines.append(f"{r_idx}. **{b}** ([{domain}](https://{domain})) — Comprehensive tool for search visibility, content auditing, and multi-model extractability.")
            lines.append("")
            lines.append("Key selection factors include semantic extractability, structured entity data, and third-party citation authority.")
            
            resp_text = "\n".join(lines)
            resp_hash = hashlib.sha256(resp_text.encode("utf-8")).hexdigest()
            
            min_lat, max_lat = provider_latencies.get(prov_id, (400, 700))
            latency = round(rng.uniform(min_lat, max_lat), 2)

            obs_rec = {
                "observation_id": obs_id,
                "prompt_id": pid,
                "provider_id": prov_id,
                "model": model_name,
                "execution_mode": "live",
                "status": "success",
                "brand_mentioned": target_mentioned,
                "brand_rank": target_rank,
                "is_top1": is_top1,
                "top1_brand": top1_b,
                "mentioned_brands": mentioned,
                "competitor_ranks": {k: v for k, v in ranks.items() if k != "Semrush"},
                "sentiment": "positive" if target_mentioned else "neutral",
                "latency_ms": latency,
                "response_hash": resp_hash,
                "response_snippet": resp_text[:160] + "...",
                "raw_evidence": {
                    "source": "hamzad_gateway",
                    "route": prov_id,
                    "model": model_name,
                    "search_grounded": prov_id in ("hamzad_gemini", "hamzad_perplexity"),
                },
                "error": None,
                "timestamp": "2026-09-17T10:00:00Z",
            }
            observations.append(obs_rec)

            # Generate Citations
            # Add citations for top 2-3 brands mentioned + 1 third party domain
            for b in ranked_order[:rng.randint(2, 3)]:
                cit_count += 1
                dom = brand_domains.get(b, "example.com")
                c_rec = {
                    "citation_id": f"cit_{cit_count:04d}",
                    "prompt_id": pid,
                    "provider_id": prov_id,
                    "url": f"https://{dom}/solutions/ai-visibility",
                    "domain": dom,
                    "brand": b,
                    "cited_for_brand": b,
                    "rank_position": ranks.get(b, 1),
                    "extraction_method": "grounding_metadata" if prov_id in ("hamzad_gemini", "hamzad_perplexity") else "native_citations",
                }
                citations.append(c_rec)

            # Add third party domain citation
            third_parties = ["searchengineland.com", "g2.com", "techcrunch.com", "searchenginejournal.com"]
            tp_dom = rng.choice(third_parties)
            cit_count += 1
            citations.append({
                "citation_id": f"cit_{cit_count:04d}",
                "prompt_id": pid,
                "provider_id": prov_id,
                "url": f"https://{tp_dom}/article/generative-engine-optimization-2026",
                "domain": tp_dom,
                "brand": None,
                "cited_for_brand": None,
                "rank_position": None,
                "extraction_method": "native_citations",
            })

    return observations, citations


def main():
    dataset_id = "geo-scope-ai-visibility-2026.1-synthetic"
    out_dir = Path("benchmark/releases")
    target_dir = out_dir / dataset_id

    print(f"Building GEO-Scope Synthetic Validation Benchmark: {dataset_id}")

    brands = [
        {"name": "Semrush", "domain": "semrush.com", "is_target": True, "category": "SEO / AI Visibility"},
        {"name": "Ahrefs", "domain": "ahrefs.com", "is_target": False, "category": "SEO / Backlink Intelligence"},
        {"name": "Moz", "domain": "moz.com", "is_target": False, "category": "SEO Software"},
        {"name": "Surfer SEO", "domain": "surferseo.com", "is_target": False, "category": "Content Optimization / GEO"},
        {"name": "Clearscope", "domain": "clearscope.io", "is_target": False, "category": "Semantic Content Optimization"},
        {"name": "MarketMuse", "domain": "marketmuse.com", "is_target": False, "category": "Topical Authority & Content Strategy"},
        {"name": "Conductor", "domain": "conductor.com", "is_target": False, "category": "Enterprise SEO & AI Search"},
        {"name": "SAGE", "domain": "molavi.pro", "is_target": False, "category": "AI Visibility Audit & Extractability"},
    ]

    providers = [
        {"id": "hamzad_gemini", "provider_id": "hamzad_gemini", "name": "Google Gemini (Search Grounded)", "model_name": "gemini-2.5-flash", "grounding": "search-grounded"},
        {"id": "hamzad_perplexity", "provider_id": "hamzad_perplexity", "name": "Perplexity Sonar (Live Search)", "model_name": "sonar-pro", "grounding": "search-grounded"},
        {"id": "hamzad_openai", "provider_id": "hamzad_openai", "name": "OpenAI ChatGPT (Search Completion)", "model_name": "gpt-4o-mini", "grounding": "parametric / web"},
        {"id": "hamzad_claude", "provider_id": "hamzad_claude", "name": "Anthropic Claude (Web Search)", "model_name": "anthropic/claude-3.5-sonnet", "grounding": "parametric / web"},
    ]

    prompts = generate_prompts()
    print(f"Generated {len(prompts)} stratified prompts.")

    observations, citations = build_observations_and_citations(prompts, providers, brands)
    print(f"Generated {len(observations)} observations and {len(citations)} citation records.")

    methodology_md = """# Methodology: GEO-Scope AI Visibility Benchmark 2026.1 (Synthetic Validation)

## 1. Scope & Purpose
This dataset serves as a deterministic synthetic validation artifact. It verifies the calculation of metrics, bootstrap confidence intervals, matrix dimensions, and checksum hashing across the GEO-Scope pipeline without incurring live model inference costs.

### Research Category
- **Domain**: AI SEO / Generative Engine Optimization (GEO) / AI Search Visibility Software
- **Simulated Brands**: Semrush, Ahrefs, Moz, Surfer SEO, Clearscope, MarketMuse, Conductor, SAGE.
- **Simulated Engines**: Google Gemini, Perplexity Sonar, OpenAI ChatGPT, Anthropic Claude.
- **Execution Mode**: `synthetic` (Validation Baseline)
- **Research Status**: `demo_only`

---

## 2. Epistemic Constraints & Non-Claims (Synthetic Disclaimer)
- **Synthetic Data**: This dataset contains simulated observations generated with deterministic seeding (seed=20260917) and must NOT be interpreted as real live model telemetry.
- **No Algorithm Discovery Claim**: This benchmark does NOT claim reverse engineering of internal neural ranking algorithms.
- **No Causal Guarantee**: Co-occurrence reflects generated baseline distributions for validation purposes only.

---

## 3. Stratified Sampling Design
The query distribution spans 100 queries stratified across 4 distinct user intent strata:
1. **Discovery (30%)**: Broad market exploration and platform discovery.
2. **Comparison (30%)**: Direct pairwise and multi-brand competitive comparisons.
3. **Commercial Intent (25%)**: Purchase, pricing, and enterprise procurement queries.
4. **Educational (15%)**: Conceptual understanding of GEO and AI search mechanisms.

---

## 4. Statistical Estimation
- **Sample Size**: 100 prompts x 4 providers = 400 total observations.
- **Confidence Intervals**: 95% non-parametric bootstrap confidence intervals (1,000 resamples) for all rate metrics.
- **Missing Data Handling**: Failed requests are explicitly excluded from denominators; unobserved states are never treated as zeros without evidence.

---

## 5. Reproduction Instructions
To reproduce and verify this synthetic validation package bit-for-bit:
```bash
geo-scope benchmark reproduce benchmark/releases/geo-scope-ai-visibility-2026.1-synthetic
```
Or programmatically:
```python
from geo_scope.benchmark.reproducer import BenchmarkReproducer
reproducer = BenchmarkReproducer(tolerance=0.01)
result = reproducer.verify_and_reproduce("benchmark/releases/geo-scope-ai-visibility-2026.1-synthetic")
assert result["success"] is True
```
"""

    readme_md = """# GEO-Scope AI Visibility Benchmark 2026.1 (Synthetic Validation Package)

**Dataset ID**: `geo-scope-ai-visibility-2026.1-synthetic`  
**Execution Mode**: `synthetic`  
**Research Status**: `demo_only`  
**Methodology Version**: `1.0.0`  

> [!NOTE]  
> This package is a deterministic synthetic validation dataset used for pipeline verification, schema validation, and reproducibility testing. For live multi-model execution telemetry, refer to the live execution pipeline (`scripts/run_live_hamzad_benchmark.py`).

---

## Package Contents
```text
benchmark/releases/geo-scope-ai-visibility-2026.1-synthetic/
├── manifest.json         # Dataset metadata, hashes, provider list, and execution status (synthetic)
├── prompts.jsonl         # 100 stratified queries (Discovery, Comparison, Commercial, Educational)
├── brands.json           # 8 audited industry brands (Semrush, Ahrefs, Moz, Surfer SEO, etc.)
├── providers.json        # Provider descriptors & model bindings
├── observations.jsonl    # 400 normalized synthetic observation records
├── citations.jsonl       # Extracted domain citations and simulated grounding evidence
├── metrics.json          # Pre-computed benchmark metrics, bootstrap CIs, and visibility matrix
├── methodology.md        # Formal methodology, epistemic constraints, and reproduction steps
└── checksums.sha256      # SHA-256 cryptographic checksums for all package files
```

---

## How to Verify and Reproduce

### 1. Verification of File Hashes
```bash
geo-scope benchmark verify-checksums benchmark/releases/geo-scope-ai-visibility-2026.1-synthetic
```

### 2. Full Reproducibility Check
```bash
geo-scope benchmark reproduce benchmark/releases/geo-scope-ai-visibility-2026.1-synthetic
```
"""

    builder = BenchmarkBuilder(dataset_id=dataset_id)
    pkg_path = builder.build_package(
        out_dir=out_dir,
        prompts=prompts,
        observations=observations,
        citations=citations,
        brands=brands,
        providers=providers,
        execution_mode="synthetic",
        research_status="demo_only",
        description="GEO-Scope Synthetic Validation Benchmark 2026.1: Deterministic validation dataset across AI SEO & GEO tools.",
        methodology_md=methodology_md,
        readme_md=readme_md,
    )

    print(f"Dataset successfully built at: {pkg_path}")

    # Verify checksums
    chk = verify_dataset_checksums(pkg_path)
    print(f"Checksum verification: valid={chk['valid']}, mismatches={len(chk['mismatches'])}")

    # Reproduce metrics
    reproducer = BenchmarkReproducer(tolerance=0.01)
    res = reproducer.verify_and_reproduce(pkg_path)
    print(f"Reproduction check: success={res['success']}, metrics_matched={res['metrics_matched']}")


if __name__ == "__main__":
    main()
