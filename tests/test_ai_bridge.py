"""
Unit tests for AI Agent Bridge (Pattern A).
Verifies capability detection, engine routing, and safe fallback mechanisms.
"""

import unittest
import os
from unittest.mock import patch
from agents.skills.ai_bridge import AIAgentBridge

class TestAIAgentBridge(unittest.TestCase):

    def setUp(self):
        self.bridge = AIAgentBridge()

    def test_capabilities_detection(self):
        caps = self.bridge.get_capabilities()
        self.assertIn("available_engines", caps)
        self.assertIn("active_engine", caps)
        self.assertIsInstance(caps["available_engines"], list)

    def test_invoke_with_none_engine(self):
        res = self.bridge.invoke("test prompt", engine="none")
        self.assertFalse(res["success"])
        self.assertEqual(res["engine"], "none")
        self.assertIn("disabled", res["error"])

    def test_enhance_storefront_missing_workspace(self):
        res = self.bridge.enhance_storefront("non_existent_workspace_path_12345", "Test Brand")
        self.assertFalse(res["success"])
        self.assertIn("not found", res["error"])

if __name__ == "__main__":
    unittest.main()
