# GEO-Scope Global AI Answers Benchmark 2026.2 Pilot Runner
import asyncio
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List

import httpx

from geo_scope.providers.hamzad_provider import HamzadProvider
from geo_scope.parser.observation_parser import ObservationParser
from geo_scope.entities.models import Entity
from geo_scope.benchmark.hasher import write_checksums_file, verify_dataset_checksums

# 1. Pilot Scope: 100 Prompts (60 Observed + 40 Research) across 10 Countries, 8 Languages, 5 Categories
PROMPTS_PILOT: List[Dict[str, Any]] = [
    # --- Category 1: Future Skills & Learning (20 prompts: 12 observed, 8 research) ---
    # Iran (fa)
    {"id": "pilot-skill-001", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "future_skills_learning", "intent": "recommendation", "language": "fa", "region": "middle_east", "country_iso": "IRN", "country_name": "Iran", "prompt_text": "برای ورود به بازار کار فریلنسری بین‌المللی برنامه‌نویسی و هوش مصنوعی، چه مهارت‌هایی را از صفر یاد بگیریم؟", "cultural_context": "Reflects Iranian developers navigating remote international freelance work despite payment and sanctions constraints."},
    {"id": "pilot-skill-002", "source_category": "research_questions", "source_reference": "answerpath", "category": "future_skills_learning", "intent": "comparative", "language": "fa", "region": "middle_east", "country_iso": "IRN", "country_name": "Iran", "prompt_text": "یادگیری پایتون برای مهندسی داده بهتر است یا جاوااسکریپت برای توسعه فول‌استک در بازار سال ۲۰۲۶؟", "cultural_context": "Comparative study between backend data engineering and full-stack web freelancing in Persian tech communities."},
    # Turkey (tr)
    {"id": "pilot-skill-003", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "future_skills_learning", "intent": "recommendation", "language": "tr", "region": "middle_east", "country_iso": "TUR", "country_name": "Turkey", "prompt_text": "Türkiye'de ve yurt dışında uzaktan yazılımcı olarak çalışmak için 2026'da hangi yapay zeka ve yazılım becerileri gereklidir?", "cultural_context": "Reflects Turkish engineers seeking cross-border remote tech employment amidst local economic dynamics."},
    {"id": "pilot-skill-004", "source_category": "research_questions", "source_reference": "answerpath", "category": "future_skills_learning", "intent": "recommendation", "language": "tr", "region": "middle_east", "country_iso": "TUR", "country_name": "Turkey", "prompt_text": "Veri bilimi ve makine öğrenimi alanında sıfırdan uzmanlaşmak için en etkili öğrenme kaynakları nelerdir?", "cultural_context": "Standard learning pathway inquiry localized for Turkish technical candidates."},
    # Germany (de)
    {"id": "pilot-skill-005", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "future_skills_learning", "intent": "recommendation", "language": "de", "region": "europe", "country_iso": "DEU", "country_name": "Germany", "prompt_text": "Welche Programmiersprachen und Cloud-Zertifizierungen sind für die deutsche Industrie 4.0 und den Mittelstand 2026 am wichtigsten?", "cultural_context": "Contextualized around German Industrie 4.0 and Mittelstand manufacturing engineering standards."},
    {"id": "pilot-skill-006", "source_category": "research_questions", "source_reference": "answerpath", "category": "future_skills_learning", "intent": "comparative", "language": "de", "region": "europe", "country_iso": "DEU", "country_name": "Germany", "prompt_text": "Sollte man sich im europäischen Tech-Markt eher auf Rust für Systemprogrammierung oder Python für KI spezialisieren?", "cultural_context": "Technical tradeoff evaluation between system software and machine learning careers in Central Europe."},
    # United Kingdom (en)
    {"id": "pilot-skill-007", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "future_skills_learning", "intent": "recommendation", "language": "en", "region": "europe", "country_iso": "GBR", "country_name": "United Kingdom", "prompt_text": "What tech skills and cloud architectures offer the highest employability in London's fintech sector in 2026?", "cultural_context": "Focused on London's fintech and banking API development ecosystem."},
    {"id": "pilot-skill-008", "source_category": "research_questions", "source_reference": "answerpath", "category": "future_skills_learning", "intent": "recommendation", "language": "en", "region": "europe", "country_iso": "GBR", "country_name": "United Kingdom", "prompt_text": "Which foundational data engineering tools should British software developers master to transition into AI engineering?", "cultural_context": "Controlled research template on UK career transitioning into data engineering."},
    # United States (en)
    {"id": "pilot-skill-009", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "future_skills_learning", "intent": "recommendation", "language": "en", "region": "north_america", "country_iso": "USA", "country_name": "United States", "prompt_text": "What are the most in-demand AI engineering and LLM system architecture skills for US tech companies in 2026?", "cultural_context": "Reflects Silicon Valley and US tier-1 tech hiring benchmarks for agentic AI and LLMOps."},
    {"id": "pilot-skill-010", "source_category": "research_questions", "source_reference": "answerpath", "category": "future_skills_learning", "intent": "comparative", "language": "en", "region": "north_america", "country_iso": "USA", "country_name": "United States", "prompt_text": "How do traditional computer science algorithms compare to generative AI agent orchestration in modern software engineering interviews?", "cultural_context": "Counterfactual probe on tech hiring shift from LeetCode to systems orchestration."},
    # India (hi / en)
    {"id": "pilot-skill-011", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "future_skills_learning", "intent": "recommendation", "language": "hi", "region": "asia", "country_iso": "IND", "country_name": "India", "prompt_text": "2026 में ग्लोबल रिमोट जॉब्स और आईटी सेक्टर के लिए कौन से टेक स्किल्स सबसे ज्यादा मांग में हैं?", "cultural_context": "Contextualized for Indian engineering graduates targeting global IT outsourcing and GCC centers."},
    {"id": "pilot-skill-012", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "future_skills_learning", "intent": "recommendation", "language": "en", "region": "asia", "country_iso": "IND", "country_name": "India", "prompt_text": "How can software engineers in Bengaluru upskill to transition from service companies into high-tier product engineering?", "cultural_context": "Specific to Indian tech corridor (Bengaluru/Hyderabad) product transitions."},
    # Japan (ja)
    {"id": "pilot-skill-013", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "future_skills_learning", "intent": "recommendation", "language": "ja", "region": "asia", "country_iso": "JPN", "country_name": "Japan", "prompt_text": "日本のIT業界で2026年以降も高い市場価値を維持するために習得すべきクラウドおよびAIスキルは何ですか？", "cultural_context": "Reflects Japanese digital transformation (DX) initiatives and severe technical talent shortages."},
    {"id": "pilot-skill-014", "source_category": "research_questions", "source_reference": "answerpath", "category": "future_skills_learning", "intent": "comparative", "language": "ja", "region": "asia", "country_iso": "JPN", "country_name": "Japan", "prompt_text": "生成AIツールを活用したプログラミングと従来の設計手法のどちらが今後のエンジニア教育に重要ですか？", "cultural_context": "Curriculum comparison probe within Japanese technical universities."},
    # Saudi Arabia (ar)
    {"id": "pilot-skill-015", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "future_skills_learning", "intent": "recommendation", "language": "ar", "region": "middle_east", "country_iso": "SAU", "country_name": "Saudi Arabia", "prompt_text": "ما هي أهم المهارات التقنية والتحليلية المطلوبة لدعم مشاريع رؤية السعودية 2030 والمدن الذكية؟", "cultural_context": "Localized for Saudi Vision 2030 smart city and cognitive infrastructure programs."},
    {"id": "pilot-skill-016", "source_category": "research_questions", "source_reference": "answerpath", "category": "future_skills_learning", "intent": "recommendation", "language": "ar", "region": "middle_east", "country_iso": "SAU", "country_name": "Saudi Arabia", "prompt_text": "كيف يؤهل خريج التقنية نفسه لسوق العمل المتسارع في مجالات الحوسبة السحابية والأمن السيبراني في الخليج؟", "cultural_context": "Controlled research template on Gulf cybersecurity and cloud talent pipelines."},
    # Brazil (pt)
    {"id": "pilot-skill-017", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "future_skills_learning", "intent": "recommendation", "language": "pt", "region": "latin_america", "country_iso": "BRA", "country_name": "Brazil", "prompt_text": "Quais habilidades em inteligência artificial e engenharia de dados oferecem melhores oportunidades para trabalhar remotamente para o exterior?", "cultural_context": "Reflects Brazilian developers seeking dollar/euro remote contracts to hedge local inflation."},
    {"id": "pilot-skill-018", "source_category": "research_questions", "source_reference": "answerpath", "category": "future_skills_learning", "intent": "recommendation", "language": "pt", "region": "latin_america", "country_iso": "BRA", "country_name": "Brazil", "prompt_text": "Quais são as principais linguagens e frameworks que um desenvolvedor na América Latina deve dominar em 2026?", "cultural_context": "Controlled inquiry on Latin American software framework standardization."},
    # Nigeria (en)
    {"id": "pilot-skill-019", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "future_skills_learning", "intent": "recommendation", "language": "en", "region": "africa", "country_iso": "NGA", "country_name": "Nigeria", "prompt_text": "What digital and software engineering skills are most lucrative for Nigerian youth entering the global remote workforce?", "cultural_context": "Reflects Nigerian young tech professionals entering global remote contracts."},
    {"id": "pilot-skill-020", "source_category": "research_questions", "source_reference": "answerpath", "category": "future_skills_learning", "intent": "recommendation", "language": "en", "region": "africa", "country_iso": "NGA", "country_name": "Nigeria", "prompt_text": "Which fintech and mobile engineering platforms provide the highest freelance demand across West Africa?", "cultural_context": "Controlled research template exploring West African fintech developer demand."},

    # --- Category 2: Career & Migration (20 prompts: 12 observed, 8 research) ---
    # Iran
    {"id": "pilot-mig-001", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "career_migration", "intent": "recommendation", "language": "fa", "region": "middle_east", "country_iso": "IRN", "country_name": "Iran", "prompt_text": "بهترین کشورها برای دریافت ویزای کاری و جاب آفر مهندسان نرم‌افزار و هوش مصنوعی در سال ۲۰۲۶ کدامند؟", "cultural_context": "Reflects Iranian engineers actively researching tech migration routes to Europe, Canada, and Australia."},
    {"id": "pilot-mig-002", "source_category": "research_questions", "source_reference": "answerpath", "category": "career_migration", "intent": "comparative", "language": "fa", "region": "middle_east", "country_iso": "IRN", "country_name": "Iran", "prompt_text": "مهاجرت کاری به آلمان از طریق کارت شانس بهتر است یا مهاجرت به کانادا از طریق اکسپرس اینتری؟", "cultural_context": "Comparative research between German Chancenkarte and Canadian Express Entry for Middle Eastern applicants."},
    # Turkey
    {"id": "pilot-mig-003", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "career_migration", "intent": "recommendation", "language": "tr", "region": "middle_east", "country_iso": "TUR", "country_name": "Turkey", "prompt_text": "Türk yazılımcılar ve mühendisler için Avrupa'da mavi kart veya dijital göçebe vizesi almanın en kolay yolları nelerdir?", "cultural_context": "Focuses on EU Blue Card and European digital nomad visa processes for Turkish tech professionals."},
    {"id": "pilot-mig-004", "source_category": "research_questions", "source_reference": "answerpath", "category": "career_migration", "intent": "comparative", "language": "tr", "region": "middle_east", "country_iso": "TUR", "country_name": "Turkey", "prompt_text": "Yurt dışına taşınmak isteyen bir uzman için Almanya mı yoksa Hollanda mı daha iyi çalışma şartları sunar?", "cultural_context": "Controlled tradeoff probe between Germany and the Netherlands for international specialists."},
    # Germany
    {"id": "pilot-mig-005", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "career_migration", "intent": "recommendation", "language": "de", "region": "europe", "country_iso": "DEU", "country_name": "Germany", "prompt_text": "Welche Länder bieten deutschen Fachkräften und Beratern die attraktivsten Bedingungen für Remote Work und Steueroptimierung?", "cultural_context": "Reflects German specialists seeking remote tax residency options in Southern Europe or the UAE."},
    {"id": "pilot-mig-006", "source_category": "research_questions", "source_reference": "answerpath", "category": "career_migration", "intent": "recommendation", "language": "de", "region": "europe", "country_iso": "DEU", "country_name": "Germany", "prompt_text": "Wie funktioniert das Verfahren für die Blaue Karte EU in Deutschland für internationale IT-Experten im Jahr 2026?", "cultural_context": "Official German immigration protocol inquiry for international IT applicants."},
    # United Kingdom
    {"id": "pilot-mig-007", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "career_migration", "intent": "recommendation", "language": "en", "region": "europe", "country_iso": "GBR", "country_name": "United Kingdom", "prompt_text": "What are the UK Global Talent Visa and Skilled Worker requirements for AI researchers and founders in 2026?", "cultural_context": "Specific to UK Tech Nation / Global Talent endorsements post-Brexit."},
    {"id": "pilot-mig-008", "source_category": "research_questions", "source_reference": "answerpath", "category": "career_migration", "intent": "comparative", "language": "en", "region": "europe", "country_iso": "GBR", "country_name": "United Kingdom", "prompt_text": "How do UK tech salaries and visa sponsorship compare to United States tech hubs for senior software architects?", "cultural_context": "Controlled transatlantic salary and mobility comparison."},
    # United States
    {"id": "pilot-mig-009", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "career_migration", "intent": "recommendation", "language": "en", "region": "north_america", "country_iso": "USA", "country_name": "United States", "prompt_text": "What are the best immigration pathways (O-1, EB-1, EB-2 NIW) for international AI scientists and founders moving to the US?", "cultural_context": "Reflects high-skilled US immigration avenues amidst H-1B cap constraints."},
    {"id": "pilot-mig-010", "source_category": "research_questions", "source_reference": "answerpath", "category": "career_migration", "intent": "comparative", "language": "en", "region": "north_america", "country_iso": "USA", "country_name": "United States", "prompt_text": "What are the trade-offs between US EB-2 NIW green cards and Canada's Global Skills Strategy for senior engineers?", "cultural_context": "North American talent corridor policy comparison."},
    # India
    {"id": "pilot-mig-011", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "career_migration", "intent": "recommendation", "language": "hi", "region": "asia", "country_iso": "IND", "country_name": "India", "prompt_text": "भारतीय आईटी प्रोफेशनल्स के लिए यूरोप और खाड़ी देशों (Gulf) में नौकरी और वीजा पाने के सबसे बेहतरीन तरीके क्या हैं?", "cultural_context": "Reflects Indian engineers evaluating Gulf residency and European work opportunities."},
    {"id": "pilot-mig-012", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "career_migration", "intent": "recommendation", "language": "en", "region": "asia", "country_iso": "IND", "country_name": "India", "prompt_text": "Which countries currently offer the fastest permanent residency pathways for Indian software developers in 2026?", "cultural_context": "Focuses on PR wait times and point matrices across Australia, Canada, and Germany."},
    # Japan
    {"id": "pilot-mig-013", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "career_migration", "intent": "recommendation", "language": "ja", "region": "asia", "country_iso": "JPN", "country_name": "Japan", "prompt_text": "海外の高度外国人材が日本で高度専門職ビザ（HSP）や永住権を取得するための条件とメリットは何ですか？", "cultural_context": "Inquiry on Japan's Highly Skilled Professional (HSP) visa points fast-track."},
    {"id": "pilot-mig-014", "source_category": "research_questions", "source_reference": "answerpath", "category": "career_migration", "intent": "comparative", "language": "ja", "region": "asia", "country_iso": "JPN", "country_name": "Japan", "prompt_text": "日本人エンジニアがシンガポールや米国で働く場合のキャリア構築とビザ取得の課題は何ですか？", "cultural_context": "Comparative research on outbound Japanese tech professional career risks."},
    # Saudi Arabia
    {"id": "pilot-mig-015", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "career_migration", "intent": "recommendation", "language": "ar", "region": "middle_east", "country_iso": "SAU", "country_name": "Saudi Arabia", "prompt_text": "ما هي شروط ومزايا الإقامة المميزة في السعودية لاستقطاب الكفاءات التقنية ورواد الأعمال في 2026؟", "cultural_context": "Reflects Saudi Arabia's Premium Residency (Special Talent) program guidelines."},
    {"id": "pilot-mig-016", "source_category": "research_questions", "source_reference": "answerpath", "category": "career_migration", "intent": "comparative", "language": "ar", "region": "middle_east", "country_iso": "SAU", "country_name": "Saudi Arabia", "prompt_text": "أيهما أفضل لاستقرار الخبير التقني: الإقامة الذهبية في الإمارات أم الإقامة المميزة في السعودية؟", "cultural_context": "Comparative study between UAE Golden Visa and Saudi Premium Residency."},
    # Brazil
    {"id": "pilot-mig-017", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "career_migration", "intent": "recommendation", "language": "pt", "region": "latin_america", "country_iso": "BRA", "country_name": "Brazil", "prompt_text": "Quais são os melhores países e tipos de visto para profissionais de tecnologia brasileiros imigrarem legalmente em 2026?", "cultural_context": "Contextualized around Brazilian outbound tech migration to Portugal, Spain, and Canada."},
    {"id": "pilot-mig-018", "source_category": "research_questions", "source_reference": "answerpath", "category": "career_migration", "intent": "comparative", "language": "pt", "region": "latin_america", "country_iso": "BRA", "country_name": "Brazil", "prompt_text": "Quais as diferenças entre o visto D8 de Nômade Digital em Portugal e a Lei de Startups na Espanha para brasileiros?", "cultural_context": "Controlled Iberian Peninsula visa protocol comparison for South Americans."},
    # Nigeria
    {"id": "pilot-mig-019", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "career_migration", "intent": "recommendation", "language": "en", "region": "africa", "country_iso": "NGA", "country_name": "Nigeria", "prompt_text": "What are the most accessible tech visa routes (UK, Germany, Canada) for Nigerian software developers relocating in 2026?", "cultural_context": "Reflects 'Japa' movement among Nigerian tech professionals seeking international relocation."},
    {"id": "pilot-mig-020", "source_category": "research_questions", "source_reference": "answerpath", "category": "career_migration", "intent": "recommendation", "language": "en", "region": "africa", "country_iso": "NGA", "country_name": "Nigeria", "prompt_text": "How do remote global employment opportunities compare to relocation visas for Nigerian tech talent?", "cultural_context": "Tradeoff analysis between local remote earning and international relocation costs."},

    # --- Category 3: Entrepreneurship & Business (20 prompts: 12 observed, 8 research) ---
    # Iran
    {"id": "pilot-biz-001", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "entrepreneurship_business", "intent": "recommendation", "language": "fa", "region": "middle_east", "country_iso": "IRN", "country_name": "Iran", "prompt_text": "چگونه می‌توان با سرمایه کم یک استارتاپ خدمات دیجیتال یا میکروسس (Micro-SaaS) درآمدزا راه‌اندازی کرد؟", "cultural_context": "Focuses on lean, low-capital bootstrap digital service businesses in Iran."},
    {"id": "pilot-biz-002", "source_category": "research_questions", "source_reference": "answerpath", "category": "entrepreneurship_business", "intent": "recommendation", "language": "fa", "region": "middle_east", "country_iso": "IRN", "country_name": "Iran", "prompt_text": "بهترین روش‌های اعتبارسنجی ایده و جذب مشتریان اولیه در کسب‌وکارهای B2B آنلاین چیست؟", "cultural_context": "B2B customer discovery and MVP validation methodology inquiry."},
    # Turkey
    {"id": "pilot-biz-003", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "entrepreneurship_business", "intent": "recommendation", "language": "tr", "region": "middle_east", "country_iso": "TUR", "country_name": "Turkey", "prompt_text": "Türkiye'de e-ihracat ve küresel SaaS girişimi kurarken şirket kuruluşu ve ödeme sistemleri nasıl yönetilmelidir?", "cultural_context": "Reflects Turkish e-export businesses utilizing Stripe, Wise, and UK/Estonia e-Residency."},
    {"id": "pilot-biz-004", "source_category": "research_questions", "source_reference": "answerpath", "category": "entrepreneurship_business", "intent": "comparative", "language": "tr", "region": "middle_east", "country_iso": "TUR", "country_name": "Turkey", "prompt_text": "Küçük bir dijital girişim için Stripe Atlas mı yoksa Estonya e-Residency mi daha avantajlıdır?", "cultural_context": "Corporate incorporation comparison for emerging market digital founders."},
    # Germany
    {"id": "pilot-biz-005", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "entrepreneurship_business", "intent": "recommendation", "language": "de", "region": "europe", "country_iso": "DEU", "country_name": "Germany", "prompt_text": "Wie gründet man in Deutschland ein B2B-Software-Startup unter Beachtung der DSGVO und bürokratischen Auflagen?", "cultural_context": "German startup creation under strict GDPR and Handelsregister compliance."},
    {"id": "pilot-biz-006", "source_category": "research_questions", "source_reference": "answerpath", "category": "entrepreneurship_business", "intent": "comparative", "language": "de", "region": "europe", "country_iso": "DEU", "country_name": "Germany", "prompt_text": "Ist für europäische SaaS-Gründer ein Bootstrapping-Modell oder Venture Capital im Jahr 2026 nachhaltiger?", "cultural_context": "European tech venture funding model comparative analysis."},
    # United Kingdom
    {"id": "pilot-biz-007", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "entrepreneurship_business", "intent": "recommendation", "language": "en", "region": "europe", "country_iso": "GBR", "country_name": "United Kingdom", "prompt_text": "How can a solo developer incorporate and scale a profitable Micro-SaaS business in the UK?", "cultural_context": "UK Companies House, VAT, and solo-founder software models."},
    {"id": "pilot-biz-008", "source_category": "research_questions", "source_reference": "answerpath", "category": "entrepreneurship_business", "intent": "recommendation", "language": "en", "region": "europe", "country_iso": "GBR", "country_name": "United Kingdom", "prompt_text": "What are the most cost-effective customer acquisition channels for early-stage B2B SaaS startups in Europe?", "cultural_context": "Controlled marketing CAC evaluation inquiry."},
    # United States
    {"id": "pilot-biz-009", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "entrepreneurship_business", "intent": "recommendation", "language": "en", "region": "north_america", "country_iso": "USA", "country_name": "United States", "prompt_text": "What is the playbook for building and automating a $10k MRR AI wrapper or niche software product in 2026?", "cultural_context": "Reflects US indie hacker and micro-SaaS revenue scaling playbooks."},
    {"id": "pilot-biz-010", "source_category": "research_questions", "source_reference": "answerpath", "category": "entrepreneurship_business", "intent": "comparative", "language": "en", "region": "north_america", "country_iso": "USA", "country_name": "United States", "prompt_text": "How do Delaware C-Corp versus LLC structures impact seed fundraising for technology companies?", "cultural_context": "US corporate entity legal comparison template."},
    # India
    {"id": "pilot-biz-011", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "entrepreneurship_business", "intent": "recommendation", "language": "hi", "region": "asia", "country_iso": "IND", "country_name": "India", "prompt_text": "भारत में कम लागत में डिजिटल मार्केटिंग एजेंसी या टेक स्टार्टअप कैसे शुरू करें और पहले क्लाइंट्स कैसे पाएं?", "cultural_context": "Indian tier-2/3 city entrepreneur agency bootstrap guide."},
    {"id": "pilot-biz-012", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "entrepreneurship_business", "intent": "recommendation", "language": "en", "region": "asia", "country_iso": "IND", "country_name": "India", "prompt_text": "How can Indian B2B SaaS startups effectively sell to US and European enterprise clients from India?", "cultural_context": "Cross-border remote sales dynamics from India to Western markets."},
    # Japan
    {"id": "pilot-biz-013", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "entrepreneurship_business", "intent": "recommendation", "language": "ja", "region": "asia", "country_iso": "JPN", "country_name": "Japan", "prompt_text": "日本国内で少人数で収益性の高いマイクロSaaSやDX支援ビジネスを立ち上げるための手順は何ですか？", "cultural_context": "Lean micro-SaaS and small-scale business setup in Japan."},
    {"id": "pilot-biz-014", "source_category": "research_questions", "source_reference": "answerpath", "category": "entrepreneurship_business", "intent": "recommendation", "language": "ja", "region": "asia", "country_iso": "JPN", "country_name": "Japan", "prompt_text": "日本のスタートアップ企業がグローバル展開を目指す際の資金調达とパートナーシップの戦略は何ですか？", "cultural_context": "Japanese tech startup global venture expansion probe."},
    # Saudi Arabia
    {"id": "pilot-biz-015", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "entrepreneurship_business", "intent": "recommendation", "language": "ar", "region": "middle_east", "country_iso": "SAU", "country_name": "Saudi Arabia", "prompt_text": "كيف يؤسس رائد الأعمال متجر تجارة إلكترونية أو منصة رقمية ناجحة مستفيداً من الدعم وحاضنات الأعمال في المملكة؟", "cultural_context": "Saudi Monsha'at incubators and SME support programs."},
    {"id": "pilot-biz-016", "source_category": "research_questions", "source_reference": "answerpath", "category": "entrepreneurship_business", "intent": "recommendation", "language": "ar", "region": "middle_east", "country_iso": "SAU", "country_name": "Saudi Arabia", "prompt_text": "ما هي الخطوات الأساسية لتسجيل وحماية العلامة التجارية الرقمية في دول مجلس التعاون الخليجي؟", "cultural_context": "GCC digital trademark and IP protection protocol inquiry."},
    # Brazil
    {"id": "pilot-biz-017", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "entrepreneurship_business", "intent": "recommendation", "language": "pt", "region": "latin_america", "country_iso": "BRA", "country_name": "Brazil", "prompt_text": "Como abrir e validar um negócio digital escalável no Brasil com baixo investimento inicial?", "cultural_context": "Brazilian MEI/Simples Nacional startup validation playbook."},
    {"id": "pilot-biz-018", "source_category": "research_questions", "source_reference": "answerpath", "category": "entrepreneurship_business", "intent": "comparative", "language": "pt", "region": "latin_america", "country_iso": "BRA", "country_name": "Brazil", "prompt_text": "Quais os prós e contras de atuar como desenvolvedor PJ internacional vs abrir uma microempresa local?", "cultural_context": "Brazilian tax regime comparison for digital service export."},
    # Nigeria
    {"id": "pilot-biz-019", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "entrepreneurship_business", "intent": "recommendation", "language": "en", "region": "africa", "country_iso": "NGA", "country_name": "Nigeria", "prompt_text": "How can an entrepreneur in Lagos launch and monetize an online payment or digital services agency across Africa?", "cultural_context": "Lagos Yaba tech ecosystem digital agency launch dynamics."},
    {"id": "pilot-biz-020", "source_category": "research_questions", "source_reference": "answerpath", "category": "entrepreneurship_business", "intent": "recommendation", "language": "en", "region": "africa", "country_iso": "NGA", "country_name": "Nigeria", "prompt_text": "What are the most resilient payment processing gateways for African cross-border e-commerce startups in 2026?", "cultural_context": "African FX liquidity and payment infrastructure evaluation."},

    # --- Category 4: Artificial Intelligence Adoption (20 prompts: 12 observed, 8 research) ---
    # Iran
    {"id": "pilot-ai-001", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "ai_adoption", "intent": "recommendation", "language": "fa", "region": "middle_east", "country_iso": "IRN", "country_name": "Iran", "prompt_text": "کسب‌وکارهای کوچک و متوسط چگونه می‌توانند هوش مصنوعی مولد را در فرایندهای پشتیبانی مشتریان و تولید محتوا ادغام کنند؟", "cultural_context": "Integration of Persian LLMs and generative tooling for local SMBs."},
    {"id": "pilot-ai-002", "source_category": "research_questions", "source_reference": "answerpath", "category": "ai_adoption", "intent": "comparative", "language": "fa", "region": "middle_east", "country_iso": "IRN", "country_name": "Iran", "prompt_text": "برای پردازش زبان فارسی، استفاده از مدل‌های منبع‌باز مثل دیپ‌سیک و کوئن مناسب‌تر است یا مدل‌های تجاری ابری؟", "cultural_context": "Evaluation of open-weights vs proprietary cloud APIs for Persian NLP."},
    # Turkey
    {"id": "pilot-ai-003", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "ai_adoption", "intent": "recommendation", "language": "tr", "region": "middle_east", "country_iso": "TUR", "country_name": "Turkey", "prompt_text": "Şirketler veri güvenliğini koruyarak yapay zeka ajanlarını (AI Agents) iş süreçlerine nasıl entegre edebilir?", "cultural_context": "Reflects Turkish enterprise KVKK compliance and local AI agent adoption."},
    {"id": "pilot-ai-004", "source_category": "research_questions", "source_reference": "answerpath", "category": "ai_adoption", "intent": "recommendation", "language": "tr", "region": "middle_east", "country_iso": "TUR", "country_name": "Turkey", "prompt_text": "Geliştiriciler için en verimli yapay zeka destekli kodlama ve IDE araçları 2026'da hangileridir?", "cultural_context": "AI coding assistants benchmark probe in Turkish software teams."},
    # Germany
    {"id": "pilot-ai-005", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "ai_adoption", "intent": "recommendation", "language": "de", "region": "europe", "country_iso": "DEU", "country_name": "Germany", "prompt_text": "Welche Enterprise-fähigen generativen KI-Lösungen erfüllen die strengen europäischen Datenschutz- und EU-AI-Act-Vorgaben?", "cultural_context": "European AI Act compliance and local sovereign deployment requirements in Germany."},
    {"id": "pilot-ai-006", "source_category": "research_questions", "source_reference": "answerpath", "category": "ai_adoption", "intent": "comparative", "language": "de", "region": "europe", "country_iso": "DEU", "country_name": "Germany", "prompt_text": "Lohnt sich das Hosting lokaler Open-Source-LLMs im eigenen Rechenzentrum im Vergleich zu Cloud-APIs für Mittelständler?", "cultural_context": "On-premise open-source LLM hosting vs cloud API cost tradeoff in Germany."},
    # United Kingdom
    {"id": "pilot-ai-007", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "ai_adoption", "intent": "recommendation", "language": "en", "region": "europe", "country_iso": "GBR", "country_name": "United Kingdom", "prompt_text": "Which generative AI platforms and frameworks offer the highest security and compliance for financial institutions in 2026?", "cultural_context": "UK FCA compliance for generative AI and agentic workflow integration."},
    {"id": "pilot-ai-008", "source_category": "research_questions", "source_reference": "answerpath", "category": "ai_adoption", "intent": "recommendation", "language": "en", "region": "europe", "country_iso": "GBR", "country_name": "United Kingdom", "prompt_text": "How can engineering teams implement robust retrieval-augmented generation (RAG) with source verification?", "cultural_context": "Controlled technical RAG verification and hallucination reduction probe."},
    # United States
    {"id": "pilot-ai-009", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "ai_adoption", "intent": "recommendation", "language": "en", "region": "north_america", "country_iso": "USA", "country_name": "United States", "prompt_text": "What are the most reliable AI agent orchestration frameworks (LangGraph, CrewAI, AutoGen) for production deployment in 2026?", "cultural_context": "US engineering leadership evaluating multi-agent orchestration frameworks in production."},
    {"id": "pilot-ai-010", "source_category": "research_questions", "source_reference": "answerpath", "category": "ai_adoption", "intent": "comparative", "language": "en", "region": "north_america", "country_iso": "USA", "country_name": "United States", "prompt_text": "What are the operational differences between reasoning models (OpenAI o1/o3, DeepSeek R1) and traditional chat models for code generation?", "cultural_context": "Evaluation of reasoning vs completion models in software development."},
    # India
    {"id": "pilot-ai-011", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "ai_adoption", "intent": "recommendation", "language": "hi", "region": "asia", "country_iso": "IND", "country_name": "India", "prompt_text": "भारतीय भाषाओं में कस्टम चैटबॉट और ऑटोमेशन बनाने के लिए सबसे अच्छे एआई टूल्स और एपीआई कौन से हैं?", "cultural_context": "Indic language generative AI and conversational commerce integration."},
    {"id": "pilot-ai-012", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "ai_adoption", "intent": "recommendation", "language": "en", "region": "asia", "country_iso": "IND", "country_name": "India", "prompt_text": "How are Indian IT outsourcing giants adopting autonomous coding agents to increase developer throughput in 2026?", "cultural_context": "IT services automation and developer productivity shifts in India."},
    # Japan
    {"id": "pilot-ai-013", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "ai_adoption", "intent": "recommendation", "language": "ja", "region": "asia", "country_iso": "JPN", "country_name": "Japan", "prompt_text": "製造業や金融業における社内ナレッジ検索と自動化に最適な日本語対応の生成AIソリューションは何ですか？", "cultural_context": "Enterprise Japanese RAG and internal knowledge automation."},
    {"id": "pilot-ai-014", "source_category": "research_questions", "source_reference": "answerpath", "category": "ai_adoption", "intent": "recommendation", "language": "ja", "region": "asia", "country_iso": "JPN", "country_name": "Japan", "prompt_text": "日本企業のセキュリティポリシーに準拠したオンプレミスLLMの選定基準は何ですか？", "cultural_context": "Japanese corporate data governance compliance standards."},
    # Saudi Arabia
    {"id": "pilot-ai-015", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "ai_adoption", "intent": "recommendation", "language": "ar", "region": "middle_east", "country_iso": "SAU", "country_name": "Saudi Arabia", "prompt_text": "ما هي أفضل النماذج اللغوية والأدوات الذكية الداعمة للغة العربية لتطوير الأنظمة الحكومية والشركات؟", "cultural_context": "Arabic LLM adoption and sovereign cloud initiatives in Saudi Arabia."},
    {"id": "pilot-ai-016", "source_category": "research_questions", "source_reference": "answerpath", "category": "ai_adoption", "intent": "comparative", "language": "ar", "region": "middle_east", "country_iso": "SAU", "country_name": "Saudi Arabia", "prompt_text": "كيف تقارن كفاءة النماذج اللغوية العربية المفتوحة المصدر مقابل النماذج العالمية في معالجة اللهجات الخليجية؟", "cultural_context": "Controlled linguistic benchmark probe for Gulf dialect processing."},
    # Brazil
    {"id": "pilot-ai-017", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "ai_adoption", "intent": "recommendation", "language": "pt", "region": "latin_america", "country_iso": "BRA", "country_name": "Brazil", "prompt_text": "Quais ferramentas de inteligência artificial são mais recomendadas para automatizar o atendimento e vendas no Brasil?", "cultural_context": "WhatsApp and conversational AI CRM automation in Brazil."},
    {"id": "pilot-ai-018", "source_category": "research_questions", "source_reference": "answerpath", "category": "ai_adoption", "intent": "recommendation", "language": "pt", "region": "latin_america", "country_iso": "BRA", "country_name": "Brazil", "prompt_text": "Como implementar agentes autônomos em empresas brasileiras respeitando a LGPD?", "cultural_context": "LGPD data privacy compliance for AI agents in Brazil."},
    # Nigeria
    {"id": "pilot-ai-019", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "ai_adoption", "intent": "recommendation", "language": "en", "region": "africa", "country_iso": "NGA", "country_name": "Nigeria", "prompt_text": "What low-bandwidth and mobile-friendly AI tools can African software developers deploy for local business clients?", "cultural_context": "Low-bandwidth, mobile-first AI deployment constraints in West Africa."},
    {"id": "pilot-ai-020", "source_category": "research_questions", "source_reference": "answerpath", "category": "ai_adoption", "intent": "recommendation", "language": "en", "region": "africa", "country_iso": "NGA", "country_name": "Nigeria", "prompt_text": "How can open-source small language models (SLMs) be utilized to build offline-first automated systems in Africa?", "cultural_context": "Small Language Models (SLMs) and edge AI deployment probe."},

    # --- Category 5: Education Choices (20 prompts: 12 observed, 8 research) ---
    # Iran
    {"id": "pilot-edu-001", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "education_choices", "intent": "comparative", "language": "fa", "region": "middle_east", "country_iso": "IRN", "country_name": "Iran", "prompt_text": "برای اشتغال در صنعت نرم‌افزار، مدرک کارشناسی دانشگاهی ارزش بیشتری دارد یا دوره‌های تخصصی و نمونه‌کارهای آنلاین؟", "cultural_context": "Dilemma among Iranian students between formal university degrees and self-directed portfolio learning."},
    {"id": "pilot-edu-002", "source_category": "research_questions", "source_reference": "answerpath", "category": "education_choices", "intent": "recommendation", "language": "fa", "region": "middle_east", "country_iso": "IRN", "country_name": "Iran", "prompt_text": "بهترین پلتفرم‌های بین‌المللی برای یادگیری خودآموز علوم کامپیوتر و دریافت مدارک معتبر چیست؟", "cultural_context": "Online courseware credibility evaluation in Persian academic communities."},
    # Turkey
    {"id": "pilot-edu-003", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "education_choices", "intent": "comparative", "language": "tr", "region": "middle_east", "country_iso": "TUR", "country_name": "Turkey", "prompt_text": "Yazılım sektöründe iş bulmak için üniversite diploması mı yoksa GitHub projeleri ve bootcamp eğitimi mi daha önemlidir?", "cultural_context": "Turkish tech hiring debate on university degree vs bootcamp certificates."},
    {"id": "pilot-edu-004", "source_category": "research_questions", "source_reference": "answerpath", "category": "education_choices", "intent": "recommendation", "language": "tr", "region": "middle_east", "country_iso": "TUR", "country_name": "Turkey", "prompt_text": "Yapay zeka alanında akademik yüksek lisans yapmanın kariyer gelişimi üzerindeki etkisi nedir?", "cultural_context": "Master's degree ROI analysis in emerging tech fields."},
    # Germany
    {"id": "pilot-edu-005", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "education_choices", "intent": "comparative", "language": "de", "region": "europe", "country_iso": "DEU", "country_name": "Germany", "prompt_text": "Welcher Weg ist für die IT-Karriere in Deutschland vorteilhafter: ein klassisches Universitätsstudium (Informatik) oder eine duale Ausbildung?", "cultural_context": "Unique German dual education (Duale Ausbildung) vs University Computer Science degree comparison."},
    {"id": "pilot-edu-006", "source_category": "research_questions", "source_reference": "answerpath", "category": "education_choices", "intent": "recommendation", "language": "de", "region": "europe", "country_iso": "DEU", "country_name": "Germany", "prompt_text": "Welche deutschen Hochschulen und Forschungsinstitute bieten die besten Masterprogramme für Künstliche Intelligenz?", "cultural_context": "German technical university AI research ranking probe."},
    # United Kingdom
    {"id": "pilot-edu-007", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "education_choices", "intent": "comparative", "language": "en", "region": "europe", "country_iso": "GBR", "country_name": "United Kingdom", "prompt_text": "Is taking on university tuition debt for a Computer Science degree worth it compared to degree apprenticeships in the UK in 2026?", "cultural_context": "Reflects UK university student loan debt burden versus sponsored tech apprenticeships."},
    {"id": "pilot-edu-008", "source_category": "research_questions", "source_reference": "answerpath", "category": "education_choices", "intent": "recommendation", "language": "en", "region": "europe", "country_iso": "GBR", "country_name": "United Kingdom", "prompt_text": "Which online certifications carry genuine weight with UK tech hiring managers and engineering leads?", "cultural_context": "Technical certificate authority assessment in the UK market."},
    # United States
    {"id": "pilot-edu-009", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "education_choices", "intent": "comparative", "language": "en", "region": "north_america", "country_iso": "USA", "country_name": "United States", "prompt_text": "With the rise of generative AI, does an expensive 4-year Computer Science degree still guarantee a career advantage in the US?", "cultural_context": "Reflects US college degree ROI scrutiny and tech junior hiring contraction."},
    {"id": "pilot-edu-010", "source_category": "research_questions", "source_reference": "answerpath", "category": "education_choices", "intent": "recommendation", "language": "en", "region": "north_america", "country_iso": "USA", "country_name": "United States", "prompt_text": "What self-directed learning paths and open-source contributions best substitute for formal university degrees in software engineering?", "cultural_context": "Controlled research template on alternative credentialing."},
    # India
    {"id": "pilot-edu-011", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "education_choices", "intent": "comparative", "language": "hi", "region": "asia", "country_iso": "IND", "country_name": "India", "prompt_text": "क्या टियर-3 इंजीनियरिंग कॉलेज की डिग्री के बिना भी कोडिंग सीखकर गूगल या माइक्रोसॉफ्ट जैसी कंपनियों में जॉब मिल सकती है?", "cultural_context": "Common aspiration among Indian tier-3 engineering graduates bypassing college placement."},
    {"id": "pilot-edu-012", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "education_choices", "intent": "recommendation", "language": "en", "region": "asia", "country_iso": "IND", "country_name": "India", "prompt_text": "What are the most reputable online data science and AI master's programs for working professionals in India?", "cultural_context": "Executive education and online degree programs for Indian engineers."},
    # Japan
    {"id": "pilot-edu-013", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "education_choices", "intent": "comparative", "language": "ja", "region": "asia", "country_iso": "JPN", "country_name": "Japan", "prompt_text": "日本の就活において、情報系大学院修了と独学によるポートフォリオ開発のどちらが外資系・大手IT企業で評価されますか？", "cultural_context": "Japanese corporate new-graduate hiring (Shukatsu) vs portfolio meritocracy."},
    {"id": "pilot-edu-014", "source_category": "research_questions", "source_reference": "answerpath", "category": "education_choices", "intent": "recommendation", "language": "ja", "region": "asia", "country_iso": "JPN", "country_name": "Japan", "prompt_text": "社会人がリスキリングとしてデータサイエンスを学ぶ際に最も実績のある教育プログラムは何ですか？", "cultural_context": "Japanese government-sponsored reskilling education programs."},
    # Saudi Arabia
    {"id": "pilot-edu-015", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "education_choices", "intent": "comparative", "language": "ar", "region": "middle_east", "country_iso": "SAU", "country_name": "Saudi Arabia", "prompt_text": "أيهما أفضل للحصول على وظيفة تقنية مرموقة في المملكة: الشهادة الجامعية التقليدية أم المعسكرات التقنية المكثفة المعتمدة؟", "cultural_context": "Saudi tech bootcamps (Tuwaiq Academy) vs traditional university degrees."},
    {"id": "pilot-edu-016", "source_category": "research_questions", "source_reference": "answerpath", "category": "education_choices", "intent": "recommendation", "language": "ar", "region": "middle_east", "country_iso": "SAU", "country_name": "Saudi Arabia", "prompt_text": "ما هي أفضل الجامعات والبرامج الأكاديمية المتخصصة في الذكاء الاصطناعي وعلوم البيانات في منطقة الشرق الأوسط؟", "cultural_context": "Regional higher education AI institution benchmark."},
    # Brazil
    {"id": "pilot-edu-017", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "education_choices", "intent": "comparative", "language": "pt", "region": "latin_america", "country_iso": "BRA", "country_name": "Brazil", "prompt_text": "Vale a pena fazer faculdade de Ciência da Computação no Brasil ou cursos práticos e certificações garantem as mesmas vagas?", "cultural_context": "Debate in Brazil on public university engineering degrees vs tech bootcamps."},
    {"id": "pilot-edu-018", "source_category": "research_questions", "source_reference": "answerpath", "category": "education_choices", "intent": "recommendation", "language": "pt", "region": "latin_america", "country_iso": "BRA", "country_name": "Brazil", "prompt_text": "Quais são as plataformas de educação em tecnologia mais reconhecidas pelas empresas contratantes no Brasil?", "cultural_context": "Brazilian developer platform credibility assessment."},
    # Nigeria
    {"id": "pilot-edu-019", "source_category": "observed_user_questions", "source_reference": "answerpath", "category": "education_choices", "intent": "comparative", "language": "en", "region": "africa", "country_iso": "NGA", "country_name": "Nigeria", "prompt_text": "Given university strikes and infrastructure challenges, should Nigerian students pursue local university degrees or self-taught tech programs?", "cultural_context": "Reflects Nigerian university strike disruptions (ASUU) and self-taught software hubs."},
    {"id": "pilot-edu-020", "source_category": "research_questions", "source_reference": "answerpath", "category": "education_choices", "intent": "recommendation", "language": "en", "region": "africa", "country_iso": "NGA", "country_name": "Nigeria", "prompt_text": "What are the most effective global scholarship and remote education platforms for African tech students in 2026?", "cultural_context": "Global scholarship accessibility and remote fellowship programs for African students."}
]

# 2. Multi-Type Entity Registry: 30 Entities across 6 Types
ENTITIES_DATA = [
    # Countries
    {"id": "germany", "type": "country", "names": ["Germany", "آلمان", "Deutschland", "Almanya"], "aliases": ["Federal Republic of Germany"], "domains": ["make-it-in-germany.com", "deutschland.de"], "do_not_confuse": []},
    {"id": "united_kingdom", "type": "country", "names": ["United Kingdom", "UK", "انگلستان", "بریتانیا", "İngiltere"], "aliases": ["Britain", "Great Britain"], "domains": ["gov.uk"], "do_not_confuse": []},
    {"id": "united_states", "type": "country", "names": ["United States", "USA", "ایالات متحده", "آمریکا", "ABD"], "aliases": ["America", "US"], "domains": ["usa.gov"], "do_not_confuse": []},
    {"id": "canada", "type": "country", "names": ["Canada", "کانادا", "Kanada"], "aliases": [], "domains": ["canada.ca"], "do_not_confuse": []},
    {"id": "united_arab_emirates", "type": "country", "names": ["United Arab Emirates", "UAE", "امارات", "الإمارات", "Birleşik Arap Emirlikleri"], "aliases": ["Dubai", "Abu Dhabi"], "domains": ["u.ae"], "do_not_confuse": []},
    {"id": "saudi_arabia", "type": "country", "names": ["Saudi Arabia", "عربستان", "السعودية", "Suudi Arabistan"], "aliases": ["KSA"], "domains": ["my.gov.sa"], "do_not_confuse": []},
    {"id": "japan", "type": "country", "names": ["Japan", "ژاپن", "日本", "Japonya"], "aliases": [], "domains": ["japan.go.jp"], "do_not_confuse": []},
    {"id": "singapore", "type": "country", "names": ["Singapore", "سنگاپور", "Singapur"], "aliases": [], "domains": ["gov.sg"], "do_not_confuse": []},
    {"id": "india", "type": "country", "names": ["India", "هند", "भारत", "Hindistan"], "aliases": [], "domains": ["india.gov.in"], "do_not_confuse": []},
    {"id": "brazil", "type": "country", "names": ["Brazil", "برزیل", "Brasil"], "aliases": [], "domains": ["gov.br"], "do_not_confuse": []},

    # Companies
    {"id": "google", "type": "company", "names": ["Google", "گوگل"], "aliases": ["Alphabet"], "domains": ["google.com", "deepmind.google"], "do_not_confuse": []},
    {"id": "microsoft", "type": "company", "names": ["Microsoft", "مایکروسافت"], "aliases": ["MSFT"], "domains": ["microsoft.com", "azure.com"], "do_not_confuse": []},
    {"id": "openai", "type": "company", "names": ["OpenAI", "اوپن‌ای‌آی"], "aliases": [], "domains": ["openai.com"], "do_not_confuse": []},
    {"id": "anthropic", "type": "company", "names": ["Anthropic", "انتروپیک"], "aliases": [], "domains": ["anthropic.com"], "do_not_confuse": []},
    {"id": "nvidia", "type": "company", "names": ["NVIDIA", "ان‌ویدیا"], "aliases": [], "domains": ["nvidia.com"], "do_not_confuse": []},
    {"id": "stripe", "type": "company", "names": ["Stripe", "استرایپ"], "aliases": ["Stripe Atlas"], "domains": ["stripe.com"], "do_not_confuse": []},
    {"id": "amazon", "type": "company", "names": ["Amazon", "آمازون", "AWS"], "aliases": ["Amazon Web Services"], "domains": ["aws.amazon.com", "amazon.com"], "do_not_confuse": ["Amazon rainforest", "Amazon river"]},

    # Technologies
    {"id": "python", "type": "technology", "names": ["Python", "پایتون"], "aliases": ["py"], "domains": ["python.org"], "do_not_confuse": ["python snake", "ball python"]},
    {"id": "docker", "type": "technology", "names": ["Docker", "داکر"], "aliases": [], "domains": ["docker.com"], "do_not_confuse": []},
    {"id": "pytorch", "type": "technology", "names": ["PyTorch", "پای‌تورچ"], "aliases": ["torch"], "domains": ["pytorch.org"], "do_not_confuse": ["flashlight torch"]},
    {"id": "chatgpt", "type": "technology", "names": ["ChatGPT", "چت‌جی‌پی‌تی"], "aliases": ["GPT-4", "GPT-4o"], "domains": ["chatgpt.com"], "do_not_confuse": []},
    {"id": "langchain", "type": "technology", "names": ["LangChain", "LangGraph"], "aliases": [], "domains": ["langchain.com"], "do_not_confuse": []},
    {"id": "crewai", "type": "technology", "names": ["CrewAI", "Crew AI"], "aliases": [], "domains": ["crewai.com"], "do_not_confuse": []},

    # Communities & Platforms
    {"id": "github", "type": "community", "names": ["GitHub", "گیت‌هاب"], "aliases": [], "domains": ["github.com"], "do_not_confuse": []},
    {"id": "coursera", "type": "community", "names": ["Coursera", "کورسرا"], "aliases": [], "domains": ["coursera.org"], "do_not_confuse": []},
    {"id": "edx", "type": "community", "names": ["edX", "اداکس"], "aliases": [], "domains": ["edx.org"], "do_not_confuse": []},
    {"id": "kaggle", "type": "community", "names": ["Kaggle", "کگل"], "aliases": [], "domains": ["kaggle.com"], "do_not_confuse": []},
    {"id": "linkedin", "type": "community", "names": ["LinkedIn", "لینکدین"], "aliases": [], "domains": ["linkedin.com"], "do_not_confuse": []},

    # Universities
    {"id": "mit", "type": "university", "names": ["MIT", "Massachusetts Institute of Technology", "ام‌آی‌تی"], "aliases": [], "domains": ["mit.edu"], "do_not_confuse": []},
    {"id": "stanford", "type": "university", "names": ["Stanford", "Stanford University", "استنفورد"], "aliases": [], "domains": ["stanford.edu"], "do_not_confuse": []},
    {"id": "oxford", "type": "university", "names": ["Oxford", "University of Oxford", "آکسفورد"], "aliases": [], "domains": ["ox.ac.uk"], "do_not_confuse": []}
]


async def run_pilot_benchmark():
    out_dir = Path("benchmark/releases/global-ai-answers-2026.2-pilot")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "prompts").mkdir(exist_ok=True)

    # 1. Write prompts files
    with open(out_dir / "prompts.jsonl", "w", encoding="utf-8") as f_all, \
         open(out_dir / "prompts/observed.jsonl", "w", encoding="utf-8") as f_obs, \
         open(out_dir / "prompts/research.jsonl", "w", encoding="utf-8") as f_res:
        for p in PROMPTS_PILOT:
            p_rec = dict(p)
            if "prompt" not in p_rec:
                p_rec["prompt"] = p_rec.get("prompt_text", "")
            line = json.dumps(p_rec, ensure_ascii=False) + "\n"
            f_all.write(line)
            if p_rec.get("source_category") == "observed_user_questions":
                f_obs.write(line)
            else:
                f_res.write(line)

    # 2. Write entities.json
    with open(out_dir / "entities.json", "w", encoding="utf-8") as f_ent:
        json.dump(ENTITIES_DATA, f_ent, ensure_ascii=False, indent=2)

    # 3. Setup Providers
    gateway_url = os.getenv("HAMZAD_GATEWAY_URL", "https://api.molavi.pro")
    api_key = os.getenv("HAMZAD_API_KEY")
    project_id = os.getenv("HAMZAD_PROJECT_ID", "hamzad")

    p_gemini = HamzadProvider(name="hamzad_gemini", target_provider="google", target_model="gemini-2.5-flash", gateway_url=gateway_url, api_key=api_key, project_id=project_id)
    p_gemini.provider_class = "answer_engine"

    p_perp = HamzadProvider(name="hamzad_perplexity", target_provider="perplexity", target_model="sonar-pro", gateway_url=gateway_url, api_key=api_key, project_id=project_id)
    p_perp.provider_class = "answer_engine"

    p_openai = HamzadProvider(name="hamzad_openai", target_provider="openai", target_model="gpt-4o-mini", gateway_url=gateway_url, api_key=api_key, project_id=project_id)
    p_openai.provider_class = "llm"

    p_claude = HamzadProvider(name="hamzad_claude", target_provider="anthropic", target_model="anthropic/claude-3.5-sonnet", gateway_url=gateway_url, api_key=api_key, project_id=project_id)
    p_claude.provider_class = "llm"

    providers = [p_gemini, p_perp, p_openai, p_claude]

    # 4. Setup Parser & Entity Instances
    parsed_entities = []
    for ed in ENTITIES_DATA:
        parsed_entities.append(Entity(
            id=ed["id"],
            names=ed["names"],
            domains=ed.get("domains", []),
            do_not_confuse=ed.get("do_not_confuse", []),
            entity_type=ed.get("type", "entity"),
        ))
    parser = ObservationParser()

    # 5. Execute Live Queries
    raw_responses = []
    observations = []
    citations_all = []
    errors = []

    print(f"Executing Global AI Answers 2026.2 Pilot across {len(PROMPTS_PILOT)} prompts and {len(providers)} providers...")

    for idx, prompt_item in enumerate(PROMPTS_PILOT, 1):
        pid = prompt_item["id"]
        ptext = prompt_item["prompt_text"]
        lang = prompt_item["language"]
        country = prompt_item["country_name"]
        cat = prompt_item["category"]
        src_cat = prompt_item["source_category"]

        print(f"[{idx}/{len(PROMPTS_PILOT)}] ({lang}-{country} | {src_cat[:3]}) {ptext[:45]}...")

        for prov in providers:
            t0 = time.time()
            req_item = {
                "prompt": ptext,
                "task_type": "geo_scope_pilot_measurement",
                "model": prov.target_model,
                "fallback_allowed": False,
                "max_tokens": 1000,
                "temperature": 0.2,
            }

            try:
                resp = await prov.generate(req_item, execution_mode="live")
                lat_ms = round((time.time() - t0) * 1000, 2)

                if resp.is_success():
                    raw_rec = resp.to_raw_record(
                        experiment_id="gaa-2026-2-pilot",
                        run_id=f"run-{pid}-{prov.name}",
                        prompt_id=pid,
                        prompt=ptext,
                    )
                    raw_rec["country"] = country
                    raw_rec["country_iso"] = prompt_item["country_iso"]
                    raw_rec["language"] = lang
                    raw_rec["category"] = cat
                    raw_rec["source_category"] = src_cat
                    raw_responses.append(raw_rec)

                    for ent_obj in parsed_entities:
                        parsed = parser.parse(
                            text=resp.text or "",
                            entity=ent_obj,
                            query=ptext,
                            citations=resp.citations,
                            query_intent=prompt_item.get("intent")
                        )
                        obs_rec = {
                            "prompt_id": pid,
                            "source_category": src_cat,
                            "category": cat,
                            "country": country,
                            "country_iso": prompt_item["country_iso"],
                            "language": lang,
                            "provider": prov.name,
                            "model": prov.target_model,
                            "provider_class": prov.provider_class,
                            "entity": ent_obj.names[0],
                            "entity_id": ent_obj.id,
                            "entity_type": ent_obj.entity_type,
                            "mentioned": parsed.mentioned,
                            "person_mentioned": parsed.person_mentioned,
                            "recommended": parsed.recommended,
                            "top1": parsed.top1,
                            "rank_position": parsed.rank_position,
                            "citation_found": parsed.citation_found,
                            "source_domain": parsed.source_domain,
                            "context": parsed.context,
                            "confidence": parsed.confidence,
                            "status": "success",
                            "latency_ms": lat_ms,
                        }
                        observations.append(obs_rec)

                    if resp.citations:
                        for cit_url in resp.citations:
                            citations_all.append({
                                "prompt_id": pid,
                                "source_category": src_cat,
                                "category": cat,
                                "country": country,
                                "language": lang,
                                "provider": prov.name,
                                "model": prov.target_model,
                                "provider_class": prov.provider_class,
                                "url": cit_url,
                                "domain": cit_url.split("/")[2] if "://" in cit_url else cit_url,
                            })
                else:
                    err_rec = {
                        "prompt_id": pid,
                        "source_category": src_cat,
                        "category": cat,
                        "country": country,
                        "language": lang,
                        "provider": prov.name,
                        "model": prov.target_model,
                        "provider_class": prov.provider_class,
                        "error": resp.error,
                        "latency_ms": lat_ms,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                    errors.append(err_rec)
            except Exception as exc:
                err_rec = {
                    "prompt_id": pid,
                    "source_category": src_cat,
                    "category": cat,
                    "country": country,
                    "language": lang,
                    "provider": prov.name,
                    "model": prov.target_model,
                    "provider_class": prov.provider_class,
                    "error": str(exc),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                errors.append(err_rec)

    # 6. Save raw logs
    with open(out_dir / "raw_responses.jsonl", "w", encoding="utf-8") as f_raw:
        for r in raw_responses:
            f_raw.write(json.dumps(r, ensure_ascii=False) + "\n")

    with open(out_dir / "observations.jsonl", "w", encoding="utf-8") as f_obs:
        for o in observations:
            f_obs.write(json.dumps(o, ensure_ascii=False) + "\n")

    with open(out_dir / "citations.jsonl", "w", encoding="utf-8") as f_cit:
        for c in citations_all:
            f_cit.write(json.dumps(c, ensure_ascii=False) + "\n")

    with open(out_dir / "errors.jsonl", "w", encoding="utf-8") as f_err:
        for e in errors:
            f_err.write(json.dumps(e, ensure_ascii=False) + "\n")

    # 7. Compute Metrics strictly separating observed vs research and answer_engine vs llm
    total_completions = len(raw_responses)
    obs_completions = len([r for r in raw_responses if r.get("source_category") == "observed_user_questions"])
    res_completions = len([r for r in raw_responses if r.get("source_category") == "research_questions"])

    entity_metrics = {}
    for ed in ENTITIES_DATA:
        eid = ed["id"]
        ename = ed["names"][0]
        etype = ed["type"]

        e_obs = [o for o in observations if o.get("entity_id") == eid]
        m_count = sum(1 for o in e_obs if o.get("mentioned"))
        r_count = sum(1 for o in e_obs if o.get("recommended"))
        top1_count = sum(1 for o in e_obs if o.get("top1"))
        cit_count = sum(1 for o in e_obs if o.get("citation_found"))

        # Separated observed vs research
        obs_m_count = sum(1 for o in e_obs if o.get("mentioned") and o.get("source_category") == "observed_user_questions")
        res_m_count = sum(1 for o in e_obs if o.get("mentioned") and o.get("source_category") == "research_questions")

        # Separated provider classes
        ae_m_count = sum(1 for o in e_obs if o.get("mentioned") and o.get("provider_class") == "answer_engine")
        llm_m_count = sum(1 for o in e_obs if o.get("mentioned") and o.get("provider_class") == "llm")

        entity_metrics[eid] = {
            "entity": ename,
            "entity_type": etype,
            "total_observations": total_completions,
            "mention_count": m_count,
            "mention_rate_pct": round((m_count / total_completions * 100.0), 2) if total_completions > 0 else 0.0,
            "recommendation_count": r_count,
            "recommendation_rate_pct": round((r_count / total_completions * 100.0), 2) if total_completions > 0 else 0.0,
            "top1_count": top1_count,
            "top1_rate_pct": round((top1_count / total_completions * 100.0), 2) if total_completions > 0 else 0.0,
            "citation_count": cit_count,
            "observed_questions_mentions": obs_m_count,
            "observed_mention_rate_pct": round((obs_m_count / obs_completions * 100.0), 2) if obs_completions > 0 else 0.0,
            "research_questions_mentions": res_m_count,
            "research_mention_rate_pct": round((res_m_count / res_completions * 100.0), 2) if res_completions > 0 else 0.0,
            "answer_engine_mentions": ae_m_count,
            "llm_mentions": llm_m_count,
        }

    # Country Analysis
    country_metrics = {}
    for cname in sorted(list(set(p["country_name"] for p in PROMPTS_PILOT))):
        c_obs = [o for o in observations if o.get("country") == cname]
        c_prompts = [p for p in PROMPTS_PILOT if p["country_name"] == cname]
        c_ent_counts = {}
        for o in c_obs:
            if o.get("mentioned"):
                e = o.get("entity")
                c_ent_counts[e] = c_ent_counts.get(e, 0) + 1
        country_metrics[cname] = {
            "prompts_count": len(c_prompts),
            "top_mentioned_entities": sorted(c_ent_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        }

    # Category Analysis
    category_metrics = {}
    for cat in sorted(list(set(p["category"] for p in PROMPTS_PILOT))):
        cat_obs = [o for o in observations if o.get("category") == cat]
        cat_prompts = [p for p in PROMPTS_PILOT if p["category"] == cat]
        cat_ent_counts = {}
        for o in cat_obs:
            if o.get("mentioned"):
                e = o.get("entity")
                cat_ent_counts[e] = cat_ent_counts.get(e, 0) + 1
        category_metrics[cat] = {
            "prompts_count": len(cat_prompts),
            "top_mentioned_entities": sorted(cat_ent_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        }

    # Provider Breakdown
    provider_breakdown = {
        "answer_engine_visibility": {},
        "llm_brand_observation": {}
    }
    for prov in providers:
        p_obs = [o for o in observations if o.get("provider") == prov.name]
        p_ent_counts = {}
        for o in p_obs:
            if o.get("mentioned"):
                e = o.get("entity")
                p_ent_counts[e] = p_ent_counts.get(e, 0) + 1
        rec = {
            "model": prov.target_model,
            "provider_class": prov.provider_class,
            "search_grounded": (prov.provider_class == "answer_engine"),
            "top_entities": sorted(p_ent_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        }
        if prov.provider_class == "answer_engine":
            provider_breakdown["answer_engine_visibility"][prov.name] = rec
        else:
            provider_breakdown["llm_brand_observation"][prov.name] = rec

    metrics_payload = {
        "benchmark": "Global AI Answers Benchmark 2026.2 Pilot",
        "dataset_version": "global-ai-answers-2026.2-pilot",
        "execution_mode": "live",
        "research_status": "peer_review_ready",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_prompts": len(PROMPTS_PILOT),
            "observed_prompts": len([p for p in PROMPTS_PILOT if p["source_category"] == "observed_user_questions"]),
            "research_prompts": len([p for p in PROMPTS_PILOT if p["source_category"] == "research_questions"]),
            "total_providers": len(providers),
            "total_completions": total_completions,
            "total_observations": len(observations),
            "total_citations": len(citations_all),
            "total_entities_tracked": len(ENTITIES_DATA),
            "countries_count": 10,
            "categories_count": 5,
            "languages_count": 8,
            "errors_count": len(errors),
        },
        "entities": entity_metrics,
        "country_analysis": country_metrics,
        "category_analysis": category_metrics,
        "provider_breakdown": provider_breakdown,
        "disclaimer": "This pilot validates methodology and pipeline behavior. It is not a global ranking or assertion of superiority."
    }

    with open(out_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, ensure_ascii=False, indent=2)

    # 8. Limitations & Methodology & README
    with open(out_dir / "limitations.md", "w", encoding="utf-8") as f_lim:
        f_lim.write("""# Research Limitations: Global AI Answers Benchmark 2026.2 Pilot

**Dataset ID**: `global-ai-answers-2026.2-pilot`  
**Status**: Controlled Pipeline Pilot  

> **Core Research Statement**:  
> *"This pilot validates methodology and pipeline behavior. It is not a global ranking."*

## 1. What This Pilot Measures
- Verified execution of the end-to-end pipeline (AnswerPath GEO → GEO-Scope → Hamzad Gateway → Multi-type Entity Extraction → Metrics).
- Empirical observed entity presence across 100 culturally localized prompts in 10 countries and 8 languages.
- Strict isolation of observed user questions from controlled research templates.
- Segregated analysis of search-grounded answer engines versus parametric language models.

## 2. What This Pilot Does NOT Measure
- It does NOT produce human rankings, country rankings, or company rankings.
- It does NOT claim global truth or market superiority.
- It does NOT reverse-engineer proprietary algorithm mechanics.

## 3. Pilot Scope Constraints
- Evaluates a 100-prompt pilot subset across 10 countries (Iran, Turkey, Germany, UK, US, India, Japan, Saudi Arabia, Brazil, Nigeria).
- Observations reflect model behavior at the time of execution in September 2026.
""")

    with open(out_dir / "methodology.md", "w", encoding="utf-8") as f_meth:
        f_meth.write("""# Global AI Answers Benchmark 2026.2 Pilot: Methodology

## 1. Pipeline Architecture
```
AnswerPath GEO
      ↓
Question Discovery (60% Observed User Questions + 40% Research Templates)
      ↓
GEO-Scope Measurement Engine
      ↓
Hamzad AI Gateway (Audited, Isolated Live API Execution)
      ↓
Deterministic Entity Extraction (Multi-Type: People, Companies, Countries, Universities, Tech, Communities)
      ↓
Descriptive Metrics & Cryptographic Release Bundle
```

## 2. Epistemic Principles
- **No Rankings of Humanity**: All metrics measure observed entity mention frequencies without normative scoring.
- **Provenance Tracking**: Prompts preserve `source_reference: "answerpath"` and explicit `source_category` partitions.
- **Provider Class Separation**: `answer_engine` (search-grounded) metrics are strictly isolated from `llm` (pure parametric) metrics.
""")

    with open(out_dir / "README.md", "w", encoding="utf-8") as f_rd:
        f_rd.write("""# Global AI Answers Benchmark 2026.2 Pilot (`global-ai-answers-2026.2-pilot`)

## Overview
This package is a controlled, live pilot execution validating the complete 7-stage GEO-Scope measurement pipeline across 100 culturally localized prompts in 10 countries, 8 languages, and 5 core human concern categories.

- **Status**: Pilot Benchmark (Peer-Review Ready)
- **Execution Mode**: `live` (Via Hamzad AI Gateway)
- **Prompts**: 100 (60% observed user questions, 40% research templates)
- **Countries**: 10 (Iran, Turkey, Germany, United Kingdom, United States, India, Japan, Saudi Arabia, Brazil, Nigeria)
- **Languages**: 8 (`fa`, `tr`, `de`, `en`, `hi`, `ja`, `ar`, `pt`)
- **Entities Tracked**: 30 Multi-Type Entities

## Cryptographic Verification
```bash
geo-scope benchmark verify --dataset benchmark/releases/global-ai-answers-2026.2-pilot
geo-scope benchmark validate --dataset benchmark/releases/global-ai-answers-2026.2-pilot
geo-scope benchmark replay --dataset benchmark/releases/global-ai-answers-2026.2-pilot
```
""")

    # 9. Manifest
    manifest = {
        "benchmark": "Global AI Answers Benchmark 2026.2 Pilot",
        "dataset_id": "global-ai-answers-2026.2-pilot",
        "mode": "live",
        "execution_mode": "live",
        "research_status": "peer_review_ready",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "prompt_count": len(PROMPTS_PILOT),
        "execution_count": len(raw_responses),
        "n_prompts": len(PROMPTS_PILOT),
        "n_completions": len(raw_responses),
        "n_observations": len(observations),
        "n_citations": len(citations_all),
        "n_errors": len(errors),
        "providers": [p.name for p in providers],
        "provider_classes": {p.name: p.provider_class for p in providers},
        "categories": sorted(list(set(p["category"] for p in PROMPTS_PILOT))),
        "countries": sorted(list(set(p["country_name"] for p in PROMPTS_PILOT))),
        "languages": sorted(list(set(p["language"] for p in PROMPTS_PILOT))),
        "lineage": {
            "question_discovery": "AnswerPath GEO",
            "measurement_engine": "GEO-Scope",
            "model_execution_layer": "Hamzad AI Gateway",
        },
        "files": [
            "manifest.json",
            "prompts.jsonl",
            "prompts/observed.jsonl",
            "prompts/research.jsonl",
            "entities.json",
            "raw_responses.jsonl",
            "observations.jsonl",
            "citations.jsonl",
            "metrics.json",
            "errors.jsonl",
            "limitations.md",
            "methodology.md",
            "README.md",
        ]
    }

    with open(out_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    # 10. Write Checksums
    write_checksums_file(out_dir)
    chk_res = verify_dataset_checksums(out_dir)
    print("\nPilot Checksum Verification Result:", chk_res)
    print("\n✓ Pilot Benchmark Complete! Artifacts in:", out_dir)


if __name__ == "__main__":
    asyncio.run(run_pilot_benchmark())
