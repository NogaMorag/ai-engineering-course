"""Offline mode: fixture feeds and fake models, so the whole pipeline runs in CI and in tests without a key or network."""

from __future__ import annotations

import json
import re
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import httpx

from morning_brief.config import SourceSpec
from morning_brief.embeddings import FakeEmbedder
from morning_brief.llm.client import FakeClient
from morning_brief.pipeline import Clients
from morning_brief.sources.base import Article
from morning_brief.sources.hn import parse_hn
from morning_brief.sources.rss import parse_feed

FIXTURES = Path(__file__).resolve().parent.parent.parent / "fixtures"


def fixture_collectors(fixtures: Path = FIXTURES):
    def rss(spec: SourceSpec, http: httpx.Client) -> list[Article]:
        path = fixtures / f"{spec.name}.xml"
        if not path.exists():
            raise FileNotFoundError(f"no fixture feed for {spec.name}")
        return parse_feed(path.read_bytes(), spec.name)

    def hn(spec: SourceSpec, http: httpx.Client) -> list[Article]:
        return parse_hn(json.loads((fixtures / "hn.json").read_text(encoding="utf-8")), spec.name)

    return {"rss": rss, "hn": hn}


class SummaryFake(FakeClient):
    """A fake that answers the summary and relevance schemas from the prompt text, so offline issues look real."""

    def complete(self, prompt: str, *, system=None, max_output_tokens=1024, temperature=0.2, response_format=None):
        schema_props = set((response_format or {}).get("schema", {}).get("properties", {}))
        if {"headline", "bullets"} <= schema_props:
            title = prompt.split("<title>", 1)[1].split("</title>", 1)[0] if "<title>" in prompt else "Untitled"
            body = prompt.split("</title>", 1)[1] if "</title>" in prompt else prompt
            sentences = [x.strip().rstrip(".") for x in re.split(r"(?<=[.!?])\s+(?=[A-Z])", body.replace("</article>", "").strip()) if len(x.strip()) > 20][:3]
            while len(sentences) < 3:
                sentences.append(f"Detail {len(sentences) + 1} from the feed blurb")
            answer = json.dumps({"is_article": True, "headline": " ".join(title.split()[:10]), "bullets": [s + "." for s in sentences], "why_it_matters": "Why it matters: it touches a topic you follow.", "tags": ["news"], "confidence": "medium"})
        elif {"score", "reason"} <= schema_props:
            lowered = prompt.lower()
            keywords = [k.strip() for line in (system or "").splitlines() if "keywords:" in line for k in line.split("keywords:", 1)[1].split(",")]
            skips = [k.strip() for line in (system or "").splitlines() if line.startswith("skip:") for k in line.split(":", 1)[1].split(",")]
            hits = sum(1 for k in keywords if k and k.lower() in lowered)
            skipped = any(k and k.lower() in lowered for k in skips)
            score = 0 if skipped else min(100, 20 + 25 * hits)
            answer = json.dumps({"score": score, "reason": "skip topic" if skipped else (f"{hits} profile keyword(s) matched" if hits else "general tech news"), "matched_topics": []})
        elif {"greeting_line", "theme"} <= schema_props:
            answer = json.dumps({"greeting_line": "Good morning, here is your brief.", "theme": "none"})
        elif {"context", "key_fact"} <= schema_props:
            answer = json.dumps({"context": "Background from the sources read.", "key_fact": "One concrete fact.", "source_ids": []})
        else:
            answer = "ok"
        self.calls.append({"prompt": prompt, "system": system, "response_format": response_format})
        from morning_brief.llm.client import Completion

        return Completion(text=answer, status="completed", model=self.model, input_tokens=max(1, len(prompt) // 4), output_tokens=max(1, len(answer) // 4))


class OfflineAgentBackend:
    """Reads the story once, then answers: exercises the real loop and tool dispatch without a model."""

    model = "fake-agent"

    def create(self, *, history: list[dict[str, Any]], tools: list[dict[str, Any]], system: str) -> Any:
        usage = SimpleNamespace(total_input_tokens=200, total_output_tokens=40)
        already_read = any(step.get("type") == "function_result" and step.get("name") == "read_item" for step in history)
        if not already_read:
            match = re.search(r"\(id ([0-9a-f]{16})\)", history[0]["content"][0]["text"])
            call = SimpleNamespace(type="function_call", id="c1", name="read_item", arguments={"item_id": match.group(1) if match else "?"})
            return SimpleNamespace(steps=[call], output_text="", usage=usage)
        return SimpleNamespace(steps=[], output_text="Background: the story continues earlier reporting. Key fact: see the item itself.", usage=usage)


def offline_clients(fixtures: Path = FIXTURES) -> Clients:
    fake = SummaryFake(model="fake-model")
    return Clients(fast=fake, smart=fake, embedder=FakeEmbedder(), agent_backend=OfflineAgentBackend(), http=None, collectors=fixture_collectors(fixtures), cluster_threshold=0.55)
