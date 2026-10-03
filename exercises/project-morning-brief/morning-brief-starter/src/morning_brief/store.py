"""SQLite store: the source of truth for articles, summaries, scores, clusters, issues, runs and deliveries."""
from __future__ import annotations
import datetime as dt
import json
import sqlite3
from pathlib import Path
from typing import Any
from morning_brief.sources.base import Article
SCHEMA_VERSION = 1
MIGRATIONS = ['\n    CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL);\n    CREATE TABLE IF NOT EXISTS articles (\n        id TEXT PRIMARY KEY, url TEXT NOT NULL, canonical_url TEXT NOT NULL, source TEXT NOT NULL, title TEXT NOT NULL,\n        published_at TEXT, summary TEXT, text TEXT, fetched_at TEXT NOT NULL, extract_status TEXT NOT NULL);\n    CREATE TABLE IF NOT EXISTS summaries (\n        article_id TEXT PRIMARY KEY, schema_version INTEGER NOT NULL, json TEXT NOT NULL, model TEXT NOT NULL,\n        tokens_in INTEGER NOT NULL, tokens_out INTEGER NOT NULL, cost REAL NOT NULL, created_at TEXT NOT NULL);\n    CREATE TABLE IF NOT EXISTS scores (\n        article_id TEXT NOT NULL, run_id TEXT NOT NULL, score REAL NOT NULL, reason TEXT NOT NULL, boosts_json TEXT NOT NULL,\n        PRIMARY KEY (article_id, run_id));\n    CREATE TABLE IF NOT EXISTS clusters (\n        run_id TEXT NOT NULL, cluster_id TEXT NOT NULL, representative_article_id TEXT NOT NULL, member_ids_json TEXT NOT NULL,\n        PRIMARY KEY (run_id, cluster_id));\n    CREATE TABLE IF NOT EXISTS issues (\n        run_id TEXT PRIMARY KEY, date TEXT NOT NULL, markdown TEXT NOT NULL, html TEXT NOT NULL, metadata_json TEXT NOT NULL);\n    CREATE TABLE IF NOT EXISTS runs (\n        id TEXT PRIMARY KEY, date TEXT NOT NULL, started_at TEXT NOT NULL, finished_at TEXT, status TEXT NOT NULL,\n        cost REAL NOT NULL DEFAULT 0, report_json TEXT);\n    CREATE TABLE IF NOT EXISTS deliveries (\n        issue_id TEXT NOT NULL, channel TEXT NOT NULL, delivered_at TEXT NOT NULL, idempotency_key TEXT NOT NULL,\n        PRIMARY KEY (issue_id, channel));\n    ']

def _now() -> str:
    raise NotImplementedError

class Store:

    def __init__(self, path: Path | str) -> None:
        raise NotImplementedError

    def migrate(self) -> None:
        raise NotImplementedError

    def upsert_articles(self, articles: list[Article]) -> int:
        """Insert new articles; existing ids are left alone (idempotent ingestion). Returns the number inserted."""
        raise NotImplementedError

    def update_extraction(self, article: Article) -> None:
        raise NotImplementedError

    def get_article(self, article_id: str) -> Article | None:
        raise NotImplementedError

    def articles_since(self, since_iso: str, limit: int=200) -> list[Article]:
        raise NotImplementedError

    def count_articles(self) -> int:
        raise NotImplementedError

    def save_summary(self, article_id: str, summary_json: str, *, model: str, tokens_in: int, tokens_out: int, cost: float) -> None:
        raise NotImplementedError

    def get_summary(self, article_id: str) -> str | None:
        raise NotImplementedError

    def save_scores(self, run_id: str, rows: list[tuple[str, float, str, dict[str, float]]]) -> None:
        raise NotImplementedError

    def save_clusters(self, run_id: str, clusters: list[tuple[str, str, list[str]]]) -> None:
        raise NotImplementedError

    def save_issue(self, run_id: str, date: str, markdown: str, html: str, metadata: dict[str, Any]) -> None:
        raise NotImplementedError

    def get_issue(self, run_id: str) -> dict[str, Any] | None:
        raise NotImplementedError

    def start_run(self, run_id: str, date: str) -> None:
        raise NotImplementedError

    def finish_run(self, run_id: str, status: str, cost: float, report: dict[str, Any]) -> None:
        raise NotImplementedError

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        raise NotImplementedError

    def record_delivery(self, issue_id: str, channel: str, idempotency_key: str) -> bool:
        """True if recorded now; False if this issue was already delivered on this channel (never twice, F8)."""
        raise NotImplementedError

    def delivered(self, issue_id: str, channel: str) -> bool:
        raise NotImplementedError

    def prune_articles(self, before_iso: str) -> int:
        raise NotImplementedError
