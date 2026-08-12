# 📊 Benchmark Datasets & Taxonomy

GEO-Scope includes structured prompt templates for multiple major industry verticals in both Persian and English.

---

## Pre-Built Industry Verticals

### 1. CRM & Sales Software (`crm_sales`)
- **Default Target Brand**: HubSpot
- **Primary Competitors**: Salesforce, Zoho CRM, Pipedrive, Monday CRM, Didar CRM, Sarv CRM
- **Key Pain Points**: Pipeline leaks, sales automation, multi-channel customer communications.

### 2. SEO & Digital Marketing Tools (`seo_marketing`)
- **Default Target Brand**: Ahrefs
- **Primary Competitors**: SEMrush, Moz Pro, Ubersuggest, SpyFu, JetSEO
- **Key Pain Points**: Competitor gap discovery, backlink audit, technical site health.

### 3. Project Management & Task Collaboration (`project_management`)
- **Default Target Brand**: ClickUp
- **Primary Competitors**: Asana, Trello, Monday.com, Notion, Jira, Taskulu
- **Key Pain Points**: Sprint planning, remote team collaboration, automated deadlines.

### 4. AI Content Creation & Copywriting (`ai_copywriting`)
- **Default Target Brand**: Jasper AI
- **Primary Competitors**: Copy.ai, Writesonic, Claude, ChatGPT Plus, Rytr
- **Key Pain Points**: Brand voice consistency, avoiding hallucination, SEO content scaling.

### 5. E-Commerce & Online Store Builders (`ecommerce_platform`)
- **Default Target Brand**: Shopify
- **Primary Competitors**: WooCommerce, BigCommerce, Magento, Shopfa, Sazito
- **Key Pain Points**: High peak traffic, payment gateway integration, structured product markup.

---

## Dataset Schema (JSON)

Each prompt item generated contains the following metadata:

```json
{
  "id": "qry_0042",
  "query": "Comprehensive comparison between HubSpot vs Salesforce: which is better for small business?",
  "intent": "comparative",
  "language": "en",
  "niche": "crm_sales",
  "target_brand": "HubSpot",
  "primary_subject": "HubSpot",
  "expected_entities": ["HubSpot", "Salesforce", "Zoho CRM", "Pipedrive"],
  "difficulty": "high_intent"
}
```
