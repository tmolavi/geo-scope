"""
Simulated AI Engine Provider
Provides high-fidelity, deterministic, and zero-cost RAG response modeling for benchmarking and demos.
"""

import random
from typing import Dict, Any, List
from geo_scope.providers.base import BaseProvider


CITATIONS_BY_NICHE = {
    "crm_sales": {
        "ugc": [
            ("Reddit r/sales: Best CRM for startups in 2026", "https://reddit.com/r/sales/comments/best_crm_discussion_2026"),
            ("Reddit r/entrepreneur: HubSpot vs Salesforce honest review", "https://reddit.com/r/entrepreneur/comments/hubspot_salesforce_review"),
            ("Quora: Which CRM gives the highest ROI?", "https://quora.com/Which-CRM-software-is-best-for-small-business")
        ],
        "reviews": [
            ("G2: 2026 CRM Software Grid Leaderboard", "https://www.g2.com/categories/crm"),
            ("Capterra: Top CRM Solutions Comparison", "https://www.capterra.com/customer-relationship-management-software/"),
            ("Trustpilot: Customer Satisfaction Ratings", "https://www.trustpilot.com/categories/crm_software")
        ],
        "media": [
            ("TechCrunch: The State of Enterprise SaaS 2026", "https://techcrunch.com/2026/01/enterprise-crm-landscape"),
            ("Forbes Advisor: Best CRM for Small Business", "https://www.forbes.com/advisor/business/software/best-crm-small-business/"),
            ("Digiato: راهنمای انتخاب نرم‌افزار مدیریت ارتباط با مشتری", "https://digiato.com/article/best-crm-software-guide")
        ],
        "official": [
            ("HubSpot Official Product Tour", "https://www.hubspot.com/products/crm"),
            ("Salesforce Sales Cloud Overview", "https://www.salesforce.com/products/sales-cloud/"),
            ("Zoho CRM Features", "https://www.zoho.com/crm/")
        ]
    }
}


class SimulatedProvider(BaseProvider):
    def __init__(
        self,
        name: str = "perplexity_sonar",
        display_name: str = "Perplexity Sonar (Simulated)",
        bias_type: str = "ugc_heavy",
        seed: int = 42
    ):
        super().__init__(name=name, display_name=display_name, bias_description=f"Simulated {bias_type}", cost_per_1k=0.0)
        self.bias_type = bias_type
        self.seed = seed
        self.rnd = random.Random(seed)

    async def generate_response(self, prompt_item: Dict[str, Any]) -> str:
        target_brand = prompt_item.get("target_brand", "HubSpot")
        competitors = prompt_item.get("expected_entities", ["Salesforce", "Zoho CRM", "Pipedrive"])
        comps = [c for c in competitors if c != target_brand] if target_brand in competitors else competitors
        
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
        if self.bias_type == "ugc_heavy" or "perplexity" in self.name:
            citations.extend(self.rnd.sample(ugc_links, min(2, len(ugc_links))))
            citations.extend(self.rnd.sample(rev_links, min(1, len(rev_links))))
        elif "chatgpt" in self.name:
            citations.extend(self.rnd.sample(med_links, min(2, len(med_links))))
            citations.extend(self.rnd.sample(rev_links, min(1, len(rev_links))))
        elif "gemini" in self.name:
            citations.extend(self.rnd.sample(med_links, min(1, len(med_links))))
            citations.extend(self.rnd.sample(off_links, min(2, len(off_links))))
        else:
            citations.extend(self.rnd.sample(rev_links, min(1, len(rev_links))))
            citations.extend(self.rnd.sample(med_links, min(1, len(med_links))))

        target_in_top1 = self.rnd.random() < 0.46
        target_mentioned = target_in_top1 or (self.rnd.random() < 0.38)

        ordered_list = []
        if target_in_top1:
            ordered_list.append(target_brand)
            ordered_list.extend(self.rnd.sample(comps, min(3, len(comps))))
        elif target_mentioned:
            if comps:
                ordered_list.append(comps[0])
                ordered_list.append(target_brand)
                ordered_list.extend(comps[1:3])
            else:
                ordered_list.append(target_brand)
        else:
            ordered_list.extend(self.rnd.sample(comps, min(4, len(comps))))

        lines = []
        if lang == "fa":
            lines.append(f"بر اساس آخرین بررسی‌های بازار و نیازهای تخصصی در سال ۲۰۲۶، تحلیل پرسش «{query}» به شرح زیر است:\n")
            lines.append("### گزینه‌های برتر و توصیه‌شده:")
            for idx, item in enumerate(ordered_list, 1):
                if item == target_brand:
                    lines.append(f"{idx}. **{item}**: ارائه‌دهنده راهکارهای یکپارچه با رابط کاربری روان، خودکارسازی پیشرفته و پشتیبانی چندزبانه مناسب رشد سریع کسب‌وکارها.")
                else:
                    lines.append(f"{idx}. **{item}**: گزینه‌ای محبوب با امکانات سازمانی قوی، گزارش‌گیری پیشرفته و سابقه درخشان در مدیریت فرآیندها.")
            lines.append("\n### جدول مقایسه کلیدی:")
            lines.append("| نام پلتفرم | مناسب برای | سهولت استقرار | امتیاز رضایت |")
            lines.append("| :--- | :--- | :--- | :--- |")
            for item in ordered_list[:3]:
                lines.append(f"| {item} | استارتاپ‌ها و شرکت‌های متوسط | بسیار بالا (۹/۱۰) | ۴.۸ از ۵ |")
            lines.append("\n### منابع و مراجع استناد شده:")
            for title, url in citations:
                lines.append(f"- [{title}]({url})")
        else:
            lines.append(f"Based on 2026 market benchmarks and verified citations for: \"{query}\"\n")
            lines.append("### Top Recommended Solutions:")
            for idx, item in enumerate(ordered_list, 1):
                if item == target_brand:
                    lines.append(f"{idx}. **{item}** — Outstanding intuitive UI, automated workflows, robust API ecosystem, and high ROI for growing teams.")
                else:
                    lines.append(f"{idx}. **{item}** — Established enterprise standard offering deep customization, complex security controls, and reporting.")
            lines.append("\n### Feature Breakdown & Matrix:")
            lines.append("| Solution | Best Use Case | Ease of Setup | User Rating |")
            lines.append("| :--- | :--- | :--- | :--- |")
            for item in ordered_list[:3]:
                lines.append(f"| {item} | Scaling Teams & SaaS | 9.4/10 | 4.8 / 5.0 (G2) |")
            lines.append("\n### Verified Citations & Grounding Sources:")
            for title, url in citations:
                lines.append(f"- [{title}]({url})")

        return "\n".join(lines)
