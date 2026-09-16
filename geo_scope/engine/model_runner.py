"""
Model Runner & Engine Simulator
Runs queries against live APIs (OpenAI, Perplexity, Gemini, Claude) via ProviderRegistry,
or high-fidelity deterministic GEO Simulation. Never silently falls back from LIVE to SIMULATION.
"""

import asyncio
import random
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Union

from geo_scope.engine.execution_mode import ExecutionMode
from geo_scope.engine.persistence import RawRunStore
from geo_scope.providers.registry import ProviderRegistry, registry as default_registry
from geo_scope.providers.models import ProviderResponse


# Pre-defined realistic domain pools for RAG simulation
CITATIONS_BY_NICHE = {
    "crm_sales": {
        "ugc": [
            (
                "Reddit r/sales: Best CRM for startups in 2026",
                "https://reddit.com/r/sales/comments/best_crm_discussion_2026",
            ),
            (
                "Reddit r/entrepreneur: HubSpot vs Salesforce honest review",
                "https://reddit.com/r/entrepreneur/comments/hubspot_salesforce_review",
            ),
            (
                "Quora: Which CRM gives the highest ROI?",
                "https://quora.com/Which-CRM-software-is-best-for-small-business",
            ),
        ],
        "reviews": [
            ("G2: 2026 CRM Software Grid Leaderboard", "https://www.g2.com/categories/crm"),
            (
                "Capterra: Top CRM Solutions Comparison",
                "https://www.capterra.com/customer-relationship-management-software/",
            ),
            ("Trustpilot: Customer Satisfaction Ratings", "https://www.trustpilot.com/categories/crm_software"),
        ],
        "media": [
            (
                "TechCrunch: The State of Enterprise SaaS 2026",
                "https://techcrunch.com/2026/01/enterprise-crm-landscape",
            ),
            (
                "Forbes Advisor: Best CRM for Small Business",
                "https://www.forbes.com/advisor/business/software/best-crm-small-business/",
            ),
            (
                "Digiato: راهنمای انتخاب نرم‌افزار مدیریت ارتباط با مشتری",
                "https://digiato.com/article/best-crm-software-guide",
            ),
        ],
        "official": [
            ("HubSpot Official Product Tour", "https://www.hubspot.com/products/crm"),
            ("Salesforce Sales Cloud Overview", "https://www.salesforce.com/products/sales-cloud/"),
            ("Zoho CRM Features", "https://www.zoho.com/crm/"),
        ],
    },
    "seo_marketing": {
        "ugc": [
            ("Reddit r/SEO: Ahrefs vs SEMrush in 2026", "https://reddit.com/r/SEO/comments/ahrefs_vs_semrush_accuracy"),
            (
                "Reddit r/BigSEO: Generative Engine Optimization strategies",
                "https://reddit.com/r/bigseo/comments/geo_ranking_tactics",
            ),
        ],
        "reviews": [
            ("G2: SEO Software Category Leaders", "https://www.g2.com/categories/seo-software"),
            ("TrustRadius: Ahrefs Deep Dive Review", "https://www.trustradius.com/products/ahrefs/reviews"),
        ],
        "media": [
            (
                "Search Engine Land: AI Search Visibility Trends",
                "https://searchengineland.com/geo-ai-search-optimization-guide-439201",
            ),
            (
                "Zoomit: مقایسه برترین ابزارهای سئو و تحلیل کلمات کلیدی",
                "https://www.zoomit.ir/software-applications/best-seo-tools-comparison/",
            ),
        ],
        "official": [
            ("Ahrefs Webmaster Tools", "https://ahrefs.com/webmaster-tools"),
            ("SEMrush Competitive Research", "https://www.semrush.com/competitive-research/"),
        ],
    },
}


class ModelRunner:
    def __init__(
        self,
        api_keys: Optional[Dict[str, str]] = None,
        mode: Union[str, ExecutionMode] = ExecutionMode.SIMULATION,
        seed: int = 42,
        providers: Optional[ProviderRegistry] = None,
        run_store: Optional[RawRunStore] = None,
        experiment_id: Optional[str] = None,
        raise_on_failure: bool = False,
    ):
        if isinstance(mode, ExecutionMode):
            self.mode = mode
        else:
            self.mode = ExecutionMode.from_string(mode)

        self.seed = seed
        self.rng = random.Random(seed)
        self.providers = providers or ProviderRegistry()
        self.api_keys = api_keys or {}
        self.run_store = run_store
        self.experiment_id = experiment_id or f"EXP-{int(datetime.now(timezone.utc).timestamp())}"
        self.raise_on_failure = raise_on_failure

        for name, key in self.api_keys.items():
            provider = self.providers.get(name)
            if provider is None or not hasattr(provider, "api_key"):
                raise ValueError(f"Unknown keyed provider: {name}")
            provider.api_key = key

        self.active_models = ["perplexity_sonar", "chatgpt_search", "gemini_grounding", "claude_3_7"]

    async def execute_batch(
        self,
        prompts: List[Dict[str, Any]],
        models: Optional[List[str]] = None,
        progress_callback=None,
    ) -> List[Dict[str, Any]]:
        """
        Executes a batch of queries across selected AI engines.
        In LIVE mode: invokes real providers via ProviderRegistry and persists raw evidence.
        In SIMULATION mode: uses deterministic simulation only.
        """
        target_models = self.active_models if models is None else models
        self.validate_models(target_models)
        self.rng = random.Random(self.seed)
        total_tasks = len(prompts) * len(target_models)
        completed = 0
        raw_responses = []

        # If persistence is active, store prompts
        if self.run_store:
            self.run_store.save_prompts(prompts)

        # Process in chunks to maintain responsiveness and avoid overwhelming event loop
        chunk_size = 20
        for i in range(0, len(prompts), chunk_size):
            chunk = prompts[i : i + chunk_size]
            for prompt_item in chunk:
                for model in target_models:
                    if self.mode == ExecutionMode.SIMULATION:
                        res_text = self._simulate_realistic_response(prompt_item, model)
                        record = {
                            "query_item": prompt_item,
                            "model": model,
                            "response_text": res_text,
                            "status": "success",
                            "error": None,
                            "provenance": {
                                "execution_mode": ExecutionMode.SIMULATION.value,
                                "seed": self.seed,
                                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                "provider_id": model,
                                "model_id": "simulation-profile:" + model,
                                "response_kind": "simulated",
                                "search_grounded": False,
                                "provider_evidence": {},
                                "fallback_disabled": True,
                            },
                        }
                    else:
                        # LIVE EXECUTION PATH
                        provider = self.providers.resolve(model)
                        provider_resp = await provider.generate(prompt_item, execution_mode=ExecutionMode.LIVE.value)

                        # Raw persistence hook
                        if self.run_store:
                            raw_rec = provider_resp.to_raw_record(
                                experiment_id=self.experiment_id,
                                run_id=f"run_{self.experiment_id}",
                                prompt_id=str(prompt_item.get("id", "")),
                                prompt=prompt_item.get("query", ""),
                            )
                            self.run_store.append_raw_record(raw_rec)

                        if provider_resp.is_failed() and self.raise_on_failure:
                            err_type = provider_resp.error.get("type", "Error") if provider_resp.error else "Error"
                            raise RuntimeError(
                                f"Provider {model} failed ({err_type}); no simulated fallback was used."
                            )

                        record = {
                            "query_item": prompt_item,
                            "model": model,
                            "response_text": provider_resp.text,
                            "status": provider_resp.status,
                            "error": provider_resp.error,
                            "provenance": {
                                "execution_mode": ExecutionMode.LIVE.value,
                                "seed": None,
                                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                "provider_id": provider.name,
                                "model_id": provider_resp.model,
                                "response_kind": provider_resp.metadata.get("response_kind", provider.response_kind),
                                "search_grounded": provider_resp.metadata.get("search_grounded", False),
                                "provider_evidence": {
                                    "citations": provider_resp.citations,
                                    "raw_payload": provider_resp.raw,
                                    "grounding_metadata": provider_resp.metadata.get("grounding_metadata", {}),
                                    "usage": provider_resp.usage,
                                    "latency_ms": provider_resp.latency_ms,
                                    "status": provider_resp.status,
                                    "error": provider_resp.error,
                                },
                                "status": provider_resp.status,
                                "error": provider_resp.error,
                                "fallback_disabled": True,
                            },
                        }

                    raw_responses.append(record)
                    completed += 1
                if progress_callback:
                    progress_callback(completed, total_tasks)
            await asyncio.sleep(0.01)

        return raw_responses

    def validate_models(self, models: List[str]):
        if not models or len(models) != len(set(models)):
            raise ValueError("Select at least one unique provider")
        for model in models:
            if self.mode == ExecutionMode.SIMULATION:
                if model not in self.active_models:
                    raise ValueError(f"No simulation profile for {model}")
            else:
                # In live mode, verify provider exists in registry
                provider = self.providers.get(model)
                if provider is None:
                    raise ValueError(f"Provider {model} is not registered; see geo-scope providers")

    def _simulate_realistic_response(self, prompt_item: Dict[str, Any], model: str) -> str:
        """
        Simulates model-specific RAG output reflecting empirical GEO behaviors.
        """
        target_brand = prompt_item.get("target_brand", "HubSpot")
        competitors = prompt_item.get("expected_entities", ["Salesforce", "Zoho CRM", "Pipedrive"])
        if target_brand in competitors:
            comps = [c for c in competitors if c != target_brand]
        else:
            comps = competitors

        intent = prompt_item.get("intent", "commercial_direct")
        lang = prompt_item.get("language", "en")
        niche = prompt_item.get("niche", "crm_sales")
        query = prompt_item.get("query", "")

        pool = CITATIONS_BY_NICHE.get(niche, CITATIONS_BY_NICHE["crm_sales"])
        ugc_links = pool.get("ugc", [])
        rev_links = pool.get("reviews", [])
        med_links = pool.get("media", [])
        off_links = pool.get("official", [])

        citations = []
        if model == "perplexity_sonar":
            citations.extend(self.rng.sample(ugc_links, min(2, len(ugc_links))))
            citations.extend(self.rng.sample(rev_links, min(1, len(rev_links))))
        elif model == "chatgpt_search":
            citations.extend(self.rng.sample(med_links, min(2, len(med_links))))
            citations.extend(self.rng.sample(rev_links, min(1, len(rev_links))))
        elif model == "gemini_grounding":
            citations.extend(self.rng.sample(med_links, min(1, len(med_links))))
            citations.extend(self.rng.sample(off_links, min(2, len(off_links))))
        else:  # Claude
            citations.extend(self.rng.sample(rev_links, min(1, len(rev_links))))
            citations.extend(self.rng.sample(med_links, min(1, len(med_links))))

        target_in_top1 = self.rng.random() < 0.45
        target_mentioned = target_in_top1 or (self.rng.random() < 0.40)

        if lang == "fa":
            return self._build_persian_response(
                query, target_brand, comps, intent, model, target_mentioned, target_in_top1, citations
            )
        else:
            return self._build_english_response(
                query, target_brand, comps, intent, model, target_mentioned, target_in_top1, citations
            )

    def _build_persian_response(self, query, brand, comps, intent, model, mentioned, is_top1, citations) -> str:
        ordered_list = []
        if is_top1:
            ordered_list.append(brand)
            ordered_list.extend(self.rng.sample(comps, min(3, len(comps))))
        elif mentioned:
            if comps:
                ordered_list.append(comps[0])
                ordered_list.append(brand)
                ordered_list.extend(comps[1:3])
            else:
                ordered_list.append(brand)
        else:
            ordered_list.extend(self.rng.sample(comps, min(4, len(comps))))

        lines = [
            "بر اساس آخرین بررسی‌های بازار و تحلیل نیازهای سازمانی در سال ۲۰۲۶، پاسخ دقیق به پرسش شما در ادامه آمده است:\n",
            "### گزینه‌های برتر و توصیه‌شده:",
        ]
        for idx, item in enumerate(ordered_list, 1):
            if item == brand:
                lines.append(
                    f"{idx}. **{item}**: ارائه‌دهنده راهکارهای یکپارچه با رابط کاربری روان، خودکارسازی پیشرفته و پشتیبانی چندزبانه مناسب رشد سریع کسب‌وکارها."
                )
            else:
                lines.append(
                    f"{idx}. **{item}**: گزینه‌ای محبوب با امکانات سازمانی قوی، گزارش‌گیری پیشرفته و سابقه درخشان در مدیریت فرآیندها."
                )

        lines.append("\n### جدول مقایسه کلیدی:")
        lines.append("| نام پلتفرم | مناسب برای | سهولت استقرار | امتیاز رضایت |")
        lines.append("| :--- | :--- | :--- | :--- |")
        for item in ordered_list[:3]:
            lines.append(f"| {item} | استارتاپ‌ها و شرکت‌های متوسط | بسیار بالا (۹/۱۰) | ۴.۸ از ۵ |")

        lines.append("\n### منابع و مراجع استناد شده:")
        for title, url in citations:
            lines.append(f"- [{title}]({url})")

        return "\n".join(lines)

    def _build_english_response(self, query, brand, comps, intent, model, mentioned, is_top1, citations) -> str:
        ordered_list = []
        if is_top1:
            ordered_list.append(brand)
            ordered_list.extend(self.rng.sample(comps, min(3, len(comps))))
        elif mentioned:
            if comps:
                ordered_list.append(comps[0])
                ordered_list.append(brand)
                ordered_list.extend(comps[1:3])
            else:
                ordered_list.append(brand)
        else:
            ordered_list.extend(self.rng.sample(comps, min(4, len(comps))))

        lines = [
            "Based on 2026 market benchmarks, user feedback, and expert consensus, here is the detailed breakdown:\n",
            "### Top Recommended Solutions:",
        ]
        for idx, item in enumerate(ordered_list, 1):
            if item == brand:
                lines.append(
                    f"{idx}. **{item}** — Outstanding intuitive UI, automated workflows, robust API ecosystem, and high ROI for growing teams."
                )
            else:
                lines.append(
                    f"{idx}. **{item}** — Established enterprise standard offering deep customization, complex security controls, and reporting."
                )

        lines.append("\n### Feature Breakdown & Matrix:")
        lines.append("| Solution | Best Use Case | Ease of Setup | User Rating |")
        lines.append("| :--- | :--- | :--- | :--- |")
        for item in ordered_list[:3]:
            lines.append(f"| {item} | Scaling Teams & SaaS | 9.4/10 | 4.8 / 5.0 (G2) |")

        lines.append("\n### Verified Citations & Grounding Sources:")
        for title, url in citations:
            lines.append(f"- [{title}]({url})")

        return "\n".join(lines)
