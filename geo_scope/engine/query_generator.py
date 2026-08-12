"""
Query Generator Module for GEO (Generative Engine Optimization) Reverse-Engineering
Generates up to 1000+ categorized, realistic user prompts across various intent dimensions.
"""

import random
from typing import List, Dict, Any

TEMPLATES_BY_INTENT = {
    "commercial_direct": {
        "fa": [
            "بهترین {topic} در سال {year} چیست؟",
            "کدام {topic} برای کسب‌وکارهای کوچک و استارتاپ‌ها مناسب‌تر است؟",
            "لیست ۵ تا از برترین {topic}ها با مقایسه قیمت و امکانات",
            "پیشنهاد شما برای یک {topic} قدرتمند و اقتصادی چیست؟",
            "اگر بخواهم بهترین {topic} بازار را انتخاب کنم سراغ کدام گزینه بروم؟",
            "رتبه‌بندی محبوب‌ترین ابزارهای {topic} بر اساس نظر کاربران",
            "کدام {topic} بیشترین امنیت و پایداری را دارد؟",
            "بهترین جایگزین‌های پیشرفته برای {topic} سنتی چیست؟",
            "برای یک تیم حرفه‌ای کدام {topic} بیشترین بازدهی را دارد؟",
            "معرفی بهترین {topic}های ایرانی و بین‌المللی با پشتیبانی عالی"
        ],
        "en": [
            "What is the best {topic} in {year}?",
            "Top 10 best {topic} solutions for startups and small business",
            "Which {topic} offers the best value for money and features?",
            "Ranking the most popular {topic} tools according to user feedback",
            "What is the most reliable and secure {topic} on the market today?",
            "Recommend the best {topic} for enterprise teams with high scalability",
            "Which {topic} is considered the industry leader right now?",
            "Best modern {topic} platforms with AI capabilities in {year}",
            "If I have to choose one {topic} for my company, which one should it be?",
            "Top rated {topic} alternatives with easy onboarding"
        ]
    },
    "comparative": {
        "fa": [
            "مقایسه کامل بین {entity_a} و {entity_b}، کدام یک بهتر است؟",
            "تفاوت‌های اصلی {entity_a} با سایر رقبای {topic} چیست؟",
            "آیا {entity_a} ارزش خرید دارد یا باید برم سراغ {entity_b}؟",
            "بررسی نقاط قوت و ضعف {entity_a} در مقایسه با {entity_b}",
            "کدام یک از ابزارهای {entity_a} یا {entity_b} پشتیبانی و رابط کاربری بهتری دارند؟",
            "اگر بودجه محدودی داشته باشم، {entity_a} بهتره یا {entity_b}؟",
            "جایگزین‌های برتر برای {entity_a} که امکانات مشابهی دارند کدامند؟",
            "چرا بعضی شرکت‌ها از {entity_a} به {entity_b} مهاجرت می‌کنند؟",
            "جدول مقایسه ویژگی‌های کلیدی {entity_a} و {entity_b}",
            "نظرات کاربران در مورد مزایا و معایب {entity_a} نسبت به رقبا"
        ],
        "en": [
            "Comprehensive comparison between {entity_a} vs {entity_b}: which is better?",
            "What are the main differences between {entity_a} and its competitors in {topic}?",
            "Is {entity_a} worth the price compared to {entity_b}?",
            "Pros and cons of using {entity_a} vs {entity_b} for team productivity",
            "Why are companies switching from {entity_a} to {entity_b}?",
            "Feature-by-feature breakdown of {entity_a} versus {entity_b}",
            "Top 5 best alternatives to {entity_a} that offer better pricing",
            "Which one has better customer satisfaction: {entity_a} or {entity_b}?",
            "{entity_a} vs {entity_b} vs {entity_c}: full benchmark review",
            "Real user experiences comparing {entity_a} with standard {topic} tools"
        ]
    },
    "problem_solving": {
        "fa": [
            "چگونه مشکل {problem} را با استفاده از یک {topic} حرفه‌ای حل کنیم؟",
            "راهنمای گام به گام انتخاب {topic} برای حل معضل {problem}",
            "چرا در فرآیند {problem} نیاز به استفاده از {topic} داریم؟",
            "بهترین استراتژی برای بهبود {problem} به کمک ابزارهای مدرن {topic}",
            "چطور بدون هزینه سنگین مشکل {problem} را با {topic} برطرف کنیم؟",
            "چه فاکتورهایی در انتخاب {topic} برای مدیریت {problem} حیاتی است؟",
            "اشتباهات رایج در پیاده‌سازی {topic} برای رفع {problem}",
            "تأثیر استفاده از {topic} بر سرعت و دقت حل {problem} چقدر است؟",
            "ابزارهای هوشمند {topic} چطور به خودکارسازی {problem} کمک می‌کنند؟",
            "تجارب شرکت‌های موفق در حل چالش {problem} به کمک {topic}"
        ],
        "en": [
            "How to effectively solve {problem} using modern {topic} solutions?",
            "Step-by-step guide to choosing the right {topic} to tackle {problem}",
            "Why is {problem} a major bottleneck and how can {topic} fix it?",
            "Best practices for streamlining {problem} with automated {topic} tools",
            "How much ROI can a company expect by solving {problem} with {topic}?",
            "Common mistakes when implementing a {topic} to resolve {problem}",
            "Which specific features of {topic} are essential for eliminating {problem}?",
            "Case study: how leading brands resolved {problem} using {topic}",
            "Cost-effective ways to manage {problem} with modern {topic} architectures",
            "What tools integrate best with {topic} to completely automate {problem}?"
        ]
    },
    "long_tail_niche": {
        "fa": [
            "بهترین {topic} ابری و مقرون‌به‌صرفه برای تیم‌های زیر ۱۰ نفر در {year}",
            "کدام {topic} بیشترین سازگاری را با سیستم‌های محلی و نیازهای خاص دارد؟",
            "پیشنهاد {topic} با قابلیت‌های هوش مصنوعی اختصاصی و امنیت بالا",
            "ارزان‌ترین {topic} با امکانات کامل و بدون محدودیت کاربر",
            "بررسی تخصصی {topic} با قابلیت گزارش‌گیری پیشرفته و سفارشی‌سازی",
            "کدام پلتفرم {topic} بهترین API و امکان اتصال به وب‌هوک‌ها را دارد؟",
            "راهنمای خرید {topic} برای صنایع تخصصی و سازمان‌های بزرگ",
            "بهترین {topic} رایگان یا اوپن‌سورس با کیفیت نزدیک به نسخه‌های پولی",
            "پلتفرم‌های نسل جدید {topic} که در سال {year} سر و صدا به پا کرده‌اند",
            "تجربه کاربری و سرعت لود در کدام {topic} بالاترین امتیاز را دارد؟"
        ],
        "en": [
            "Best lightweight cloud-based {topic} for teams under 10 members in {year}",
            "Which {topic} has the best developer API and webhook integrations?",
            "Top self-hosted or open-source {topic} alternatives with enterprise security",
            "Most affordable {topic} with unlimited users and advanced analytics",
            "Deep-dive review of modern {topic} platforms featuring native AI agents",
            "Which {topic} offers the fastest onboarding and easiest user interface?",
            "Best high-compliance {topic} for regulated industries (healthcare, finance)",
            "Emerging next-generation {topic} software gaining traction in {year}",
            "How to customize your {topic} workflow without writing complex code",
            "Top zero-cost or freemium {topic} tools that actually deliver results"
        ]
    },
    "reputation_sentiment": {
        "fa": [
            "آیا {entity_a} معتبر و قابل اعتماد است؟ بررسی نظرات و تجربیات کاربران",
            "بزرگترین معایب و شکایات گزارش شده درباره {entity_a} چیست؟",
            "نظر کاربران در ردیت و شبکه‌های اجتماعی درباره کیفیت {entity_a}",
            "آیا مهاجرت به {entity_a} تصمیم درستی برای یک کسب‌وکار در حال رشد است؟",
            "امتیاز واقعی {entity_a} در سایت‌های بررسی تخصصی چقدر است؟",
            "آیا پشتیبانی مشتریان {entity_a} سریع و پاسخگو است؟",
            "چالش‌های امنیتی و حریم خصوصی در استفاده از {entity_a}",
            "چه کسانی نباید از {entity_a} استفاده کنند؟ موارد منع استفاده",
            "تجربه کار بلندمدت با {entity_a}: آیا بعد از ۶ ماه همچنان رضایت‌بخش است؟",
            "مقایسه میزان رضایت مشتریان {entity_a} با رقبای اصلی بازار"
        ],
        "en": [
            "Is {entity_a} trustworthy and legit? Deep dive into user reviews & sentiment",
            "What are the biggest complaints and limitations reported for {entity_a}?",
            "What do developers and users on Reddit say about {entity_a} in {year}?",
            "Is {entity_a} really worth the hype or is it overpriced marketing?",
            "Customer support responsiveness and SLA reliability of {entity_a}",
            "Security, privacy, and compliance review for {entity_a}",
            "Who should NOT use {entity_a}? Key disqualifying use cases",
            "Long-term user reviews on {entity_a}: satisfaction after 12 months",
            "Hidden costs, price increases, and renewal traps in {entity_a}",
            "Real user ratings across G2, Trustpilot, and Reddit for {entity_a}"
        ]
    }
}

INDUSTRY_PRESETS = {
    "crm_sales": {
        "name_fa": "نرم‌افزارهای CRM و مدیریت فروش",
        "name_en": "CRM & Sales Management Software",
        "topic_fa": "نرم‌افزار CRM",
        "topic_en": "CRM software",
        "target_brand": "HubSpot",
        "competitors": ["Salesforce", "Zoho CRM", "Pipedrive", "Monday CRM", "Didar CRM", "Sarv CRM"],
        "problems_fa": [
            "پیگیری مشتریان و جلوگیری از ریزش سرنخ‌ها",
            "اتوماسیون فرآیند فروش و پایپ‌لاین",
            "یکپارچه‌سازی ایمیل و پیام‌رسان‌ها با پرونده مشتری",
            "گزارش‌گیری دقیق از عملکرد تیم فروش",
            "مدیریت کمپین‌های بازاریابی و نرخ تبدیل"
        ],
        "problems_en": [
            "lead tracking and preventing pipeline leaks",
            "sales automation and funnel optimization",
            "omnichannel customer communication sync",
            "accurate sales forecasting and rep reporting",
            "marketing campaign attribution and ROI tracking"
        ]
    },
    "seo_marketing": {
        "name_fa": "ابزارهای سئو و بازاریابی دیجیتال",
        "name_en": "SEO & Digital Marketing Tools",
        "topic_fa": "ابزار سئو و تحقیق کلمات کلیدی",
        "topic_en": "SEO & Keyword Research Tool",
        "target_brand": "Ahrefs",
        "competitors": ["SEMrush", "Moz Pro", "Ubersuggest", "SpyFu", "SE Ranking", "JetSEO"],
        "problems_fa": [
            "کشف شکاف کلمات کلیدی رقبا",
            "تحلیل بک‌لینک و خطاهای تکنیکال سایت",
            "بهینه‌سازی محتوا برای دیده‌شدن در هوش مصنوعی (GEO)",
            "رهگیری رتبه کلمات در نتایج جستجو",
            "کاهش بانس‌ریت و افزایش ورودی ارگانیک"
        ],
        "problems_en": [
            "competitor keyword gap discovery",
            "backlink audit and technical site health fixing",
            "optimizing content for AI visibility and GEO",
            "accurate multi-location rank tracking",
            "reducing bounce rate and boosting organic search traffic"
        ]
    },
    "project_management": {
        "name_fa": "مدیریت پروژه و وظایف تیم‌ها",
        "name_en": "Project Management & Collaboration",
        "topic_fa": "نرم‌افزار مدیریت پروژه و تسک‌ها",
        "topic_en": "Project Management Software",
        "target_brand": "ClickUp",
        "competitors": ["Asana", "Trello", "Monday.com", "Notion", "Jira", "Taskulu", "Mizito"],
        "problems_fa": [
            "هماهنگی تسک‌ها در تیم‌های ریموت و دورکار",
            "مدیریت اسپرینت‌ها و متدولوژی چابک (Agile)",
            "ردیابی زمان و بودجه پروژه‌ها",
            "جلوگیری از فراموشی ددلاین‌ها",
            "یکپارچگی با اسلک و گوگل درایو"
        ],
        "problems_en": [
            "cross-functional coordination in remote teams",
            "agile sprint planning and backlog management",
            "time tracking and project budget overruns",
            "deadline monitoring and automated task reminders",
            "native integrations with Slack, GitHub, and Google Drive"
        ]
    },
    "ai_copywriting": {
        "name_fa": "ابزارهای تولید محتوا با هوش مصنوعی",
        "name_en": "AI Content Creation & Copywriting",
        "topic_fa": "ابزار تولید محتوای هوش مصنوعی",
        "topic_en": "AI Content & Copywriting Platform",
        "target_brand": "Jasper AI",
        "competitors": ["Copy.ai", "Writesonic", "Claude", "ChatGPT Plus", "Rytr", "Neveshtan"],
        "problems_fa": [
            "تولید مقالات تخصصی با لحن برند",
            "حفظ اصالت محتوا و عدم شناسایی به عنوان اسپم",
            "تولید سریع متن پست‌های شبکه‌های اجتماعی",
            "ترجمه و بومی‌سازی محتوا به زبان‌های مختلف",
            "بهینه‌سازی سئو و سرپ مقالات با هوش مصنوعی"
        ],
        "problems_en": [
            "generating long-form blog posts matching brand voice",
            "maintaining factual accuracy and avoiding AI hallucination",
            "scaling multi-channel social media copy",
            "multilingual content localization and translation",
            "SERP-optimized content generation with high readability"
        ]
    },
    "ecommerce_platform": {
        "name_fa": "پلتفرم‌های فروشگاه‌ساز اینترنتی",
        "name_en": "E-Commerce & Store Builders",
        "topic_fa": "سیستم فروشگاه‌ساز اینترنتی",
        "topic_en": "E-commerce Platform",
        "target_brand": "Shopify",
        "competitors": ["WooCommerce", "BigCommerce", "Magento", "Wix eCommerce", "Shopfa", "Sazito"],
        "problems_fa": [
            "اتصال به درگاه‌های پرداخت و سیستم انبارداری",
            "سرعت بارگذاری بالا در ترافیک سنگین جشنواره‌ها",
            "سئو فنی و بهینه‌سازی ساختار محصولات",
            "مدیریت سفارشات چندکاناله",
            "طراحی صفحات فرود جذاب با نرخ تبدیل بالا"
        ],
        "problems_en": [
            "payment gateway integration and inventory sync",
            "high page speed handling peak flash-sale traffic",
            "technical SEO and rich snippet product markup",
            "omnichannel inventory and order fulfillment",
            "high-converting landing page creation with custom checkout"
        ]
    }
}


def generate_prompt_dataset(
    niche_key: str = "crm_sales",
    target_brand: str = None,
    competitors: List[str] = None,
    language: str = "both",  # "fa", "en", "both"
    total_count: int = 1000,
    custom_topic: str = None,
    custom_problems: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Generates a structured dataset of N prompts (e.g. 1000) for AI benchmarking.
    """
    preset = INDUSTRY_PRESETS.get(niche_key, INDUSTRY_PRESETS["crm_sales"])
    
    brand = target_brand if target_brand else preset["target_brand"]
    comp_list = competitors if competitors and len(competitors) > 0 else preset["competitors"]
    all_brands = [brand] + comp_list
    
    topic_fa = custom_topic if custom_topic else preset["topic_fa"]
    topic_en = custom_topic if custom_topic else preset["topic_en"]
    
    problems_fa = custom_problems if custom_problems else preset["problems_fa"]
    problems_en = custom_problems if custom_problems else preset["problems_en"]
    
    intents = ["commercial_direct", "comparative", "problem_solving", "long_tail_niche", "reputation_sentiment"]
    intent_weights = [0.30, 0.25, 0.20, 0.15, 0.10]
    
    langs = ["fa", "en"] if language == "both" else [language]
    
    prompts = []
    current_year = "2026"
    
    for i in range(total_count):
        # Choose intent based on distribution
        intent = random.choices(intents, weights=intent_weights, k=1)[0]
        lang = random.choice(langs)
        
        template_list = TEMPLATES_BY_INTENT[intent][lang]
        template = random.choice(template_list)
        
        # Pick entities for comparative
        entity_a = brand if random.random() < 0.6 else random.choice(comp_list)
        other_comps = [c for c in all_brands if c != entity_a]
        entity_b = random.choice(other_comps) if other_comps else "Competitor B"
        other_comps2 = [c for c in other_comps if c != entity_b]
        entity_c = random.choice(other_comps2) if other_comps2 else "Competitor C"
        
        problem = random.choice(problems_fa if lang == "fa" else problems_en)
        topic = topic_fa if lang == "fa" else topic_en
        
        # Fill template
        query_text = template.format(
            topic=topic,
            entity_a=entity_a,
            entity_b=entity_b,
            entity_c=entity_c,
            problem=problem,
            year=current_year
        )
        
        prompt_item = {
            "id": f"qry_{i+1:04d}",
            "query": query_text,
            "intent": intent,
            "language": lang,
            "niche": niche_key,
            "target_brand": brand,
            "primary_subject": entity_a if intent in ["comparative", "reputation_sentiment"] else topic,
            "expected_entities": all_brands,
            "difficulty": random.choice(["high_intent", "exploratory", "niche_tail"]),
        }
        prompts.append(prompt_item)
        
    return prompts


if __name__ == "__main__":
    dataset = generate_prompt_dataset(total_count=1000)
    print(f"Generated {len(dataset)} prompts successfully.")
    print("Sample prompt #1:", dataset[0])
    print("Sample prompt #500:", dataset[500])
