"""Delivery: a file always; email when configured; never the same issue twice on a channel."""
from __future__ import annotations
from collections.abc import Callable
from morning_brief.store import Store

def deliver_once(store: Store, issue_id: str, channel: str, send: Callable[[], str]) -> tuple[bool, str]:
    """Run `send` only if this issue was not delivered on this channel. Returns (sent_now, receipt)."""
    raise NotImplementedError
