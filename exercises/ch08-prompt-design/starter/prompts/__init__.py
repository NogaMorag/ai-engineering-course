"""Chapter 8 starter: prompts as versioned files. Fill in the two TODOs.

A template file looks like:

    # version: 2
    # changelog: what changed and why
    ---
    ...prompt body with {{variables}}...
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
    # TODO 1: use list_versions; raise FileNotFoundError when the prompt or the version is missing.
    # Read the file, split header and body at the first "\n---\n" line (ValueError if absent),
    # take the changelog from the "# changelog:" header line, and return a PromptTemplate.
    raise NotImplementedError


def render(template: PromptTemplate, **variables: str) -> str:
    """Fill every {{variable}}. Missing or unexpected variables are errors, never silent."""
    # TODO 2: compare template.variables with the given names; raise ValueError listing missing
    # and unexpected ones; otherwise substitute every placeholder (regex sub) and return the text.
    raise NotImplementedError
