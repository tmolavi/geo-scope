"""
Algorithmic Reverse-Engineering & Statistical Attribution Module
Analyzes parsed AI outputs to compute Share of Model, Citation Distributions, and Ranking Factor Weights.
"""

from typing import List, Dict, Any
from collections import defaultdict, Counter
import numpy as np
import hashlib
import json


class AlgoAnalyzer:
    def __init__(self, parsed_records: List[Dict[str, Any]], target_brand: str, competitors: List[str]):
        self.records = parsed_records
        self.target_brand = target_brand
        self.competitors = competitors
        self.all_brands = [target_brand] + [c for c in competitors if c != target_brand]

    def compute_full_analysis(self) -> Dict[str, Any]:
        """
        Computes the complete reverse-engineered algorithmic intelligence report.
        """
        sov_data = self._compute_share_of_voice()
        citation_data = self._compute_citation_analytics()
        algo_weights = self._reverse_engineer_factor_weights()
        intent_breakdown = self._compute_intent_sensitivity()
        competitor_matrix = self._compute_competitor_matrix()
        gaps_and_opportunities = self._generate_strategic_gaps(sov_data, citation_data, algo_weights)

        modes = sorted({r.get("provenance", {}).get("execution_mode", "unknown") for r in self.records})
        return {
            "summary": {
                "experiment_signature": hashlib.sha256(
                    json.dumps(
                        sorted(
                            {
                                (
                                    r.get("query_text", ""),
                                    r["model"],
                                    r.get("provenance", {}).get("model_id", "unknown"),
                                )
                                for r in self.records
                            }
                        ),
                        ensure_ascii=False,
                    ).encode()
                ).hexdigest(),
                "execution_mode": modes[0] if len(modes) == 1 else "mixed",
                "measurement_scope": "Observed responses for this prompt set; no causal ranking-factor inference",
                "provider_provenance": {r["model"]: r.get("provenance", {}) for r in self.records},
                "total_queries_tested": len(set(r["query_id"] for r in self.records)),
                "total_ai_executions": len(self.records),
                "target_brand": self.target_brand,
                "competitors": self.competitors,
                "overall_sov": sov_data["overall_target_sov"],
                "overall_top1_rate": sov_data["overall_target_top1_rate"],
                "best_performing_model": sov_data["best_model"],
                "weakest_performing_model": sov_data["weakest_model"],
            },
            "share_of_model": sov_data,
            "citation_analytics": citation_data,
            "algorithmic_factors": algo_weights,
            "intent_sensitivity": intent_breakdown,
            "competitor_matrix": competitor_matrix,
            "strategic_gaps": gaps_and_opportunities,
        }

    def _compute_share_of_voice(self) -> Dict[str, Any]:
        models = sorted(list(set(r["model"] for r in self.records)))
        by_model = {}

        total_target_mentions = 0
        total_target_top1 = 0
        total_records = len(self.records)

        for model in models:
            m_records = [r for r in self.records if r["model"] == model]
            n = len(m_records) or 1

            target_mentions = sum(1 for r in m_records if r["target_mentioned"])
            target_top1 = sum(1 for r in m_records if r["target_is_top_1"])

            # Rank average (for queries where target was mentioned)
            ranks = [r["target_rank"] for r in m_records if r["target_mentioned"] and (r["target_rank"] or 0) > 0]
            avg_rank = float(np.mean(ranks)) if ranks else None

            # Sentiment breakdown
            sentiments = Counter(r["target_sentiment"] for r in m_records if r["target_mentioned"])

            by_model[model] = {
                "total_queries": n,
                "mention_count": target_mentions,
                "mention_rate_pct": round((target_mentions / n) * 100, 1),
                "top1_count": target_top1,
                "top1_rate_pct": round((target_top1 / n) * 100, 1),
                "avg_rank": round(avg_rank, 2) if avg_rank is not None else None,
                "rank_known_count": len(ranks),
                "rank_unknown_count": target_mentions - len(ranks),
                "sentiment_dist": dict(sentiments),
            }
            total_target_mentions += target_mentions
            total_target_top1 += target_top1

        overall_sov = round((total_target_mentions / total_records) * 100, 1) if total_records else 0
        overall_top1 = round((total_target_top1 / total_records) * 100, 1) if total_records else 0

        # Best and weakest model
        best_m = max(by_model.keys(), key=lambda m: by_model[m]["mention_rate_pct"]) if by_model else "N/A"
        weakest_m = min(by_model.keys(), key=lambda m: by_model[m]["mention_rate_pct"]) if by_model else "N/A"

        return {
            "by_model": by_model,
            "overall_target_sov": overall_sov,
            "overall_target_top1_rate": overall_top1,
            "best_model": best_m,
            "weakest_model": weakest_m,
        }

    def _compute_citation_analytics(self) -> Dict[str, Any]:
        all_citations = []
        domain_counts = Counter()
        category_counts = Counter()
        model_citation_dist = defaultdict(lambda: Counter())

        for r in self.records:
            model = r["model"]
            for cite in r.get("citations", []):
                domain = cite.get("domain", "other")
                category = cite.get("category", "other_web")
                domain_counts[domain] += 1
                category_counts[category] += 1
                model_citation_dist[model][category] += 1
                all_citations.append(cite)

        total_citations = sum(category_counts.values()) or 1
        cat_percentages = {k: round((v / total_citations) * 100, 1) for k, v in category_counts.items()}

        top_domains = [{"domain": dom, "count": cnt} for dom, cnt in domain_counts.most_common(12)]

        return {
            "total_citations_analyzed": len(all_citations),
            "category_distribution": dict(category_counts),
            "category_percentages": cat_percentages,
            "top_cited_domains": top_domains,
            "model_citation_breakdown": {m: dict(c) for m, c in model_citation_dist.items()},
        }

    def _reverse_engineer_factor_weights(self) -> Dict[str, Any]:
        """
        Reverse engineers the estimated weight of each ranking vector per AI model.
        Research priors for hypothesis design; not fitted from these response records.
        """
        factor_definitions = {
            "ugc_community": {
                "name_fa": "حضور در ردیت و فروم‌های تخصصی (UGC)",
                "name_en": "Reddit & Community UGC Mentions",
                "description_fa": "میزان بحث و نظرات واقعی کاربران در ردیت، کورا و انجمن‌ها",
                "description_en": "Authentic discussion density on Reddit, Quora, and forums",
            },
            "review_aggregators": {
                "name_fa": "رهبری در سایت‌های بررسی (G2 / Capterra)",
                "name_en": "Review Site Ratings & Grid Rank (G2/Capterra)",
                "description_fa": "تعداد بررسی‌ها و امتیاز بالا در پایگاه‌های تخصصی مقایسه نرم‌افزار",
                "description_en": "High volume of verified 4.5+ star reviews on review aggregators",
            },
            "tier1_pr_media": {
                "name_fa": "پوشش رسانه‌ای تراز اول (PR & Media)",
                "name_en": "Tier-1 Editorial PR & News Media",
                "description_fa": "مقالات و نام بردن در مجلات معتبر مانند فوربز، تک‌کرانچ، زومیت و دیجیاتو",
                "description_en": "Features and mentions in high-DR authoritative publications",
            },
            "knowledge_graph": {
                "name_fa": "موجودیت رسمی در گراف دانش (Wikipedia / Schema)",
                "name_en": "Knowledge Graph & Entity Grounding (Wikipedia)",
                "description_fa": "وجود صفحه رسمی در ویکی‌پدیا، ویکی‌دیتا و ساختار داده سازمان‌یافته",
                "description_en": "Verified entity status in Wikidata, Wikipedia, and organization schema",
            },
            "content_structure": {
                "name_fa": "ساختاردهی محتوا (جداول مقایسه، آمار و بولت)",
                "name_en": "Structured Content (Comparison Tables & Stats)",
                "description_fa": "استفاده از آمار دقیق، جداول شفاف و پاسخ مستقیم در ابتدای صفحه",
                "description_en": "Direct answers, quantitative statistics, and Markdown/HTML tables",
            },
            "freshness_recency": {
                "name_fa": "تازگی و به‌روزرسانی مداوم (Freshness Index)",
                "name_en": "Information Freshness & Recency Bias",
                "description_fa": "مطالب منتشر شده در سال جاری و به‌روزرسانی مداوم صفحات قیمت‌گذاری",
                "description_en": "Recent publications, active changelogs, and 2026 updated content",
            },
        }

        # Fixed prior vectors, not observed algorithm weights
        weights_by_model = {
            "perplexity_sonar": {
                "ugc_community": 38,
                "review_aggregators": 24,
                "tier1_pr_media": 14,
                "knowledge_graph": 8,
                "content_structure": 10,
                "freshness_recency": 6,
            },
            "chatgpt_search": {
                "ugc_community": 16,
                "review_aggregators": 26,
                "tier1_pr_media": 28,
                "knowledge_graph": 12,
                "content_structure": 12,
                "freshness_recency": 6,
            },
            "gemini_grounding": {
                "ugc_community": 14,
                "review_aggregators": 20,
                "tier1_pr_media": 24,
                "knowledge_graph": 22,
                "content_structure": 8,
                "freshness_recency": 12,
            },
            "claude_3_7": {
                "ugc_community": 18,
                "review_aggregators": 22,
                "tier1_pr_media": 22,
                "knowledge_graph": 18,
                "content_structure": 14,
                "freshness_recency": 6,
            },
        }

        # Global average weights
        avg_weights = {}
        for factor in factor_definitions.keys():
            vals = [weights_by_model[m][factor] for m in weights_by_model]
            avg_weights[factor] = round(float(np.mean(vals)), 1)

        return {
            "factor_definitions": factor_definitions,
            "status": "hypothesis_prior_not_fitted",
            "weights_by_model": weights_by_model,
            "global_average_weights": avg_weights,
        }

    def _compute_intent_sensitivity(self) -> Dict[str, Any]:
        intents = sorted(list(set(r["intent"] for r in self.records)))
        intent_stats = {}

        for intent in intents:
            i_records = [r for r in self.records if r["intent"] == intent]
            n = len(i_records) or 1

            target_mentions = sum(1 for r in i_records if r["target_mentioned"])
            target_top1 = sum(1 for r in i_records if r["target_is_top_1"])

            intent_stats[intent] = {
                "query_count": n,
                "mention_rate_pct": round((target_mentions / n) * 100, 1),
                "top1_rate_pct": round((target_top1 / n) * 100, 1),
            }

        return intent_stats

    def _compute_competitor_matrix(self) -> List[Dict[str, Any]]:
        competitor_stats = defaultdict(lambda: {"mentions": 0, "top1": 0, "positive": 0})
        total_queries = len(self.records) or 1

        for r in self.records:
            brand_stats = r.get("all_brands_stats", {})
            for brand, stats in brand_stats.items():
                if stats.get("mentioned", False):
                    competitor_stats[brand]["mentions"] += 1
                if stats.get("is_top_1", False):
                    competitor_stats[brand]["top1"] += 1
                if stats.get("sentiment") == "positive":
                    competitor_stats[brand]["positive"] += 1

        total_brand_mentions = sum(st["mentions"] for st in competitor_stats.values())
        matrix = []
        for brand in self.all_brands:
            st = competitor_stats[brand]
            mention_rate = round((st["mentions"] / total_queries) * 100, 1)
            top1_rate = round((st["top1"] / total_queries) * 100, 1)
            matrix.append(
                {
                    "brand": brand,
                    "is_target": brand == self.target_brand,
                    "share_of_voice_pct": (
                        round(st["mentions"] / total_brand_mentions * 100, 1) if total_brand_mentions else 0.0
                    ),
                    "total_mentions": st["mentions"],
                    "mention_rate_pct": mention_rate,
                    "top1_count": st["top1"],
                    "top1_rate_pct": top1_rate,
                    "positive_sentiment_count": st["positive"],
                    "sentiment_score": round((st["positive"] / (st["mentions"] or 1)) * 100, 1),
                }
            )

        # Sort by mention rate descending
        matrix.sort(key=lambda x: x["mention_rate_pct"], reverse=True)
        return matrix

    def _generate_strategic_gaps(
        self, sov_data: Dict[str, Any], citation_data: Dict[str, Any], algo_weights: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        return [
            {
                "title_en": "Validate visibility opportunities with controlled follow-up experiments",
                "title_fa": "اعتبارسنجی فرصت‌های دیده‌شدن با آزمایش‌های کنترل‌شده",
                "priority": "RESEARCH",
                "finding_en": "Mention and citation distributions describe these responses; they do not establish ranking causes.",
                "finding_fa": "توزیع اشاره‌ها و منابع، پاسخ‌های این آزمایش را توصیف می‌کند؛ علت رتبه‌بندی را اثبات نمی‌کند.",
                "action_en": "Review raw responses, label ambiguous ranks, and compare matched prompt sets before changing strategy.",
                "action_fa": "پاسخ‌های خام و رتبه‌های مبهم را بررسی کنید و مجموعه پرسش‌های یکسان را مقایسه کنید.",
            }
        ]
