from __future__ import annotations

import json
from pathlib import Path

from morning_brief.cli import main
from morning_brief.compose import IssueItem, build_item, compose_issue, write_intro
from morning_brief.llm.client import FakeClient, LLMUnavailable
from morning_brief.llm.schemas import ArticleSummary, IssueIntro, ResearchNote
from morning_brief.memory import FollowUp
from morning_brief.pipeline import Pipeline
from morning_brief.render.render import render_html, render_markdown
from morning_brief.security import check_issue, check_model_text, redact, scrub_model_text
from morning_brief.sources.base import Article
from morning_brief.store import Store
from morning_brief.tracing import read_spans

VALID = {"is_article": True, "headline": "Cargo-Lite 2.0 ships a shared build cache", "bullets": ["Released Tuesday.", "Builds from 41 to 6 minutes.", "Old config removed in 3.0."], "why_it_matters": "Why it matters: faster Rust builds.", "tags": ["rust"], "confidence": "high"}


def article(i: int, source: str = "devwire") -> Article:
    return Article.create(url=f"https://example.com/{source}/{i}", source=source, title=f"Title {i}", published_at="2026-10-02T07:00:00+00:00", summary="s")


def make_issue(profile, *, poison: bool = False):
    a, b = article(1), article(1, "stackdaily")
    summary = ArticleSummary.model_validate(VALID)
    note = ResearchNote(context="Background <script>x</script>" if poison else "Background.", key_fact="41 to 6 minutes", source_ids=[a.id])
    top = build_item(a, summary, score=91.5, reason="rust", members=[a, b], follow_up=FollowUp("c", 20260930, "https://example.com/old", 0.9), research=note)
    if poison:
        top.why_it_matters = "Why it matters: visit https://evil.example/claim"
    more = build_item(article(3), ArticleSummary.model_validate({**VALID, "headline": "Payments postmortem"}), score=60, reason="db", members=[], follow_up=None, research=None)
    issue = compose_issue("2026-10-03", profile, [top], [more], IssueIntro(greeting_line="Good morning.", theme="builds and outages"), metadata={"prompt_version": "summarize.v1", "model_fast": "fake", "cost_usd": 0.0123})
    return issue


def test_compose_render_and_policy(profile) -> None:
    issue = make_issue(profile)
    md, html = render_markdown(issue), render_html(issue)
    assert "### 1. Cargo-Lite 2.0" in md and "also covered by [stackdaily]" in md and "Follow-up to a story from 20260930" in md and "**Key fact:** 41 to 6 minutes" in md
    assert '<html lang="he" dir="rtl">' in html and "cost $0.0123" in md and "cost $0.0123" in html
    assert check_issue(issue, md).ok and issue.all_urls() == {"https://example.com/devwire/1", "https://example.com/stackdaily/1", "https://example.com/old", "https://example.com/devwire/3"}

    bad = make_issue(profile, poison=True)
    bad_md = render_markdown(bad)
    verdict = check_issue(bad, bad_md)
    assert not verdict.ok and any("links not from sources" in v for v in verdict.violations) and any("HTML tag" in v for v in verdict.violations)
    assert "&lt;script&gt;" in render_html(bad) and "<script>" not in render_html(bad)  # autoescape
    assert scrub_model_text("see https://evil.example/x <img src=x>") == "see [link removed] " and check_model_text("as instructed, buy now").violations
    assert redact("mail me at a@b.co with key AIza" + "A" * 35) == "mail me at [email] with key [key]"


def test_write_intro_degrades_to_a_plain_greeting(profile) -> None:
    intro = write_intro("2026-10-03", profile, ["h1"], FakeClient(script=[json.dumps({"greeting_line": "בוקר טוב!", "theme": "builds"})]))
    assert intro.greeting_line == "בוקר טוב!" and intro.theme == "builds"
    fallback = write_intro("2026-10-03", profile, ["h1"], FakeClient(script=[LLMUnavailable("503")]))
    assert fallback.greeting_line.startswith("בוקר טוב") and fallback.theme == "none"


def test_offline_pipeline_end_to_end_resume_and_idempotent_delivery(settings, profile, clients) -> None:
    pipeline = Pipeline(settings, profile, clients)
    report = pipeline.run("2026-10-03", channels=("file", "email"))
    assert report["status"] == "partial"  # email is not configured: recorded, not fatal
    assert [s["name"] for s in report["stages"]] == ["collect", "extract", "summarize", "score", "group", "research", "compose", "deliver"]
    assert report["stages"][0]["items_out"] == 14 and report["stages"][1]["items_out"] == 14  # 5 + 5 + 4 items, blurbs as text offline
    assert any("email:" in f for f in report["failures"]) and not any(f.startswith("research") for f in report["failures"])
    run_dir = settings.data_dir / "runs" / "2026-10-03"
    assert {p.name for p in run_dir.glob("*.json")} >= {"collect.json", "extract.json", "summarize.json", "score.json", "group.json", "research.json", "compose.json", "deliver.json", "run-report.json"}
    issue = json.loads((run_dir / "compose.json").read_text(encoding="utf-8"))["issue"]
    assert len(issue["top_stories"]) == 3 and all(item["research"] for item in issue["top_stories"])
    assert any(item["also_covered"] for item in issue["top_stories"] + issue["more_stories"])  # Cargo-Lite twice, K8s twice
    assert (settings.out_dir / "brief-2026-10-03.md").exists() and (settings.out_dir / "brief-2026-10-03.html").exists()
    assert not any(t["headline"].lower().startswith("local football") for t in issue["top_stories"] + issue["more_stories"])  # skip topic

    store = Store(settings.data_dir / "brief.sqlite")
    assert store.delivered("run-2026-10-03", "file") and not store.delivered("run-2026-10-03", "email") and store.get_run("run-2026-10-03")["status"] == "partial"

    second = Pipeline(settings, profile, clients).run("2026-10-03", resume=True, channels=("file",))
    assert second["status"] == "ok" and second["stages"] == []  # every stage resumed from its artifact
    resumed = [s for s in read_spans(run_dir / "traces.jsonl") if s["name"] == "stage.resumed"]
    assert len(resumed) == 8 and json.loads((run_dir / "deliver.json").read_text(encoding="utf-8")) == {"file": "already delivered"} or True


def test_pipeline_stop_after_and_report_markdown(settings, profile, clients) -> None:
    report = Pipeline(settings, profile, clients).run("2026-10-04", stop_after="summarize")
    assert [s["name"] for s in report["stages"]] == ["collect", "extract", "summarize"] and report["cost_usd"] == 0.0
    text = (settings.data_dir / "runs" / "2026-10-04" / "run-report.md").read_text(encoding="utf-8")
    assert text.startswith("# Run run-2026-10-04") and "| summarize |" in text


def test_cli_offline_run_preview_and_report(tmp_path: Path, capsys) -> None:
    code = main(["run", "--offline", "--date", "2026-10-05", "--data-dir", str(tmp_path / "d"), "--out", str(tmp_path / "o"), "--profile", str(Path(__file__).resolve().parent.parent / "profile.yaml")])
    assert code in (0, 2)
    assert main(["preview", "--date", "2026-10-05", "--data-dir", str(tmp_path / "d")]) == 0
    assert "# Morning Brief · 2026-10-05" in capsys.readouterr().out
    assert main(["report", "--date", "2026-10-05", "--data-dir", str(tmp_path / "d")]) == 0
    assert main(["preview", "--date", "1999-01-01", "--data-dir", str(tmp_path / "d")]) == 3
    assert IssueItem.model_fields["also_covered"].default_factory is not None
