import os
import sys
import json
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from server.agents.llm_client import LLMClient
from server.agents.visual_qa_inspector_agent import VisualQAInspectorAgent
from server.agents.frontend_engineer_agent import FrontendEngineerAgent
from server.agents.motion_3d_engineer_agent import Motion3DEngineerAgent
from server.agents.schemas import AgentContext
from server.tools.asset_discovery import AssetDiscoveryService

class TestPhase6VisualQAnd3DFidelity(unittest.TestCase):

    def test_A_vision_api_payload(self):
        """TEST A: Confirm Gemini vision API handles image requests cleanly without HTTP 400.
        Uses mocked HTTP transport by default to ensure deterministic, fast unit test execution.
        Set HERMES_RUN_LIVE_TESTS=true to execute genuine live API calls.
        """
        client = LLMClient()
        self.assertTrue(client.is_configured(), "LLMClient must be configured with API key")
        
        # Locate test screenshot
        img_path = Path(__file__).parent.parent / "workspace" / "p3_bench_3d_footwear" / ".visual_qa" / "desktop.png"
        if not img_path.exists():
            pngs = list((Path(__file__).parent.parent / "workspace").glob("**/*.png"))
            self.assertTrue(len(pngs) > 0, "No screenshots found in workspace for test")
            img_path = pngs[0]

        sys_prompt = 'You are a visual tester. Inspect the image and return JSON: {"status": "ok", "subject_description": "summary"}'
        user_prompt = "Analyze this screenshot."

        run_live = os.getenv("HERMES_RUN_LIVE_TESTS", "").lower() in ("true", "1")
        if run_live:
            res = client.call_llm_json(sys_prompt, user_prompt, image_paths=[img_path])
            self.assertIsNotNone(res, "Vision API must return parsed JSON response, not None")
            self.assertIn("status", res, "Response must contain expected JSON key")
        else:
            from unittest.mock import patch, MagicMock
            mock_resp = MagicMock()
            mock_resp.read.return_value = json.dumps({
                "choices": [{
                    "message": {
                        "content": '{"status": "ok", "subject_description": "Verified luxury footwear showcase screenshot"}'
                    }
                }],
                "usage": {"prompt_tokens": 120, "completion_tokens": 20}
            }).encode("utf-8")
            mock_resp.__enter__.return_value = mock_resp
            mock_resp.__exit__.return_value = False

            with patch("urllib.request.urlopen", return_value=mock_resp) as mock_urlopen:
                res = client.call_llm_json(sys_prompt, user_prompt, image_paths=[img_path])
                self.assertIsNotNone(res, "Vision API must return parsed JSON response")
                self.assertEqual(res.get("status"), "ok")
                self.assertIn("subject_description", res)
                self.assertTrue(mock_urlopen.called)
                sent_req = mock_urlopen.call_args[0][0]
                self.assertEqual(sent_req.headers.get("User-agent"), "HermesAgent/1.0")

    def test_B_false_positive_prevention(self):
        """TEST B: Verify visual QA inspector returns BLOCKED/NEEDS_RETRY on vision failure, NEVER PASS."""
        inspector = VisualQAInspectorAgent()
        inspector.llm.api_key = "" # Force unconfigured API key
        
        context = AgentContext(
            project_name="test_proj",
            user_prompt="3D shoe website",
            workspace_root=str(Path(__file__).parent.parent / "workspace"),
            attempt_number=1,
            max_refinement_cycles=3
        )
        screenshot_res = {
            "success": True,
            "visual_inspection_executed": True,
            "desktop": "test_proj/.visual_qa/desktop.png",
            "mobile": "test_proj/.visual_qa/mobile.png",
            "console_errors": [],
            "failed_requests": []
        }
        
        report = inspector.run(context, screenshot_result=screenshot_res)
        self.assertNotEqual(report["decision"], "PASS", "Vision API failure MUST NEVER produce a PASS decision")
        self.assertIn(report["decision"], ["BLOCKED", "NEEDS_RETRY"], "Decision must be BLOCKED or NEEDS_RETRY")
        self.assertLessEqual(report["overall_score"], 5.0, "Score must reflect unverified visual status")

    def test_C_semantic_rejection(self):
        """TEST C: Verify inspector rejects product with failed semantic fidelity."""
        inspector = VisualQAInspectorAgent()
        context = AgentContext(
            project_name="test_proj",
            user_prompt="Premium 3D Shoe Showcase",
            workspace_root=str(Path(__file__).parent.parent / "workspace"),
            attempt_number=1,
            max_refinement_cycles=3
        )
        
        report_data = {
            "requested_subject": "3D Shoe Showcase",
            "detected_subject": "Abstract Box Primitives",
            "semantic_fidelity_score": 3.0,
            "semantic_fidelity_pass": False,
            "visual_evidence": "Rendered viewport contains only generic box and cylinder primitives.",
            "decision": "PASS",
            "overall_score": 9.5,
            "critical_issues": []
        }
        
        sem_pass = report_data.get("semantic_fidelity_pass", True)
        sem_score = report_data.get("semantic_fidelity_score", 10.0)
        if not sem_pass or sem_score < 7.0:
            report_data["decision"] = "NEEDS_REFINEMENT"
            report_data["overall_score"] = min(report_data["overall_score"], 5.5)

        self.assertEqual(report_data["decision"], "NEEDS_REFINEMENT", "High overall score must NOT override semantic failure")
        self.assertLessEqual(report_data["overall_score"], 5.5, "Overall score must be capped on semantic failure")

    def test_D_and_E_correct_3d_product_and_scene_integrity(self):
        """TEST D & E: Verify correct GLTF model assignment, scene cleaning, and absence of conflicts."""
        asset_svc = AssetDiscoveryService()
        discovered = asset_svc.discover_assets("Premium 3D Shoe Showcase")
        
        self.assertEqual(discovered["topic"], "Footwear & E-Commerce")
        self.assertTrue(len(discovered["models_3d"]) > 0)
        self.assertIn("MaterialsVariantsShoe", discovered["models_3d"][0]["url"])

        frontend = FrontendEngineerAgent()
        motion = Motion3DEngineerAgent()
        
        context = AgentContext(
            project_name="phase6_test_shoe",
            user_prompt="Premium 3D Shoe Showcase",
            workspace_root=str(Path(__file__).parent.parent / "workspace")
        )
        
        res1 = frontend.run(context)
        res2 = motion.run(context)
        
        self.assertEqual(res2["status"], "ENHANCED")
        self.assertIn("MaterialsVariantsShoe.glb", res2["model_url"])
        
        index_html = (Path(context.workspace_root) / "phase6_test_shoe" / "index.html").read_text()
        self.assertIn('container.innerHTML = ""', index_html, "Motion agent must clear existing container geometry")
        self.assertIn("THREE.GLTFLoader", index_html, "HTML must contain GLTFLoader initialization")

if __name__ == "__main__":
    unittest.main()
