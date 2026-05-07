"""Tests for ThreatWinds Vision MCP FastMCP server."""

from __future__ import annotations

from skills.mcp_builder.examples.threatwinds_vision_mcp.server import mcp


def test_server_is_initialized() -> None:
    """The MCP server instance should be created and non-None."""
    assert mcp is not None
