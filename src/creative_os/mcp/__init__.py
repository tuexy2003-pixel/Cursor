"""Narrow MCP-style interface. It calls the same services as the API."""

from creative_os.mcp.server import MUTATION_TOOLS, PROHIBITED_TOOLS, READ_TOOLS, invoke

__all__ = ["MUTATION_TOOLS", "PROHIBITED_TOOLS", "READ_TOOLS", "invoke"]
