"""
Multilingual Entity Normalizer and Rule-Traced Matcher for GEO-Scope.
Supports:
  - Persian (Yeh/Kaf unification, ZWNJ, Teh Marbuta, Alef, digits)
  - Arabic (Diacritics, Tashkeel, Hamza carriers, Tatweel)
  - Turkish & Azerbaijani Latin (Dotted/dotless I, Schwa, Cedillas, Soft G)
  - English & European (Apostrophes, hyphens/dashes, case folding)
  - 3-Tier Classification: exact, normalized_exact, probable
  - Rule-based transformation auditing
  - Negative homonym (do_not_confuse) and collision (excluded_aliases) filtering
"""

import re
import unicodedata
from typing import Dict, List, Tuple, Optional, Any, Set
from pydantic import BaseModel, Field


class EntityMatchResult(BaseModel):
    """Detailed result of an entity match with complete rule tracing."""
    entity_id: str
    matched_text: str
    match_type: str  # "exact" | "normalized_exact" | "probable"
    normalization_rules_applied: List[str] = Field(default_factory=list)
    confidence: float = 1.0
    human_validated: bool = False
    start_pos: Optional[int] = None
    end_pos: Optional[int] = None


class MultilingualNormalizer:
    """
    Deterministic text normalization pipeline across 5 target languages
    with transparent rule tracing.
    """

    # Persian/Arabic Digits to Latin
    DIGIT_MAP = {
        # Persian digits
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9',
        # Arabic-Indic digits
        '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
        '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9',
    }

    # Apostrophe variants to ASCII single quote
    APOSTROPHE_VARIANTS = ["’", "‘", "ʻ", "`", "´"]

    # Dash variants to ASCII hyphen
    DASH_VARIANTS = ["–", "—", "―", "−", "‐"]

    @classmethod
    def turkish_casefold(cls, text: str) -> Tuple[str, List[str]]:
        """
        Locale-sensitive case folding for Turkish and Azerbaijani Latin.
        Correctly maps:
          'İ' (\u0130) -> 'i'
          'I' (\u0049) -> 'ı' (\u0131)
        """
        rules = []
        if not text:
            return "", rules

        res = []
        for ch in text:
            if ch == 'İ':
                res.append('i')
                if "turkish_dotted_i_folded" not in rules:
                    rules.append("turkish_dotted_i_folded")
            elif ch == 'I':
                res.append('ı')
                if "turkish_dotless_i_folded" not in rules:
                    rules.append("turkish_dotless_i_folded")
            elif ch == 'Ə':
                res.append('ə')
                if "azerbaijani_schwa_folded" not in rules:
                    rules.append("azerbaijani_schwa_folded")
            else:
                res.append(ch.lower())
        return "".join(res), rules

    @classmethod
    def normalize(
        cls,
        text: str,
        language: Optional[str] = None,
        unify_digits: bool = False,
    ) -> Tuple[str, List[str]]:
        """
        Applies comprehensive multilingual normalization and returns
        (normalized_text, rules_applied).
        """
        if not text:
            return "", []

        rules: List[str] = []
        t = str(text)

        # 1. Unicode NFKC
        t_nfkc = unicodedata.normalize("NFKC", t)
        if t_nfkc != t:
            rules.append("unicode_nfkc_normalized")
            t = t_nfkc

        # 2. Straight vs Curly Apostrophes
        orig_t = t
        for ap in cls.APOSTROPHE_VARIANTS:
            t = t.replace(ap, "'")
        if t != orig_t:
            rules.append("apostrophe_unified")

        # 3. Dash & Hyphen Unification
        orig_t = t
        for dash in cls.DASH_VARIANTS:
            t = t.replace(dash, "-")
        if t != orig_t:
            rules.append("hyphen_dash_unified")

        # 4. Digits Unification (Persian/Arabic to Latin)
        if unify_digits:
            orig_t = t
            for src_d, tgt_d in cls.DIGIT_MAP.items():
                t = t.replace(src_d, tgt_d)
            if t != orig_t:
                rules.append("digits_unified")

        # 5. Persian & Arabic Letter Unification
        orig_t = t
        # Arabic Yeh / Alef Maksura -> Persian Yeh
        for yeh_ch in ["\u064a", "\u0649", "\u06d2"]:
            t = t.replace(yeh_ch, "\u06cc")
        if t != orig_t and "persian_yeh_unified" not in rules:
            rules.append("persian_yeh_unified")

        # Arabic Kaf / Swash Kaf -> Persian Kaf
        orig_t = t
        for kaf_ch in ["\u0643", "\u06aa", "\u06ac", "\u06ad"]:
            t = t.replace(kaf_ch, "\u06a9")
        if t != orig_t and "persian_kaf_unified" not in rules:
            rules.append("persian_kaf_unified")

        # Teh Marbuta -> Heh
        orig_t = t
        for tm in ["\u0629", "\u06c0", "\u06c1", "\u06d5"]:
            t = t.replace(tm, "\u0647")
        if t != orig_t and "teh_marbuta_normalized" not in rules:
            rules.append("teh_marbuta_normalized")

        # Alef variants -> Bare Alef
        orig_t = t
        for al in ["\u0622", "\u0623", "\u0625", "\u0671"]:
            t = t.replace(al, "\u0627")
        if t != orig_t and "alef_variants_unified" not in rules:
            rules.append("alef_variants_unified")

        # Hamza carriers
        orig_t = t
        t = t.replace("\u0624", "\u0648")  # Waw with Hamza -> Waw
        t = t.replace("\u0626", "\u06cc")  # Yeh with Hamza -> Yeh
        t = t.replace("\u0647\u0654", "\u0647")
        if t != orig_t and "hamza_carriers_normalized" not in rules:
            rules.append("hamza_carriers_normalized")

        # 6. Remove Tatweel / Kashida
        orig_t = t
        t = t.replace("\u0640", "")
        if t != orig_t:
            rules.append("tatweel_removed")

        # 7. Remove Diacritics / Tashkeel
        orig_t = t
        t = re.sub(r"[\u064b-\u065f\u0670]", "", t)
        if t != orig_t:
            rules.append("diacritics_removed")

        # 8. Zero-Width Non-Joiner (ZWNJ) and Zero-Width characters
        orig_t = t
        t = t.replace("\u200c", " ")  # ZWNJ -> space for boundary segmentation
        t = t.replace("\u200b", "")   # ZWSP
        t = t.replace("\u200d", "")   # ZWJ
        t = t.replace("\u200e", "")   # LTR
        t = t.replace("\u200f", "")   # RTL
        t = re.sub(r"[\u202a-\u202e]", "", t)
        t = t.replace("\ufeff", "")
        if t != orig_t:
            rules.append("zwnj_zero_width_handled")

        # 9. Case Folding (Turkish vs Standard)
        orig_t = t
        if language in ("tr", "az"):
            t_folded, tr_rules = cls.turkish_casefold(t)
            t = t_folded
            rules.extend(tr_rules)
        else:
            t = t.lower()
            if t != orig_t:
                rules.append("ascii_case_folded")

        # 10. Whitespace Collapse
        orig_t = t
        t = re.sub(r"\s+", " ", t).strip()
        if t != orig_t:
            rules.append("whitespace_collapsed")

        return t, rules

    @classmethod
    def match_entity(
        cls,
        text: str,
        entity_id: str,
        names: List[str],
        do_not_confuse: Optional[List[str]] = None,
        excluded_aliases: Optional[List[str]] = None,
        language: Optional[str] = None,
    ) -> List[EntityMatchResult]:
        """
        Scans text for candidate matches of an entity.
        Classifies into exact, normalized_exact, or probable.
        Enforces negative homonyms (do_not_confuse) and collision prevention.
        """
        results: List[EntityMatchResult] = []
        if not text or not names:
            return results

        dnc_list = do_not_confuse or []
        excluded_set = set(e.strip().lower() for e in (excluded_aliases or []) if e)

        norm_text, text_rules = cls.normalize(text, language)
        norm_dnc_list = [cls.normalize(d, language)[0] for d in dnc_list if d]

        for name in names:
            if not name or not name.strip():
                continue
            raw_name = name.strip()
            if raw_name.lower() in excluded_set:
                continue

            # 1. Check Tier 1: exact verbatim match
            exact_pattern = re.compile(r"(?<![\w-])" + re.escape(raw_name) + r"(?![\w-])")
            exact_matches = list(exact_pattern.finditer(text))
            exact_swallowed = cls._is_swallowed_by_dnc(text, raw_name, dnc_list) if exact_matches else False

            has_valid_exact = bool(exact_matches and not exact_swallowed)
            if has_valid_exact:
                results.append(EntityMatchResult(
                    entity_id=entity_id,
                    matched_text=raw_name,
                    match_type="exact",
                    normalization_rules_applied=[],
                    confidence=1.0,
                ))

            # 2. Check Tier 2: normalized_exact match
            norm_name, name_rules = cls.normalize(raw_name, language)
            if norm_name in excluded_set:
                continue

            norm_pattern = re.compile(r"(?<![\w-])" + re.escape(norm_name) + r"(?![\w-])", re.IGNORECASE)
            norm_matches = list(norm_pattern.finditer(norm_text))
            norm_swallowed = cls._is_swallowed_by_dnc(norm_text, norm_name, norm_dnc_list) if norm_matches else False

            has_valid_norm = bool(norm_matches and not norm_swallowed)

            if has_valid_norm:
                exact_count = len(exact_matches) if not exact_swallowed else 0
                norm_count = len(norm_matches)

                # If no exact match, or if additional occurrences were brought in via normalization
                if exact_count == 0 or norm_count > exact_count:
                    combined_rules = list(dict.fromkeys(text_rules + name_rules))
                    results.append(EntityMatchResult(
                        entity_id=entity_id,
                        matched_text=raw_name,
                        match_type="normalized_exact",
                        normalization_rules_applied=combined_rules,
                        confidence=1.0,
                    ))

            # 3. Check Tier 3: probable match (multi-token subset)
            if not has_valid_exact and not has_valid_norm:
                tokens = [t for t in norm_name.split() if len(t) >= 4]
                if len(tokens) >= 2 and all(tok in norm_text for tok in tokens):
                    results.append(EntityMatchResult(
                        entity_id=entity_id,
                        matched_text=raw_name,
                        match_type="probable",
                        normalization_rules_applied=list(dict.fromkeys(text_rules + name_rules + ["token_set_subset_match"])),
                        confidence=0.75,
                    ))

        return results

    @classmethod
    def _is_swallowed_by_dnc(cls, text: str, name: str, dnc_list: List[str]) -> bool:
        """Checks if all appearances of name are swallowed by forbidden negative phrases."""
        if not dnc_list or not name:
            return False

        pattern = re.compile(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])", re.IGNORECASE)
        name_matches = list(pattern.finditer(text))
        if not name_matches:
            return False

        dnc_spans = []
        for dnc in dnc_list:
            if not dnc or name not in dnc:
                continue
            dnc_pat = re.compile(re.escape(dnc), re.IGNORECASE)
            for m in dnc_pat.finditer(text):
                dnc_spans.append((m.start(), m.end()))

        if not dnc_spans:
            return False

        for nm in name_matches:
            n_start, n_end = nm.start(), nm.end()
            inside_dnc = any(d_start <= n_start and n_end <= d_end for d_start, d_end in dnc_spans)
            if not inside_dnc:
                return False

        return True
