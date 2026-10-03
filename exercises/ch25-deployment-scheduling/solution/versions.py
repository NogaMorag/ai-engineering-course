"""Chapter 25 solution: prompts, models and indexes are versioned together, in one file the job reads first.

    versions.json
    {
      "prompt_version": "summarize.v3",
      "model_fast": "gemini-3.5-flash-lite",
      "model_smart": "gemini-3.8-flash",
      "embedding_model": "gemini-embedding-2",
      "index_version": "notes-2026-10",
      "schema_version": 1
    }

Rollback means restoring this file (and the index it names), not reverting one prompt edit.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from pydantic import BaseModel, Field


class Versions(BaseModel):
    prompt_version: str = Field(pattern=r"^[a-z0-9_-]+\.v\d+$")
    model_fast: str
    model_smart: str
    embedding_model: str
    index_version: str
    schema_version: int = Field(ge=1)


def load_versions(path: Path) -> Versions:
    return Versions.model_validate_json(path.read_text(encoding="utf-8"))


def check_versions(versions: Versions, *, prompts_dir: Path, env: dict[str, str] | None = None, index_metadata: dict[str, str] | None = None) -> list[str]:
    """Mismatches between the declared versions and what the runtime would actually use."""
    env = os.environ if env is None else env
    problems = []
    name, _, number = versions.prompt_version.rpartition(".v")
    if not (prompts_dir / f"{name}.v{number}.txt").exists():
        problems.append(f"prompt file {name}.v{number}.txt not found in {prompts_dir}")
    for key, declared in (("MODEL_FAST", versions.model_fast), ("MODEL_SMART", versions.model_smart)):
        actual = env.get(key)
        if actual and actual != declared:
            problems.append(f"{key}={actual} in the environment but versions.json says {declared}")
    if index_metadata is not None:
        stored = index_metadata.get("embedding_model")
        if stored and stored != versions.embedding_model:
            problems.append(f"index was built with {stored}, versions.json says {versions.embedding_model}")
        if index_metadata.get("index_version") not in (None, versions.index_version):
            problems.append(f"index version {index_metadata.get('index_version')} differs from {versions.index_version}")
    return problems


def write_default(path: Path) -> None:
    path.write_text(json.dumps({
        "prompt_version": "summarize.v3", "model_fast": "gemini-3.5-flash-lite", "model_smart": "gemini-3.8-flash",
        "embedding_model": "gemini-embedding-2", "index_version": "notes-2026-10", "schema_version": 1,
    }, indent=2) + "\n", encoding="utf-8")
