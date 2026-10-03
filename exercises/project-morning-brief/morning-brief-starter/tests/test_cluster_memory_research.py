from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from morning_brief.budget import BudgetGuard
from morning_brief.cluster import cluster_items, story_text
from morning_brief.embeddings import CachedEmbedder, FakeEmbedder
from morning_brief.llm.client import FakeClient
from morning_brief.memory import StoryMemory, day_int, days_before
from morning_brief.research import Budgets, dispatch, make_tools, research_story
from morning_brief.sources.base import Article

A = "Cargo-Lite 2.0 ships a shared build cache. Builds dropped from 41 to 6 minutes."
B = "Cargo-Lite 2.0 released: shared build cache brings 41-minute compiles down to six. Builds dropped from 41 to 6 minutes."
C = "Kubernetes 1.36 upgrade breaks pod networking on legacy CNI. Operators lost pod networking."
D = "Clusters on the legacy CNI plugin lose pod networking after upgrading to Kubernetes 1.36. Operators lost pod networking."
E = "Satellite constellation photographs every hurricane from orbit. Images arrive within ten minutes."


def test_cluster_groups_paraphrases_and_picks_the_priority_representative() -> None:
    clusters = cluster_items([("a", A), ("b", B), ("c", C), ("d", D), ("e", E)], FakeEmbedder(), threshold=0.6, priority={"a": 50, "b": 90, "c": 70, "d": 60, "e": 10})
    groups = {tuple(sorted(c.member_ids)): c.representative_id for c in clusters}
    assert ("a", "b") in groups and groups[("a", "b")] == "b" and ("c", "d") in groups and groups[("c", "d")] == "c" and ("e",) in groups
    assert next(c.representative_id for c in clusters) == "b"  # sorted by priority
    assert cluster_items([], FakeEmbedder()) == [] and story_text("T", "lead") == "T. lead"


def test_cached_embedder_hits(tmp_path: Path) -> None:
    cached = CachedEmbedder(FakeEmbedder(), tmp_path / "cache.sqlite")
    cached.embed(["x", "y"])
    cached.embed(["y", "z"])
    assert cached.hits == 1 and cached.misses == 3


def test_story_memory_follow_ups_prune_and_model_guard(tmp_path: Path) -> None:
    memory = StoryMemory(tmp_path / "chroma", FakeEmbedder())
    memory.remember("2026-09-30", [("c-old", A, "https://example.com/old-a"), ("c-far", E, "https://example.com/old-e")])
    memory.remember("2026-09-01", [("c-ancient", C, "https://example.com/ancient-c")])
    found = memory.follow_ups("2026-10-03", [("c-new", B), ("c-k8s", D), ("c-x", "Completely unrelated gardening tips for autumn")], window_days=14, threshold=0.6)
    assert set(found) == {"c-new"} and found["c-new"].url == "https://example.com/old-a" and found["c-new"].seen_day == 20260930
    assert memory.follow_ups("2026-10-03", [("c-new", B)], window_days=1) == {}  # outside the window
    assert memory.prune(days_before("2026-10-03", 20)) == 1 and memory.count() == 2
    assert day_int("2026-10-03") == 20261003 and days_before("2026-10-03", 60) == 20260804
    with pytest.raises(RuntimeError):
        StoryMemory(tmp_path / "chroma", FakeEmbedder(model="other-model"))


def make_article(i: int, title: str, text: str) -> Article:
    a = Article.create(url=f"https://example.com/{i}", source="devwire", title=title, published_at="2026-10-02T07:00:00+00:00", summary=text[:80])
    a.text = text
    return a


def test_tools_search_read_and_fetch_allowlist() -> None:
    items = [make_article(1, "Cargo-Lite 2.0 ships a shared build cache", A + " More at https://example.com/cargo-docs"), make_article(2, "Kubernetes 1.36 breaks CNI", C)]
    tools = make_tools(items, http=None)
    text, err = dispatch(tools, "search_items", {"query": "cargo build cache"})
    assert not err and json.loads(text)["results"][0]["id"] == items[0].id
    text, err = dispatch(tools, "fetch_url", {"url": "https://example.com/cargo-docs"})
    assert err and "only links that appear in an item you read" in text
    dispatch(tools, "read_item", {"item_id": items[0].id})
    text, err = dispatch(tools, "fetch_url", {"url": "https://example.com/cargo-docs"})
    assert err and "network is disabled" in text  # allowlisted now, but no http client in this run
    assert dispatch(tools, "read_item", {"item_id": "nope"})[1] and dispatch(tools, "nope", {})[1]


class FakeBackend:
    def __init__(self, scripted, model: str = "fake-agent"):
        self.scripted = list(scripted)
        self.model = model

    def create(self, *, history, tools, system):
        item = self.scripted.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def interaction(steps=None, text=""):
    return SimpleNamespace(steps=steps or [], output_text=text, usage=SimpleNamespace(total_input_tokens=300, total_output_tokens=50))


def call(cid, name, args):
    return SimpleNamespace(type="function_call", id=cid, name=name, arguments=args)


def test_research_story_reads_sources_then_structures_the_note() -> None:
    items = [make_article(1, "Cargo-Lite 2.0 ships a shared build cache", A), make_article(2, "Rust survey: compile times", "Compile times are the top complaint.")]
    backend = FakeBackend([
        interaction([call("c1", "read_item", {"item_id": items[0].id})]),
        interaction([call("c2", "search_items", {"query": "rust compile"}), call("c3", "read_item", {"item_id": items[1].id})]),
        interaction(text="Context: builds were slow. Key fact: 41 to 6 minutes."),
    ])
    structurer = FakeClient(script=[json.dumps({"context": "Builds were slow across the ecosystem.", "key_fact": "Builds dropped from 41 to 6 minutes.", "source_ids": ["made-up"]})])
    guard = BudgetGuard(1.0)
    result = research_story(items[0], items, backend, structurer, budgets=Budgets(max_steps=6), guard=guard)
    assert result.stop_reason == "answered" and result.steps == 3 and result.sources == [items[0].id, items[1].id]
    assert result.note is not None and result.note.source_ids == result.sources  # the code's list wins over the model's
    assert result.tool_calls == ["read_item", "search_items", "read_item"] and guard.calls == 4


def test_research_budgets_and_loop_detection() -> None:
    items = [make_article(1, "t", A)]
    looping = FakeBackend([interaction([call("c1", "read_item", {"item_id": items[0].id})]), interaction([call("c2", "read_item", {"item_id": items[0].id})])])
    assert research_story(items[0], items, looping, FakeClient(), budgets=Budgets(max_steps=6)).stop_reason == "loop_detected"
    forever = FakeBackend([interaction([call(f"c{i}", "search_items", {"query": f"q{i}"})]) for i in range(10)])
    assert research_story(items[0], items, forever, FakeClient(), budgets=Budgets(max_steps=2)).stop_reason == "max_steps"
    ticks = iter([0.0, 0.0, 100.0, 100.0, 100.0])
    slow = FakeBackend([interaction([call(f"c{i}", "search_items", {"query": f"q{i}"})]) for i in range(10)])
    assert research_story(items[0], items, slow, FakeClient(), budgets=Budgets(max_seconds=60), clock=lambda: next(ticks)).stop_reason == "timeout"
    broke = BudgetGuard(0.0)
    assert research_story(items[0], items, FakeBackend([interaction(text="x")], model="gemini-3.8-flash"), FakeClient(), guard=broke).stop_reason == "budget"  # a priced model, so the guard can trip
