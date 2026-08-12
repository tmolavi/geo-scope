"""
Strategy Builder for Generative Engine Optimization (GEO)
Generates end-to-end actionable playbooks based on reverse-engineered algorithm findings.
"""

from typing import Dict, Any, List


def generate_geo_playbook(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a personalized step-by-step GEO implementation roadmap.
    """
    target = analysis["summary"]["target_brand"]
    sov = analysis["summary"]["overall_sov"]
    top1 = analysis["summary"]["overall_top1_rate"]
    
    pillars = [
        {
            "pillar_id": 1,
            "name_fa": "۱. معماری محتوای سازگار با هوش مصنوعی (AI-First Content Architecture)",
            "name_en": "1. AI-First On-Page Content Architecture",
            "impact_score": "95/100",
            "tactics": [
                {
                    "title_fa": "پاسخ مستقیم در ۳۰ کلمه اول (BLUF Method)",
                    "title_en": "Bottom Line Up Front (BLUF) in First 30 Words",
                    "desc_fa": "هوش مصنوعی‌ها پاراگراف اول صفحه را اسکن می‌کنند. بدون حاشیه‌روی در ابتدای هر صفحه دقیقا پاسخ سوال کاربر، قیمت و مزیت کلیدی را بنویسید.",
                    "desc_en": "LLMs extract executive summaries. State the direct answer, exact pricing, and key value proposition in the very first sentence."
                },
                {
                    "title_fa": "جداول مقایسه‌ای شفاف با فرمت Markdown/HTML",
                    "title_en": "Direct Markdown & HTML Comparison Tables",
                    "desc_fa": "جداول با ستون‌های واضح (امکانات، قیمت، مناسب برای چه کسی) به مدل‌های LLM کمک می‌کند در سوالات 'مقایسه X با Y' برند شما را در پاسخ جدول بگنجانند.",
                    "desc_en": "Include clear feature vs competitor tables. LLM parsers heavily prioritize table tokens for comparative synthesis."
                },
                {
                    "title_fa": "تزریق داده‌های آماری دقیق (Quantitative Citations)",
                    "title_en": "High-Density Statistical Assertions",
                    "desc_fa": "به جای عبارات کلی ('سرعت بسیار بالا')، از اعداد مشخص استفاده کنید ('افزایش ۴۳ درصدی سرعت پردازش در تست‌های بنچمارک'). هوش مصنوعی‌ها عاشق استناد به اعدادند.",
                    "desc_en": "Replace generic marketing claims with concrete metrics (e.g. '43% faster throughput'). LLMs favor stat-backed sentences."
                }
            ]
        },
        {
            "pillar_id": 2,
            "name_fa": "۲. نفوذ در منابع سنتز هوش مصنوعی (UGC & Reddit Strategy)",
            "name_en": "2. Community & UGC Signal Infiltration (Reddit/Quora)",
            "impact_score": "90/100",
            "tactics": [
                {
                    "title_fa": "پوشش تاپیک‌های پرتکرار در ساب‌ردیت‌های مرتبط",
                    "title_en": "Dominating Niche Subreddits & Quora Threads",
                    "desc_fa": "موتور Perplexity و ChatGPT به‌طور مستقیم پاسخ‌های ردیت با بیشترین Upvote را استخراج می‌کنند. ایجاد و پاسخ‌دهی به تاپیک‌های 'بهترین نرم‌افزار برای...' با نظرات کاربران واقعی.",
                    "desc_en": "Perplexity and ChatGPT Search index Reddit upvoted answers directly. Participate in relevant discussion threads with real-world case studies."
                },
                {
                    "title_fa": "حضور در انجمن‌های تخصصی ایرانی و جهانی (ویرگول، گیت‌هاب، مدیوم)",
                    "title_en": "Technical Forum Footprint (GitHub, Medium, StackOverflow)",
                    "desc_fa": "انتشار مقالات بررسی فنی و تجربیات واقعی مشتریان در پلتفرم‌های آزاد بدون تبلیغ اغراق‌آمیز.",
                    "desc_en": "Publish technical case studies on public open blogging platforms where search engines crawl for consensus."
                }
            ]
        },
        {
            "pillar_id": 3,
            "name_fa": "۳. تثبیت رتبه در پایگاه‌های بررسی شخص ثالث (Review Aggregators)",
            "name_en": "3. 3rd-Party Review Site Leadership (G2, Capterra, Trustpilot)",
            "impact_score": "88/100",
            "tactics": [
                {
                    "title_fa": "جمع‌آوری ۵۰+ نقد معتبر در G2 و Capterra",
                    "title_en": "Accumulating 50+ Verified Reviews on G2 / Capterra",
                    "desc_fa": "مدل‌های هوش مصنوعی لیست‌های رتبه‌بندی خود را از ماتریس G2 Grid Leader و Capterra Top 20 استخراج می‌کنند.",
                    "desc_en": "AI models pull ranking lists directly from G2 Grid Leader and Capterra Shortlists. Keep profile completeness at 100%."
                },
                {
                    "title_fa": "پاسخ‌دهی رسمی به نظرات منفی و شفافیت در قیمت‌گذاری",
                    "title_en": "Public Pricing Disclosure & Review Responses",
                    "desc_fa": "ابزارهایی که قیمت شفاف در دایرکتوری‌ها دارند، در سوالات بودجه‌محور هوش مصنوعی ۲ برابر بیشتر پیشنهاد می‌شوند.",
                    "desc_en": "Transparent pricing on review directories increases recommendation likelihood by 2x for budget-conscious prompts."
                }
            ]
        },
        {
            "pillar_id": 4,
            "name_fa": "۴. تزریق موجودیت در گراف دانش (Knowledge Graph & Entity Grounding)",
            "name_en": "4. Knowledge Graph & Brand Entity Authority",
            "impact_score": "85/100",
            "tactics": [
                {
                    "title_fa": "ایجاد و تکمیل آیتم Wikidata و صفحه Wikipedia",
                    "title_en": "Wikidata Entity & Wikipedia Page Creation",
                    "desc_fa": "مدل‌های گوگل جمینای و کلود از گراف دانش ویکی‌پدیا برای تشخیص این‌که آیا یک برند واقعا وجود دارد یا خیر استفاده می‌کنند.",
                    "desc_en": "Gemini and Claude verify brand legitimacy through Wikidata entities, founders, and authoritative knowledge bases."
                },
                {
                    "title_fa": "اسکیما مارک‌آپ کامل سازمان و محصول (Organization & SoftwareApplication Schema)",
                    "title_en": "Rich Structured Schema Data (JSON-LD)",
                    "desc_fa": "تزریق دقیق تگ‌های `sameAs` (پیوند به پروفایل‌های رسمی لینکدین، توییتر، گیت‌هاب) در ساختار JSON-LD وب‌سایت.",
                    "desc_en": "Use deep JSON-LD markup with `sameAs` properties linking to official corporate registries and social entities."
                }
            ]
        },
        {
            "pillar_id": 5,
            "name_fa": "۵. مانیتورینگ مستمر و چرخه تست ۱۰۰۰ سوال (Automated GEO Loop)",
            "name_en": "5. Continuous Monitoring & Automated 1000-Prompt Benchmark",
            "impact_score": "92/100",
            "tactics": [
                {
                    "title_fa": "اجرای ماهانه بنچمارک ۱۰۰۰ پرسش برای رهگیری سهم دیده‌شدن (SoM)",
                    "title_en": "Monthly 1,000 Prompt Automated Benchmark Runs",
                    "desc_fa": "الگوریتم‌های هوش مصنوعی هر هفته با داده‌های وب جدید به‌روزرسانی می‌شوند. اجرای مستمر بنچمارک کاهش رتبه را فورا هشدار می‌دهد.",
                    "desc_en": "AI indexes refresh continuously. Running automated 1,000 prompt audits every month catches visibility drops immediately."
                }
            ]
        }
    ]

    return {
        "target_brand": target,
        "current_sov": sov,
        "current_top1_rate": top1,
        "pillars": pillars
    }
