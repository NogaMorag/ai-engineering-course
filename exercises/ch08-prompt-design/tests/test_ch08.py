"""Offline tests for the chapter 8 prompts package. Copy to ai-course/tests/test_ch08.py."""

from pathlib import Path

import pytest

from ch08.prompts import PromptTemplate, list_versions, load, render


def test_three_versions_exist_in_order() -> None:
    assert list_versions("summarize") == [1, 2, 3]
    assert list_versions("does_not_exist") == []


def test_load_newest_by_default_and_reads_changelog() -> None:
    template = load("summarize")
    assert template.version == 3
    assert "example" in template.changelog.lower()
    assert "{{article}}" in template.body


def test_load_specific_version_and_unknown_version() -> None:
    assert load("summarize", 1).version == 1
    with pytest.raises(FileNotFoundError):
        load("summarize", 99)


def test_render_fills_placeholders() -> None:
    template = PromptTemplate(name="t", version=1, changelog="", body="Hello {{name}}, read {{doc}}.")
    assert render(template, name="Noga", doc="this") == "Hello Noga, read this."


def test_render_rejects_missing_and_extra_variables() -> None:
    template = PromptTemplate(name="t", version=1, changelog="", body="Hello {{name}}.")
    with pytest.raises(ValueError):
        render(template)
    with pytest.raises(ValueError):
        render(template, name="Noga", extra="x")


def test_v2_and_v3_keep_the_edge_case_rule_and_tags() -> None:
    for version in (2, 3):
        body = load("summarize", version).body
        assert "NOT_AN_ARTICLE" in body
        assert "<article>" in body and "</article>" in body


def test_sample_articles_are_present() -> None:
    data_dir = Path(__file__).resolve().parents[1] / "ch08" / "data" / "articles"
    files = sorted(data_dir.glob("*.txt"))
    assert len(files) == 3
    assert all(len(path.read_text(encoding="utf-8").split()) > 60 for path in files)
