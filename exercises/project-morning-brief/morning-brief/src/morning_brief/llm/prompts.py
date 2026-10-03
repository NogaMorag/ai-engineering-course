"""Prompts are versioned files: `<name>.v<n>.txt` with a header, a separator and a body with {{variables}}."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent / "prompts"
PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")


@dataclass(frozen=True)
class PromptTemplate:
    name: str
    version: int
    changelog: str
    body: str

    @property
    def variables(self) -> set[str]:
        return set(PLACEHOLDER.findall(self.body))

    @property
    def id(self) -> str:
        return f"{self.name}.v{self.version}"


def load(name: str, version: int, directory: Path = PROMPTS_DIR) -> PromptTemplate:
    text = (directory / f"{name}.v{version}.txt").read_text(encoding="utf-8")
    header, _, body = text.partition("\n---\n")
    changelog = next((line.split(":", 1)[1].strip() for line in header.splitlines() if line.startswith("# changelog:")), "")
    return PromptTemplate(name, version, changelog, body.strip())


def render(template: PromptTemplate, **variables: str) -> str:
    missing = template.variables - set(variables)
    extra = set(variables) - template.variables
    if missing or extra:
        raise ValueError(f"prompt {template.id}: missing {sorted(missing)}, extra {sorted(extra)}")
    return PLACEHOLDER.sub(lambda m: variables[m.group(1)], template.body)
