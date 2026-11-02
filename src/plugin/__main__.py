"""The MCP server: each call's input built into its contract class, its output checked against its own."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

import anyio
from mcp import types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server
from slimconfig import build_output, output_schema, plain_output

from contract import TOOLS, Tool
from plugin import submit

server = Server("formula-validity")

# NanoAgent names the one folder this plugin may write to.
WORKSPACE_ENV = "NANOAGENT_WORKSPACE"

# Each tool's implementation: (its input, the workspace) -> its output.
IMPLEMENTATIONS = {
    Tool.SUBMIT: submit,
}


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name        = tool.value,
            inputSchema = output_schema(given),
        )
        for tool, (given, _made) in TOOLS.items()
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    tool          = Tool(name)
    given, made   = TOOLS[tool]
    workspace     = Path(os.environ[WORKSPACE_ENV])
    started       = time.perf_counter()

    try:
        inp    = build_output(arguments, given)
        output = IMPLEMENTATIONS[tool](inp, workspace)
        if not isinstance(output, made):
            raise TypeError(f"{name} returned {type(output).__name__}, not {made.__name__}")
    except Exception as error:
        raise

    import json
    return [types.TextContent(type="text", text=json.dumps(plain_output(output)))]


def main() -> None:
    if WORKSPACE_ENV not in os.environ:
        raise SystemExit(
            f"{WORKSPACE_ENV} is not set: NanoAgent passes the plugin's workspace folder"
        )
    if set(IMPLEMENTATIONS) != set(Tool):
        missing = set(Tool) - set(IMPLEMENTATIONS)
        raise SystemExit(f"Missing implementations for: {missing}")

    anyio.run(_serve)


async def _serve() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    main()
