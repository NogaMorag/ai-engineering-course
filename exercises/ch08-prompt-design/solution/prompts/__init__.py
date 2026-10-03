"""Chapter 8 solution: prompts as versioned files.

A template file looks like:

    # version: 2
    # changelog: what changed and why
    ---
    ...prompt body with {{variables}}...

Usage:

    from ch08.prompts import load, render
    template = load("summarize", version=2)      # or load("summarize") for the newest
    text = render(template, article="...")
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent
_FILENAME = re.compile(r"^(?P<name>[a-z0-9_]+)\.v(?P<version>\d+)\.txt$")
_PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")


@dataclass(frozen=True)
class PromptTemplate:
    name: str
    version: int
    changelog: str
    body: str

    @property
    def variables(self) -> set[str]:
        return set(_PLACEHOLDER.findall(self.body))


def list_versions(name: str) -> list[int]:
    """All versions of a prompt, ascending. Empty if the prompt does not exist."""
    versions = []
    for path in PROMPTS_DIR.glob(f"{name}.v*.txt"):
        match = _FILENAME.match(path.name)
        if match:
            versions.append(int(match.group("version")))
    return sorted(versions)


def load(name: str, version: int | None = None) -> PromptTemplate:
    """Load one version of a prompt (the newest when version is None)."""
    versions = list_versions(name)
    if not versions:
        raise FileNotFoundError(f"no prompt named {name!r} in {PROMPTS_DIR}")
    if version is None:
        version = versions[-1]
    if version not in versions:
        raise FileNotFoundError(f"prompt {name!r} has versions {versions}, not {version}")
    raw = (PROMPTS_DIR / f"{name}.v{version}.txt").read_text(encoding="utf-8")
    header, separator, body = raw.partition("\n---\n")
    if not separator:
        raise ValueError(f"{name}.v{version}.txt has no '---' line between header and body")
    changelog = ""
    for line in header.splitlines():
        if line.startswith("# changelog:"):
            changelog = line.removeprefix("# changelog:").strip()
    return PromptTemplate(name=name, version=version, changelog=changelog, body=body.strip("\n"))


def render(template: PromptTemplate, **variables: str) -> str:
    """Fill every {{variable}}. Missing or unexpected variables are errors, never silent."""
    expected = template.variables
    given = set(variables)
    missing = expected - given
    extra = given - expected
    if missing or extra:
        raise ValueError(
            f"{template.name} v{template.version}: missing variables {sorted(missing)}, unexpected {sorted(extra)}"
        )
    return _PLACEHOLDER.sub(lambda match: variables[match.group(1)], template.body)
