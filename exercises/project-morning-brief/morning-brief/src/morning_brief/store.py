"""SQLite store: the source of truth for articles, summaries, scores, clusters, issues, runs and deliveries."""

from __future__ import annotations

import datetime as dt
import json
import sqlite3
from pathlib import Path
from typing import Any

from morning_brief.sources.base import Article

SCHEMA_VERSION = 1
MIGRATIONS = [
    """
    CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL);
    CREATE TABLE IF NOT EXISTS articles (
        id TEXT PRIMARY KEY, url TEXT NOT NULL, canonical_url TEXT NOT NULL, source TEXT NOT NULL, title TEXT NOT NULL,
        published_at TEXT, summary TEXT, text TEXT, fetched_at TEXT NOT NULL, extract_status TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS summaries (
        article_id TEXT PRIMARY KEY, schema_version INTEGER NOT NULL, json TEXT NOT NULL, model TEXT NOT NULL,
        tokens_in INTEGER NOT NULL, tokens_out INTEGER NOT NULL, cost REAL NOT NULL, created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS scores (
        article_id TEXT NOT NULL, run_id TEXT NOT NULL, score REAL NOT NULL, reason TEXT NOT NULL, boosts_json TEXT NOT NULL,
        PRIMARY KEY (article_id, run_id));
    CREATE TABLE IF NOT EXISTS clusters (
        run_id TEXT NOT NULL, cluster_id TEXT NOT NULL, representative_article_id TEXT NOT NULL, member_ids_json TEXT NOT NULL,
        PRIMARY KEY (run_id, cluster_id));
    CREATE TABLE IF NOT EXISTS issues (
        run_id TEXT PRIMARY KEY, date TEXT NOT NULL, markdown TEXT NOT NULL, html TEXT NOT NULL, metadata_json TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS runs (
        id TEXT PRIMARY KEY, date TEXT NOT NULL, started_at TEXT NOT NULL, finished_at TEXT, status TEXT NOT NULL,
        cost REAL NOT NULL DEFAULT 0, report_json TEXT);
    CREATE TABLE IF NOT EXISTS deliveries (
        issue_id TEXT NOT NULL, channel TEXT NOT NULL, delivered_at TEXT NOT NULL, idempotency_key TEXT NOT NULL,
        PRIMARY KEY (issue_id, channel));
    """
]


def _now() -> str:
    return dt.datetime.now(tz=dt.UTC).isoformat(timespec="seconds")


class Store:
    def __init__(self, path: Path | str) -> None:
        if str(path) != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(path))
        self.conn.row_factory = sqlite3.Row
        self.migrate()

    def migrate(self) -> None:
        for statement in MIGRATIONS:
            self.conn.executescript(statement)
        row = self.conn.execute("SELECT version FROM schema_version").fetchone()
        if row is None:
            self.conn.execute("INSERT INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,))
        self.conn.commit()

    # -- articles -----------------------------------------------------------------------------
    def upsert_articles(self, articles: list[Article]) -> int:
        """Insert new articles; existing ids are left alone (idempotent ingestion). Returns the number inserted."""
        inserted = 0
        for a in articles:
            cursor = self.conn.execute(
                "INSERT OR IGNORE INTO articles (id, url, canonical_url, source, title, published_at, summary, text, fetched_at, extract_status) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (a.id, a.url, a.canonical_url, a.source, a.title, a.published_at, a.summary, a.text, a.fetched_at, a.extract_status),
            )
            inserted += cursor.rowcount
        self.conn.commit()
        return inserted

    def update_extraction(self, article: Article) -> None:
        self.conn.execute("UPDATE articles SET text = ?, extract_status = ? WHERE id = ?", (article.text, article.extract_status, article.id))
        self.conn.commit()

    def get_article(self, article_id: str) -> Article | None:
        row = self.conn.execute("SELECT * FROM articles WHERE id = ?", (article_id,)).fetchone()
        return Article(**dict(row)) if row else None

    def articles_since(self, since_iso: str, limit: int = 200) -> list[Article]:
        rows = self.conn.execute("SELECT * FROM articles WHERE fetched_at >= ? ORDER BY published_at DESC LIMIT ?", (since_iso, limit)).fetchall()
        return [Article(**dict(r)) for r in rows]

    def count_articles(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]

    # -- summaries ----------------------------------------------------------------------------
    def save_summary(self, article_id: str, summary_json: str, *, model: str, tokens_in: int, tokens_out: int, cost: float) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO summaries (article_id, schema_version, json, model, tokens_in, tokens_out, cost, created_at) VALUES (?,?,?,?,?,?,?,?)",
            (article_id, SCHEMA_VERSION, summary_json, model, tokens_in, tokens_out, cost, _now()),
        )
        self.conn.commit()

    def get_summary(self, article_id: str) -> str | None:
        row = self.conn.execute("SELECT json FROM summaries WHERE article_id = ? AND schema_version = ?", (article_id, SCHEMA_VERSION)).fetchone()
        return row["json"] if row else None

    # -- scores and clusters -------------------------------------------------------------------
    def save_scores(self, run_id: str, rows: list[tuple[str, float, str, dict[str, float]]]) -> None:
        self.conn.executemany(
            "INSERT OR REPLACE INTO scores (article_id, run_id, score, reason, boosts_json) VALUES (?,?,?,?,?)",
            [(aid, run_id, score, reason, json.dumps(boosts)) for aid, score, reason, boosts in rows],
        )
        self.conn.commit()

    def save_clusters(self, run_id: str, clusters: list[tuple[str, str, list[str]]]) -> None:
        self.conn.executemany(
            "INSERT OR REPLACE INTO clusters (run_id, cluster_id, representative_article_id, member_ids_json) VALUES (?,?,?,?)",
            [(run_id, cid, rep, json.dumps(members)) for cid, rep, members in clusters],
        )
        self.conn.commit()

    # -- issues, runs, deliveries --------------------------------------------------------------
    def save_issue(self, run_id: str, date: str, markdown: str, html: str, metadata: dict[str, Any]) -> None:
        self.conn.execute("INSERT OR REPLACE INTO issues (run_id, date, markdown, html, metadata_json) VALUES (?,?,?,?,?)", (run_id, date, markdown, html, json.dumps(metadata)))
        self.conn.commit()

    def get_issue(self, run_id: str) -> dict[str, Any] | None:
        row = self.conn.execute("SELECT * FROM issues WHERE run_id = ?", (run_id,)).fetchone()
        return {**dict(row), "metadata": json.loads(row["metadata_json"])} if row else None

    def start_run(self, run_id: str, date: str) -> None:
        self.conn.execute("INSERT OR REPLACE INTO runs (id, date, started_at, status) VALUES (?,?,?,?)", (run_id, date, _now(), "running"))
        self.conn.commit()

    def finish_run(self, run_id: str, status: str, cost: float, report: dict[str, Any]) -> None:
        self.conn.execute("UPDATE runs SET finished_at = ?, status = ?, cost = ?, report_json = ? WHERE id = ?", (_now(), status, cost, json.dumps(report), run_id))
        self.conn.commit()

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        row = self.conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
        return dict(row) if row else None

    def record_delivery(self, issue_id: str, channel: str, idempotency_key: str) -> bool:
        """True if recorded now; False if this issue was already delivered on this channel (never twice, F8)."""
        cursor = self.conn.execute("INSERT OR IGNORE INTO deliveries (issue_id, channel, delivered_at, idempotency_key) VALUES (?,?,?,?)", (issue_id, channel, _now(), idempotency_key))
        self.conn.commit()
        return cursor.rowcount == 1

    def delivered(self, issue_id: str, channel: str) -> bool:
        return self.conn.execute("SELECT 1 FROM deliveries WHERE issue_id = ? AND channel = ?", (issue_id, channel)).fetchone() is not None

    def prune_articles(self, before_iso: str) -> int:
        cursor = self.conn.execute("DELETE FROM articles WHERE fetched_at < ?", (before_iso,))
        self.conn.commit()
        return cursor.rowcount
