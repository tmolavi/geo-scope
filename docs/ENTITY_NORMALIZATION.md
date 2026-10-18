# GEO-Scope Multilingual Entity Normalization Specification

**Version:** 1.0.0  
**Effective Date:** October 2026  
**Status:** Canonical Standard for Entity Matching & Disambiguation  
**Scope:** Multi-Engine AI Outputs across Persian, English, Turkish, Azerbaijani (Latin), and Arabic  

---

## 1. Objective and Core Principles

In empirical AI visibility benchmarking, subtle linguistic variations, script differences, orthographic quirks, and transliterations often cause false negatives (failing to recognize a brand) or false positives (attributing a homonym or generic word to a brand).

This specification establishes a deterministic, multi-tier normalization and entity recognition standard that:
1. Prevents false negatives from script orthography (e.g., Persian vs. Arabic Yeh/Kaf, ZWNJ vs. space, Turkish dotted/dotless I).
2. Prevents false positives through strict negative homonym filtering (`do_not_confuse`) and excluded alias lists (`excluded_aliases`).
3. Classifies matches into three explicit tiers: **`exact`**, **`normalized_exact`**, and **`probable`**.
4. Records an auditable trace of every normalization rule applied.
5. Models parent-brand vs. subsidiary/product hierarchies without double counting.

---

## 2. Supported Languages & Linguistic Rules

GEO-Scope provides first-class support for five languages:

### 2.1 Persian (`fa`)
- **Yeh & Kaf Unification:**
  - Arabic Yeh (`ي`, `\u064A`), Alef Maksura (`ى`, `\u0649`), Urdu Yeh (`ے`, `\u06D2`) $\rightarrow$ Persian Yeh (`ی`, `\u06CC`).
  - Arabic Kaf (`ك`, `\u0643`), Swash Kaf (`ڪ`, `\u06AA`) $\rightarrow$ Persian Kaf (`ک`, `\u06A9`).
- **Zero-Width Non-Joiner (ZWNJ):**
  - Half-space (`\u200C`) is handled with dual tokenization: it preserves intra-word compound boundaries while matching both spaced and unspaced variants.
- **Teh Marbuta & Heh:**
  - Arabic Teh Marbuta (`ة`, `\u0629`) $\rightarrow$ Heh (`ه`, `\u0647`).
- **Alef Variants:**
  - `آ`, `أ`, `إ`, `ٱ` $\rightarrow$ Bare Alef (`ا`, `\u0627`).
- **Diacritics & Tatweel:**
  - Strips Arabic/Persian Harakat (Fatha, Damma, Kasra, Sukun, Tanwin, Shadda: `[\u064B-\u065F\u0670]`).
  - Strips Tatweel/Kashida (`ـ`, `\u0640`).
- **Numerals:**
  - Unifies Persian digits (`۰-۹`) and Arabic-Indic digits (`٠-٩`) to Latin digits (`0-9`) for numeric brand name matching.

### 2.2 Turkish (`tr`) & Azerbaijani Latin (`az`)
- **Dotted and Dotless I:**
  - Turkish and Azerbaijani feature dotted `İ` / `i` and dotless `I` / `ı`. Standard Python `.lower()` on Unicode transforms English `I` $\rightarrow$ `i`, which alters Turkish words (e.g., `İSTANBUL` vs `ISTANBUL`).
  - GEO-Scope applies locale-aware casing preserving dotted/dotless equivalence in brand dictionaries.
- **Azerbaijani Specific Characters:**
  - Schwa (`Ə` / `ə`, `\u018F` / `\u0259`) is preserved and normalized.
  - Soft G (`Ğ` / `ğ`), S with Cedilla (`Ş` / `ş`), C with Cedilla (`Ç` / `ç`), O with Umlaut (`Ö` / `ö`), U with Umlaut (`Ü` / `ü`).

### 2.3 Arabic (`ar`)
- Strips full Tashkeel, Tanwin, and Shadda diacritics.
- Normalizes Hamza carriers: `ؤ` $\rightarrow$ `و`, `ئ` $\rightarrow$ `ی`.
- Unifies straight and curly punctuation.

### 2.4 English (`en`)
- Case-folding with Unicode NFKC normalization.
- Straight (`'`) and curly (`’`, `‘`) apostrophe unification (e.g., *L'Oréal* vs *L’Oreal*).
- Hyphen and dash unification: ASCII hyphen (`-`), en-dash (`–`, `\u2013`), em-dash (`—`, `\u2014`).

---

## 3. Entity Schema & Structure

Entities are declared using the versioned JSON/Pydantic schema:

```json
{
  "entity_id": "brand-inten",
  "canonical_name": "InTen",
  "entity_type": "organization",
  "parent_entity_id": null,
  "aliases": [
    {
      "value": "اینتن",
      "language": "fa",
      "match_type": "exact"
    },
    {
      "value": "Inten",
      "language": "en",
      "match_type": "case_insensitive"
    },
    {
      "value": "in-ten",
      "language": "en",
      "match_type": "normalized_exact"
    }
  ],
  "excluded_aliases": [
    "intent",
    "intents"
  ],
  "do_not_confuse": [
    "اینترن",
    "اینترنت"
  ],
  "domains": ["inten.asia"],
  "related_domains": ["molavi.pro"],
  "same_as": ["https://wikidata.org/wiki/Q..."],
  "normalization_version": "1.0"
}
```

---

## 4. The Three Match Tiers

To eliminate subjective or noisy detections, entity matches are partitioned into three rigorous tiers:

| Match Tier | Description | Inclusion in Official Benchmarks & MAVI | Confidence Score |
|:---|:---|:---|:---|
| **`exact`** | Byte-for-byte verbatim match or standard ASCII case-fold. | **Automatic** | `1.0` |
| **`normalized_exact`** | Match achieved after applying documented deterministic normalization rules (Yeh/Kaf, ZWNJ, diacritics, apostrophes). | **Automatic** | `1.0` |
| **`probable`** | Heuristic match, fuzzy similarity, transliteration without predefined alias, or substring match in ambiguous compound words. | **Requires Human Review.** Excluded from public leaderboards until confirmed. | `< 1.0` |

### 4.1 Match Record Schema

For every candidate detection, the parser produces an auditable trace:

```json
{
  "entity_id": "brand-inten",
  "matched_text": "اينتن",
  "match_type": "normalized_exact",
  "normalization_rules_applied": [
    "arabic_yeh_to_persian_yeh",
    "whitespace_collapsed"
  ],
  "confidence": 1.0,
  "human_validated": false
}
```

---

## 5. False-Positive Protection & Disambiguation

1. **`do_not_confuse` (Negative Homonym Filter):**
   - If an occurrence of a name matches a declared negative homonym pattern (e.g. *Taghi Molavi* vs *Mowlavi Bazaar* or *Rumi / Mawlana*), the match is immediately vetoed.
2. **`excluded_aliases` (Lexical Collision Filter):**
   - Brand names that collide with common vocabulary (e.g. English word *intent* colliding with *Inten*) must declare the colliding terms in `excluded_aliases`. Token boundary matching enforces that generic occurrences are never attributed to the brand.
3. **Person vs. Organization Separation:**
   - Mentions of executive founders (e.g. *Taghi Molavi*) are parsed separately as `person_mentioned` and do not increment the organization's brand mention counter unless the organization name itself is also present.

---

## 6. Parent Brand vs. Product Aggregation

When tracking a conglomerate or multi-product ecosystem (e.g., Google $\rightarrow$ Android, Google Cloud; or Microsoft $\rightarrow$ Azure):
- Each entity possesses an optional `parent_entity_id`.
- Benchmarks can report at either the **child product level** or the **aggregated parent brand level**.
- In parent rollups, if both the parent and child are mentioned in the same answer, the parent receives **one** mention (no double counting).

---

*GEO-Scope Multilingual Entity Normalization Specification v1.0.*
