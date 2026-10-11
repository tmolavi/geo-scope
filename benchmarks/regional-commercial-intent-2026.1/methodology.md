# Methodology: Regional Commercial AI Visibility Pilot (Iran & Türkiye)

**Benchmark Version:** `regional-commercial-intent-2026.1`  
**Standard:** GEO-Scope Measurement Contract v1 & Schema v0.3  
**Markets:** Iran (`fa-IR`), Türkiye (`tr-TR`)  
**Inspiration Reference:** Peak Ace AI Visibility LLM Benchmark 2026 ([peakace.agency](https://peakace.agency/en/latest/ai-visibility-llm-benchmark-2026/))  
**Notice:** Independent regional pilot inspired by Peak Ace's intent-based measurement design. This study does not claim to reproduce Peak Ace's results.

---

## 1. Executive Research Overview

Generative AI answer engines (ChatGPT Search, Google Gemini with Search Grounding, and Perplexity Sonar) have rapidly emerged as critical discovery channels for enterprise services. Traditional SEO ranking trackers fail to capture the probabilistic, multi-source synthesis of answer engines.

The **GEO-Scope Regional Commercial AI Visibility Pilot** establishes a standardized, reproducible measurement framework evaluating how generative search engines answer commercial buying queries in two major regional markets: **Iran (`fa-IR`)** and **Türkiye (`tr-TR`)**.

---

## 2. Intent Taxonomy & Prompt Engineering

Inspired by the intent-driven architecture of Peak Ace's 2026 benchmark, prompts are stratified across **four distinct buyer journey intents**:

```
                              ┌──────────────────────────────────┐
                              │  Buyer Intent Journey Strata     │
                              └─────────────────┬────────────────┘
                                                │
         ┌──────────────────┬───────────────────┴───────────────────┬──────────────────┐
         ▼                  ▼                                       ▼                  ▼
┌──────────────────┐ ┌──────────────────┐               ┌──────────────────┐ ┌──────────────────┐
│ 1. Best / Rec.   │ │ 2. Comparison    │               │ 3. Pricing / Sel.│ │ 4. Criteria / Gui│
│ Direct queries   │ │ Head-to-head or  │               │ Fee structures & │ │ Readiness KPIs & │
│ for top vendors  │ │ paradigm trade-off│              │ selection steps  │ │ evaluation rules │
└──────────────────┘ └──────────────────┘               └──────────────────┘ └──────────────────┘
```

### 2.1 The 24 Curated Prompts

To prevent artificial bias and vendor steering, all 24 queries adhere to **strict neutrality principles**:
- **Zero-Brand Mentioning:** No existing agency, tool, or practitioner name is mentioned in any user prompt.
- **Native Phrasing:** Queries were designed natively in Persian and Turkish reflecting natural regional commercial search patterns—never mechanically translated.
- **Topical Coverage:** Queries evenly cover six key service areas:
  1. SEO agencies
  2. GEO (Generative Engine Optimization) service providers
  3. AI visibility measurement tools
  4. Technical SEO auditing
  5. Digital PR providers
  6. AI search consulting

| ID | Market | Intent Group | Topic | Query (Original Language) |
| :--- | :--- | :--- | :--- | :--- |
| `prm-reg-ir-001` | fa-IR | Best/recommendation | SEO agencies | بهترین آژانس‌های سئو در ایران برای وب‌سایت‌های بزرگ فروشگاهی کدامند؟ |
| `prm-reg-ir-002` | fa-IR | Best/recommendation | GEO service providers | کدام شرکت‌ها در ایران خدمات بهینه‌سازی برای موتورهای هوش مصنوعی (GEO) ارائه می‌دهند؟ |
| `prm-reg-ir-003` | fa-IR | Best/recommendation | Technical SEO auditing | برترین ارائه‌دهندگان خدمات ممیزی تکنیکال سئو برای کسب‌وکارهای سازمانی در ایران چه کسانی هستند؟ |
| `prm-reg-ir-004` | fa-IR | Comparison | AI search consulting | تفاوت خدمات سئوی سنتی با مشاوره‌های بهینه‌سازی برای جستجوی هوش مصنوعی چیست و کدام به صرفه‌تر است؟ |
| `prm-reg-ir-005` | fa-IR | Comparison | SEO agencies | مقایسه عملکرد آژانس‌های سئوی تخصصی سازمانی با تیم‌های اختصاصی داخلی در ایران |
| `prm-reg-ir-006` | fa-IR | Comparison | AI visibility measurement tools | مقایسه ابزارهای بومی و بین‌المللی برای سنجش سهم مدل و دیده‌شدن برند در موتورهای هوش مصنوعی |
| `prm-reg-ir-007` | fa-IR | Pricing/vendor selection | SEO agencies | تعرفه و مدل‌های قیمت‌گذاری قراردادهای سالانه سئو و بازاریابی مبتنی بر هوش مصنوعی در ایران چگونه تعیین می‌شود؟ |
| `prm-reg-ir-008` | fa-IR | Pricing/vendor selection | Digital PR providers | هزینه اجرای کمپین‌های روابط عمومی دیجیتال و رپورتاژ آگهی برای تقویت اعتبار برند در موتورهای جستجو چقدر است؟ |
| `prm-reg-ir-009` | fa-IR | Pricing/vendor selection | Technical SEO auditing | چگونه یک پیمانکار مطمئن برای ممیزی سئوی فنی و مشاوره استراتژیک جستجو در بازار ایران انتخاب کنیم؟ |
| `prm-reg-ir-010` | fa-IR | Criteria/guidance | SEO agencies | چه معیارهایی را باید پیش از عقد قرارداد با شرکت‌های سئو و بازاریابی جستجو در ایران ارزیابی کرد؟ |
| `prm-reg-ir-011` | fa-IR | Criteria/guidance | AI search consulting | شاخص‌های کلیدی برای سنجش آمادگی وب‌سایت جهت حضور و پیشنهاد شدن در پاسخ‌های هوش مصنوعی چیست؟ |
| `prm-reg-ir-012` | fa-IR | Criteria/guidance | Digital PR providers | مهم‌ترین فاکتورها در سنجش اثربخشی خدمات روابط عمومی آنلاین بر سئو و سیگنال‌های اعتبار برند چیست؟ |
| `prm-reg-tr-001` | tr-TR | Best/recommendation | SEO agencies | Türkiye'de büyük ölçekli e-ticaret siteleri için en iyi SEO ajansları hangileridir? |
| `prm-reg-tr-002` | tr-TR | Best/recommendation | GEO service providers | Türkiye'de yapay zeka arama motorları optimizasyonu (GEO) ve yapay zeka arama danışmanlığı sunan önde gelen ajanslar hangileridir? |
| `prm-reg-tr-003` | tr-TR | Best/recommendation | Technical SEO auditing | Kurumsal web siteleri için kapsamlı teknik SEO denetimi hizmeti veren en başarılı ajanslar hangileridir? |
| `prm-reg-tr-004` | tr-TR | Comparison | SEO agencies | Türkiye pazarında butik SEO ajansları ile tam hizmet dijital pazarlama ajanslarının artı ve eksi yönleri nelerdir? |
| `prm-reg-tr-005` | tr-TR | Comparison | AI search consulting | Klasik arama motoru optimizasyonu ile yapay zeka motoru optimizasyonu (GEO) arasındaki temel farklar nelerdir? |
| `prm-reg-tr-006` | tr-TR | Comparison | AI visibility measurement tools | Yapay zeka modellerinde marka görünürlüğünü ölçen araçlar ile geleneksel SEO sıralama takip araçlarının karşılaştırması |
| `prm-reg-tr-007` | tr-TR | Pricing/vendor selection | SEO agencies | Türkiye'de kurumsal SEO ve GEO danışmanlığı aylık ve yıllık hizmet bedelleri hangi kriterlere göre belirlenir? |
| `prm-reg-tr-008` | tr-TR | Pricing/vendor selection | Digital PR providers | Arama görünürlüğünü artırmak için dijital PR ve backlink stratejisi yürüten ajansları seçerken bütçe planlaması nasıl yapılmalıdır? |
| `prm-reg-tr-009` | tr-TR | Pricing/vendor selection | Technical SEO auditing | Teknik SEO denetimi ve yapay zeka arama uyumluluğu için hizmet sağlayıcı seçerken nelere dikkat edilmelidir? |
| `prm-reg-tr-010` | tr-TR | Criteria/guidance | SEO agencies | Bir SEO ve yapay zeka görünürlük ajansı ile sözleşme imzalamadan önce hangi performans kriterleri (KPI) sorgulanmalıdır? |
| `prm-reg-tr-011` | tr-TR | Criteria/guidance | AI search consulting | Bir markanın yapay zeka yanıtlarında tavsiye edilme ve kaynak gösterilme oranını artırmak için hangi adımlar izlenmelidir? |
| `prm-reg-tr-012` | tr-TR | Criteria/guidance | Digital PR providers | Yapay zeka modelleri tarafından yetkin kaynak kabul edilmek için dijital PR çalışmalarında hangi metrikler takip edilmelidir? |

---

## 3. Sampling Design & Statistical Boundaries

- **Universe:** 24 unique buyer prompts.
- **Provider Matrix:** 3 answer engines (`chatgpt_search`, `gemini_grounding`, `perplexity_sonar`).
- **Repetitions ($k$):** 2 repetitions per prompt per provider.
- **Planned Observations:** $24 \times 3 \times 2 = 144$ observations.
- **Statistical Status:** **Exploratory Pilot Calibration**. Findings represent initial directional baseline data; they are not generalized to the full population distribution.
- **Confidence Intervals:** For any proportion $p = x/n$, uncertainty is calculated using the **Wilson Score Interval** with 95% confidence:
  $$CI_{95\%} = \frac{p + \frac{z^2}{2n} \pm z \sqrt{\frac{p(1-p)}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}} \quad (z = 1.96)$$

---

## 4. Provider Selection & Grounding Governance

Under GEO-Scope Provider Governance (`providers.yml`), only verified live search-grounded engines are valid for AI visibility measurement:

1. **ChatGPT Search (`chatgpt_search`):** OpenAI GPT-4o with web search grounding.
2. **Google Gemini (`gemini_grounding`):** Gemini 2.5 Flash with Google Search grounding metadata.
3. **Perplexity Sonar (`perplexity_sonar`):** Perplexity Sonar with native web index citations.

### Strict Governance Rules:
- **No Non-Search Substitution:** A base model without web grounding (such as raw GPT-4o or Claude without web search) will **never** be substituted and labeled as search-grounded.
- **Gating on Credentials:** If API credentials for grounded execution are unconfigured, provider adapters are marked `PROVIDER_UNAVAILABLE`, and execution status is recorded as `NOT_RUN`.
- **Zero Fabrication:** Neither mock responses nor simulated text are ever stored as empirical records.

---

## 5. Metrics Architecture

In accordance with the GEO-Scope AI Visibility Measurement Contract v1, visibility is evaluated across mutually exclusive, rigorous dimensions:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        AI Visibility Metric Layers                     │
├────────────────────────────┬───────────────────────────┬───────────────┤
│ 1. Mention Rate            │ 2. Recommendation Rate    │ 3. Citation   │
│ Binary response-level      │ Explicit endorsement or   │ Target domain │
│ appearance (Count >= 1)    │ numbered rank positioning │ or URL cited  │
├────────────────────────────┼───────────────────────────┼───────────────┤
│ 4. First Rec. Position     │ 5. Share of Voice (SOV)   │ 6. Domain Freq│
│ 1-based ordinal rank in    │ Proportion of mentions    │ Most cited    │
│ structured numbered lists  │ among competitor entities │ web sources   │
└────────────────────────────┴───────────────────────────┴───────────────┘
```

### Core Methodological Invariants:
1. **Mention $\neq$ Recommendation:** Mentioning a vendor as an example or in a critical context does not constitute a recommendation. An entity is marked `recommended: true` only when semantic recommendation or numbered rank positioning occurs.
2. **Citation $\neq$ Endorsement:** A URL cited as an informational reference does not mean the cited brand was recommended.
3. **Denominator Accounting:** Every rate metric explicitly reports `successful_n / metric_denominator_n`, tracking failed queries rather than dropping them.

---

## 6. Budget & Execution Cost Estimation

Pilot execution cost is strictly capped at **\$10.00**.

| Provider Adapter | Planned Queries | Unit Pricing | Subtotal |
| :--- | :--- | :--- | :--- |
| `perplexity_sonar` | 48 | \$0.005 / query | \$0.24 |
| `gemini_grounding` | 48 | \$0.035 / grounded query | \$1.68 |
| `chatgpt_search` | 48 | \$0.015 / search query | \$0.72 |
| **Total Pilot Execution** | **144** | — | **\$2.64** |

The \$2.64 estimated cost is well below the \$10.00 ceiling, ensuring sustainable reproducibility.

---

## 7. Comparative Framework: Peak Ace 2026 vs. GEO-Scope Regional Pilot

| Dimension | Peak Ace AI Visibility Benchmark (2026) | GEO-Scope Regional Pilot 2026.1 |
| :--- | :--- | :--- |
| **Study Role** | Comprehensive Western Enterprise Benchmark | Independent Regional Exploratory Pilot |
| **Sample Size** | Large-scale ($>10,000$ queries) | 24 prompts, 144 planned observations |
| **Markets Covered** | United States, United Kingdom, DACH | Iran (`fa-IR`), Türkiye (`tr-TR`) |
| **Languages** | English, German | Persian (`fa`), Turkish (`tr`) |
| **Focus Industries** | Broad multi-vertical (e-commerce, SaaS, travel, finance) | B2B Commercial Buying (SEO, GEO, PR, Auditing) |
| **Grounded Providers** | ChatGPT, Perplexity, Copilot, Google Overviews | ChatGPT Search, Gemini Grounding, Perplexity Sonar |
| **Shared Principles** | Intent-based prompt strata; citation & rank extraction | Intent strata; binary mention; citation separation; numbered rank |
| **Cross-Comparison Rule** | Baseline study for inspiration | **Do not directly compare raw percentages** |

Researchers must not treat percentage figures from this regional calibration as directly comparable to Peak Ace's figures due to distinct linguistic tokenizers, local search index depths, sample sizes, and market dynamics.
