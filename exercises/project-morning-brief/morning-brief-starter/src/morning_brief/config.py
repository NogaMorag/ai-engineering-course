"""Settings (environment, secrets) and the reader profile (a YAML file in the repo). Kept apart on purpose."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Everything that differs between machines or must stay secret. Read from the environment / .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    model_fast: str = "gemini-3.5-flash-lite"
    model_smart: str = "gemini-3.8-flash"
    embedding_model: str = "gemini-embedding-2"
    data_dir: Path = Path("data")
    out_dir: Path = Path("out")
    budget_usd: float = 0.25
    max_articles: int = 40
    summarize_concurrency: int = 3
    smtp_host: str = ""
    smtp_port: int = 465
    smtp_user: str = ""
    smtp_password: str = ""
    mail_to: str = ""

    @property
    def email_configured(self) -> bool:
        return bool(self.smtp_host and self.smtp_user and self.smtp_password and self.mail_to)


class Topic(BaseModel):
    name: str
    weight: float = Field(default=1.0, ge=0.0, le=2.0)
    keywords: list[str] = Field(default_factory=list)


class SourceSpec(BaseModel):
    name: str
    kind: Literal["rss", "hn"]
    url: str | None = None
    weight: float = Field(default=1.0, ge=0.0, le=2.0)


class Profile(BaseModel):
    """What the reader cares about. No identity here: it is committed to the repo."""

    language: Literal["he", "en"] = "he"
    issue_size: int = Field(default=10, ge=3, le=30)
    top_stories: int = Field(default=3, ge=0, le=5)
    follow_up_days: int = Field(default=14, ge=1, le=60)
    topics: list[Topic]
    skip_topics: list[str] = Field(default_factory=list)
    sources: list[SourceSpec]

    def as_prompt_block(self) -> str:
        """The stable text that goes at the START of every prompt (prefix caching, chapter 15)."""
        topics = "\n".join(f"- {t.name} (weight {t.weight}); keywords: {', '.join(t.keywords)}" for t in self.topics)
        skip = ", ".join(self.skip_topics) or "none"
        return f"<reader_profile>\nlanguage: {self.language}\ntopics:\n{topics}\nskip: {skip}\n</reader_profile>"


def load_profile(path: Path | str = "profile.yaml") -> Profile:
    return Profile.model_validate(yaml.safe_load(Path(path).read_text(encoding="utf-8")))
