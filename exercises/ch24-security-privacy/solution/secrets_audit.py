r"""Chapter 24 solution, day 48: find secrets in the working tree AND in git history.

    uv run python -m ch24.secrets_audit .            # exit 1 when something is found

A key that was committed and then deleted is still in the history. Rotation, not deletion, fixes that.
"""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

PATTERNS: dict[str, re.Pattern[str]] = {
    "google_api_key": re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
    "openai_key": re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}"),
    "github_token": re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}"),
    "private_key": re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "generic_assignment": re.compile(r"(?i)\b(api[_-]?key|secret|token|password)\b\s*[:=]\s*['\"][^'\"\s]{12,}['\"]"),
}
PLACEHOLDERS = re.compile(r"(?i)(your[-_ ]?key|changeme|example|placeholder|xxxx|<[^>]+>|\.\.\.)")
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", ".ruff_cache"}
TEXT_SUFFIXES = {".py", ".md", ".txt", ".toml", ".yaml", ".yml", ".json", ".jsonl", ".env", ".example", ".ps1", ".sh", ".cfg", ".ini", ""}


@dataclass(frozen=True)
class Finding:
    where: str  # path:line or commit:path
    kind: str
    preview: str  # masked, never the full secret


def mask(value: str) -> str:
    return value[:6] + "…" + value[-3:] if len(value) > 12 else "…"


def scan_text(text: str, where: str) -> list[Finding]:
    findings = []
    for number, line in enumerate(text.splitlines(), start=1):
        if PLACEHOLDERS.search(line):
            continue
        for kind, pattern in PATTERNS.items():
            for match in pattern.finditer(line):
                findings.append(Finding(f"{where}:{number}", kind, mask(match.group(0))))
    return findings


def scan_tree(root: Path) -> list[Finding]:
    findings = []
    for path in root.rglob("*"):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.parts) or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        findings += scan_text(text, path.relative_to(root).as_posix())
    return findings


def scan_history(root: Path) -> list[Finding]:
    """Every added line in every commit on every branch. Deleted secrets are still here."""
    try:
        log = subprocess.run(["git", "-C", str(root), "log", "-p", "--all", "--no-color", "--no-ext-diff", "--text"], capture_output=True, text=True, check=True, encoding="utf-8", errors="replace").stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    findings, commit, path = [], "?", "?"
    for line in log.splitlines():
        if line.startswith("commit "):
            commit = line.split()[1][:8]
        elif line.startswith("+++ b/"):
            path = line[6:]
        elif line.startswith("+") and not line.startswith("+++"):
            findings += [Finding(f"{commit}:{path}", f.kind, f.preview) for f in scan_text(line[1:], "")]
    return findings


def audit(root: Path) -> list[Finding]:
    seen: set[tuple[str, str, str]] = set()
    unique = []
    for f in scan_tree(root) + scan_history(root):
        key = (f.where, f.kind, f.preview)
        if key not in seen:
            seen.add(key)
            unique.append(f)
    return unique


def main(argv: list[str] | None = None) -> int:
    root = Path((argv or sys.argv[1:] or ["."])[0]).resolve()
    findings = audit(root)
    for f in findings:
        print(f"{f.kind:<20} {f.where:<50} {f.preview}")
    print(f"{len(findings)} finding(s) in {root}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
