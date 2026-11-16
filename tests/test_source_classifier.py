"""
Unit tests for SourceClassifier and domain provenance categorization in geo-scope.
"""

import pytest
from geo_scope.parser.sources import (
    SourceClassifier,
    SourceCategory,
    DomainSourceMeta,
)


def test_classify_owned_domain():
    classifier = SourceClassifier(owned_domains=["inten.asia", "molavi.pro"])

    res1 = classifier.classify_domain("https://inten.asia/services/seo")
    assert res1.category == SourceCategory.OWNED
    assert res1.is_owned is True
    assert res1.clean_domain == "inten.asia"

    res2 = classifier.classify_domain("sub.molavi.pro")
    assert res2.category == SourceCategory.OWNED
    assert res2.is_owned is True


def test_classify_ugc_community():
    classifier = SourceClassifier(owned_domains=["inten.asia"])

    res_reddit = classifier.classify_domain("https://www.reddit.com/r/SEO/comments/123")
    assert res_reddit.category == SourceCategory.UGC_COMMUNITY
    assert res_reddit.is_ugc is True

    res_virgool = classifier.classify_domain("https://virgool.io/@user/post")
    assert res_virgool.category == SourceCategory.UGC_COMMUNITY
    assert res_virgool.is_ugc is True


def test_classify_aggregators():
    classifier = SourceClassifier()

    res_g2 = classifier.classify_domain("https://www.g2.com/products/inten/reviews")
    assert res_g2.category == SourceCategory.AGGREGATOR_REVIEWS
    assert res_g2.is_aggregator is True

    res_torob = classifier.classify_domain("torob.com")
    assert res_torob.category == SourceCategory.AGGREGATOR_REVIEWS


def test_classify_earned_media():
    classifier = SourceClassifier()

    res_zoomit = classifier.classify_domain("https://www.zoomit.ir/software/123")
    assert res_zoomit.category == SourceCategory.EARNED_MEDIA
    assert res_zoomit.is_earned_media is True

    res_techcrunch = classifier.classify_domain("techcrunch.com")
    assert res_techcrunch.category == SourceCategory.EARNED_MEDIA


def test_classify_official_docs():
    classifier = SourceClassifier()

    res_wiki = classifier.classify_domain("https://en.wikipedia.org/wiki/Search_engine_optimization")
    assert res_wiki.category == SourceCategory.OFFICIAL_DOCS
    assert res_wiki.is_official_doc is True


def test_classify_general_web_fallback():
    classifier = SourceClassifier(owned_domains=["inten.asia"])

    res_random = classifier.classify_domain("https://some-unknown-blog-123.com/article")
    assert res_random.category == SourceCategory.GENERAL_WEB
    assert res_random.is_owned is False
    assert res_random.is_ugc is False
