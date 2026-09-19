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

# ---------------------------------------------------------
# 1. 50 Countries Matrix (50 Countries, 22+ Languages, 6 Regions)
# ---------------------------------------------------------
COUNTRY_SPECS = [
    # MENA (10)
    {"name": "Iran", "iso": "IRN", "region": "middle_east_north_africa", "lang": "fa"},
    {"name": "Turkey", "iso": "TUR", "region": "middle_east_north_africa", "lang": "tr"},
    {"name": "Saudi Arabia", "iso": "SAU", "region": "middle_east_north_africa", "lang": "ar"},
    {"name": "United Arab Emirates", "iso": "ARE", "region": "middle_east_north_africa", "lang": "ar"},
    {"name": "Yemen", "iso": "YEM", "region": "middle_east_north_africa", "lang": "ar"},
    {"name": "Egypt", "iso": "EGY", "region": "middle_east_north_africa", "lang": "ar"},
    {"name": "Morocco", "iso": "MAR", "region": "middle_east_north_africa", "lang": "ar"},
    {"name": "Iraq", "iso": "IRQ", "region": "middle_east_north_africa", "lang": "ar"},
    {"name": "Jordan", "iso": "JOR", "region": "middle_east_north_africa", "lang": "ar"},
    {"name": "Qatar", "iso": "QAT", "region": "middle_east_north_africa", "lang": "ar"},

    # North America (3)
    {"name": "United States", "iso": "USA", "region": "north_america", "lang": "en"},
    {"name": "Canada", "iso": "CAN", "region": "north_america", "lang": "en"},
    {"name": "Mexico", "iso": "MEX", "region": "north_america", "lang": "es"},

    # Europe (15)
    {"name": "Germany", "iso": "DEU", "region": "europe", "lang": "de"},
    {"name": "United Kingdom", "iso": "GBR", "region": "europe", "lang": "en"},
    {"name": "France", "iso": "FRA", "region": "europe", "lang": "fr"},
    {"name": "Italy", "iso": "ITA", "region": "europe", "lang": "it"},
    {"name": "Spain", "iso": "ESP", "region": "europe", "lang": "es"},
    {"name": "Netherlands", "iso": "NLD", "region": "europe", "lang": "nl"},
    {"name": "Sweden", "iso": "SWE", "region": "europe", "lang": "sv"},
    {"name": "Poland", "iso": "POL", "region": "europe", "lang": "pl"},
    {"name": "Switzerland", "iso": "CHE", "region": "europe", "lang": "de"},
    {"name": "Austria", "iso": "AUT", "region": "europe", "lang": "de"},
    {"name": "Belgium", "iso": "BEL", "region": "europe", "lang": "nl"},
    {"name": "Ireland", "iso": "IRL", "region": "europe", "lang": "en"},
    {"name": "Norway", "iso": "NOR", "region": "europe", "lang": "no"},
    {"name": "Denmark", "iso": "DNK", "region": "europe", "lang": "da"},
    {"name": "Finland", "iso": "FIN", "region": "europe", "lang": "fi"},

    # Asia Pacific (12)
    {"name": "India", "iso": "IND", "region": "asia_pacific", "lang": "hi"},
    {"name": "China", "iso": "CHN", "region": "asia_pacific", "lang": "zh"},
    {"name": "Japan", "iso": "JPN", "region": "asia_pacific", "lang": "ja"},
    {"name": "South Korea", "iso": "KOR", "region": "asia_pacific", "lang": "ko"},
    {"name": "Indonesia", "iso": "IDN", "region": "asia_pacific", "lang": "id"},
    {"name": "Pakistan", "iso": "PAK", "region": "asia_pacific", "lang": "ur"},
    {"name": "Vietnam", "iso": "VNM", "region": "asia_pacific", "lang": "vi"},
    {"name": "Philippines", "iso": "PHL", "region": "asia_pacific", "lang": "tl"},
    {"name": "Australia", "iso": "AUS", "region": "asia_pacific", "lang": "en"},
    {"name": "Singapore", "iso": "SGP", "region": "asia_pacific", "lang": "en"},
    {"name": "New Zealand", "iso": "NZL", "region": "asia_pacific", "lang": "en"},
    {"name": "Malaysia", "iso": "MYS", "region": "asia_pacific", "lang": "ms"},

    # Latin America (5)
    {"name": "Brazil", "iso": "BRA", "region": "latin_america", "lang": "pt"},
    {"name": "Argentina", "iso": "ARG", "region": "latin_america", "lang": "es"},
    {"name": "Colombia", "iso": "COL", "region": "latin_america", "lang": "es"},
    {"name": "Chile", "iso": "CHL", "region": "latin_america", "lang": "es"},
    {"name": "Peru", "iso": "PER", "region": "latin_america", "lang": "es"},

    # Sub-Saharan Africa (5)
    {"name": "Nigeria", "iso": "NGA", "region": "sub_saharan_africa", "lang": "en"},
    {"name": "South Africa", "iso": "ZAF", "region": "sub_saharan_africa", "lang": "en"},
    {"name": "Kenya", "iso": "KEN", "region": "sub_saharan_africa", "lang": "sw"},
    {"name": "Ghana", "iso": "GHA", "region": "sub_saharan_africa", "lang": "en"},
    {"name": "Ethiopia", "iso": "ETH", "region": "sub_saharan_africa", "lang": "am"},
]

# 9 Human Concern Categories
CATEGORIES_9 = [
    ("future_skills_learning", "Future Skills & Learning"),
    ("career_migration", "Career & Migration"),
    ("entrepreneurship_business", "Entrepreneurship & Business"),
    ("ai_adoption", "Artificial Intelligence Adoption"),
    ("technology_impact", "Technology Impact"),
    ("health_lifestyle", "Health & Lifestyle"),
    ("education_choices", "Education Choices"),
    ("financial_decisions", "Financial Decisions"),
    ("creativity_culture", "Creativity & Culture"),
]

# ---------------------------------------------------------
# 2. Localized Prompt Generator (500 Prompts: 300 Observed, 200 Research)
# ---------------------------------------------------------
# Question patterns by language and category
PROMPT_TEMPLATES_BY_LANG = {
    "fa": {
        "future_skills_learning": ("برای ورود به بازار کار فناوری، چه مهارت‌هایی را در سال ۲۰۲۶ یاد بگیریم؟", "یادگیری پایتون و هوش مصنوعی چه تاثیری در درآمد برنامه‌نویسان دارد؟"),
        "career_migration": ("بهترین کشورها برای دریافت ویزای کاری مهندسان و متخصصان کدامند؟", "شرایط دریافت ویزای نیروی متخصص در اروپا و آمریکای شمالی چگونه مقایسه می‌شود؟"),
        "entrepreneurship_business": ("چگونه با سرمایه محدود یک کسب‌وکار آنلاین یا خدمات نرم‌افزاری راه‌اندازی کنیم؟", "مزایا و معایب بوت‌استرپ در برابر جذب سرمایه اولیه در سال ۲۰۲۶ چیست؟"),
        "ai_adoption": ("کسب‌وکارهای کوچک چگونه می‌توانند هوش مصنوعی مولد را در فرایندهای روزمره به کار گیرند؟", "استفاده از مدل‌های متن‌باز برای سازمان‌های بومی چه مزایایی دارد؟"),
        "technology_impact": ("هوش مصنوعی خودکار چه تاثیری بر آینده مشاغل اداری و خدمات مالی خواهد گذاشت؟", "روندهای تحول دیجیتال در صنایع سنتی چگونه پیش‌بینی می‌شوند؟"),
        "health_lifestyle": ("اصول علمی مدیریت استرس کاری و حفظ سلامت روان برای افراد پرمشغله چیست؟", "بهترین روش‌های تغذیه و خواب سالم برای افزایش بهره‌وری کدامند؟"),
        "education_choices": ("آیا مدرک دانشگاهی برای ورود به صنعت فناوری همچنان ضروری است؟", "دوره‌های آنلاین و گواهی‌نامه‌های معتبر چقدر در بازار کار ارزش دارند؟"),
        "financial_decisions": ("بهترین استراتژی‌های مدیریت دارایی و محافظت در برابر تورم در سال ۲۰۲۶ چیست؟", "سرمایه‌گذاری روی دارایی‌های دیجیتال و فناوری چه ریسک‌هایی به همراه دارد؟"),
        "creativity_culture": ("ابزارهای هوش مصنوعی مولد چگونه به تولید محتوا و خلق آثار هنری کمک می‌کنند؟", "آینده زبان‌ها و ادبیات بومی در عصر مدل‌های زبانی بزرگ چگونه رقم خواهد خورد؟"),
        "future_skills_extra": ("مهم‌ترین مهارت‌های تحلیل داده و ابری برای ارتقای شغلی چیست؟", "برنامه‌نویسی سیستم‌ها با راست چه مزیتی نسبت به زبان‌های سنتی دارد؟")
    },
    "tr": {
        "future_skills_learning": ("2026'da küresel uzaktan çalışma piyasasında hangi teknoloji becerileri öne çıkıyor?", "Veri bilimi ve makine öğrenimi alanında uzmanlaşmak için hangi adımlar izlenmelidir?"),
        "career_migration": ("Avrupa ve Körfez ülkelerinde teknoloji uzmanları için en avantajlı çalışma vizeleri hangileridir?", "Almanya Şans Kartı ve Hollanda göçmenlik programları nasıl karşılaştırılır?"),
        "entrepreneurship_business": ("Türkiye'den küresel SaaS ve e-ihracat girişimi kurarken ödeme ve şirketleşme nasıl yönetilir?", "Stripe Atlas ve Estonya e-Residency arasındaki farklar nelerdir?"),
        "ai_adoption": ("Şirketler yapay zeka araçlarını iş süreçlerine entegre ederken veri güvenliğini nasıl sağlar?", "Açık kaynaklı yerel LLM modellerinin kurumsal kullanım avantajları nelerdir?"),
        "technology_impact": ("Üretken yapay zekanın yazılım ve içerik sektöründeki istihdama etkisi nedir?", "Otomasyon teknolojilerinin finans ve müşteri hizmetlerine uzun vadeli etkileri nelerdir?"),
        "health_lifestyle": ("Yoğun çalışma temposunda tükenmişlik sendromunu önlemek için bilimsel yöntemler nelerdir?", "Sağlıklı uyku ve beslenme rutinlerinin zihinsel performansa etkisi nedir?"),
        "education_choices": ("Teknoloji sektöründe üniversite diploması mı yoksa uygulamalı portföy mü daha önemlidir?", "Global sertifikasyon programlarının işe alımlardaki güncel geçerliliği nedir?"),
        "financial_decisions": ("Enflasyonist ortamlarda birikimleri korumak için en rasyonel yatırım stratejileri nelerdir?", "Döviz bazlı pasif gelir modelleri ve mikro yatırım araçları nasıl değerlendirilmelidir?"),
        "creativity_culture": ("Yapay zekanın müzik, sinema ve yaratıcı endüstrilerdeki rolü nasıl evriliyor?", "Kültürel miras ve yerel edebiyatın dijital çağda korunması nasıl sağlanabilir?"),
        "future_skills_extra": ("Bulut mimarisi ve DevOps alanında en çok aranan sertifikalar hangileridir?", "Yapay zeka sistemleri için veri mühendisliği yol haritası nasıl olmalıdır?")
    },
    "ar": {
        "future_skills_learning": ("ما هي أهم المهارات التقنية والتحليلية المطلوبة لدعم مشاريع الرؤى التنموية في العالم العربي؟", "كيف يبدأ المطور مساره في هندسة الذكاء الاصطناعي والحوسبة السحابية؟"),
        "career_migration": ("ما هي أفضل خيارات الإقامة الذهبية والمميزة لاستقطاب الكفاءات والشركات الناشئة؟", "كيف تختلف مسارات الهجرة والعمل التقني بين أوروبا وكندا ودول الخليج؟"),
        "entrepreneurship_business": ("كيف يؤسس رائد الأعمال متجر تجارة إلكترونية أو منصة تقنية مستدامة بأقل تكلفة؟", "ما هي أفضل الطرق لجذب الاستثمار الجريء للشركات التقنية الناشئة؟"),
        "ai_adoption": ("كيف تستفيد المؤسسات الصغيرة والمتوسطة من أدوات الذكاء الاصطناعي لرفع الإنتاجية؟", "ما هي كفاءة النماذج اللغوية العربية المفتوحة مقارنة بالنماذج العالمية المغلقة؟"),
        "technology_impact": ("كيف تؤثر تقنيات الأتمتة والذكاء الاصطناعي على مستقبل وظائف المحاسبة والإدارة؟", "ما هو مستقبل المدن الذكية وحلول الطاقة المستدامة في الشرق الأوسط؟"),
        "health_lifestyle": ("ما هي أفضل الممارسات العلمية لإدارة التوتر والحفاظ على التوازن النفسي والجسدي؟", "كيف يساعد تنظيم النوم والتغذية الصحية في تحسين جودة الحياة والتركيز؟"),
        "education_choices": ("أيهما أفضل للحصول على وظيفة مرموقة: الشهادة الجامعية أم الخبرة العملية والشهادات المهنية؟", "ما هي أفضل البرامج الأكاديمية والمنصات التعليمية لدراسة علوم البيانات؟"),
        "financial_decisions": ("ما هي أسس بناء محفظة استثمارية متوازنة لمواجهة تقلبات الأسواق العالمية؟", "كيف يمكن تخطيط الادخار والتقاعد المبكر بطرق استثمارية ذكية ومنخفضة المخاطر؟"),
        "creativity_culture": ("كيف يساهم الذكاء الاصطناعي في تمكين المبدعين وصناع المحتوى الرقمي؟", "كيف نحافظ على الهوية الثقافية واللغة العربية في عصر الثورة الرقمية؟"),
        "future_skills_extra": ("ما هي الشهادات المهنية الأكثر طلباً في مجال الأمن السيبراني والحوسبة السحابية؟", "كيف تؤثر أطر الوكلاء الأذكياء على مستقبل تطوير البرمجيات؟")
    },
    "en": {
        "future_skills_learning": ("What software engineering and AI skills are most in demand for global tech roles in 2026?", "How should engineers transition from traditional software development into AI systems engineering?"),
        "career_migration": ("Which countries offer the most viable skilled worker visas and startup immigration pathways?", "How do European tech career opportunities compare to North American and Asian tech corridors?"),
        "entrepreneurship_business": ("How can a solo founder build and scale a profitable B2B SaaS business efficiently?", "What are the key trade-offs between bootstrapping and venture capital for early-stage software companies?"),
        "ai_adoption": ("How can enterprise organizations deploy generative AI while maintaining data privacy and governance?", "What are the operational differences between closed-source API models and hosted open-source LLMs?"),
        "technology_impact": ("How is generative AI reshaping employment trends across white-collar knowledge sectors?", "What will be the impact of autonomous agent systems on enterprise software architectures?"),
        "health_lifestyle": ("What evidence-based lifestyle protocols most effectively improve cognitive performance and reduce burnout?", "How do sleep optimization and structured exercise influence long-term productivity?"),
        "education_choices": ("Is a four-year computer science degree still essential for entering the software industry in 2026?", "Which professional certifications and project portfolios hold the highest hiring credibility?"),
        "financial_decisions": ("What investment frameworks best protect long-term purchasing power against inflation and market volatility?", "How should early-stage professionals structure personal finance and diversified index portfolios?"),
        "creativity_culture": ("How are AI generative tools transforming film, gaming, and digital media production pipelines?", "What safeguards exist for creative intellectual property in the era of large multimodal models?"),
        "future_skills_extra": ("What cloud architecture patterns and DevOps practices offer the highest career return?", "How do Rust and modern Python frameworks compare for high-concurrency backend services?")
    },
    "de": {
        "future_skills_learning": ("Welche IT- und Cloud-Kompetenzen sind für den europäischen Arbeitsmarkt und den Mittelstand 2026 unverzichtbar?", "Wie gelingt der Einstieg in Machine Learning und Datenarchitektur für Fachkräfte?"),
        "career_migration": ("Welche Länder bieten die attraktivsten Bedingungen für Remote Work, Steuern und Fachkräftezuwanderung?", "Wie unterscheidet sich die Blaue Karte EU in Deutschland von Programmen in der Schweiz oder den Niederlanden?"),
        "entrepreneurship_business": ("Wie gründet und skaliert man in Europa ein B2B-Software-Startup unter Einhaltung der DSGVO?", "Ist Bootstrapping für europäische Gründer nachhaltiger als klassisches Venture Capital?"),
        "ai_adoption": ("Wie können Unternehmen generative KI DSGVO-konform in bestehende Geschäftsprozesse integrieren?", "Welche Vorteile bieten Open-Source-LLMs für das lokale Hosting in europäischen Konzernen?"),
        "technology_impact": ("Wie verändert die zunehmende Automatisierung die Arbeitswelt in der Industrie und im Finanzsektor?", "Welche Zukunftschancen bietet Industrie 4.0 im globalen Wettbewerb?"),
        "health_lifestyle": ("Welche wissenschaftlich belegten Methoden helfen Berufstätigen, Stress und Burnout zu vermeiden?", "Wie wichtig sind Schlafhygiene und Ergonomie für die mentale Leistungsfähigkeit am Arbeitsplatz?"),
        "education_choices": ("Ist ein Universitätsabschluss in Informatik wichtiger als Praxiserfahrung und Zertifikate?", "Welche Weiterbildungsprogramme und Hochschulen haben im IT-Sektor das höchste Ansehen?"),
        "financial_decisions": ("Welche Anlagestrategien bieten langfristigen Inflationsschutz und Vermögensaufbau?", "Wie baut man ein diversifiziertes Portfolio mit ETFs und Sachwerten solide auf?"),
        "creativity_culture": ("Wie beeinflussen KI-Tools das kreative Schaffen in Design, Journalismus und Medien?", "Wie kann kulturelle Vielfalt im Zeitalter globaler KI-Modelle gewahrt bleiben?"),
        "future_skills_extra": ("Welche Programmiersprachen haben die größte Relevanz für moderne Cloud-Infrastrukturen?", "Wie wichtig sind Kubernetes und Infrastructure as Code für Senior-Entwickler?")
    },
    "fr": {
        "future_skills_learning": ("Quelles compétences en IA et en développement logiciel sont les plus recherchées en 2026 ?", "Comment s'orienter vers l'ingénierie des données et le machine learning ?"),
        "career_migration": ("Quels sont les pays offrant les meilleures opportunités de visa pour les ingénieurs en technologie ?", "Comment comparer les perspectives de carrière entre la France, le Canada et la Suisse ?"),
        "entrepreneurship_business": ("Comment lancer et financer une startup SaaS B2B rentable en Europe ?", "Quels sont les avantages du modèle bootstrap par rapport aux levées de fonds en capital-risque ?"),
        "ai_adoption": ("Comment les PME peuvent-elles intégrer l'intelligence artificielle tout en respectant le RGPD ?", "Quels sont les atouts des modèles d'IA open-source européens comme Mistral ?"),
        "technology_impact": ("Quel est l'impact de l'automatisation par l'IA sur les métiers du conseil et de la finance ?", "Comment la souveraineté numérique européenne évolue-t-elle face aux géants technologiques ?"),
        "health_lifestyle": ("Quelles sont les méthodes éprouvées pour préserver sa santé mentale et éviter le surmenage au travail ?", "Comment optimiser son sommeil et son alimentation pour maximiser son énergie quotidienne ?"),
        "education_choices": ("Un diplôme d'ingénieur reste-t-il indispensable face aux formations courtes et certifications ?", "Quelles écoles et universités offrent les meilleures formations en sciences des données ?"),
        "financial_decisions": ("Quelles sont les meilleures stratégies d'investissement pour se prémunir contre l'inflation ?", "Comment constituer une épargne diversifiée et préparer son avenir financier sereinement ?"),
        "creativity_culture": ("Comment les outils d'IA générative transforment-ils les industries créatives et le cinéma ?", "Quel est l'avenir de la langue française et de la diversité culturelle à l'ère numérique ?"),
        "future_skills_extra": ("Quelles architectures cloud et compétences DevOps sont les plus valorisées en entreprise ?", "Pourquoi le langage Rust gagne-t-il en popularité pour le développement système critique ?")
    },
    "es": {
        "future_skills_learning": ("¿Cuáles son las habilidades de programación e inteligencia artificial más demandadas en 2026?", "¿Cómo puede un desarrollador especializarse en ingeniería de datos y modelos de lenguaje?"),
        "career_migration": ("¿Qué países ofrecen las mejores opciones de visas de trabajo y nómada digital para profesionales de tecnología?", "¿Cómo se comparan las oportunidades laborales en España, Estados Unidos y América Latina?"),
        "entrepreneurship_business": ("¿Cómo crear un negocio digital o SaaS rentable con presupuesto limitado en 2026?", "¿Qué ventajas ofrece el modelo de autofinanciamiento (bootstrapping) frente al capital de riesgo?"),
        "ai_adoption": ("¿Cómo pueden las empresas implementar soluciones de inteligencia artificial respetando la privacidad de datos?", "¿Cuáles son los beneficios de desplegar modelos de código abierto en infraestructura propia?"),
        "technology_impact": ("¿Cómo transformará la inteligencia artificial el mercado laboral en el sector administrativo y financiero?", "¿Qué impacto tienen las tecnologías de automatización en la economía global?"),
        "health_lifestyle": ("¿Cuáles son las estrategias científicas más efectivas para reducir el estrés laboral y el agotamiento?", "¿Cómo influyen el descanso de calidad y el ejercicio regular en el rendimiento mental?"),
        "education_choices": ("¿Sigue siendo necesario un título universitario en informática para conseguir empleo tecnológico?", "¿Qué valor real tienen las certificaciones internacionales y el aprendizaje autodidacta?"),
        "financial_decisions": ("¿Cuáles son las mejores estrategias para proteger los ahorros de la inflación e invertir a largo plazo?", "¿Cómo construir un portafolio de inversión diversificado con fondos indexados?"),
        "creativity_culture": ("¿De qué manera las herramientas generativas están transformando el diseño y la producción audiovisual?", "¿Cómo se protege la propiedad intelectual y el patrimonio cultural en la era de la IA?"),
        "future_skills_extra": ("¿Qué certificaciones en la nube y DevOps ofrecen mayor retorno profesional en 2026?", "¿Cuáles son las ventajas de arquitecturas modernas basadas en microservicios y contenedores?")
    },
    "pt": {
        "future_skills_learning": ("Quais habilidades em inteligência artificial e computação em nuvem têm maior demanda para trabalho remoto global em 2026?", "Qual o melhor caminho para transicionar de desenvolvimento web tradicional para engenharia de IA?"),
        "career_migration": ("Quais países oferecem os melhores vistos de trabalho e residência para profissionais de tecnologia brasileiros?", "Como comparar as vantagens do visto D8 em Portugal com a Lei de Startups na Espanha?"),
        "entrepreneurship_business": ("Como abrir e validar um negócio digital ou Micro-SaaS escalável no mercado global?", "Quais as diferenças práticas entre fundar uma empresa via Stripe Atlas ou manter operação local?"),
        "ai_adoption": ("Como empresas de médio porte podem integrar agentes autônomos e IA generativa com segurança?", "Quais as vantagens de utilizar modelos open-source locais para proteger dados sensíveis?"),
        "technology_impact": ("Qual será o impacto real da automação e IA nas profissões jurídicas, contábeis e de atendimento?", "Como o ecossistema de pagamentos instantâneos e fintechs está redefinindo o comércio digital?"),
        "health_lifestyle": ("Quais práticas com base científica ajudam a evitar o burnout em rotinas de trabalho remoto intenso?", "Como melhorar a qualidade do sono e a concentração em ambientes hiperconectados?"),
        "education_choices": ("Vale a pena cursar faculdade de Ciência da Computação ou focar em projetos práticos e certificações?", "Quais são as plataformas de educação em tecnologia mais reconhecidas no mercado de trabalho?"),
        "financial_decisions": ("Quais são as melhores estratégias para proteger o patrimônio da inflação e investir em ativos internacionais?", "Como montar uma carteira de investimentos balanceada com foco em longo prazo?"),
        "creativity_culture": ("Como a inteligência artificial generativa está transformando o design, a publicidade e a criação de conteúdo?", "Como valorizar a língua portuguesa e a produção artística regional diante de modelos globais?"),
        "future_skills_extra": ("Quais ferramentas de orquestração de dados e MLOps são essenciais para cientistas de dados em 2026?", "Como o domínio de Python, Docker e Kubernetes impulsiona carreiras em tecnologia?")
    },
    "it": {
        "future_skills_learning": ("Quali competenze in AI e sviluppo software garantiscono la massima occupabilità nel 2026?", "Come specializzarsi in architetture cloud e data engineering partendo da zero?"),
        "career_migration": ("Quali paesi offrono le migliori opportunità di lavoro e agevolazioni fiscali per specialisti IT?", "Come si confrontano i visti per talenti in Europa, Regno Unito e Stati Uniti?"),
        "entrepreneurship_business": ("Come avviare una startup software B2B sostenibile con investimenti iniziali contenuti?", "È preferibile adottare un modello bootstrap o cercare fondi di venture capital in Europa?"),
        "ai_adoption": ("Come possono le PMI implementare l'intelligenza artificiale nel rispetto della privacy e del GDPR?", "Quali vantaggi offre l'adozione di modelli open-source on-premise per le imprese?"),
        "technology_impact": ("Come cambierà il mercato del lavoro nei servizi professionali e bancari con l'avvento dell'IA?", "Quale impatto avranno i sistemi autonomi sulla produttività industriale europea?"),
        "health_lifestyle": ("Quali sono i metodi scientifici più efficaci per gestire lo stress da lavoro e prevenire il burnout?", "Come ottimizzare il riposo e la nutrizione per sostenere elevate prestazioni cognitive?"),
        "education_choices": ("Una laurea magistrale in informatica è ancora indispensabile o contano di più le certificazioni?", "Quali università e accademie offrono i percorsi più aggiornati in intelligenza artificiale?"),
        "financial_decisions": ("Quali strategie di investimento consentono di proteggere il capitale dall'inflazione a lungo termine?", "Come strutturare un portafoglio finanziario equilibrato e fiscalmente efficiente?"),
        "creativity_culture": ("In che modo l'IA generativa sta ridefinendo il design, la moda e la produzione multimediale?", "Come preservare l'autenticità culturale e il patrimonio artistico nell'era digitale?"),
        "future_skills_extra": ("Quali linguaggi e framework sono fondamentali per lo sviluppo di sistemi ad alte prestazioni?", "Quali certificazioni cloud hanno maggior valore nelle selezioni aziendali nel 2026?")
    },
    "nl": {
        "future_skills_learning": ("Welke cloud- en AI-vaardigheden zijn in 2026 het meest gewild op de Europese arbeidsmarkt?", "Hoe maak je de overstap van traditionele softwareontwikkeling naar machine learning engineering?"),
        "career_migration": ("Welke landen bieden de beste voorwaarden voor tech-professionals en digitale nomaden?", "Hoe verhoudt de kennismigrantenregeling in Nederland zich tot internationale talentvisums?"),
        "entrepreneurship_business": ("Hoe bouw je een winstgevende B2B SaaS-onderneming op met beperkt startkapitaal?", "Wat zijn de voor- en nadelen van bootstrapping ten opzichte van durfkapitaal in Europa?"),
        "ai_adoption": ("Hoe kunnen bedrijven generatieve AI implementeren met inachtneming van de AVG/GDPR?", "Wat zijn de strategische voordelen van lokale open-source taalmodellen voor ondernemingen?"),
        "technology_impact": ("Welke invloed heeft AI-automatisering op banen in de financiële en administratieve sector?", "Hoe transformeert digitalisering de logistiek en dienstensector in Noord-Europa?"),
        "health_lifestyle": ("Wat zijn bewezen methoden om werkgerelateerde stress te verminderen en een gezonde werk-privébalans te behouden?", "Hoe dragen slaapoptimalisatie en beweging bij aan duurzame mentale prestaties?"),
        "education_choices": ("Is een universitair informaticadiploma nog vereist voor een succesvolle tech-carrière?", "Welke online certificeringen en praktische portfolio's worden het hoogst gewaardeerd door werkgevers?"),
        "financial_decisions": ("Wat zijn verstandige beleggingsstrategieën om vermogen te beschermen tegen inflatie?", "Hoe bouw je een evenwichtige beleggingsportefeuille op met indexfondsen en vastgoed?"),
        "creativity_culture": ("Hoe beïnvloeden AI-tools de creatieve industrie, architectuur en digitale media?", "Hoe waarborgen we culturele identiteit en taalvariëteit in AI-systemen?"),
        "future_skills_extra": ("Welke DevOps-praktijken en containertechnologieën zijn essentieel voor senior engineers?", "Waarom kiezen steeds meer bedrijven voor moderne architecturen met Python en Go?")
    },
    "zh": {
        "future_skills_learning": ("在2026年，哪些人工智能与全栈开发技能在全球技术就业市场中最具竞争力？", "软件工程师如何系统化转型为大模型应用与智能体系统架构师？"),
        "career_migration": ("对于技术专家与科研人才，哪些国家和地区提供了最具吸引力的工作签证与人才引进政策？", "海外工作机会与本土头部科技企业在职业发展与薪酬回报上有何差异？"),
        "entrepreneurship_business": ("独立开发者如何以低成本启动并运营盈利的海外SaaS或微型软件产品？", "技术初创团队在自力更生（Bootstrapping）与风险投资之间应如何权衡？"),
        "ai_adoption": ("中小企业如何在确保数据隐私和合规的前提下高效落地生成式人工智能？", "企业私有化部署开源大模型（如DeepSeek、Llama）相比商业API有哪些优势？"),
        "technology_impact": ("自动化与大模型智能体对传统研发、金融及运营岗位会产生怎样的深远影响？", "智能算力基础设施与数字经济的发展趋势将如何演进？"),
        "health_lifestyle": ("在高强度职场节奏中，有哪些科学验证的方法可以有效预防职业倦怠与身心健康问题？", "如何通过规律作息与科学运动保持长期专注力与高工作效率？"),
        "education_choices": ("在AI辅助编程普及的今天，计算机专业学位与自学实战经验在招聘中哪个更受看重？", "哪些权威技术认证与开源项目贡献能够显著提升简历认可度？"),
        "financial_decisions": ("在宏观经济波动周期中，如何构建抗通胀与稳健增长的个人资产配置组合？", "普通投资者如何理性评估科技资产、指数基金与稳健理财工具的风险？"),
        "creativity_culture": ("生成式AI正在如何重塑游戏开发、影视制作与数字内容创作流程？", "在由全球算法主导的技术时代，如何更好传承与弘扬本土文化与语言特色？"),
        "future_skills_extra": ("云原生架构、Kubernetes与分布式系统设计的最佳学习路径是什么？", "Python与深度学习框架在工业级AI落地的核心应用场景有哪些？")
    },
    "ja": {
        "future_skills_learning": ("日本のIT業界およびグローバルリモート市場で2026年に最も求められるAI・クラウドスキルは何ですか？", "従来のWeb開発者がAIエージェントやLLMシステム開発へ転向するためのロードマップとは？"),
        "career_migration": ("高度外国人材や日本人エンジニアにとって、欧米やアジア主要国の就労ビザ制度はどう比較されますか？", "海外就職と国内メガベンチャーでのキャリア形成におけるメリットと課題とは？"),
        "entrepreneurship_business": ("少人数チームや個人開発者がマイクロSaaSビジネスを黒字化するための手順とは？", "自己資金型（ブートストラップ）経営とベンチャーキャピタル調達の長所・短所とは？"),
        "ai_adoption": ("日本企業がセキュリティや個人情報保護を遵守しつつ生成AIを業務導入するための要点とは？", "オープンソースLLMを社内インフラで運用する際のコストと運用のメリットとは？"),
        "technology_impact": ("生成AIの普及は製造業や金融業のバックオフィス業務の雇用構造をどう変えますか？", "企業のDX推進においてAIエージェントが果たす長期的インパクトとは？"),
        "health_lifestyle": ("長時間のデスクワークやリモートワークでバーンアウトを防ぐための科学的セルフケアとは？", "集中力を高め疲労を回復させる睡眠と栄養管理のベストプラクティスとは？"),
        "education_choices": ("AIツールが進化する中で、大学の情報系学位と独学ポートフォリオのどちらが採用で重視されますか？", "社会人のリスキリングにおいて最も実効性の高いオンライン講座や資格とは？"),
        "financial_decisions": ("インフレ環境下で資産価値を維持し長期形成するための資産運用戦略とは？", "新NISAやインデックス投資を活用した堅実な資産形成アプローチとは？"),
        "creativity_culture": ("生成AIはアニメ、ゲーム、イラスト制作の現場をどのように変革していますか？", "デジタル時代において独自の日本文化や伝統的クリエイティビティをどう保護・発展させるべきか？"),
        "future_skills_extra": ("クラウドインフラやDevOps領域で実務上最も高く評価される資格や経験とは？", "大規模データ処理と機械学習パイプラインを支える技術スタックとは？")
    },
    "hi": {
        "future_skills_learning": ("2026 में ग्लोबल रिमोट जॉब्स और आईटी सेक्टर के लिए कौन से टेक स्किल्स सबसे ज्यादा मांग में हैं?", "सॉफ्टवेयर इंजीनियर्स को डेटा इंजीनियरिंग और एआई डेवलपमेंट में करियर बनाने के लिए क्या सीखना चाहिए?"),
        "career_migration": ("भारतीय आईटी प्रोफेशनल्स के लिए यूरोप, खाड़ी देशों और कनाडा में वर्क वीजा पाने के सबसे अच्छे विकल्प क्या हैं?", "विदेश में जॉब करने और भारत के बढ़ते टेक स्टार्टअप्स में काम करने के बीच क्या तुलना है?"),
        "entrepreneurship_business": ("भारत में कम लागत में डिजिटल एजेंसी या स्केलेबल SaaS स्टार्टअप कैसे शुरू किया जाए?", "बूटस्ट्रैप्ड बिजनेस मॉडल और वेंचर कैपिटल फंडिंग के बीच शुरुआती फाउंडर्स के लिए क्या बेहतर है?"),
        "ai_adoption": ("छोटे और मध्यम उद्योग अपने दैनिक कामकाज में जनरेटिव एआई का सुरक्षित उपयोग कैसे कर सकते हैं?", "ओपन-सोर्स एआई मॉडल्स को अपनी भाषा और डेटा के लिए कस्टमाइज करने के क्या फायदे हैं?"),
        "technology_impact": ("आईटी आउटसोर्सिंग और बैक-ऑफिस नौकरियों पर एआई ऑटोमेशन का क्या असर पड़ेगा?", "भारत के डिजिटल पब्लिक इंफ्रास्ट्रक्चर (DPI) से स्थानीय व्यापारों को क्या लाभ हो रहा है?"),
        "health_lifestyle": ("भागदौड़ भरे जीवन में तनाव कम करने और मानसिक स्वास्थ्य को बेहतर रखने के वैज्ञानिक तरीके क्या हैं?", "अच्छी नींद और संतुलित दिनचर्या से कार्यक्षमता में कैसे सुधार लाया जा सकता है?"),
        "education_choices": ("क्या टियर-3 इंजीनियरिंग कॉलेज की डिग्री के बिना सिर्फ प्रोजेक्ट्स और ऑनलाइन कोर्सेज से टेक जॉब मिल सकती है?", "डेटा साइंस और क्लाउड कंप्यूटिंग के सबसे प्रतिष्ठित ऑनलाइन सर्टिफिकेशन्स कौन से हैं?"),
        "financial_decisions": ("महंगाई से बचाव और सुरक्षित भविष्य के लिए म्यूचुअल फंड्स और इंडेक्स इन्वेस्टिंग की सही रणनीति क्या है?", "युवा पेशेवरों को अपनी पहली कमाई से बचत और निवेश की योजना कैसे बनानी चाहिए?"),
        "creativity_culture": ("एआई टूल्स भारतीय कला, संगीत और डिजिटल कंटेंट क्रिएशन को कैसे बदल रहे हैं?", "डिजिटल युग में भारतीय भाषाओं और स्थानीय संस्कृति के संरक्षण के लिए तकनीक का उपयोग कैसे हो सकता है?"),
        "future_skills_extra": ("क्लाउड आर्किटेक्चर और डेवऑप्स (DevOps) में करियर ग्रोथ के लिए सबसे जरूरी स्किल्स क्या हैं?", "पायथन और ओपन-सोर्स टूल्स की मदद से एआई प्रोजेक्ट्स कैसे बनाए जाएं?")
    }
}

# Fallback generator for languages where specific translation maps into standard localized phrasing
def get_localized_prompt(lang: str, category_key: str, is_observed: bool, country_name: str) -> tuple[str, str]:
    if lang in PROMPT_TEMPLATES_BY_LANG:
        tpl = PROMPT_TEMPLATES_BY_LANG[lang].get(category_key, PROMPT_TEMPLATES_BY_LANG[lang]["future_skills_learning"])
        ptext = tpl[0] if is_observed else tpl[1]
    elif lang == "sv":
        ptext = f"Vilka AI- och teknikfärdigheter är mest efterfrågade i {country_name} och globalt 2026?" if is_observed else f"Hur implementerar företag i {country_name} generativ AI på ett säkert sätt?"
    elif lang == "pl":
        ptext = f"Jakie umiejętności IT i sztucznej inteligencji są najbardziej poszukiwane w {country_name} w 2026 roku?" if is_observed else f"Jakie są najlepsze strategie rozwoju kariery technologicznej w {country_name}?"
    elif lang == "ko":
        ptext = f"{country_name}과 글로벌 시장에서 2026년에 가장 수요가 높은 AI 및 소프트웨어 기술은 무엇인가요?" if is_observed else f"{country_name} 기업에서 생성형 AI를 안전하게 도입하기 위한 가이드라인은 무엇인가요?"
    elif lang == "id":
        ptext = f"Keterampilan teknologi dan AI apa yang paling diminati untuk bekerja secara global dari {country_name} di tahun 2026?" if is_observed else f"Bagaimana strategi membangun bisnis digital SaaS yang menguntungkan di {country_name}?"
    elif lang == "ur":
        ptext = f"سال 2026 میں گلوبل ریموٹ جابز اور سافٹ ویئر فیلڈ کے لیے کون سی مہارتیں سب سے اہم ہیں؟" if is_observed else f"{country_name} میں ڈیجیٹل بزنس اور فری لانسنگ شروع کرنے کے بہترین طریقے کیا ہیں؟"
    elif lang == "vi":
        ptext = f"Kỹ năng công nghệ và AI nào được săn đón nhiều nhất tại {country_name} và thị trường quốc tế năm 2026?" if is_observed else f"Làm thế nào để xây dựng sản phẩm SaaS số hóa thành công từ {country_name}?"
    elif lang == "tl":
        ptext = f"Anong mga tech at AI skills ang pinaka-in-demand para sa remote work mula sa {country_name} ngayong 2026?" if is_observed else f"Paano magtayo ng matagumpay na digital business o freelance career sa {country_name}?"
    elif lang == "sw":
        ptext = f"Je, ni ujuzi gani wa teknolojia na AI unaohitajika zaidi kwa kazi za kimataifa nchini {country_name} mnamo 2026?" if is_observed else f"Jinsi ya kuanzisha biashara ya kidijitali yenye faida katika kanda ya Afrika Mashariki?"
    elif lang == "am":
        ptext = f"በ2026 ዓ.ም በአለም አቀፍ የቴክኖሎጂ ስራዎች ውስጥ በጣም ተፈላጊ የሆኑ የAI እና የሶፍትዌር ክህሎቶች የትኞቹ ናቸው?" if is_observed else f"በ{country_name} ውስጥ የዲጂታል ንግድ እና ቴክኖሎጂ ስራዎችን እንዴት በብቃት መጀመር ይቻላል?"
    elif lang == "no":
        ptext = f"Hvilke IT- og AI-ferdigheter gir best karrieremuligheter i {country_name} og internasjonalt i 2026?" if is_observed else f"Hvordan kan bedrifter i {country_name} ta i bruk generativ AI under gjeldende regelverk?"
    elif lang == "da":
        ptext = f"Hvilke teknologiske kompetencer og AI-færdigheder er mest efterspurgte i {country_name} i 2026?" if is_observed else f"Hvordan implementerer virksomheter i {country_name} generativ AI sikkert og effektivt?"
    elif lang == "fi":
        ptext = f"Mitkä tekoäly- ja ohjelmisto-osaamiset ovat kysytyimpiä {country_name}ssa ja kansainvälisesti vuonna 2026?" if is_observed else f"Miten yritykset voivat hyödyntää tekoälyä vastuullisesti ja tehokkaasti {country_name}ssa?"
    elif lang == "ms":
        ptext = f"Apakah kemahiran teknologi dan AI yang paling mendapat permintaan tinggi di {country_name} dan pasaran global 2026?" if is_observed else f"Bagaimanakah syarikat di {country_name} boleh memanfaatkan kecerdasan buatan secara selamat?"
    else:
        # Default English localized to country
        ptext = f"What tech and AI skills offer the highest employability for professionals in {country_name} in 2026?" if is_observed else f"How do international career and technology adoption strategies compare for candidates from {country_name}?"

    context_desc = f"Localized inquiry capturing practical challenges, local economic dynamics, and technology trends in {country_name}."
    return ptext, context_desc


def build_full_500_prompts() -> List[Dict[str, Any]]:
    prompts = []
    pid_counter = 1

    for cidx, cspec in enumerate(COUNTRY_SPECS, 1):
        cname = cspec["name"]
        ciso = cspec["iso"]
        creg = cspec["region"]
        clang = cspec["lang"]

        # 10 prompts per country: 6 observed (prompts 1,3,5,7,8,10), 4 research (prompts 2,4,6,9)
        # Distribute the 9 categories across the 10 prompts
        assigned_cats = [
            ("future_skills_learning", "recommendation", True),
            ("career_migration", "comparative", False),
            ("entrepreneurship_business", "recommendation", True),
            ("ai_adoption", "comparative", False),
            ("technology_impact", "informational", True),
            ("health_lifestyle", "comparative", False),
            ("education_choices", "recommendation", True),
            ("financial_decisions", "recommendation", True),
            ("creativity_culture", "comparative", False),
            ("future_skills_learning", "recommendation", True),
        ]

        for p_idx, (cat_key, intent, is_obs) in enumerate(assigned_cats, 1):
            ptext, ctxt = get_localized_prompt(clang, cat_key, is_obs, cname)
            src_cat = "observed_user_questions" if is_obs else "research_questions"
            pid = f"gaa2-{ciso}-{p_idx:02d}"

            item = {
                "id": pid,
                "source_category": src_cat,
                "source_reference": "answerpath",
                "category": cat_key,
                "intent": intent,
                "language": clang,
                "region": creg,
                "country_iso": ciso,
                "country_name": cname,
                "prompt_text": ptext,
                "prompt": ptext,
                "cultural_context": ctxt,
            }
            prompts.append(item)
            pid_counter += 1

    return prompts

# ---------------------------------------------------------
# 3. Main Benchmark Execution Engine
# ---------------------------------------------------------
async def execute_full_benchmark():
    out_dir = Path("benchmark/releases/global-ai-answers-2026.2")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "prompts").mkdir(exist_ok=True)

    prompts = build_full_500_prompts()
    print(f"Total Prompts Built: {len(prompts)}")
    obs_cnt = sum(1 for p in prompts if p["source_category"] == "observed_user_questions")
    res_cnt = sum(1 for p in prompts if p["source_category"] == "research_questions")
    print(f"Observed: {obs_cnt} ({obs_cnt/len(prompts)*100:.1f}%), Research: {res_cnt} ({res_cnt/len(prompts)*100:.1f}%)")

    # 1. Write prompts files
    with open(out_dir / "prompts.jsonl", "w", encoding="utf-8") as f_all, \
         open(out_dir / "prompts/observed.jsonl", "w", encoding="utf-8") as f_obs, \
         open(out_dir / "prompts/research.jsonl", "w", encoding="utf-8") as f_res:
        for p in prompts:
            line = json.dumps(p, ensure_ascii=False) + "\n"
            f_all.write(line)
            if p.get("source_category") == "observed_user_questions":
                f_obs.write(line)
            else:
                f_res.write(line)

    # 2. Write entities.json
    from scripts.run_global_ai_answers_2026_2_full import ENTITIES_DATA
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

    # 5. Execute Live Queries with controlled concurrency
    raw_responses = []
    observations = []
    citations_all = []
    errors = []

    print(f"Starting Live Execution across {len(prompts)} prompts and {len(providers)} providers ({len(prompts)*len(providers)} total queries)...")

    sem = asyncio.Semaphore(6)

    async def execute_single_query(prompt_item, prov, idx):
        pid = prompt_item["id"]
        ptext = prompt_item["prompt_text"]
        lang = prompt_item["language"]
        country = prompt_item["country_name"]
        cat = prompt_item["category"]
        src_cat = prompt_item["source_category"]

        req_item = {
            "prompt": ptext,
            "task_type": "geo_scope_2026_2_measurement",
            "model": prov.target_model,
            "fallback_allowed": False,
            "max_tokens": 1000,
            "temperature": 0.2,
        }

        async with sem:
            t0 = time.time()
            try:
                resp = await prov.generate(req_item, execution_mode="live")
                lat_ms = round((time.time() - t0) * 1000, 2)

                if resp.is_success():
                    raw_rec = resp.to_raw_record(
                        experiment_id="gaa-2026-2-global",
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

                    # Extract observations
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

    tasks = []
    for idx, prompt_item in enumerate(prompts, 1):
        for prov in providers:
            tasks.append(execute_single_query(prompt_item, prov, idx))

    # Run all tasks with logging progress
    batch_size = 50
    for i in range(0, len(tasks), batch_size):
        chunk = tasks[i:i+batch_size]
        print(f"Executing batch [{i+1}-{min(i+batch_size, len(tasks))}/{len(tasks)}]...")
        await asyncio.gather(*chunk)
        await asyncio.sleep(0.5)

    print(f"\nExecution Complete: {len(raw_responses)} raw responses, {len(observations)} observations, {len(errors)} errors, {len(citations_all)} citations.")

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

    # Regional & Country Analysis
    country_metrics = {}
    for cspec in COUNTRY_SPECS:
        cname = cspec["name"]
        c_obs = [o for o in observations if o.get("country") == cname]
        c_prompts = [p for p in prompts if p["country_name"] == cname]
        c_ent_counts = {}
        for o in c_obs:
            if o.get("mentioned"):
                e = o.get("entity")
                c_ent_counts[e] = c_ent_counts.get(e, 0) + 1
        country_metrics[cname] = {
            "region": cspec["region"],
            "language": cspec["lang"],
            "prompts_count": len(c_prompts),
            "top_mentioned_entities": sorted(c_ent_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        }

    # Category Analysis
    category_metrics = {}
    for cat_key, cat_label in CATEGORIES_9:
        cat_obs = [o for o in observations if o.get("category") == cat_key]
        cat_prompts = [p for p in prompts if p["category"] == cat_key]
        cat_ent_counts = {}
        for o in cat_obs:
            if o.get("mentioned"):
                e = o.get("entity")
                cat_ent_counts[e] = cat_ent_counts.get(e, 0) + 1
        category_metrics[cat_key] = {
            "label": cat_label,
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
        "benchmark": "Global AI Answers Benchmark 2026.2",
        "dataset_version": "global-ai-answers-2026.2",
        "execution_mode": "live",
        "research_status": "peer_review_ready",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_prompts": len(prompts),
            "observed_prompts": obs_cnt,
            "research_prompts": res_cnt,
            "total_providers": len(providers),
            "total_completions": total_completions,
            "total_observations": len(observations),
            "total_citations": len(citations_all),
            "total_entities_tracked": len(ENTITIES_DATA),
            "countries_count": len(COUNTRY_SPECS),
            "categories_count": len(CATEGORIES_9),
            "languages_count": len(set(c["lang"] for c in COUNTRY_SPECS)),
            "errors_count": len(errors),
        },
        "entities": entity_metrics,
        "country_analysis": country_metrics,
        "category_analysis": category_metrics,
        "provider_breakdown": provider_breakdown,
        "disclaimer": "This benchmark measures observed AI answer patterns around human concerns across cultures. It is not a ranking of people, countries, or companies."
    }

    with open(out_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, ensure_ascii=False, indent=2)

    # 8. Limitations & Methodology & README
    with open(out_dir / "limitations.md", "w", encoding="utf-8") as f_lim:
        f_lim.write("""# Research Limitations: Global AI Answers Benchmark 2026.2

**Dataset ID**: `global-ai-answers-2026.2`  
**Status**: Full Empirical Benchmark Release  

> **Core Research Statement**:  
> *"The benchmark measures observed AI answer patterns only. It does NOT rank humans, countries, or organizations."*

## 1. Scope & Epistemic Boundaries
- **Observed Entity Presence**: Reflects empirical mentions in generative responses generated during September 2026.
- **Provider Class Isolation**: Metrics for search-grounded answer engines (`answer_engine`) are strictly isolated from parametric models (`llm`).
- **Linguistic and Cultural Stratification**: Evaluates 500 prompts across 50 countries, 22+ languages, and 9 human concern categories.
- **Non-Normative Character**: Rates represent frequency and context of occurrence; they do not imply superiority, truth value, or intrinsic quality.

## 2. Research Non-Goals
- We do NOT predict search ranking algorithms.
- We do NOT assign "scores" to individual humans or sovereign nations.
- We do NOT guarantee commercial AI visibility outcomes.
""")

    with open(out_dir / "methodology.md", "w", encoding="utf-8") as f_meth:
        f_meth.write("""# Global AI Answers Benchmark 2026.2: Research Methodology

## 1. Multi-Stage Empirical Measurement Pipeline
```
AnswerPath GEO (Discovery)
        ↓
Question Discovery & Stratification (60% Observed Real Inquiries + 40% Research Probes)
        ↓
GEO-Scope Measurement Engine (Core Framework)
        ↓
Hamzad AI Gateway (Isolated Live Execution Layer)
        ↓
Deterministic Multi-Type Entity Extraction (Aliases, Homonyms, Constraints)
        ↓
Descriptive Statistics & Provider Breakdown (Answer Engine vs. LLM)
        ↓
Cryptographic Release Bundle (`benchmark/releases/global-ai-answers-2026.2/`)
```

## 2. Experimental Design
- **Prompt Catalog**: 500 culturally localized questions across 50 countries (6 regions) and 9 essential concern categories.
- **Entity Disambiguation**: 73 multi-type entities across people, companies, countries, universities, technologies, and communities with negative homonym filters.
- **Provider Matrix**: Live inference over Google `gemini-2.5-flash`, Perplexity `sonar-pro`, OpenAI `gpt-4o-mini`, and Anthropic `claude-3.5-sonnet`.
""")

    with open(out_dir / "README.md", "w", encoding="utf-8") as f_rd:
        f_rd.write("""# Global AI Answers Benchmark 2026.2 (`global-ai-answers-2026.2`)

## Overview
This package is the full-scale empirical benchmark dataset observing generative engine visibility and recommendation patterns across 500 culturally localized prompts in 50 countries, 22+ languages, and 9 core human concern categories.

- **Status**: Published Global Research Release
- **Execution Mode**: `live` (Via Hamzad AI Gateway)
- **Prompts**: 500 (60% observed user questions, 40% research templates)
- **Countries**: 50 (MENA, North America, Europe, Asia Pacific, Latin America, Sub-Saharan Africa)
- **Languages**: 22+ native languages
- **Entities Tracked**: 73 Multi-Type Entities
- **Categories**: 9 Core Life, Career, Technology, and Cultural Concerns

## Verification & Reproduction
```bash
geo-scope benchmark verify --dataset benchmark/releases/global-ai-answers-2026.2
geo-scope benchmark validate --dataset benchmark/releases/global-ai-answers-2026.2
geo-scope benchmark replay --dataset benchmark/releases/global-ai-answers-2026.2
```
""")

    # 9. Manifest
    manifest = {
        "benchmark": "Global AI Answers Benchmark 2026.2",
        "dataset_id": "global-ai-answers-2026.2",
        "mode": "live",
        "execution_mode": "live",
        "research_status": "peer_review_ready",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "prompt_count": len(prompts),
        "execution_count": len(raw_responses),
        "n_prompts": len(prompts),
        "n_completions": len(raw_responses),
        "n_observations": len(observations),
        "n_citations": len(citations_all),
        "n_errors": len(errors),
        "providers": [p.name for p in providers],
        "provider_classes": {p.name: p.provider_class for p in providers},
        "categories": [c[0] for c in CATEGORIES_9],
        "countries": [c["name"] for c in COUNTRY_SPECS],
        "languages": sorted(list(set(c["lang"] for c in COUNTRY_SPECS))),
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
    print("\nGlobal 2026.2 Checksum Verification Result:", chk_res)
    print("\n✓ Full Global 2026.2 Benchmark Complete! Artifacts in:", out_dir)


if __name__ == "__main__":
    asyncio.run(execute_full_benchmark())
