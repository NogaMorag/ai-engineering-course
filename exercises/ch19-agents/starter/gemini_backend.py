"""Chapter 19 starter: the real ModelBackend. Explicit history in, interaction out. Errors are classified (chapter 11)."""

from __future__ import annotations

import os
from typing import Any

from google import genai
from google.genai import types

from ch11.llm_client import classify


class GeminiAgentBackend:
    def __init__(self, model: str | None = None, timeout_s: float = 60.0) -> None:
        self.model = model or os.environ.get("MODEL_SMART", "gemini-3.8-flash")
        self.client = genai.Client(http_options=types.HttpOptions(timeout=int(timeout_s * 1000), retry_options=types.HttpRetryOptions(attempts=1)))

    def create(self, *, history: list[dict[str, Any]], tools: list[dict[str, Any]], system: str) -> Any:
        try:
            return self.client.interactions.create(
                model=self.model, input=history, tools=tools, system_instruction=system,
                generation_config={"temperature": 0.2, "max_output_tokens": 700},
            )
        except Exception as exc:
            raise classify(exc) from exc
