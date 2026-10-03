"""Chapter 21 solution: a tiny MCP server (stdio) that exposes two tools. ~20 lines of our own code.

    uv run python -m ch21.mcp_server          # speaks MCP over stdin/stdout; start it from a client, not by hand
"""

from __future__ import annotations

import datetime as dt

from mcp.server.mcpserver import MCPServer

from ch10.tools import search_notes as _search_notes

server = MCPServer("course-notes", instructions="Tools over the user's local course notes.")


@server.tool()
def search_notes(query: str, max_results: int = 5) -> dict:
    """Search the user's markdown notes for lines containing the query (case-insensitive)."""
    return _search_notes(query, max_results)


@server.tool()
def today() -> str:
    """Today's date (UTC) in ISO format."""
    return dt.datetime.now(tz=dt.UTC).date().isoformat()


if __name__ == "__main__":
    server.run()
