import unittest
import asyncio
from pathlib import Path
from server.hermes_adapter import HermesAgentAdapter

class TestProjectMetadata(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.adapter = HermesAgentAdapter(str(Path(__file__).parent.parent.parent))

    async def test_python_email_validator(self):
        prompt = "Create a python script to validate emails"
        metadata = await self.adapter.analyze_prompt_for_project(prompt)
        self.assertEqual(metadata["language"], "python")
        self.assertNotEqual(metadata["project_name"], "python")
        self.assertIn("email", metadata["project_name"])

    async def test_javascript_calculator(self):
        prompt = "Build a javascript calculator app"
        metadata = await self.adapter.analyze_prompt_for_project(prompt)
        self.assertEqual(metadata["language"], "javascript")
        self.assertNotEqual(metadata["project_name"], "javascript")
        self.assertIn("calculator", metadata["project_name"])

    async def test_web_counter_no_lang(self):
        prompt = "Build a web counter with a database"
        metadata = await self.adapter.analyze_prompt_for_project(prompt)
        self.assertIsNone(metadata["language"])
        self.assertNotEqual(metadata["project_name"], "temp_project")
        self.assertIn("counter", metadata["project_name"])

    async def test_go_url_shortener(self):
        prompt = "Implement go url shortener"
        metadata = await self.adapter.analyze_prompt_for_project(prompt)
        self.assertEqual(metadata["language"], "go")
        self.assertNotEqual(metadata["project_name"], "go")
        self.assertIn("url", metadata["project_name"])

if __name__ == "__main__":
    unittest.main()
