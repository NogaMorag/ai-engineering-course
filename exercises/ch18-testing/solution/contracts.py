"""Chapter 18 solution: contract (snapshot) tests for the schemas and tool declarations the model sees.

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
    update = updating_snapshots() if update is None else update
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    path = snapshot_dir / f"{name}.json"
    current = _dump(value)
    if not path.exists():
        path.write_text(current, encoding="utf-8")
        return "created"
    stored = path.read_text(encoding="utf-8")
    if stored == current:
        return "matched"
    if update:
        path.write_text(current, encoding="utf-8")
        return "updated"
    diff = "".join(difflib.unified_diff(stored.splitlines(True), current.splitlines(True), fromfile=f"snapshot/{name}", tofile="current"))
    raise SnapshotMismatch(f"snapshot {name!r} drifted. Review the diff; rerun with AI_COURSE_UPDATE_SNAPSHOTS=1 to accept.\n{diff}")
