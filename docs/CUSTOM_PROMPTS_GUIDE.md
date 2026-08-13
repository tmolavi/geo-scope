# 📂 Bring Your Own Prompts (BYOP) Guide

GEO-Scope enables you to benchmark **YOUR real market, YOUR brand, and YOUR customer queries**.

You can supply custom prompt files in **CSV**, **JSON**, **TXT**, or **YAML** format using the `--prompts` flag:

```bash
geo-scope run \
  --brand "My Brand" \
  --competitors "Competitor A, Competitor B" \
  --prompts my_queries.csv \
  --out results/my_audit/
```

---

## Supported File Formats

### 1. CSV Format (`.csv`)
GEO-Scope automatically recognizes columns named `query`, `prompt`, `question`, `text`, or `keyword`:

```csv
query,intent,language
What is the best project management tool for remote teams?,commercial_direct,en
ClickUp vs Asana comparison for engineering teams,comparative,en
How to reduce project delivery delays with automated sprints?,problem_solving,en
```

### 2. Plain Text Format (`.txt`)
Simply put one search query per line (lines starting with `#` are ignored):

```text
# Best CRM queries 2026
What is the best CRM software for startups in 2026?
HubSpot vs Salesforce price and features comparison
How to prevent sales pipeline leaks with automation?
```

### 3. JSON Format (`.json`)
You can pass an array of strings or an array of prompt objects:

```json
[
  {
    "query": "Best lightweight database for edge computing",
    "intent": "commercial_direct"
  },
  {
    "query": "SQLite vs DuckDB for local analytics",
    "intent": "comparative"
  }
]
```

---

## Best Practices for Prompt Selection

1. **Stratify by Search Intent**: Include commercial direct, head-to-head comparison, and problem-solving queries.
2. **Avoid Bias in Prompt Phrasing**: Use neutral queries (e.g. *"Best CRM for startups"* rather than *"Why Brand X is the best CRM"*).
3. **Include Competitor Brand Terms**: Test queries comparing your brand directly with 2-4 primary competitors.
