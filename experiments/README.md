# 🧪 Community GEO Experiments & Replications

Welcome to the **GEO-Scope Community Experiments** registry!

This directory contains empirical experiments, replications, contradictory findings, and hypotheses submitted by the open-source research and SEO community.

---

## 🎯 Experimental Manifesto

> **"Don't trust GEO claims. Test them."**

In generative engine optimization, unverified claims are everywhere. Our goal is to replace marketing dogma with **reproducible, empirical evidence**.

Whether your experiment **confirms**, **contradicts**, or **extends** existing observations, your contribution is valuable scientific data.

---

## 📂 Directory Structure

```text
experiments/
├── README.md                          # This guide
├── templates/
│   └── experiment_template.md         # Copy this template to submit an experiment
└── community/
    ├── 01_reddit_correlation_study.md # Study on Reddit UGC citation correlation
    ├── 02_g2_review_volume_study.md   # Study on G2 review grid influence
    ├── 03_schema_tables_study.md      # Study on comparison tables & BLUF markup
    └── 04_bilingual_study.md          # Multi-lingual citation behavior study
```

---

## 🚀 How to Submit an Experiment

1. **Copy the template**:
   ```bash
   cp experiments/templates/experiment_template.md experiments/community/YOUR_STUDY_NAME.md
   ```
2. **Run your benchmark**:
   ```bash
   geo-scope run --brand "YourBrand" --prompts my_prompts.csv --out results/my_experiment/
   ```
3. **Fill out the template** with your hypothesis, models, prompts, configuration, and generated artifacts (`summary.md`, `citations.csv`).
4. **Submit a Pull Request** or open a **"New Experiment"** issue!
