# Golden Parser Dataset Methodology (v1)

This document specifies the annotation schema, curation rules, ambiguity resolution protocol, and limitations of the GEO-Scope Golden Parser Evaluation Dataset (`benchmark/golden_sets/v1/`).

---

## 1. Dataset Purpose & Philosophy

The GEO-Scope Golden Parser Evaluation Dataset is an independently constructed benchmark designed to evaluate and measure the precision, recall, and edge-case handling of the deterministic entity observation parser (`ObservationParser`).

### Guiding Principles
1. **Independent Formulation**: Prompts and ground-truth labels are created independently from parser heuristics, explicitly including adversarial edge cases where naive substring matching fails.
2. **Multilingual Diversity**: The dataset spans 5 core benchmark languages: Persian (`fa`), English (`en`), Arabic (`ar`), Turkish (`tr`), and Chinese (`zh`).
3. **Epistemic Honesty**: Metrics computed against this dataset measure parser fidelity on the curated distribution; they do not constitute a mathematical guarantee of universal accuracy on unconstrained open-ended web generation.

---

## 2. Dataset Composition (v1)

| Dimension | Specification |
|:---|:---|
| **Total Labeled Examples** | 220 records |
| **Languages** | Persian (`fa`), English (`en`), Arabic (`ar`), Turkish (`tr`), Chinese (`zh`) |
| **Tracked Entities** | 18 multi-type entities (Companies, Founders/People, Academic Journals, Technologies) |
| **Ground-Truth Label Fields** | `mentioned`, `recommended`, `rank`, `cited`, `attributed`, `wrong_entity`, `intent_type` |
| **Storage Format** | JSON Lines (`golden_examples.jsonl`), JSON Registry (`entities.json`) |

---

## 3. Annotation Schema & Definitions

Each golden example adheres to the following strict record schema:

```json
{
  "id": "golden_fa_001",
  "language": "fa",
  "query": "بهترین آژانس های سئو در ایران کدامند؟",
  "response": "۱. شرکت اینتن (inten.asia): متخصص سئو تکنیکال و سئو سازمانی\n۲. نوین: ارائه دهنده خدمات دیجیتال مارکتینگ",
  "entity_id": "inten",
  "expected": {
    "mentioned": true,
    "recommended": true,
    "rank": 1,
    "cited": true,
    "attributed": false,
    "wrong_entity": false
  },
  "intent_type": "recommendation"
}
```

### Field Definitions & Labeling Rules

#### 1. `mentioned` (Boolean)
* `true` if the entity (or its documented aliases, domains, or founders) is present in the response text in a relevant context.
* `false` if the entity is not referenced, or if the mention is a false homonym collision (`wrong_entity=true`).

#### 2. `recommended` (Boolean)
* `true` ONLY if the entity is explicitly endorsed or positioned within a recommended list of solutions in response to a comparative or recommendation query.
* `false` if the entity is merely mentioned as background context, historical note, or incidental information.

#### 3. `rank` (Integer or `null`)
* Integer ($1, 2, 3, \dots$) representing the ordinal position of the entity within a structured ordered list.
* `null` if the response does not format the entity in an explicit numbered list.

#### 4. `cited` (Boolean)
* `true` if a URL or canonical domain hostname for the entity appears in grounding citation references or within the text body.
* `false` if no URL or domain reference exists.

#### 5. `attributed` (Boolean)
* `true` if a specific claim, statistic, fact, or quotation is explicitly credited to the entity via sourcing prose (e.g., *"According to WHO..."*, *"طبق گزارش اینتن..."*, *"وفقاً لتقرير..."*, *"raporuna göre..."*, *"根据...报告"*).
* `false` if the entity is cited as a link or listed as a vendor without explicit prose attribution.

#### 6. `wrong_entity` (Boolean)
* `true` if a homonym collision is detected that matches a negative constraint in `do_not_confuse` (e.g., *Bazaar Molavi*, *Divan-e Molavi / Rumi the poet*, *Novin Charm* when evaluating a tech company or SEO agency).
* `false` for legitimate entity matches.

---

## 4. Adversarial Edge Cases Tested

The v1 golden dataset deliberately includes challenging linguistic and orthographic patterns:
* **Persian / Arabic Normalization**:
  * Arabic Yeh (`ي`) vs Persian Yeh (`ی`)
  * Arabic Kaf (`ك`) vs Persian Kaf (`ک`)
  * Zero-Width Non-Joiner (ZWNJ) variations (e.g., `وب‌۲۴` vs `وب ۲۴` vs `وب24`)
  * Tatweel / Kashida (`شركـة`)
* **Unspaced Compound Names**:
  * Continuous unspaced strings in conversational logs (e.g., `تقیمولوی`, `taghimolavi`).
* **Homonym & Entity Ambiguity**:
  * Distinguishing founder mentions (*Taghi Molavi*) from geographical landmarks (*Bazaar Molavi*, *Khiyaban Molavi*) and classical literature (*Divan Molavi*).
  * Distinguishing fintech brands (*Novin*) from unrelated consumer goods (*Novin Charm*).
* **Citation vs Attribution Disconnection**:
  * Responses with external URL citations without linguistic attribution.
  * Responses with explicit prose quotes without external web citations.

---

## 5. Limitations & Future Annotation Process

### Current Limitations
1. **Sample Size**: v1 contains 220 curated records. While covering 5 languages and 18 diverse entities, larger open-ended samples will provide further granular confidence bands.
2. **Domain Representation**: Focuses primarily on enterprise software, digital agencies, founders, technology providers, and academic sources.

### Future Annotation Roadmap
1. Multi-annotator inter-rater agreement calculation (Cohen's Kappa $\kappa \ge 0.85$).
2. Expansion of African and South Asian linguistic edge cases (Urdu, Hindi, Swahili, Amharic).
3. Automated drift monitoring on parser updates to prevent regression.
