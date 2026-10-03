"""Shared fixtures: fixture feeds, fake models, a temporary data directory, an offline pipeline."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from morning_brief.config import Profile, Settings, load_profile
from morning_brief.offline import offline_clients

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures"


def live_enabled(flag: bool, key_present: bool) -> tuple[bool, str]:
    if not flag:
        return False, "live tests run only with --live"
    if not key_present:
        return False, "GEMINI_API_KEY is not set"
    return True, ""


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--live", action="store_true", default=False)


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    run_live, reason = live_enabled(config.getoption("--live"), bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")))
    if run_live:
        return
    for item in items:
        if "live" in item.keywords:
            item.add_marker(pytest.mark.skip(reason=reason))


@pytest.fixture
def profile() -> Profile:
    return load_profile(ROOT / "profile.yaml")


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(data_dir=tmp_path / "data", out_dir=tmp_path / "out", budget_usd=0.25)


@pytest.fixture
def clients():
    return offline_clients(FIXTURES)
