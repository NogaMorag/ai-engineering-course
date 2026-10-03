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
STAGES = ['collect', 'extract', 'summarize', 'score', 'group', 'research', 'compose', 'deliver']

@dataclass
class Clients:
    fast: LLMClient
    smart: LLMClient
    embedder: Embedder
    agent_backend: AgentBackend | None = None
    http: httpx.Client | None = None
    collectors: dict[str, Collector] | None = None
    cluster_threshold: float = DEFAULT_THRESHOLD

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
    channels: tuple[str, ...] = ('file',)

class Pipeline:

    def __init__(self, settings: Settings, profile: Profile, clients: Clients, *, versions: dict[str, Any] | None=None) -> None:
        raise NotImplementedError

    @staticmethod
    def _artifact(ctx: RunContext, stage: str) -> Path:
        raise NotImplementedError

    @staticmethod
    def _save(ctx: RunContext, stage: str, payload: Any) -> None:
        raise NotImplementedError

    @staticmethod
    def _load(ctx: RunContext, stage: str) -> Any:
        raise NotImplementedError

    def _run_stage(self, ctx: RunContext, name: str, fn, *, resume: bool) -> Any:
        raise NotImplementedError

    def run(self, date: str | None=None, *, resume: bool=False, channels: tuple[str, ...]=('file',), stop_after: str | None=None) -> dict[str, Any]:
        raise NotImplementedError

    def _stages(self, ctx: RunContext, *, resume: bool, stop_after: str | None) -> None:
        raise NotImplementedError

    @staticmethod
    def _offline_extract(article: Article) -> Article:
        """Offline runs have no network: the feed blurb stands in for the page text."""
        raise NotImplementedError
