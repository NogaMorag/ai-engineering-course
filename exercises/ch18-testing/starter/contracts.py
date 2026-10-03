"""Chapter 18 starter: contract (snapshot) tests for the schemas and tool declarations the model sees.

A snapshot pins the JSON the model receives. Changing it is allowed, but it must be a decision:
run with AI_COURSE_UPDATE_SNAPSHOTS=1 to rewrite, then review the diff in git.
"""

from __future__ import annotations

import difflib
import json
import os
from pathlib import Path
from typing import Any


class SnapshotMismatch(AssertionError):
    pass


def _dump(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def updating_snapshots() -> bool:
    return os.environ.get("AI_COURSE_UPDATE_SNAPSHOTS") == "1"


def assert_matches_snapshot(name: str, value: Any, snapshot_dir: Path, *, update: bool | None = None) -> str:
    """Create the snapshot on first use; afterwards fail with a unified diff when the value drifts.

    Returns "created", "updated" or "matched" so a test can assert on first-run behaviour.
    """
    # TODO 2: resolve `update`; make the dir; path = snapshot_dir / f"{name}.json"; current = _dump(value).
    # No file -> write it and return "created". Same content -> "matched". Different and update -> write,
    # "updated". Different and not update -> raise SnapshotMismatch with a unified diff (difflib).
    raise NotImplementedError
