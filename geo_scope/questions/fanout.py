"""
Query Fan-Out Decomposer for AnswerPath GEO.
Models Gemini 4 Hydrogen and advanced AI Search subtopic decomposition,
generating parallel sub-queries to evaluate multi-hop retrieval and
citation survival across diverse web surfaces.

(c) 2026 Taqi Molavi — https://molavi.pro — MIT License
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SubQueryItem:
    """Represents an atomic sub-query generated during Query Fan-Out."""
    sub_query_id: str
    sub_query_text: str
    subtopic: str
    target_intent: str
    priority: int = 1
    expected_source_types: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FanOutDecompositionResult:
    """The complete result of decomposing a complex parent query into subtopics."""
    parent_prompt_id: str
    original_prompt: str
    language: str
    primary_intent: str
    subtopics: List[str]
    sub_queries: List[SubQueryItem]
    decomposition_strategy: str = "gemini_hydrogen_fanout_v1"

    @property
    def fan_out_ratio(self) -> float:
        return float(len(self.sub_queries))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "parent_prompt_id": self.parent_prompt_id,
            "original_prompt": self.original_prompt,
            "language": self.language,
            "primary_intent": self.primary_intent,
            "subtopics": self.subtopics,
            "fan_out_ratio": self.fan_out_ratio,
            "decomposition_strategy": self.decomposition_strategy,
            "sub_queries": [sq.to_dict() for sq in self.sub_queries],
        }


class QueryFanOutDecomposer:
    """
    Decomposes multi-faceted user prompts into structured sub-query graphs
    mirroring modern search engines' parallel retrieval mechanisms.
    """

    SUBTOPIC_TEMPLATES_EN = {
        "comparative": [
            ("architecture_features", "core feature comparison and technical architecture of {entity}", "technical", ["official_docs"]),
            ("pricing_licensing", "pricing tiers, total cost of ownership, and licensing for {entity}", "commercial", ["official_pricing", "review_aggregators"]),
            ("user_reviews_sentiment", "independent customer reviews, pros and cons of {entity} in 2026", "trust", ["review_aggregators", "ugc_community"]),
            ("integration_ecosystem", "API integration and ecosystem compatibility for {entity}", "technical", ["developer_docs", "community_forums"]),
        ],
        "commercial_direct": [
            ("pricing_cost", "current pricing models, discounts, and packages for {entity}", "commercial", ["official_pricing"]),
            ("feature_checklist", "key product capabilities and enterprise features of {entity}", "technical", ["official_docs"]),
            ("alternative_options", "top competitive alternatives to {entity} in 2026", "comparative", ["review_aggregators", "niche_publications"]),
            ("customer_case_studies", "customer satisfaction and enterprise implementation case studies for {entity}", "trust", ["case_studies", "tier1_media"]),
        ],
        "informational": [
            ("prerequisites_basics", "fundamental concepts and prerequisites for {entity}", "informational", ["educational", "official_docs"]),
            ("best_practices", "recommended best practices and architectural patterns for {entity}", "technical", ["documentation", "expert_blogs"]),
            ("common_pitfalls", "common mistakes and troubleshooting guide for {entity}", "technical", ["ugc_community", "forums"]),
            ("future_trends_2026", "2026 trends and latest developments regarding {entity}", "informational", ["tier1_media", "research_papers"]),
        ],
    }

    SUBTOPIC_TEMPLATES_FA = {
        "comparative": [
            ("architecture_features", "مقایسه مشخصات فنی و قابلیت‌های اصلی {entity}", "technical", ["official_docs"]),
            ("pricing_licensing", "قیمت، تعرفه و شرایط خرید {entity} در سال ۲۰۲۶", "commercial", ["official_pricing"]),
            ("user_reviews_sentiment", "نظرات کاربران، نقاط قوت و ضعف {entity}", "trust", ["review_aggregators", "ugc_community"]),
            ("integration_ecosystem", "سازگاری، پشتیبانی و نحوه راه‌اندازی {entity}", "technical", ["developer_docs"]),
        ],
        "commercial_direct": [
            ("pricing_cost", "قیمت روز، تعرفه و پکیج‌های {entity}", "commercial", ["official_pricing"]),
            ("feature_checklist", "امکانات اختصاصی و مزایای رقابتی {entity}", "technical", ["official_docs"]),
            ("alternative_options", "بهترین گزینه‌ها و جایگزین‌های {entity}", "comparative", ["review_aggregators"]),
            ("customer_case_studies", "تجربه مشتریان و رضایت از خدمات {entity}", "trust", ["ugc_community"]),
        ],
        "informational": [
            ("prerequisites_basics", "مفاهیم پایه و پیش‌نیازهای {entity}", "informational", ["educational"]),
            ("best_practices", "اصول و استانداردهای کلیدی {entity}", "technical", ["documentation"]),
            ("common_pitfalls", "چالش‌ها و اشتباهات رایج در {entity}", "technical", ["forums"]),
            ("future_trends_2026", "آخرین تغییرات و وضعیت {entity} در سال ۲۰۲۶", "informational", ["tier1_media"]),
        ],
    }

    def __init__(self, default_strategy: str = "gemini_hydrogen_fanout_v1"):
        self.strategy = default_strategy

    def detect_intent(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        if any(w in prompt_lower for w in ["vs", "versus", "compare", "مقایسه", "فرق", "تفاوت", "یا"]):
            return "comparative"
        if any(w in prompt_lower for w in ["price", "buy", "cost", "قیمت", "خرید", "تعرفه", "پکیج", "سفارش", "best", "بهترین"]):
            return "commercial_direct"
        return "informational"

    def detect_language(self, prompt: str) -> str:
        # Detect Persian / Arabic script
        if re.search(r"[\u0600-\u06FF]", prompt):
            return "fa"
        return "en"

    def extract_core_entity(self, prompt: str) -> str:
        """Extracts cleaned subject matter or entity name from prompt."""
        cleaned = re.sub(r"^(what is|how to|best|compare|مقایسه|بهترین|قیمت|چیست|چگونه)\s+", "", prompt, flags=re.IGNORECASE)
        cleaned = re.sub(r"[?!.,،؟]", "", cleaned).strip()
        return cleaned if cleaned else prompt.strip()

    def decompose(
        self,
        prompt: str,
        parent_prompt_id: Optional[str] = None,
        language: Optional[str] = None,
        max_subqueries: int = 4,
    ) -> FanOutDecompositionResult:
        """
        Decomposes a given prompt into a sub-query graph.
        """
        p_id = parent_prompt_id or f"fo_{abs(hash(prompt)) % 10000000}"
        detected_lang = language or self.detect_language(prompt)
        intent = self.detect_intent(prompt)
        entity = self.extract_core_entity(prompt)

        templates_pool = self.SUBTOPIC_TEMPLATES_FA if detected_lang == "fa" else self.SUBTOPIC_TEMPLATES_EN
        templates = templates_pool.get(intent, templates_pool["informational"])

        sub_queries: List[SubQueryItem] = []
        subtopics: List[str] = []

        for idx, (subtopic_key, tmpl, target_intent, source_types) in enumerate(templates[:max_subqueries], start=1):
            sq_text = tmpl.format(entity=entity)
            sq_id = f"{p_id}_sq{idx}"
            subtopics.append(subtopic_key)
            sub_queries.append(
                SubQueryItem(
                    sub_query_id=sq_id,
                    sub_query_text=sq_text,
                    subtopic=subtopic_key,
                    target_intent=target_intent,
                    priority=idx,
                    expected_source_types=source_types,
                )
            )

        return FanOutDecompositionResult(
            parent_prompt_id=p_id,
            original_prompt=prompt,
            language=detected_lang,
            primary_intent=intent,
            subtopics=subtopics,
            sub_queries=sub_queries,
            decomposition_strategy=self.strategy,
        )
