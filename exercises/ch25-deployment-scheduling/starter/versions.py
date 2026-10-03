"""Chapter 25 starter: prompts, models and indexes are versioned together, in one file the job reads first.

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
    # TODO 2: (a) the prompt file <name>.v<n>.txt must exist in prompts_dir; (b) MODEL_FAST / MODEL_SMART in
    # `env` (default os.environ) must equal the declared models when set; (c) with index_metadata, its
    # embedding_model and index_version must match. Return the list of human-readable problems.
    raise NotImplementedError


def write_default(path: Path) -> None:
    path.write_text(json.dumps({
        "prompt_version": "summarize.v3", "model_fast": "gemini-3.5-flash-lite", "model_smart": "gemini-3.8-flash",
        "embedding_model": "gemini-embedding-2", "index_version": "notes-2026-10", "schema_version": 1,
    }, indent=2) + "\n", encoding="utf-8")
