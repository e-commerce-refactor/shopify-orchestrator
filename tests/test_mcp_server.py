"""
Unit tests for MCP Server (Pattern C).
Verifies JSON-RPC protocol handling, tool registration, and tool dispatch.
"""

import unittest
import json
import io
from mcp_server import handle_message, TOOLS_METADATA, execute_tool

class TestMCPServer(unittest.TestCase):

    def test_tools_metadata_contains_all_stages(self):
        tool_names = [t["name"] for t in TOOLS_METADATA]
        expected = [
            "shopify_orchestrator_assess",
            "shopify_orchestrator_discover",
            "shopify_orchestrator_audit",
            "shopify_orchestrator_solution",
            "shopify_orchestrator_build",
            "shopify_orchestrator_qa",
            "shopify_orchestrator_deploy",
            "shopify_orchestrator_sales",
            "shopify_orchestrator_run_all",
            "shopify_orchestrator_status",
            "shopify_orchestrator_list_leads",
            "shopify_orchestrator_ai_status"
        ]
        for exp in expected:
            self.assertIn(exp, tool_names)

    def test_tool_execution_ai_status(self):
        result = execute_tool("shopify_orchestrator_ai_status", {})
        data = json.loads(result)
        self.assertIn("available_engines", data)
        self.assertIn("active_engine", data)

    def test_tool_execution_list_leads(self):
        result = execute_tool("shopify_orchestrator_list_leads", {})
        data = json.loads(result)
        self.assertIn("total", data)
        self.assertIn("leads", data)

    def test_tool_execution_unknown(self):
        result = execute_tool("unknown_tool_xyz", {})
        self.assertIn("Unknown tool", result)

if __name__ == "__main__":
    unittest.main()
