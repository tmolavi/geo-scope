# GEO-Scope Golden Parser Evaluation Dataset (v1)

## Overview

The Golden Set v1 is a human-labeled, versioned ground-truth dataset designed to empirically measure the accuracy, precision, and recall of the GEO-Scope `ObservationParser`.

## Dataset Scope & Statistics

- **Total Labeled Examples**: 220
- **Supported Languages**: Persian (`fa`), English (`en`), Arabic (`ar`), Turkish (`tr`), Chinese (`zh`)
- **Supported Intent Categories**:
  - `informational` (definitions, founder queries, biographical queries, how-to, overviews)
  - `recommendation` (best options, top lists, explicit endorsements)
  - `comparison` (comparative evaluations)
  - `navigational` (portal and login queries)
  - `general`

## Evaluated Edge Cases

1. **Homonyms & Negative Disambiguation (`do_not_confuse`)**:
   - `بازار مولوی` / `فرش مولوی` vs `اینتن` / `تقی مولوی`
   - `Robert Altman` / `Altman Z-score` vs `Sam Altman`
   - `slack variable` vs `Slack Technologies`
   - `صلاة الظهر` vs `منصة نون`
   - `رجل كريم` vs `شركة كريم`
   - `طعام جاهز` vs `شركة جاهز`
   - `su getir` vs `Getir`
   - `一百度` vs `百度`
2. **Person vs Organization**: Distinguishes executive founders from company mentions.
3. **Persian & Arabic Normalization**: Handles ZWNJ (`نیم‌فاصله`), unspaced continuous variants (`تقیمولوی`, `taghimolavi`), Arabic `ي`/`ی`, `ك`/`ک`, `ة`/`ه`, and Alef variants.
4. **Independent Citation and Attribution**:
   - `cited`: Verification of domain/URL references in markdown citations or footer notes.
   - `attributed`: Verification of explicit sourcing and attribution statements in generated prose.
5. **Strict Rank Extraction**: Ensures ranks are extracted strictly from recognized numbered list syntax and prevents paragraph ordering from being inferred as algorithmic ranks.

## Evaluation CLI

```bash
geo-scope parser evaluate --golden-set benchmark/golden_sets/v1
```
