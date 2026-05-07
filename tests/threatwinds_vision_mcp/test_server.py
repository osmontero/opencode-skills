"""Tests for ThreatWinds Vision MCP FastMCP server."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from mcp_servers.threatwinds_vision.server import (
    analyze_image,
    analyze_pdf,
    mcp,
)


class TestServerInitialization:
    """Tests for MCP server initialization."""

    def test_server_is_initialized(self) -> None:
        """The MCP server instance should be created and non-None."""
        assert mcp is not None

    def test_server_has_correct_name(self) -> None:
        """The MCP server should have the correct name."""
        assert mcp.name == "threatwinds_vision_mcp"


class TestToolRegistration:
    """Tests for tool registration on the MCP server."""

    def test_analyze_pdf_tool_is_registered(self) -> None:
        """The analyze_pdf tool should be registered on the MCP server."""
        tools = mcp._tool_manager.list_tools()
        tool_names = {t.name for t in tools}
        assert "analyze_pdf" in tool_names

    def test_analyze_image_tool_is_registered(self) -> None:
        """The analyze_image tool should be registered on the MCP server."""
        tools = mcp._tool_manager.list_tools()
        tool_names = {t.name for t in tools}
        assert "analyze_image" in tool_names

    def test_both_tools_registered(self) -> None:
        """Both tools should be registered on the MCP server."""
        tools = mcp._tool_manager.list_tools()
        tool_names = {t.name for t in tools}
        assert "analyze_pdf" in tool_names
        assert "analyze_image" in tool_names
        assert len(tool_names) >= 2

    def test_analyze_pdf_tool_has_title(self) -> None:
        """The analyze_pdf tool should have a title."""
        tools = mcp._tool_manager.list_tools()
        pdf_tool = next(t for t in tools if t.name == "analyze_pdf")
        assert pdf_tool.title == "Analyze PDF Document"

    def test_analyze_image_tool_has_title(self) -> None:
        """The analyze_image tool should have a title."""
        tools = mcp._tool_manager.list_tools()
        img_tool = next(t for t in tools if t.name == "analyze_image")
        assert img_tool.title == "Analyze Image"


class TestAnalyzePdfTool:
    """Tests for the analyze_pdf tool function."""

    def test_produces_valid_json_on_success(self) -> None:
        """analyze_pdf should return valid JSON on success."""
        mock_result = type(
            "MockResult",
            (),
            {
                "model_dump": lambda self: {
                    "input_type": "pdf",
                    "source_type": "path",
                    "model": "qwen-3.6",
                    "prompt": "test",
                    "results": [{"page": 1, "content": "hello"}],
                    "combined_content": "hello",
                    "warnings": [],
                    "errors": [],
                }
            },
        )()

        with patch(
            "mcp_servers.threatwinds_vision.server.analyze_pdf_source",
            return_value=mock_result,
        ):
            output = analyze_pdf(
                prompt="test",
                pdf_path="/tmp/test.pdf",
            )
            data = json.loads(output)
            assert data["input_type"] == "pdf"
            assert data["combined_content"] == "hello"
            assert len(data["results"]) == 1

    def test_handles_validation_error(self) -> None:
        """analyze_pdf should return an error JSON on validation failure."""
        output = analyze_pdf(
            prompt="test",
            # No source provided — triggers validation error
        )
        data = json.loads(output)
        assert data["input_type"] == "pdf"
        assert len(data["errors"]) == 1
        assert data["errors"][0]["code"] == "server_error"
        assert "Exactly one source" in data["errors"][0]["message"]

    def test_handles_service_error(self) -> None:
        """analyze_pdf should return an error JSON when the service raises."""
        with patch(
            "mcp_servers.threatwinds_vision.server.analyze_pdf_source",
            side_effect=RuntimeError("API timeout"),
        ):
            output = analyze_pdf(
                prompt="test",
                pdf_path="/tmp/test.pdf",
            )
            data = json.loads(output)
            assert data["input_type"] == "pdf"
            assert data["combined_content"] == ""
            assert data["results"] == []
            assert len(data["errors"]) == 1
            assert data["errors"][0]["code"] == "server_error"
            assert "API timeout" in data["errors"][0]["message"]


class TestAnalyzeImageTool:
    """Tests for the analyze_image tool function."""

    def test_produces_valid_json_on_success(self) -> None:
        """analyze_image should return valid JSON on success."""
        mock_result = type(
            "MockResult",
            (),
            {
                "model_dump": lambda self: {
                    "input_type": "image",
                    "source_type": "url",
                    "model": "qwen-3.6",
                    "prompt": "describe",
                    "content": "a chart",
                    "warnings": [],
                    "errors": [],
                }
            },
        )()

        with patch(
            "mcp_servers.threatwinds_vision.server.analyze_image_source",
            return_value=mock_result,
        ):
            output = analyze_image(
                prompt="describe",
                image_url="https://example.com/img.png",
            )
            data = json.loads(output)
            assert data["input_type"] == "image"
            assert data["content"] == "a chart"

    def test_handles_validation_error(self) -> None:
        """analyze_image should return an error JSON on validation failure."""
        output = analyze_image(
            prompt="test",
            # No source provided — triggers validation error
        )
        data = json.loads(output)
        assert data["input_type"] == "image"
        assert len(data["errors"]) == 1
        assert data["errors"][0]["code"] == "server_error"
        assert "Exactly one source" in data["errors"][0]["message"]

    def test_handles_service_error(self) -> None:
        """analyze_image should return an error JSON when the service raises."""
        with patch(
            "mcp_servers.threatwinds_vision.server.analyze_image_source",
            side_effect=ConnectionError("network down"),
        ):
            output = analyze_image(
                prompt="test",
                image_path="/tmp/test.png",
            )
            data = json.loads(output)
            assert data["input_type"] == "image"
            assert data["content"] == ""
            assert len(data["errors"]) == 1
            assert data["errors"][0]["code"] == "server_error"
            assert "network down" in data["errors"][0]["message"]
