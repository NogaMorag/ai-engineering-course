"""Render the Issue model to Markdown and HTML."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from morning_brief.compose import Issue

TEMPLATES = Path(__file__).parent / "templates"
_env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=select_autoescape(["html", "j2"]), trim_blocks=True, lstrip_blocks=True)
_md_env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=False, trim_blocks=True, lstrip_blocks=True)  # Markdown is plain text: no HTML escaping


def render_markdown(issue: Issue) -> str:
    return _md_env.get_template("issue.md.j2").render(issue=issue, dir="rtl" if issue.language == "he" else "ltr")


def render_html(issue: Issue) -> str:
    return _env.get_template("issue.html.j2").render(issue=issue, dir="rtl" if issue.language == "he" else "ltr")
