"""The orchestrated pipeline: explicit stages, an artifact per stage, resume from the last complete stage, a cost ceiling.

Every stage reads the previous artifact and writes its own under data/runs/<date>/. A re-run with --resume
skips stages whose artifact exists. One failing feed, article or model call never kills the run (N3).
"""

from __future__ import annotations

import datetime as dt
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx

from morning_brief import __version__
from morning_brief.budget import BudgetGuard
from morning_brief.cluster import DEFAULT_THRESHOLD, cluster_items, story_text
from morning_brief.compose import Issue, IssueItem, build_item, compose_issue, write_intro
from morning_brief.config import Profile, Settings
from morning_brief.deliver import deliver_once
from morning_brief.deliver.email import send_email
from morning_brief.deliver.file import deliver_file
from morning_brief.embeddings import Embedder
from morning_brief.extract import extract_all
from morning_brief.llm.client import LLMClient
from morning_brief.llm.schemas import ArticleSummary, ResearchNote
from morning_brief.memory import StoryMemory, days_before
from morning_brief.rank import score_articles
from morning_brief.render.render import render_html, render_markdown
from morning_brief.report import build_report, render_report
from morning_brief.research import AgentBackend, Budgets, research_story
from morning_brief.security import check_issue, scrub_model_text
from morning_brief.sources import Collector, collect
from morning_brief.sources.base import Article
from morning_brief.store import Store
from morning_brief.summarize import summarize_articles
from morning_brief.tracing import Tracer

STAGES = ["collect", "extract", "summarize", "score", "group", "research", "compose", "deliver"]


@dataclass
class Clients:
    fast: LLMClient
    smart: LLMClient
    embedder: Embedder
    agent_backend: AgentBackend | None = None  # None = skip research (offline runs)
    http: httpx.Client | None = None
    collectors: dict[str, Collector] | None = None
    cluster_threshold: float = DEFAULT_THRESHOLD  # the fake embedder needs a lower one; the real one is tuned in M3


@dataclass
class RunContext:
    settings: Settings
    profile: Profile
    store: Store
    tracer: Tracer
    guard: BudgetGuard
    date: str
    run_id: str
    run_dir: Path
    versions: dict[str, Any]
    stages: list[dict[str, Any]] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    channels: tuple[str, ...] = ("file",)


class Pipeline:
    def __init__(self, settings: Settings, profile: Profile, clients: Clients, *, versions: dict[str, Any] | None = None) -> None:
        self.settings, self.profile, self.clients = settings, profile, clients
        self.versions = versions or {"prompt_version": "summarize.v1", "model_fast": clients.fast.model, "model_smart": clients.smart.model, "embedding_model": clients.embedder.model, "index_version": "story-memory"}

    # -- artifacts ------------------------------------------------------------------------------
    @staticmethod
    def _artifact(ctx: RunContext, stage: str) -> Path:
        return ctx.run_dir / f"{stage}.json"

    @staticmethod
    def _save(ctx: RunContext, stage: str, payload: Any) -> None:
        ctx.run_dir.mkdir(parents=True, exist_ok=True)
        Pipeline._artifact(ctx, stage).write_text(json.dumps(payload, ensure_ascii=False, default=str), encoding="utf-8")

    @staticmethod
    def _load(ctx: RunContext, stage: str) -> Any:
        return json.loads(Pipeline._artifact(ctx, stage).read_text(encoding="utf-8"))

    def _run_stage(self, ctx: RunContext, name: str, fn, *, resume: bool) -> Any:
        if resume and self._artifact(ctx, name).exists():
            ctx.tracer.event("stage.resumed", name)
            return self._load(ctx, name)
        started = time.monotonic()
        with ctx.tracer.span(name, "stage"):
            payload, items_in, items_out, failures = fn()
        ctx.stages.append({"name": name, "items_in": items_in, "items_out": items_out, "seconds": round(time.monotonic() - started, 2), "failures": len(failures)})
        ctx.failures.extend(f"{name}: {f}" for f in failures)
        self._save(ctx, name, payload)
        return payload

    # -- the run --------------------------------------------------------------------------------
    def run(self, date: str | None = None, *, resume: bool = False, channels: tuple[str, ...] = ("file",), stop_after: str | None = None) -> dict[str, Any]:
        date = date or dt.datetime.now(tz=dt.UTC).date().isoformat()
        run_id = f"run-{date}"
        run_dir = self.settings.data_dir / "runs" / date
        tracer = Tracer(run_dir / "traces.jsonl", trace_id=run_id)
        store = Store(self.settings.data_dir / "brief.sqlite")
        ctx = RunContext(self.settings, self.profile, store, tracer, BudgetGuard(self.settings.budget_usd), date, run_id, run_dir, self.versions, channels=channels)
        store.start_run(run_id, date)
        status = "ok"
        try:
            self._stages(ctx, resume=resume, stop_after=stop_after)
        except Exception as exc:  # noqa: BLE001 - the report must be written whatever happened
            status = "failed"
            ctx.failures.append(f"pipeline: {type(exc).__name__}: {exc}")
            tracer.event("pipeline.failed", f"{type(exc).__name__}: {exc}")
        if status == "ok" and ctx.failures:
            status = "partial"
        report = build_report(run_id=run_id, date=date, status=status, stages=ctx.stages, cost_usd=ctx.guard.spent_usd, cost_by_stage=ctx.guard.by_stage, trace_path=str(tracer.path), failures=ctx.failures)
        (run_dir / "run-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        (run_dir / "run-report.md").write_text(render_report(report), encoding="utf-8")
        store.finish_run(run_id, status, ctx.guard.spent_usd, report)
        return report

    def _stages(self, ctx: RunContext, *, resume: bool, stop_after: str | None) -> None:
        c, s, p = self.clients, ctx.store, self.profile
        http = c.http or httpx.Client()

        def collect_stage():
            articles, failures = collect(p, http, collectors=c.collectors)
            articles = articles[: self.settings.max_articles]
            inserted = s.upsert_articles(articles)
            ctx.tracer.event("collect.done", f"{len(articles)} articles, {inserted} new")
            return [a.as_dict() for a in articles], len(p.sources), len(articles), failures

        articles = [Article.from_dict(d) for d in self._run_stage(ctx, "collect", collect_stage, resume=resume)]
        if stop_after == "collect":
            return

        def extract_stage():
            todo = [a for a in articles if (stored := s.get_article(a.id)) is None or stored.extract_status == "pending"]
            offline = c.http is None and c.collectors is not None
            done = [self._offline_extract(a) for a in todo] if offline else extract_all(todo, http, concurrency=4)
            for a in done:
                s.update_extraction(a)
            merged = {a.id: a for a in articles}
            for a in done:
                merged[a.id] = a
            for a in merged.values():
                stored = s.get_article(a.id)
                if stored and stored.extract_status != "pending":
                    merged[a.id] = stored
            failures = [f"{a.id}: {a.extract_status}" for a in merged.values() if not a.extract_status.startswith("ok")]
            return [a.as_dict() for a in merged.values()], len(articles), sum(1 for a in merged.values() if a.extract_status == "ok"), failures

        articles = [Article.from_dict(d) for d in self._run_stage(ctx, "extract", extract_stage, resume=resume)]
        if stop_after == "extract":
            return

        def summarize_stage():
            result = summarize_articles(articles, c.fast, s, tracer=ctx.tracer, guard=ctx.guard, concurrency=self.settings.summarize_concurrency)
            return {aid: sm.model_dump() for aid, sm in result.summaries.items()}, len(articles), len(result.summaries), result.failures

        summaries = {aid: ArticleSummary.model_validate(d) for aid, d in self._run_stage(ctx, "summarize", summarize_stage, resume=resume).items()}
        by_id = {a.id: a for a in articles}
        if stop_after == "summarize":
            return

        def score_stage():
            items = [(by_id[aid], sm) for aid, sm in summaries.items() if aid in by_id and sm.is_article]
            scored, failures = score_articles(items, p, c.fast, guard=ctx.guard)
            s.save_scores(ctx.run_id, [(sc.article_id, sc.final, sc.reason, sc.boosts) for sc in scored])
            return [{"article_id": sc.article_id, "final": sc.final, "llm_score": sc.llm_score, "reason": sc.reason, "boosts": sc.boosts} for sc in scored], len(items), len(scored), failures

        scored = self._run_stage(ctx, "score", score_stage, resume=resume)
        if stop_after == "score":
            return

        def group_stage():
            candidates = [sc for sc in scored if sc["final"] > 0]
            priority = {sc["article_id"]: sc["final"] for sc in candidates}
            texts = [(sc["article_id"], story_text(by_id[sc["article_id"]].title, summaries[sc["article_id"]].bullets[0] if summaries[sc["article_id"]].bullets else "")) for sc in candidates]
            clusters = cluster_items(texts, c.embedder, threshold=c.cluster_threshold, priority=priority)
            s.save_clusters(ctx.run_id, [(cl.cluster_id, cl.representative_id, cl.member_ids) for cl in clusters])
            follow_ups: dict[str, dict[str, Any]] = {}
            failures: list[str] = []
            try:
                memory = StoryMemory(self.settings.data_dir / "chroma", c.embedder)
                rep_texts = [(cl.cluster_id, dict(texts)[cl.representative_id]) for cl in clusters]
                for cid, fu in memory.follow_ups(ctx.date, rep_texts, window_days=p.follow_up_days).items():
                    follow_ups[cid] = {"day": fu.seen_day, "url": fu.url, "similarity": fu.similarity}
                memory.remember(ctx.date, [(cl.cluster_id, dict(texts)[cl.representative_id], by_id[cl.representative_id].url) for cl in clusters])
                memory.prune(days_before(ctx.date, 60))
            except Exception as exc:  # noqa: BLE001 - memory is an enrichment; the issue goes out without it
                failures.append(f"memory: {type(exc).__name__}: {exc}")
            return {"clusters": [{"cluster_id": cl.cluster_id, "representative_id": cl.representative_id, "member_ids": cl.member_ids} for cl in clusters], "follow_ups": follow_ups}, len(candidates), len(clusters), failures

        grouped = self._run_stage(ctx, "group", group_stage, resume=resume)
        clusters, follow_ups = grouped["clusters"], grouped["follow_ups"]
        if stop_after == "group":
            return

        def research_stage():
            top = clusters[: p.top_stories]
            notes: dict[str, Any] = {}
            failures: list[str] = []
            if c.agent_backend is None:
                return notes, len(top), 0, ["research skipped: no agent backend (offline run)"]
            for cl in top:
                story = by_id[cl["representative_id"]]
                result = research_story(story, articles, c.agent_backend, c.fast, http=c.http, budgets=Budgets(), guard=ctx.guard)
                ctx.tracer.event("research.call", story.id, stop_reason=result.stop_reason, steps=result.steps, tokens=result.tokens, sources=result.sources, tool_calls=result.tool_calls)
                if result.note:
                    notes[cl["cluster_id"]] = result.note.model_dump()
                else:
                    failures.append(f"{story.id}: {result.stop_reason}")
            return notes, len(top), len(notes), failures

        notes = self._run_stage(ctx, "research", research_stage, resume=resume)
        if stop_after == "research":
            return

        def compose_stage():
            items: list[IssueItem] = []
            for cl in clusters:
                rep = by_id[cl["representative_id"]]
                sm = summaries[rep.id]
                sc = next(x for x in scored if x["article_id"] == rep.id)
                research = ResearchNote.model_validate(notes[cl["cluster_id"]]) if cl["cluster_id"] in notes else None
                fu = follow_ups.get(cl["cluster_id"])
                item = build_item(rep, sm, score=sc["final"], reason=sc["reason"], members=[by_id[m] for m in cl["member_ids"] if m in by_id], follow_up=None, research=research)
                if fu:
                    item.follow_up_of = fu
                item.headline, item.why_it_matters = scrub_model_text(item.headline), scrub_model_text(item.why_it_matters)
                item.bullets = [scrub_model_text(b) for b in item.bullets]
                items.append(item)
            items = items[: p.issue_size]
            top, more = items[: p.top_stories], items[p.top_stories :]
            intro = write_intro(ctx.date, p, [i.headline for i in top], c.smart, guard=ctx.guard)
            skipped = f"{len(ctx.failures)} item(s) could not be processed today; see the run report." if ctx.failures else ""
            metadata = {**self.versions, "run_id": ctx.run_id, "cost_usd": round(ctx.guard.spent_usd, 6), "generator": f"morning-brief {__version__}"}
            issue = compose_issue(ctx.date, p, top, more, intro, metadata=metadata, skipped_note=skipped)
            markdown = render_markdown(issue)
            policy = check_issue(issue, markdown)
            failures = [f"policy: {v}" for v in policy.violations]
            html = render_html(issue)
            s.save_issue(ctx.run_id, ctx.date, markdown, html, metadata)
            return {"issue": issue.model_dump(), "markdown": markdown, "html": html}, len(clusters), len(items), failures

        composed = self._run_stage(ctx, "compose", compose_stage, resume=resume)
        if stop_after == "compose":
            return

        def deliver_stage():
            issue = Issue.model_validate(composed["issue"])
            receipts: dict[str, str] = {}
            failures: list[str] = []
            for channel in ctx.channels:
                try:
                    if channel == "file":
                        sent, receipt = deliver_once(s, ctx.run_id, "file", lambda: deliver_file(self.settings.out_dir, ctx.date, composed["markdown"], composed["html"]))
                    elif channel == "email":
                        sent, receipt = deliver_once(s, ctx.run_id, "email", lambda: send_email(self.settings, f"Morning Brief · {issue.date}", composed["markdown"], composed["html"]))
                    else:
                        raise ValueError(f"unknown channel {channel}")
                    receipts[channel] = receipt if sent else "already delivered"
                except Exception as exc:  # noqa: BLE001 - a dead mail server must not lose the file delivery
                    failures.append(f"{channel}: {type(exc).__name__}: {exc}")
            return receipts, len(ctx.channels), len(receipts), failures

        self._run_stage(ctx, "deliver", deliver_stage, resume=resume)

    @staticmethod
    def _offline_extract(article: Article) -> Article:
        """Offline runs have no network: the feed blurb stands in for the page text."""
        article.text = article.text or article.summary
        article.extract_status = "ok" if article.text else "failed:no-text"
        return article
