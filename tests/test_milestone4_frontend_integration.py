import unittest
from pathlib import Path
from server.hermes_adapter import HermesAgentAdapter

class TestMilestone4FrontendIntegration(unittest.TestCase):
    def test_chat_panel_contains_visual_qa_section(self):
        chat_panel_path = Path("client/src/components/ChatPanel.jsx")
        self.assertTrue(chat_panel_path.exists())
        content = chat_panel_path.read_text(encoding="utf-8")
        
        self.assertIn("Visual QA Verification", content)
        self.assertIn("TECHNICAL DOM & CSS QA", content)
        self.assertIn("AESTHETIC VISION QA", content)
        self.assertIn("Responsive Screenshots", content)

    def test_compile_project_results_payload_structure(self):
        adapter = HermesAgentAdapter("workspace/sample_test")
        res = adapter.compile_project_results()
        self.assertIn("visual_qa", res)
        self.assertIn("is_web_project", res["visual_qa"])
        self.assertIn("technical_qa", res["visual_qa"])

if __name__ == "__main__":
    unittest.main()
