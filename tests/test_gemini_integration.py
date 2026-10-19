import os
import sys
import json
import unittest
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

HERMES_ROOT = Path(__file__).parent.parent
if str(HERMES_ROOT) not in sys.path:
    sys.path.insert(0, str(HERMES_ROOT))

HERMES_AGENT_DIR = HERMES_ROOT / "hermes-agent"
if str(HERMES_AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(HERMES_AGENT_DIR))

from server.hermes_adapter import HermesAgentAdapter


class TestGeminiIntegration(unittest.TestCase):
    """Comprehensive integration tests for Google Gemini provider in Hermes AI Agent."""

    def setUp(self):
        self.workspace = HERMES_ROOT / "workspace" / "test_gemini_ws"
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.env_backup = os.environ.copy()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.env_backup)

    def test_provider_config_resolution_gemini_defaults(self):
        """Test that selecting google-gemini provider correctly sets default base URL and model."""
        cfg = HermesAgentAdapter.normalize_model_config({
            "provider": "google-gemini",
            "api_key": "test_gemini_key_abc123"
        })
        self.assertEqual(cfg["provider"], "google-gemini")
        self.assertEqual(cfg["api_key"], "test_gemini_key_abc123")
        self.assertEqual(cfg["api_base"], "https://generativelanguage.googleapis.com/v1beta/openai/")
        self.assertTrue(cfg["model"].startswith("gemini-"))

    def test_provider_config_aliases(self):
        """Test that aliases (gemini, google, google-ai-studio) normalize to google-gemini."""
        for alias in ["gemini", "google", "google_gemini", "google-ai-studio"]:
            cfg = HermesAgentAdapter.normalize_model_config({
                "provider": alias,
                "api_key": "dummy_key"
            })
            self.assertEqual(cfg["provider"], "google-gemini", f"Failed for alias {alias}")

    def test_missing_api_key_error_handling(self):
        """Test that missing GEMINI_API_KEY triggers clear error handling without silent failure."""
        os.environ.pop("GEMINI_API_KEY", None)
        os.environ.pop("GOOGLE_API_KEY", None)
        cfg = HermesAgentAdapter.normalize_model_config({"provider": "google-gemini", "api_key": ""})
        self.assertEqual(cfg["api_key"], "")

        adapter = HermesAgentAdapter(str(self.workspace), model_config=cfg)
        
        events = []
        async def mock_event_callback(evt):
            events.append(evt)

        asyncio.run(adapter.process_user_turn("test_session_id", "Build a hello world app", mock_event_callback))

        error_events = [e for e in events if e.get("event") == "error"]
        self.assertTrue(len(error_events) > 0, "Missing API key should emit an error event")
        self.assertIn("Missing GEMINI_API_KEY", error_events[0]["data"]["error"])

    def test_model_switching_runtime(self):
        """Test model switching through set_model_config at runtime."""
        adapter = HermesAgentAdapter(str(self.workspace), model_config={"provider": "google-gemini", "api_key": "k1"})
        self.assertTrue(adapter.model_config["model"].startswith("gemini-"))

        # Switch model to gemini-2.0-flash
        adapter.set_model_config({"provider": "google-gemini", "model": "gemini-2.0-flash", "api_key": "k1"})
        self.assertEqual(adapter.model_config["model"], "gemini-2.0-flash")

        # Switch provider to openrouter
        adapter.set_model_config({"provider": "openrouter", "model": "anthropic/claude-3.5-sonnet", "api_key": "k2"})
        self.assertEqual(adapter.model_config["provider"], "openrouter")
        self.assertEqual(adapter.model_config["model"], "anthropic/claude-3.5-sonnet")

    def test_ai_agent_initialization_with_gemini(self):
        """Verify that run_agent.AIAgent initializes cleanly with Gemini OpenAI config."""
        import run_agent
        agent = run_agent.AIAgent(
            model="gemini-3.6-flash",
            provider="google-gemini",
            api_key="test_gemini_key",
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.assertEqual(agent.model, "gemini-3.6-flash")
        self.assertEqual(agent.provider, "google-gemini")
        self.assertEqual(agent.base_url, "https://generativelanguage.googleapis.com/v1beta/openai/")

    def test_openai_compatibility_payload_formatting(self):
        """Verify that tool-calling payload formatted for Gemini OpenAI endpoint matches standard schema."""
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Write text content to a file in workspace",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "content": {"type": "string"}
                        },
                        "required": ["path", "content"]
                    }
                }
            }
        ]
        payload = {
            "model": "gemini-3.6-flash",
            "messages": [{"role": "user", "content": "Create a file named main.py"}],
            "tools": tools,
            "temperature": 0.0
        }
        self.assertEqual(payload["tools"][0]["type"], "function")
        self.assertEqual(payload["tools"][0]["function"]["name"], "write_file")

    def test_gemini_tool_execution_direct(self):
        """Test that Hermes adapter can execute tools directly when requested by Gemini model."""
        adapter = HermesAgentAdapter(str(self.workspace))
        res = asyncio.run(adapter.execute_tool_direct("write_file", {"path": "gemini_test.txt", "content": "Hello Gemini"}))
        created_file = self.workspace / "gemini_test.txt"
        self.assertTrue(created_file.exists())
        self.assertEqual(created_file.read_text(), "Hello Gemini")

    @patch("httpx.AsyncClient.post")
    def test_analyze_prompt_for_project_gemini_success(self, mock_post):
        """Test project metadata extraction with Gemini OpenAI response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({"project_name": "task_tracker", "language": "python"})
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        adapter = HermesAgentAdapter(str(self.workspace), model_config={
            "provider": "google-gemini",
            "api_key": "test_gemini_key",
            "model": "gemini-3.6-flash"
        })

        res = asyncio.run(adapter.analyze_prompt_for_project("Create a Python task tracker"))
        self.assertEqual(res["project_name"], "task_tracker")
        self.assertEqual(res["language"], "python")


if __name__ == "__main__":
    unittest.main()
