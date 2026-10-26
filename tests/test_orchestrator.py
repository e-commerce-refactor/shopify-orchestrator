import json
import os
import tempfile
import unittest
from unittest import mock

import orchestrator
from agents import agent_deployment
from agents.agent_audit import run_audit
from agents.skills.social_extractor import extract_social_intelligence


class OrchestratorSafetyTests(unittest.TestCase):
    def test_workspace_rejects_path_traversal(self):
        for value in ("..", "../escape", "C:/escape", ""):
            with self.subTest(value=value), self.assertRaises(ValueError):
                orchestrator.get_lead_workspace(value)

    def test_handoff_schema_and_gate_consistency(self):
        handoff = {
            "status": "passed",
            "summary": "ok",
            "artifacts": [{"path": "artifact", "schema_version": "1", "sha256": "abc"}],
            "evidence": [{"source": "https://example.com", "collected_at": orchestrator.utc_now_iso(), "method": "test", "confidence": "high"}],
            "assumptions": [],
            "risks": [],
            "blockers": [],
            "gate_results": [{"criterion": "test", "result": "pass", "details": "ok"}],
            "recommended_next_action": "done",
        }
        self.assertIs(orchestrator.validate_handoff(handoff), handoff)
        handoff["gate_results"][0]["result"] = "fail"
        with self.assertRaises(ValueError):
            orchestrator.validate_handoff(handoff)

    def test_stage_transition_blocks_unmet_prerequisite(self):
        with mock.patch.object(orchestrator, "load_lead_run", return_value=({"lead_id": "lead"}, {"stage": "discovery", "status": "failed"})):
            with self.assertRaises(RuntimeError):
                orchestrator.require_stage_ready("lead", "audit")

    def test_atomic_json_write(self):
        with tempfile.TemporaryDirectory(dir=os.getcwd()) as directory:
            path = os.path.join(directory, "state.json")
            orchestrator.atomic_write_json(path, {"valid": True})
            with open(path, "r", encoding="utf-8") as f:
                self.assertEqual(json.load(f), {"valid": True})

    def test_social_extractor_does_not_invent_profile_data(self):
        result = extract_social_intelligence("https://example.com", "Example", {}, "", "")
        self.assertIsNone(result["instagram_handle"])
        self.assertIsNone(result["follower_count"])
        self.assertEqual(result["verified_claims"], [])
        self.assertEqual(result["ugc_media"], [])

    def test_audit_omits_unmeasured_performance_and_financial_claims(self):
        with tempfile.TemporaryDirectory(dir=os.getcwd()) as workspace:
            os.makedirs(os.path.join(workspace, "evidence"))
            with open(os.path.join(workspace, "evidence", "network_evidence.json"), "w", encoding="utf-8") as f:
                json.dump({
                    "target_url": "https://example.com",
                    "collected_at": orchestrator.utc_now_iso(),
                    "method": "live_http_get",
                    "http_status": 200,
                    "raw_html_sha256": "abc",
                    "total_external_scripts": 3,
                    "detected_apps": ["Shopify Core CDN"],
                }, f)
            with open(os.path.join(workspace, "lead.json"), "w", encoding="utf-8") as f:
                json.dump({}, f)
            handoff = run_audit("Example", workspace, "Example", "https://example.com")
            self.assertEqual(handoff["status"], "passed")
            with open(os.path.join(workspace, "audit", "audit_report.json"), "r", encoding="utf-8") as f:
                report = json.load(f)
            self.assertEqual(report["financial_analysis"]["status"], "not_calculated")
            self.assertIn("Lighthouse performance score", report["not_measured"])

    def test_deployment_failure_is_reported_and_stops(self):
        with tempfile.TemporaryDirectory(dir=os.getcwd()) as workspace:
            os.makedirs(os.path.join(workspace, "demo", "source"))
            with mock.patch.object(agent_deployment, "load_root_env"), mock.patch.object(
                agent_deployment, "run_cmd", return_value=(1, "", "simulated failure")
            ):
                handoff = agent_deployment.run_live_deployment(
                    "Example", workspace, "Example", "https://example.com"
                )
            self.assertEqual(handoff["status"], "failed")
            self.assertTrue(handoff["blockers"])
            orchestrator.validate_handoff(handoff)

    def test_deployment_prep_conforms_to_handoff_schema(self):
        with tempfile.TemporaryDirectory(dir=os.getcwd()) as workspace:
            handoff = agent_deployment.run_deployment_prep(
                "Example", workspace, "Example", "https://example.com"
            )
            orchestrator.validate_handoff(handoff)

    def test_deployment_migration_does_not_grant_anonymous_reads(self):
        with open(agent_deployment.__file__, "r", encoding="utf-8") as f:
            source = f.read()
        self.assertNotIn("FOR SELECT TO anon USING (true)", source)


if __name__ == "__main__":
    unittest.main()
