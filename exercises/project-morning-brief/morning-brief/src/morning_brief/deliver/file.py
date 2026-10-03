"""File delivery: the zero-setup path. Markdown and HTML side by side."""

from __future__ import annotations

from pathlib import Path


def deliver_file(out_dir: Path, date: str, markdown: str, html: str) -> str:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"brief-{date}.md").write_text(markdown, encoding="utf-8")
    (out_dir / f"brief-{date}.html").write_text(html, encoding="utf-8")
    return str(out_dir / f"brief-{date}.html")
