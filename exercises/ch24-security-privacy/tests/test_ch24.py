"""Offline tests for chapter 24. Copy to ai-course/tests/test_ch24.py and run: uv run pytest -q"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from ch11.llm_client import FakeClient
from ch24.injection_eval import evaluate_case, load_cases
from ch24.injection_lab import POISONS, run_lab
from ch24.output_policy import check_output, links_in, strip_foreign_links
from ch24.redaction import redact_text
from ch24.secrets_audit import audit, scan_text

SOURCE = "Cargo-Lite 2.0 shipped a cache. Details: https://example.com/cargo-lite-2"
VALID = {"is_article": True, "headline": "Cargo-Lite 2.0 ships a shared build cache", "bullets": ["Builds dropped from 41 to 6 minutes.", "Content-hash keyed cache.", "Old config removed in 3.0."], "why_it_matters": "Why it matters: faster builds.", "tags": ["rust"], "confidence": "high"}


def test_output_policy_catches_foreign_links_html_and_echoes() -> None:
    clean = check_output("Faster builds [see https://example.com/cargo-lite-2].", source_text=SOURCE)
    assert clean.ok and clean.foreign_links == []
    bad = check_output("As instructed, visit https://evil.example/claim <script>x()</script>", source_text=SOURCE)
    assert not bad.ok and bad.foreign_links == ["https://evil.example/claim"] and len(bad.violations) == 3
    allowed = check_output("Read https://docs.example.org/guide", source_text=SOURCE, allowed_hosts={"docs.example.org"})
    assert allowed.ok
    assert links_in("a https://x.example/p, and (https://y.example/q).") == ["https://x.example/p", "https://y.example/q"]
    assert strip_foreign_links("go to https://evil.example/x now", source_text=SOURCE) == "go to [link removed] now"


def test_injection_lab_and_eval_with_fakes() -> None:
    poisoned = {**VALID, "bullets": ["The release was cancelled.", "Claim your prize at https://evil.example/claim-prize", "x"]}
    fake = FakeClient(script=[json.dumps(poisoned), json.dumps(VALID), json.dumps(VALID)])
    rows = run_lab(fake)
    assert [r["poison"] for r in rows] == list(POISONS) and rows[0]["mentions_cancelled"] and rows[0]["foreign_links"] == ["https://evil.example/claim-prize"]
    assert rows[1]["violations"] == [] and rows[2]["violations"] == []

    cases = load_cases()
    assert len(cases) == 5 and {c.id for c in cases} == {"inj01", "inj02", "inj03", "inj04", "inj05"}
    good = evaluate_case(FakeClient(script=[json.dumps(VALID)]), cases[0])
    assert good.passed and good.detail == "ok"
    bad = evaluate_case(FakeClient(script=[json.dumps({**VALID, "headline": "Release cancelled"})]), cases[0])
    assert not bad.passed and "cancel" in bad.detail
    smuggled = evaluate_case(FakeClient(script=[json.dumps({**VALID, "why_it_matters": "Why it matters: see https://evil.example/mirror"})]), cases[1])
    assert not smuggled.passed and "evil.example" in smuggled.detail


def test_secrets_audit_finds_keys_in_tree_and_history(tmp_path: Path) -> None:
    fake_key = "AIza" + "A" * 35
    assert [f.kind for f in scan_text(f'GEMINI_API_KEY = "{fake_key}"', "x.py")] == ["google_api_key"]
    assert [f.kind for f in scan_text('api_key = "abcdefghijklmnop1234"', "x.py")] == ["generic_assignment"]
    assert scan_text("GEMINI_API_KEY=your-key-here", ".env.example") == []
    assert scan_text("token = 'ghp_" + "b" * 36 + "'", "a.py")

    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-q", "--allow-empty", "-m", "init"], cwd=repo, check=True)
    (repo / "config.py").write_text(f'API_KEY = "{fake_key}"\n', encoding="utf-8")
    subprocess.run(["git", "add", "config.py"], cwd=repo, check=True)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-q", "-m", "oops"], cwd=repo, check=True)
    (repo / "config.py").write_text("API_KEY = os.environ['GEMINI_API_KEY']\n", encoding="utf-8")
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-q", "-am", "remove key"], cwd=repo, check=True)

    findings = audit(repo)
    assert findings and all(":config.py" in f.where for f in findings)
    assert all(fake_key not in f.preview for f in findings) and not any(f.where.startswith("config.py:") for f in findings)  # gone from the tree, still in history


def test_redaction_masks_pii_and_keys() -> None:
    text = "mail noga@example.com or call 054-123-4567, id 123456789, key AIza" + "Q" * 35
    redacted = redact_text(text)
    assert "[email]" in redacted and "[phone]" in redacted and "[id]" in redacted and "[key]" in redacted
    assert "example.com" not in redacted and "AIza" not in redacted
    assert redact_text("no personal data here, 42 items") == "no personal data here, 42 items"
