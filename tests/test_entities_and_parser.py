"""
Tests for Entity Registry, Multi-lingual Normalization, and Observation Parser.
"""

import pytest
from geo_scope.entities.models import Entity
from geo_scope.entities.registry import EntityRegistry, normalize_text
from geo_scope.parser.observation_parser import ObservationParser, classify_query_intent


def test_arabic_persian_normalization():
    # Test Arabic Yeh vs Persian Yeh, Arabic Kaf vs Persian Kaf, Tatweel, ZWNJ
    raw_ar = "شركـة اينتـن يافـت نشـد"
    norm = normalize_text(raw_ar)
    assert "ک" in norm
    assert "ی" in norm
    assert "ـ" not in norm

    # ZWNJ replacement
    zwnj_text = "وب\u200c۲۴"
    assert normalize_text(zwnj_text) == "وب ۲۴"


def test_entity_registry_loading():
    data = [
        {
            "id": "inten",
            "names": ["Inten", "اینتن"],
            "people": ["Taghi Molavi", "تقی مولوی"],
            "domains": ["inten.asia"],
            "related_domains": ["molavi.pro"],
            "do_not_confuse": ["بازار مولوی", "خیابان مولوی", "مولوی شاعر"],
        },
        {
            "id": "novin",
            "names": ["Novin", "نوین"],
            "people": [],
            "domains": ["novin.com"],
            "do_not_confuse": ["بانک اقتصاد نوین", "نوین چرم"],
        }
    ]
    reg = EntityRegistry.from_list(data)
    assert len(reg) == 2
    assert reg.get("inten").id == "inten"
    assert "تقی مولوی" in reg.get("inten").people
    assert reg.ids() == ["inten", "novin"]


def test_person_vs_brand_mention_separation():
    parser = ObservationParser()
    entity = Entity(
        id="inten",
        names=["Inten", "اینتن"],
        people=["Taghi Molavi", "تقی مولوی"],
        domains=["inten.asia"],
        do_not_confuse=["بازار مولوی"],
    )

    # Text mentioning ONLY the person, not the brand
    text_person_only = "تقی مولوی یکی از متخصصین برجسته بهینه‌سازی موتورهای جستجو است."
    res = parser.parse(text_person_only, entity, query="تقی مولوی کیست؟")
    assert res.person_mentioned is True
    assert res.mentioned is False

    # Text mentioning the brand
    text_brand = "شرکت سئو اینتن ارائه‌دهنده خدمات طراحی سایت است."
    res2 = parser.parse(text_brand, entity, query="آژانس های سئو")
    assert res2.mentioned is True
    assert res2.person_mentioned is False

    # Text mentioning both
    text_both = "تقی مولوی مدیرعامل آژانس دیجیتال مارکتینگ اینتن است."
    res3 = parser.parse(text_both, entity, query="درباره اینتن")
    assert res3.mentioned is True
    assert res3.person_mentioned is True


def test_homonym_negative_disambiguation():
    parser = ObservationParser()
    entity = Entity(
        id="inten",
        names=["Inten", "اینتن", "مولوی"],
        people=["Taghi Molavi", "تقی مولوی"],
        domains=["inten.asia"],
        do_not_confuse=["بازار مولوی", "خیابان مولوی", "مولوی شاعر"],
    )

    # Text contains "بازار مولوی" which is in do_not_confuse
    text_confused = "برای خرید عمده پارچه می‌توانید به بازار مولوی تهران مراجعه کنید."
    res = parser.parse(text_confused, entity, query="خرید پارچه")
    assert res.mentioned is False
    assert len(res.confused_with) > 0
    assert "بازار مولوی" in res.confused_with

    # Text contains "نوین چرم" vs entity "Novin"
    entity_novin = Entity(
        id="novin",
        names=["Novin", "نوین"],
        domains=["novin.com"],
        do_not_confuse=["بانک اقتصاد نوین", "نوین چرم"],
    )
    text_leather = "فروشگاه نوین چرم تخفیف ویژه زمستانه ارائه داده است."
    res_novin = parser.parse(text_leather, entity_novin, query="خرید پالتو چرم")
    assert res_novin.mentioned is False
    assert "نوین چرم" in res_novin.confused_with


def test_intent_gating_and_scoring_status():
    parser = ObservationParser()
    entity = Entity(
        id="inten",
        names=["Inten", "اینتن"],
        people=["Taghi Molavi", "تقی مولوی"],
        domains=["inten.asia"],
    )

    # Informational query: "تقی مولوی کیست؟"
    info_query = "تقی مولوی کیست؟"
    assert classify_query_intent(info_query) == "informational"

    info_text = "تقی مولوی موسس آژانس اینتن است."
    res_info = parser.parse(info_text, entity, query=info_query)
    assert res_info.mentioned is True
    # Informational queries must NOT be scored for rank or recommendation
    assert res_info.scoring_status == "unscored"
    assert res_info.rank is None
    assert res_info.recommended is False
    assert res_info.top1 is False

    # Recommendation query: "بهترین شرکت سئو در ایران"
    rec_query = "بهترین شرکت های سئو کدامند؟"
    assert classify_query_intent(rec_query) == "recommendation"

    rec_text = """
    برترین شرکت‌های سئو:
    1. اینتن (Inten)
    2. وب ۲۴
    3. نوین
    """
    res_rec = parser.parse(rec_text, entity, query=rec_query)
    assert res_rec.mentioned is True
    assert res_rec.scoring_status == "scored"
    assert res_rec.recommended is True
    assert res_rec.rank == 1
    assert res_rec.top1 is True


def test_confidence_thresholding():
    parser = ObservationParser(confidence_threshold=0.75)
    entity = Entity(
        id="web24",
        names=["Web24", "وب24"],
        domains=["web24.ir"],
    )
    # If confidence is below threshold, scoring_status must be 'unscored'
    res = parser.parse("متن کوتاهی درباره وب24", entity, query="اطلاعات سئو")
    if res.parser_confidence < 0.75:
        assert res.scoring_status == "unscored"
