"""Render the Issue model to Markdown and HTML."""
from __future__ import annotations
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from morning_brief.compose import Issue
TEMPLATES = Path(__file__).parent / 'templates'
_env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=select_autoescape(['html', 'j2']), trim_blocks=True, lstrip_blocks=True)
_md_env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=False, trim_blocks=True, lstrip_blocks=True)

def render_markdown(issue: Issue) -> str:
    raise NotImplementedError

def render_html(issue: Issue) -> str:
    raise NotImplementedError
