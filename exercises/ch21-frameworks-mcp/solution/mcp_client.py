"""Chapter 21 solution: connect an MCP server to the chapter 19 loop.

The server runs as a subprocess speaking MCP over stdio. One background thread owns an event loop and the
session; the synchronous agent loop sends it calls through a queue. Tool declarations are translated to the
Interactions format, so the model sees MCP tools exactly like our own.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import json
import sys
import threading
from pathlib import Path
from typing import Any, Self

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic import BaseModel, ConfigDict

from ch09.schemas import clean_schema
from ch19.agent import Tool

_CLOSE = object()


class McpToolbox:
    """Sync facade over one stdio MCP server. Use as a context manager."""

    def __init__(self, command: str, args: list[str], cwd: Path | None = None, timeout_s: float = 60.0) -> None:
        self.params = StdioServerParameters(command=command, args=args, cwd=str(cwd) if cwd else None)
        self.timeout_s = timeout_s
        self.tools: list[Any] = []
        self._queue: asyncio.Queue | None = None
        self._loop = asyncio.new_event_loop()
        self._ready = threading.Event()
        self._error: BaseException | None = None
        self._thread = threading.Thread(target=self._run_loop, daemon=True)

    # -- lifecycle -------------------------------------------------------------------------------
    def __enter__(self) -> Self:
        self._thread.start()
        if not self._ready.wait(self.timeout_s):
            raise TimeoutError("MCP server did not become ready")
        if self._error:
            raise RuntimeError(f"MCP server failed to start: {self._error!r}") from self._error
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        if self._queue is not None and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._queue.put_nowait, (_CLOSE, None, None))
        self._thread.join(timeout=10)

    def _run_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._serve())
        except BaseException as exc:  # noqa: BLE001 - surfaced to the caller thread through _error
            self._error = exc
            self._ready.set()
        finally:
            self._loop.close()

    async def _serve(self) -> None:
        # Everything that touches the session happens in this one task; anyio requires it.
        self._queue = asyncio.Queue()
        async with stdio_client(self.params) as (read, write), ClientSession(read, write) as session:
            await session.initialize()
            self.tools = (await session.list_tools()).tools
            self._ready.set()
            while True:
                name, arguments, future = await self._queue.get()
                if name is _CLOSE:
                    return
                try:
                    future.set_result(await session.call_tool(name, arguments))
                except BaseException as exc:  # noqa: BLE001 - delivered to the waiting caller as the failure
                    future.set_exception(exc)

    # -- what the agent uses --------------------------------------------------------------------
    def call(self, name: str, arguments: dict[str, Any]) -> tuple[str, bool]:
        future: concurrent.futures.Future = concurrent.futures.Future()
        assert self._queue is not None
        self._loop.call_soon_threadsafe(self._queue.put_nowait, (name, arguments, future))
        result = future.result(self.timeout_s)
        text = "\n".join(getattr(c, "text", "") for c in result.content if getattr(c, "text", None))
        if result.structured_content and not text:
            text = json.dumps(result.structured_content, ensure_ascii=False)
        return text, bool(result.is_error)

    def declarations(self) -> list[dict[str, Any]]:
        """MCP tool descriptions in the Interactions tool format: same three fields, different spelling."""
        return [{"type": "function", "name": t.name, "description": t.description or "", "parameters": clean_schema(t.input_schema)} for t in self.tools]


class _AnyArgs(BaseModel):
    model_config = ConfigDict(extra="allow")  # the server validates; we pass arguments through


def as_agent_tools(toolbox: McpToolbox, prefix: str = "") -> dict[str, Tool]:
    """Wrap every MCP tool as a chapter-19 Tool so the loop dispatches it like a local one."""
    tools: dict[str, Tool] = {}
    for mcp_tool in toolbox.tools:
        name = f"{prefix}{mcp_tool.name}"

        def func(_name: str = mcp_tool.name, **arguments: Any) -> Any:
            text, is_error = toolbox.call(_name, arguments)
            if is_error:
                raise RuntimeError(text)
            try:
                return json.loads(text)
            except ValueError:
                return {"text": text}

        tools[name] = Tool(name, mcp_tool.description or "", _AnyArgs, func)
    return tools


def course_notes_server(project_root: Path) -> McpToolbox:
    return McpToolbox(sys.executable, ["-m", "ch21.mcp_server"], cwd=project_root)


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    with course_notes_server(root) as toolbox:
        print("tools from the MCP server:")
        for declaration in toolbox.declarations():
            print(f"  {declaration['name']}: {declaration['description']}  params={list(declaration['parameters'].get('properties', {}))}")
        text, is_error = toolbox.call("search_notes", {"query": "temperature"})
        print(f"\nsearch_notes -> is_error={is_error}\n{text[:300]}")
        text, is_error = toolbox.call("today", {})
        print(f"\ntoday -> {text}")


if __name__ == "__main__":
    main()
