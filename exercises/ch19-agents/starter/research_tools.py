"""Chapter 19 starter: the research agent's tools. Read-only, local first, network optional."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from ch10.tools import fetch_url
from ch19.agent import Tool

FEEDS = Path(__file__).parent / "data" / "feeds.jsonl"


def load_feeds(path: Path = FEEDS) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class SearchFeedsArgs(BaseModel):
    query: str = Field(description="Words to look for in titles and summaries (case-insensitive, any word matches).")
    max_results: int = Field(default=5, ge=1, le=10)


class ReadItemArgs(BaseModel):
    item_id: str = Field(description="The id returned by search_feeds, e.g. 'f03'.")


class FetchUrlArgs(BaseModel):
    url: str = Field(description="Absolute http(s) URL of a public page.")


def make_tools(feeds: list[dict[str, Any]] | None = None, *, allow_network: bool = False) -> dict[str, Tool]:
    items = feeds if feeds is not None else load_feeds()
    by_id = {item["id"]: item for item in items}

    def search_feeds(query: str, max_results: int = 5) -> dict[str, Any]:
        words = [w for w in query.lower().split() if len(w) > 2]
        scored = []
        for item in items:
            haystack = f"{item['title']} {item['summary']}".lower()
            score = sum(1 for w in words if w in haystack)
            if score:
                scored.append((score, item))
        scored.sort(key=lambda pair: (-pair[0], pair[1]["published"]), reverse=False)
        top = [{"id": i["id"], "title": i["title"], "source": i["source"], "published": i["published"], "summary": i["summary"]} for _, i in scored[:max_results]]
        return {"query": query, "results": top, "total_matches": len(scored)}

    def read_item(item_id: str) -> dict[str, Any]:
        item = by_id.get(item_id)
        if item is None:
            raise KeyError(f"no item with id {item_id!r}")
        return {"id": item_id, "title": item["title"], "published": item["published"], "text": item["text"]}

    tools = {
        "search_feeds": Tool("search_feeds", "Search the local news feed items by keywords. Returns ids, titles and one-line summaries. Call this first.", SearchFeedsArgs, search_feeds),
        "read_item": Tool("read_item", "Read the full text of one feed item by id. Use it for the items you intend to cite.", ReadItemArgs, read_item),
    }
    if allow_network:
        tools["fetch_url"] = Tool("fetch_url", "Download a public web page and return its main text. Only for URLs that appear in an item you read.", FetchUrlArgs, fetch_url)
    return tools
