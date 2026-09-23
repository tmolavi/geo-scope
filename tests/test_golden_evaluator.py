"""
Tests for Golden Parser Evaluation and Reproducible Benchmark Protocol.
"""

from pathlib import Path
import pytest
from geo_scope.entities.models import Entity
from geo_scope.parser.observation_parser import ObservationParser, classify_query_intent
from geo_scope.parser.evaluator import evaluate_golden_set


def test_golden_set_evaluation_runs_and_meets_thresholds():
    golden_dir = Path("benchmark/golden_sets/v1")
    if not golden_dir.exists():
        pytest.skip("Golden set v1 directory not found.")

    eval_result = evaluate_golden_set(str(golden_dir))
    metrics = eval_result["metrics_by_field"]

    assert eval_result["total_records"] >= 200
    assert metrics["mentioned"]["f1_score"] >= 0.95
    assert metrics["recommended"]["f1_score"] >= 0.95
    assert metrics["cited"]["f1_score"] >= 0.95
    assert metrics["attributed"]["f1_score"] >= 0.80
    assert metrics["wrong_entity"]["f1_score"] >= 0.80
    assert eval_result["rank_evaluation"]["rank_accuracy"] >= 0.95


def test_unspaced_persian_and_latin_name_resolution():
    parser = ObservationParser()
    entity = Entity(
        id="inten",
        names=["Inten", "اینتن"],
        people=["Taghi Molavi", "تقی مولوی"],
        domains=["inten.asia"],
        do_not_confuse=["بازار مولوی"],
    )

    # Unspaced Persian name
    text_unspaced_fa = "بر اساس مصاحبه با تقیمولوی، استراتژی سئو در سال ۲۰۲۶ تغییر کرده است."
    res_fa = parser.parse(text_unspaced_fa, entity, query="تقی مولوی کیست؟")
    assert res_fa.person_mentioned is True

    # Unspaced Latin name
    text_unspaced_en = "According to taghimolavi, AI answer engines prioritize authority."
    res_en = parser.parse(text_unspaced_en, entity, query="Who is Taghi Molavi?")
    assert res_en.person_mentioned is True


def test_context_aware_homonym_rejection():
    parser = ObservationParser()
    entity = Entity(
        id="inten",
        names=["Inten", "اینتن"],
        people=["Taghi Molavi", "تقی مولوی"],
        domains=["inten.asia"],
        do_not_confuse=["بازار مولوی", "خیابان مولوی", "دیوان مولوی"],
    )

    # False positive context: Bazaar Molavi
    text_bazaar = "برای خرید عمده پارچه و ظروف می‌توانید به بازار مولوی در تهران مراجعه کنید."
    res_bazaar = parser.parse(text_bazaar, entity, query="مرکز خرید پارچه تهران کجاست؟")
    assert res_bazaar.wrong_entity is True
    assert res_bazaar.person_mentioned is False

    # False positive context: Divan Molavi
    text_divan = "اشعار دیوان مولوی و شمس تبریزی از شاهکارهای ادبیات فارسی هستند."
    res_divan = parser.parse(text_divan, entity, query="اشعار مولوی چه ویژگی دارند؟")
    assert res_divan.wrong_entity is True
    assert res_divan.person_mentioned is False


def test_citation_vs_attribution_distinction():
    parser = ObservationParser()
    entity = Entity(
        id="nature_journal",
        names=["Nature", "نیچر"],
        domains=["nature.com"],
        do_not_confuse=[],
    )

    # Response with domain citation in list, but no sourcing quote
    text_citation_only = "1. Scientific literature can be accessed at nature.com or science.org."
    res_cite = parser.parse(text_citation_only, entity, citations=["https://www.nature.com/articles/123"])
    assert res_cite.cited is True
    assert res_cite.attributed is False

    # Response with explicit attribution prose
    text_attributed = "According to Nature, the experimental results demonstrate quantum supremacy."
    res_attr = parser.parse(text_attributed, entity)
    assert res_attr.attributed is True


def test_multilingual_intent_classification():
    assert classify_query_intent("Best SEO agencies in Tehran") == "recommendation"
    assert classify_query_intent("بهترین شرکت های سئو کدامند؟") == "recommendation"
    assert classify_query_intent("أفضل أدوات تحسين محركات البحث") == "recommendation"
    assert classify_query_intent("En iyi dijital pazarlama ajansları") == "recommendation"
    assert classify_query_intent("最好的SEO工具有哪些") == "recommendation"

    assert classify_query_intent("What is generative engine optimization?") == "informational"
    assert classify_query_intent("مفهوم بهینه‌سازی موتورهای هوش مصنوعی چیست؟") == "informational"
    assert classify_query_intent("ما هو الفرق بين الذكاء الاصطناعي ومحركات البحث") == "informational"
