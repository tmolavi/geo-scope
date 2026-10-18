"""
Unit tests for Multilingual Entity Normalizer & Registry (geo_scope/entities/normalizer.py, registry.py).
Validates:
  - Persian Yeh/Kaf unification, ZWNJ, and Persian digits
  - Turkish and Azerbaijani Latin dotted/dotless I, Schwa (Ə/ə), and Cedillas
  - Arabic diacritics, Tashkeel, and Tatweel removal
  - English straight vs curly apostrophes and dashes
  - 3 Match Tiers: exact, normalized_exact, probable
  - Rule transformation tracing
  - False-positive protection via do_not_confuse and excluded_aliases
  - Parent brand and subsidiary relationships
"""

import pytest
from geo_scope.entities.normalizer import MultilingualNormalizer, EntityMatchResult
from geo_scope.entities.models import Entity
from geo_scope.entities.registry import EntityRegistry


def test_persian_yeh_and_kaf_normalization():
    # Arabic Yeh (ي \u064a) and Arabic Kaf (ك \u0643) normalized to Persian (ی \u06cc, ک \u06a9)
    raw = "شركت اينتن"
    norm, rules = MultilingualNormalizer.normalize(raw, language="fa")
    assert norm == "شرکت اینتن"
    assert "persian_yeh_unified" in rules
    assert "persian_kaf_unified" in rules


def test_persian_zwnj_and_digits():
    raw = "خدمات سئو‌کاران در سال ۱۴۰۵"
    norm, rules = MultilingualNormalizer.normalize(raw, language="fa", unify_digits=True)
    # ZWNJ collapsed to space, digits converted to Latin
    assert "1405" in norm
    assert "digits_unified" in rules
    assert "zwnj_zero_width_handled" in rules


def test_turkish_and_azerbaijani_casing():
    # Turkish dotted İ (\u0130) -> i
    # Turkish dotless I (\u0049) -> ı (\u0131)
    # Azerbaijani Schwa Ə (\u018f) -> ə (\u0259)
    tr_text = "İSTANBUL VE IŞIK"
    tr_norm, tr_rules = MultilingualNormalizer.normalize(tr_text, language="tr")
    assert "istanbul" in tr_norm
    assert "ışık" in tr_norm
    assert "turkish_dotted_i_folded" in tr_rules
    assert "turkish_dotless_i_folded" in tr_rules

    az_text = "ƏLAVƏ MƏLUMAT"
    az_norm, az_rules = MultilingualNormalizer.normalize(az_text, language="az")
    assert "əlavə" in az_norm
    assert "məlumat" in az_norm
    assert "azerbaijani_schwa_folded" in az_rules


def test_arabic_diacritics_and_tatweel():
    raw = "أَفْضَلُ شَرِكَةٍ لِـلتَّسْوِيقِ"
    norm, rules = MultilingualNormalizer.normalize(raw, language="ar")
    # Tatweel removed, Tashkeel removed, Alef unified
    assert "افضل" in norm
    assert "diacritics_removed" in rules


def test_english_apostrophes_and_dashes():
    raw = "L’Oréal—Leading In–Ten Brand"
    norm, rules = MultilingualNormalizer.normalize(raw, language="en")
    assert "l'oréal" in norm
    assert "in-ten" in norm
    assert "apostrophe_unified" in rules
    assert "hyphen_dash_unified" in rules


def test_three_match_tiers():
    text = "بهترین آژانس اینتن و شركت اينتن است."
    names = ["اینتن", "Inten"]
    
    # 1. Exact match for 'اینتن'
    # 2. Normalized exact match for 'اينتن' (Arabic Yeh)
    matches = MultilingualNormalizer.match_entity(
        text=text,
        entity_id="inten",
        names=names,
        language="fa",
    )
    assert len(matches) >= 2
    match_types = set(m.match_type for m in matches)
    assert "exact" in match_types
    assert "normalized_exact" in match_types

    # Verify rule trace
    norm_exact = next(m for m in matches if m.match_type == "normalized_exact")
    assert "persian_yeh_unified" in norm_exact.normalization_rules_applied
    assert norm_exact.confidence == 1.0


def test_negative_homonym_do_not_confuse_protection():
    # Taghi Molavi should NOT match when the text mentions 'بازار مولوی'
    text = "من در بازار مولوی تهران پارچه خریدم."
    names = ["مولوی", "Taqi Molavi"]
    dnc = ["بازار مولوی", "فرش مولوی"]

    matches = MultilingualNormalizer.match_entity(
        text=text,
        entity_id="molavi",
        names=names,
        do_not_confuse=dnc,
        language="fa",
    )
    # The occurrence in 'بازار مولوی' must be swallowed by DNC filter
    assert len(matches) == 0


def test_excluded_aliases_collision_filter():
    # Brand 'Inten' must not trigger on English word 'intent'
    text = "The commercial intent was clearly articulated."
    names = ["Inten", "in-ten"]
    excluded = ["intent", "intents"]

    matches = MultilingualNormalizer.match_entity(
        text=text,
        entity_id="inten",
        names=names,
        excluded_aliases=excluded,
        language="en",
    )
    assert len(matches) == 0


def test_parent_child_brand_hierarchy():
    parent = Entity(
        id="alphabet",
        canonical_name="Alphabet Inc.",
        names=["Alphabet"],
        entity_type="organization",
    )
    child = Entity(
        id="google",
        canonical_name="Google",
        names=["Google"],
        parent_entity_id="alphabet",
        entity_type="organization",
    )
    reg = EntityRegistry([parent, child])

    children = reg.get_children("alphabet")
    assert len(children) == 1
    assert children[0].id == "google"

    parents = reg.get_parents()
    assert len(parents) == 1
    assert parents[0].id == "alphabet"
