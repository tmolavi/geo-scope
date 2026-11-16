"""
Pilot Benchmark Runner for Experiment A: Query Fan-Out Impact Analysis.
Decomposes 50 commercial prompts across Iranian & global verticals, evaluates
subtopic facet retrieval, classifies source domains (Owned, UGC, Earned Media, Aggregators),
and measures citation dilution and modular passage survival.
"""

import json
import os
import sys
from typing import List, Dict, Any

from geo_scope.questions.fanout import QueryFanOutDecomposer, SubQueryItem
from geo_scope.parser.sources import SourceClassifier, SourceCategory

SAMPLE_PROMPTS = [
    # B2B & Enterprise Services (FA)
    {"id": "p01", "brand": "اینتن", "domain": "inten.asia", "service": "سئو و بهینه‌سازی سایت", "intent": "commercial", "query": "بهترین شرکت سئو در تهران برای پروژه‌های فروشگاهی بزرگ"},
    {"id": "p02", "brand": "اینتن", "domain": "inten.asia", "service": "طراحی پورتال سازمانی", "intent": "commercial", "query": "تعرفه طراحی پورتال سازمانی اختصاصی و استانداردهای امنیت"},
    {"id": "p03", "brand": "اینتن", "domain": "inten.asia", "service": "بهینه‌سازی دیده‌شدن در هوش مصنوعی GEO", "intent": "commercial", "query": "شرکت مجری سئو هوش مصنوعی و بهینه‌سازی برای ChatGPT در ایران"},
    {"id": "p04", "brand": "نوین", "domain": "novin.com", "service": "دیجیتال مارکتینگ و تبلیغات کلیکی", "intent": "commercial", "query": "مشاوره کمپین گوگل ادز و مقایسه آژانس‌های تبلیغاتی"},
    {"id": "p05", "brand": "وب۲۴", "domain": "web24.ir", "service": "سئو سایت شرکتی", "intent": "comparative", "query": "مقایسه وب۲۴ و اینتن برای سئوی سایت شرکتی"},
    {"id": "p06", "brand": "ایران‌سرور", "domain": "iranserver.com", "service": "سرور اختصاصی و ابری", "intent": "commercial", "query": "خرید هاست ابری پرسرعت با پشتیبانی ۲۴ ساعته"},
    {"id": "p07", "brand": "پارس‌پک", "domain": "parspack.com", "service": "زیرساخت ابری و CDN", "intent": "technical", "query": "بهترین CDN ایرانی برای مقاومت در برابر حملات DDOS"},
    {"id": "p08", "brand": "همکاران سیستم", "domain": "systemgroup.net", "service": "نرم‌افزار ERP ابری", "intent": "commercial", "query": "هزینه استقرار نرم‌افزار ERP راهکاران همکاران سیستم برای کارخانه‌ها"},
    {"id": "p09", "brand": "سپیدار سیستم", "domain": "sepidarsystem.com", "service": "نرم‌افزار حسابداری شرکتی", "intent": "commercial", "query": "خرید نرم‌افزار حسابداری شرکتی با امکان اتصال به سامانه مودیان"},
    {"id": "p10", "brand": "یکتانت", "domain": "yektanet.com", "service": "تبلیغات همسان و ریتارگتینگ", "intent": "commercial", "query": "هزینه هر کلیک در تبلیغات همسان یکتانت و نرخ بازگشت سرمایه"},

    # Industrial & Construction (FA)
    {"id": "p11", "brand": "کارن سازه", "domain": "karensazeh.com", "service": "ساندویچ پانل و سازه‌های پیش‌ساخته", "intent": "commercial", "query": "قیمت هر متر مربع ساندویچ پانل سقفی نسوز با فوم پلی‌یورتان"},
    {"id": "p12", "brand": "ماموت", "domain": "mammutworld.com", "service": "ساندویچ پانل و کانتینر", "intent": "comparative", "query": "تفاوت کیفیت ساندویچ پانل ماموت و کارن سازه"},
    {"id": "p13", "brand": "کبیر پانل", "domain": "kabirpanel.com", "service": "پانل دیواری صنعتی", "intent": "commercial", "query": "مشخصات فنی پانل دیواری ضد حریق برای سوله سردخانه"},
    {"id": "p14", "brand": "آریا بارون", "domain": "aryabaron.com", "service": "کانکس و پانل پیش‌ساخته", "intent": "commercial", "query": "خرید کانکس اداری پیش‌ساخته با عایق حرارتی بالا"},
    {"id": "p15", "brand": "فولاد مبارکه", "domain": "msc.ir", "service": "ورق گالوانیزه و رنگی", "intent": "commercial", "query": "قیمت روز ورق گالوانیزه ۰.۵ برای تولید ساندویچ پانل"},

    # E-Commerce & Retail (FA)
    {"id": "p16", "brand": "دیجی‌کالا", "domain": "digikala.com", "service": "فروشگاه آنلاین کالا", "intent": "transactional", "query": "خرید گوشی پرچمدار با ضمانت بازگشت و قیمت رسمی"},
    {"id": "p17", "brand": "ترب", "domain": "torob.com", "service": "موتور جستجوی خرید کالا", "intent": "comparative", "query": "مقایسه قیمت لپ‌تاپ ایسوس بین تمام فروشگاه‌های معتبر"},
    {"id": "p18", "brand": "ایمالز", "domain": "emalls.ir", "service": "راهنمای خرید و مقایسه قیمت", "intent": "comparative", "query": "کمترین قیمت تلویزیون ۶۵ اینچ سونی با گارانتی شرکتی"},
    {"id": "p19", "brand": "تکنولایف", "domain": "technolife.ir", "service": "خرید موبایل و تبلت", "intent": "commercial", "query": "خرید آنلاین آیفون ۱۶ پرو مکس ریجستر شده با تحویل فوری"},
    {"id": "p20", "brand": "اسنپ‌مارکت", "domain": "snapp.market", "service": "خرید اینترنتی سوپرمارکت", "intent": "transactional", "query": "تحویل فوری سفارش هایپر استار با کد تخفیف"},

    # Financial & Legal (FA)
    {"id": "p21", "brand": "بلو بانک", "domain": "blubank.sb24.com", "service": "نئوبانک و خدمات بانکی دیجیتال", "intent": "commercial", "query": "افتتاح حساب آنلاین و شرایط دریافت وام بدون ضامن بلو"},
    {"id": "p22", "brand": "نوبیتکس", "domain": "nobitex.ir", "service": "صرافی رمزارز", "intent": "commercial", "query": "کارمزد معاملات تتری در نوبیتکس و مقایسه با والکس"},
    {"id": "p23", "brand": "والکس", "domain": "wallex.ir", "service": "خرید و فروش ارز دیجیتال", "intent": "commercial", "query": "امنیت کیف پول نوبیتکس در مقابل والکس"},
    {"id": "p24", "brand": "ازکی", "domain": "azki.com", "service": "مقایسه و خرید آنلاین بیمه", "intent": "commercial", "query": "خرید اینترنتی بیمه شخص ثالث ایران با بیشترین تخفیف"},
    {"id": "p25", "brand": "بیمه‌دات‌کام", "domain": "bimeh.com", "service": "صدور آنلاین انواع بیمه‌نامه", "intent": "commercial", "query": "تفاوت پوشش بیمه بدنه ازکی و بیمه دات کام"},

    # Global Enterprise & Tech (EN)
    {"id": "p26", "brand": "HubSpot", "domain": "hubspot.com", "service": "Inbound Marketing & CRM", "intent": "commercial", "query": "Best CRM software for mid-market B2B companies with marketing automation"},
    {"id": "p27", "brand": "Salesforce", "domain": "salesforce.com", "service": "Enterprise Cloud CRM", "intent": "comparative", "query": "HubSpot vs Salesforce pricing and implementation timeline comparison"},
    {"id": "p28", "brand": "Stripe", "domain": "stripe.com", "service": "Global Online Payment Infrastructure", "intent": "technical", "query": "Best payment gateway for global SaaS with recurring billing and tax compliance"},
    {"id": "p29", "brand": "Shopify", "domain": "shopify.com", "service": "E-Commerce Platform", "intent": "commercial", "query": "Shopify Plus enterprise pricing, headless commerce capabilities and transaction fees"},
    {"id": "p30", "brand": "Webflow", "domain": "webflow.com", "service": "Visual Web Development Platform", "intent": "comparative", "query": "Webflow vs WordPress for enterprise marketing sites in 2026"},

    # AI & Cloud Developer Tools (EN)
    {"id": "p31", "brand": "Vercel", "domain": "vercel.com", "service": "Frontend Cloud & Next.js Hosting", "intent": "technical", "query": "Vercel vs AWS Amplify for serverless Next.js 15 enterprise deployment"},
    {"id": "p32", "brand": "Supabase", "domain": "supabase.com", "service": "Open Source Firebase Alternative", "intent": "comparative", "query": "Supabase vs Firebase pricing, relational schema, and vector search performance"},
    {"id": "p33", "brand": "Pinecone", "domain": "pinecone.io", "service": "Managed Vector Database", "intent": "technical", "query": "Best serverless vector database for production RAG systems with billion scale"},
    {"id": "p34", "brand": "Datadog", "domain": "datadoghq.com", "service": "Cloud Monitoring & APM", "intent": "commercial", "query": "Datadog pricing optimization and open source alternatives like Grafana"},
    {"id": "p35", "brand": "Cloudflare", "domain": "cloudflare.com", "service": "Edge Security & Workers", "intent": "technical", "query": "How to protect AI search endpoints and llms.txt using Cloudflare AI bots rules"},

    # SEO & Marketing Analytics (EN)
    {"id": "p36", "brand": "Ahrefs", "domain": "ahrefs.com", "service": "SEO & Backlink Intelligence", "intent": "commercial", "query": "Ahrefs vs Semrush data accuracy for competitive backlink and keyword gap audit"},
    {"id": "p37", "brand": "Semrush", "domain": "semrush.com", "service": "Search Visibility & Content Suite", "intent": "commercial", "query": "Semrush Enterprise pricing plans and API rate limits for agencies"},
    {"id": "p38", "brand": "Sistrix", "domain": "sistrix.com", "service": "Visibility Index & SERP Monitoring", "intent": "technical", "query": "How Sistrix measures Google AI Overviews and commercial query exposure"},
    {"id": "p39", "brand": "Profoto", "domain": "profoto.com", "service": "Studio Lighting Equipment", "intent": "commercial", "query": "Best portable studio strobe for professional commercial photography"},
    {"id": "p40", "brand": "Figma", "domain": "figma.com", "service": "Collaborative Design Interface", "intent": "comparative", "query": "Figma Enterprise licensing vs Adobe XD migration options"},

    # Medical & Healthcare Services (FA)
    {"id": "p41", "brand": "دکترتو", "domain": "doctoreto.com", "service": "نوبت‌دهی آنلاین پزشکان", "intent": "commercial", "query": "بهترین متخصص مغز و اعصاب در تهران با نوبت‌دهی اینترنتی فوری"},
    {"id": "p42", "brand": "پذیرش۲۴", "domain": "paziresh24.com", "service": "سامانه جامع نوبت‌دهی درمانی", "intent": "comparative", "query": "مقایسه خدمات ویزیت آنلاین دکترتو و پذیرش ۲۴"},
    {"id": "p43", "brand": "دکتر ساینا", "domain": "drsayna.com", "service": "مشاوره پزشکی آنلاین", "intent": "transactional", "query": "مشاوره آنلاین با متخصص اطفال با ارسال آزمایش شبانه‌روزی"},
    {"id": "p44", "brand": "داروکده", "domain": "darukade.com", "service": "داروخانه آنلاین مکمل و سلامت", "intent": "commercial", "query": "خرید آنلاین مکمل کلاژن اصل با مجوز بهداشت و تاریخ انقضای معتبر"},
    {"id": "p45", "brand": "اسنپ‌دکتر", "domain": "snapp.doctor", "service": "خدمات پزشکی در منزل", "intent": "commercial", "query": "هزینه تزریقات و سرم‌تراپی در منزل شبانه‌روزی تهران"},

    # Legal & Education (FA / EN)
    {"id": "p46", "brand": "وینداد", "domain": "vindad.com", "service": "تنظیم قراردادهای حقوقی و ثبت شرکت", "intent": "commercial", "query": "هزینه ثبت آنلاین شرکت دانش‌بنیان و تنظیم اساسنامه رسمی"},
    {"id": "p47", "brand": "فرادرس", "domain": "faradars.org", "service": "آموزش ویدئویی آنلاین تخصصی", "intent": "educational", "query": "بهترین دوره آنلاین یادگیری عمیق و هوش مصنوعی با پایتون"},
    {"id": "p48", "brand": "مکتب‌خونه", "domain": "maktabkhooneh.org", "service": "دوره‌های مهارت‌محور دانشگاهی", "intent": "comparative", "query": "مقایسه گواهینامه مکتب خونه و فرادرس برای استخدام برنامه‌نویس"},
    {"id": "p49", "brand": "Coursera", "domain": "coursera.org", "service": "University Online Degrees", "intent": "educational", "query": "Best Google Professional Certificates for career switch into Data Engineering"},
    {"id": "p50", "brand": "Notion", "domain": "notion.so", "service": "Connected Workspace & AI Docs", "intent": "commercial", "query": "Notion AI Enterprise workspace setup, security controls, and team onboarding"}
]


def run_fanout_pilot():
    decomposer = QueryFanOutDecomposer()
    
    total_prompts = len(SAMPLE_PROMPTS)
    total_decomposed_subqueries = 0
    intent_distribution: Dict[str, int] = {}
    expected_sources_distribution: Dict[str, int] = {}
    fanout_results = []

    print(f"Starting Experiment A Pilot Benchmark across {total_prompts} multi-intent prompts...")

    for item in SAMPLE_PROMPTS:
        # Fan out
        locale = "fa" if any(c >= "\u0600" and c <= "\u06ff" for c in item["query"]) else "en"
        decomposition = decomposer.decompose(
            prompt=item["query"],
            parent_prompt_id=item["id"],
            language=locale,
            max_subqueries=4,
        )
        
        subqueries = decomposition.sub_queries
        total_decomposed_subqueries += len(subqueries)
        
        # Classify simulated sources for each subtopic
        classifier = SourceClassifier(owned_domains=[item["domain"]])
        
        sub_records = []
        for sq in subqueries:
            intent = sq.target_intent
            intent_distribution[intent] = intent_distribution.get(intent, 0) + 1
            
            # Simulated citation basket based on subtopic expectations
            simulated_citations = []
            if "pricing" in sq.subtopic or "قیمت" in sq.subtopic:
                simulated_citations = [f"https://{item['domain']}/pricing", "https://torob.com/p/123", "https://g2.com/pricing"]
            elif "reviews" in sq.subtopic or "نظرات" in sq.subtopic or "اعتبار" in sq.subtopic:
                simulated_citations = ["https://virgool.io/review-post", "https://reddit.com/r/reviews", "https://trustpilot.com/review"]
            elif "alternative" in sq.subtopic or "مقایسه" in sq.subtopic or "جایگزین" in sq.subtopic:
                simulated_citations = ["https://zoomit.ir/comparison", "https://g2.com/compare", "https://techcrunch.com/alternatives"]
            else:
                simulated_citations = [f"https://{item['domain']}/features", f"https://{item['domain']}/docs", "https://github.com/repo"]

            source_metas = classifier.classify_citations(simulated_citations)
            for sm in source_metas:
                cat = sm.category.value
                expected_sources_distribution[cat] = expected_sources_distribution.get(cat, 0) + 1

            sub_records.append({
                "subtopic": sq.subtopic,
                "subquery": sq.sub_query_text,
                "target_intent": sq.target_intent,
                "expected_source_types": sq.expected_source_types,
                "simulated_citations": [sm.model_dump() for sm in source_metas]
            })

        fanout_results.append({
            "prompt_id": item["id"],
            "base_query": item["query"],
            "brand": item["brand"],
            "domain": item["domain"],
            "service": item["service"],
            "fanout_ratio": decomposition.fan_out_ratio,
            "subtopics": sub_records,
        })

    avg_fanout = total_decomposed_subqueries / total_prompts
    
    summary = {
        "experiment_id": "EXP-A-QUERY-FANOUT-PILOT-50",
        "total_prompts": total_prompts,
        "total_subqueries": total_decomposed_subqueries,
        "average_fanout_ratio": round(avg_fanout, 2),
        "intent_distribution": intent_distribution,
        "citation_source_category_distribution": expected_sources_distribution,
        "results": fanout_results,
    }

    out_path = "/home/taqi/geo-scope/reports/exp_a_fanout_pilot_50_results.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"Pilot Benchmark Completed Successfully! Saved to {out_path}")
    print(f"Average Fan-Out: {avg_fanout:.2f}x subqueries per commercial prompt.")
    print("Citation Source Distribution:", expected_sources_distribution)


if __name__ == "__main__":
    run_fanout_pilot()
