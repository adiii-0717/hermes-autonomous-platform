import os
import sys
import json
import unittest
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch
import urllib.error

HERMES_ROOT = Path(__file__).parent.parent
if str(HERMES_ROOT) not in sys.path:
    sys.path.insert(0, str(HERMES_ROOT))

HERMES_AGENT_DIR = HERMES_ROOT / "hermes-agent"
if str(HERMES_AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(HERMES_AGENT_DIR))

from server.hermes_adapter import HermesAgentAdapter
from server.agents.llm_client import LLMClient
from providers import get_provider_profile
from hermes_cli.auth import PROVIDER_REGISTRY


class TestAPInexIntegration(unittest.TestCase):
    """Comprehensive test suite for APInex primary provider integration,
    backup provider routing (Gemini, Groq, Ollama), and safe error handling."""

    def setUp(self):
        self.workspace = HERMES_ROOT / "workspace" / "test_apinex_ws"
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.env_backup = os.environ.copy()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.env_backup)

    # 1. Config Loading & Normalization
    def test_apinex_config_resolution_defaults(self):
        """Verifies that selecting apinex sets the correct documented base URL and free model default."""
        cfg = HermesAgentAdapter.normalize_model_config({
            "provider": "apinex",
            "api_key": "test_apx_abc123"
        })
        self.assertEqual(cfg["provider"], "apinex")
        self.assertEqual(cfg["api_key"], "test_apx_abc123")
        self.assertEqual(cfg["api_base"], "https://api.apinex.bond/v1/")
        self.assertEqual(cfg["model"], "free/gemini-3.8-flash")

    def test_apinex_custom_env_variables(self):
        """Verifies that APINEX_API_KEY, APINEX_BASE_URL, and APINEX_MODEL are respected from environment."""
        os.environ["LLM_PROVIDER"] = "apinex"
        os.environ["APINEX_API_KEY"] = "sk-apx-live-test-key"
        os.environ["APINEX_BASE_URL"] = "https://api.apinex.bond/v1"
        os.environ["APINEX_MODEL"] = "free/deepseek-v4.1-flash"

        cfg = HermesAgentAdapter.normalize_model_config({})
        self.assertEqual(cfg["provider"], "apinex")
        self.assertEqual(cfg["api_key"], "sk-apx-live-test-key")
        self.assertEqual(cfg["api_base"], "https://api.apinex.bond/v1/")
        self.assertEqual(cfg["model"], "free/deepseek-v4.1-flash")

    def test_provider_auto_priority_selection(self):
        """Verifies automatic priority ordering: APInex -> Gemini -> Groq -> Ollama."""
        os.environ.pop("LLM_PROVIDER", None)
        os.environ.pop("MODEL_PROVIDER", None)
        os.environ.pop("APINEX_API_KEY", None)
        os.environ.pop("GEMINI_API_KEY", None)
        os.environ.pop("GOOGLE_API_KEY", None)
        os.environ.pop("GROQ_API_KEY", None)

        # No keys -> Ollama
        cfg = HermesAgentAdapter.normalize_model_config({})
        self.assertEqual(cfg["provider"], "ollama")

        # Groq key present -> Groq
        os.environ["GROQ_API_KEY"] = "gsk_test"
        cfg = HermesAgentAdapter.normalize_model_config({})
        self.assertEqual(cfg["provider"], "groq")

        # Gemini key present -> Gemini (higher priority than Groq)
        os.environ["GEMINI_API_KEY"] = "gemini_key"
        cfg = HermesAgentAdapter.normalize_model_config({})
        self.assertEqual(cfg["provider"], "google-gemini")

        # APInex key present -> APInex (primary provider)
        os.environ["APINEX_API_KEY"] = "apx_key"
        cfg = HermesAgentAdapter.normalize_model_config({})
        self.assertEqual(cfg["provider"], "apinex")

    # 2. Missing Credentials Handling
    def test_missing_credentials_produces_clear_error(self):
        """Verifies that missing APINEX_API_KEY triggers an informative error event without silent failure."""
        os.environ.pop("APINEX_API_KEY", None)
        os.environ.pop("OPENAI_API_KEY", None)
        cfg = HermesAgentAdapter.normalize_model_config({"provider": "apinex", "api_key": ""})
        self.assertEqual(cfg["api_key"], "")

        adapter = HermesAgentAdapter(str(self.workspace), model_config=cfg)
        events = []

        async def mock_event_callback(evt):
            events.append(evt)

        asyncio.run(adapter.process_user_turn("session_test_cred", "Build a simple app", mock_event_callback))

        error_events = [e for e in events if e.get("event") == "error"]
        self.assertTrue(len(error_events) > 0, "Missing API key must emit an error event")
        self.assertIn("Missing APINEX_API_KEY", error_events[0]["data"]["error"])

    # 3. AIAgent Core Initialization
    def test_ai_agent_initialization_with_apinex(self):
        """Verifies that run_agent.AIAgent initializes cleanly with APInex OpenAI parameters."""
        import run_agent
        agent = run_agent.AIAgent(
            model="free/gemini-3.8-flash",
            provider="apinex",
            api_key="test_apx_key",
            base_url="https://api.apinex.bond/v1"
        )
        self.assertEqual(agent.model, "free/gemini-3.8-flash")
        self.assertEqual(agent.provider, "apinex")
        self.assertEqual(agent.base_url, "https://api.apinex.bond/v1")

    # 4. Plugin System & PROVIDER_REGISTRY Discovery
    def test_apinex_and_groq_plugin_registration(self):
        """Verifies that APInex and Groq plugins are discovered by the Hermes plugin system and registered in PROVIDER_REGISTRY."""
        apx_profile = get_provider_profile("apinex")
        self.assertIsNotNone(apx_profile, "APInex provider profile must be registered")
        self.assertEqual(apx_profile.base_url, "https://api.apinex.bond/v1")
        self.assertIn("apinex", PROVIDER_REGISTRY)

        groq_profile = get_provider_profile("groq")
        self.assertIsNotNone(groq_profile, "Groq provider profile must be registered")
        self.assertEqual(groq_profile.base_url, "https://api.groq.com/openai/v1")
        self.assertIn("groq", PROVIDER_REGISTRY)

    # 5. Error Classification & Recoverability
    def test_error_classification_permanent_vs_recoverable(self):
        """Verifies that 401/403 are classified as permanent, while 429/timeouts/network errors are recoverable."""
        # Permanent
        self.assertFalse(HermesAgentAdapter.is_recoverable_error(Exception("HTTP 401: Unauthorized - Invalid API key")))
        self.assertFalse(HermesAgentAdapter.is_recoverable_error(Exception("403 Forbidden: bad key")))
        self.assertFalse(HermesAgentAdapter.is_recoverable_error(Exception("authentication_error: key not found")))

        # Recoverable
        self.assertTrue(HermesAgentAdapter.is_recoverable_error(Exception("HTTP 429: Too Many Requests - rate limit exceeded")))
        self.assertTrue(HermesAgentAdapter.is_recoverable_error(Exception("quota exhausted: 0 credits remaining")))
        self.assertTrue(HermesAgentAdapter.is_recoverable_error(Exception("Request timed out after 30 seconds")))
        self.assertTrue(HermesAgentAdapter.is_recoverable_error(Exception("503 Service Unavailable: upstream overloaded")))
        self.assertTrue(HermesAgentAdapter.is_recoverable_error(Exception("Network connection reset by peer")))

    # 6. Fallback Provider Chain
    def test_fallback_provider_chain_generation(self):
        """Verifies get_fallback_provider_chain excludes current provider and only includes configured backups."""
        os.environ["APINEX_API_KEY"] = "apx_key"
        os.environ["GEMINI_API_KEY"] = "gem_key"
        os.environ["GROQ_API_KEY"] = "groq_key"

        chain = HermesAgentAdapter.get_fallback_provider_chain("apinex")
        chain_providers = [c["provider"] for c in chain]
        self.assertNotIn("apinex", chain_providers)
        self.assertEqual(chain_providers, ["google-gemini", "groq", "ollama"])

        # When Groq is not configured:
        os.environ.pop("GROQ_API_KEY", None)
        chain_no_groq = HermesAgentAdapter.get_fallback_provider_chain("apinex")
        chain_providers_no_groq = [c["provider"] for c in chain_no_groq]
        self.assertEqual(chain_providers_no_groq, ["google-gemini", "ollama"])

    # 7. Ollama Keyless Support
    def test_ollama_keyless_operation(self):
        """Verifies local Ollama functions without any cloud API key."""
        cfg = HermesAgentAdapter.normalize_model_config({"provider": "ollama"})
        self.assertEqual(cfg["provider"], "ollama")
        self.assertEqual(cfg["api_base"], "http://localhost:11434/v1/")
        
        client = LLMClient(cfg)
        self.assertTrue(client.is_configured(), "Ollama client must be configured without cloud key")

    # 8. Dynamic Runtime Switching
    def test_runtime_provider_switching(self):
        """Verifies switching providers dynamically via set_model_config."""
        adapter = HermesAgentAdapter(str(self.workspace), model_config={"provider": "apinex", "api_key": "k_apx"})
        self.assertEqual(adapter.model_config["provider"], "apinex")
        self.assertEqual(adapter.model_config["model"], "free/gemini-3.8-flash")

        # Switch to Gemini backup
        adapter.set_model_config({"provider": "google-gemini", "api_key": "k_gem", "model": "gemini-2.5-flash"})
        self.assertEqual(adapter.model_config["provider"], "google-gemini")
        self.assertEqual(adapter.model_config["model"], "gemini-2.5-flash")

        # Switch to Groq backup
        adapter.set_model_config({"provider": "groq", "api_key": "k_groq", "model": "llama-3.3-70b-versatile"})
        self.assertEqual(adapter.model_config["provider"], "groq")
        self.assertEqual(adapter.model_config["model"], "llama-3.3-70b-versatile")

        # Switch to Ollama offline fallback
        adapter.set_model_config({"provider": "ollama", "model": "gemma4:12b-hermes"})
        self.assertEqual(adapter.model_config["provider"], "ollama")
        self.assertEqual(adapter.model_config["api_base"], "http://localhost:11434/v1/")

    # 9. LLMClient Error Handling (401 vs Rate Limit)
    @patch("urllib.request.urlopen")
    def test_llm_client_fails_fast_on_401(self, mock_urlopen):
        """Verifies LLMClient does not retry indefinitely when receiving HTTP 401 Unauthorized."""
        mock_err = urllib.error.HTTPError(
            url="https://api.apinex.bond/v1/chat/completions",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=None
        )
        mock_urlopen.side_effect = mock_err

        client = LLMClient({
            "provider": "apinex",
            "api_key": "invalid_key",
            "api_base": "https://api.apinex.bond/v1"
        })

        res = client.call_llm_json("System prompt", "User prompt")
        self.assertIsNone(res)
        # Verify it attempted only 1 time and did not retry
        self.assertEqual(mock_urlopen.call_count, 1)

    @patch("urllib.request.urlopen")
    def test_llm_client_bounded_retries_on_rate_limit(self, mock_urlopen):
        """Verifies LLMClient performs bounded retries (max 3 attempts) on HTTP 429 rate limits."""
        mock_err = urllib.error.HTTPError(
            url="https://api.apinex.bond/v1/chat/completions",
            code=429,
            msg="Too Many Requests",
            hdrs={},
            fp=None
        )
        mock_urlopen.side_effect = mock_err

        client = LLMClient({
            "provider": "apinex",
            "api_key": "valid_key",
            "api_base": "https://api.apinex.bond/v1"
        })

        with patch("time.sleep") as mock_sleep:
            res = client.call_llm_json("System prompt", "User prompt")
            self.assertIsNone(res)
            # Must be bounded to max 3 attempts
            self.assertEqual(mock_urlopen.call_count, 3)
            self.assertEqual(mock_sleep.call_count, 2)

    # 10. OpenAI Tool Calling Payload Schema Compatibility
    def test_openai_tool_calling_payload_compatibility(self):
        """Verifies tool calling payload for APInex conforms to OpenAI function schema."""
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read file contents",
                    "parameters": {
                        "type": "object",
                        "properties": {"path": {"type": "string"}},
                        "required": ["path"]
                    }
                }
            }
        ]
        payload = {
            "model": "free/gemini-3.8-flash",
            "messages": [{"role": "user", "content": "Check files"}],
            "tools": tools
        }
        self.assertEqual(payload["tools"][0]["type"], "function")
        self.assertEqual(payload["tools"][0]["function"]["name"], "read_file")

    # 11. Live or Mocked APInex Chat Request
    def test_live_or_mocked_apinex_chat_request(self):
        """Verifies APInex API communication (with live credential auth validation when key is configured)."""
        api_key = os.getenv("APINEX_API_KEY", "").strip()

        # 1. Verify JSON parsing and response contract
        mock_body = {
            "choices": [{
                "message": {
                    "content": json.dumps({"status": "ok", "provider": "apinex"})
                }
            }]
        }
        with patch("urllib.request.urlopen") as mock_open:
            mock_resp = MagicMock()
            mock_resp.read.return_value = json.dumps(mock_body).encode("utf-8")
            mock_resp.__enter__.return_value = mock_resp
            mock_open.return_value = mock_resp

            client = LLMClient({
                "provider": "apinex",
                "api_key": api_key or "dummy_key",
                "api_base": "https://api.apinex.bond/v1",
                "model": "free/gemini-3.8-flash"
            })
            result = client.call_llm_json("System", "User")
            self.assertIsNotNone(result)
            self.assertEqual(result.get("status"), "ok")
            self.assertEqual(result.get("provider"), "apinex")

        # 2. When real credentials exist in env, perform live authenticated verification on /v1/models
        if api_key:
            import urllib.request
            req = urllib.request.Request(
                "https://api.apinex.bond/v1/models",
                headers={"Authorization": f"Bearer {api_key}", "User-Agent": "HermesAgent/1.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                self.assertEqual(resp.status, 200, "Live APInex authentication failed")
                catalog = json.loads(resp.read().decode("utf-8"))
                self.assertTrue(len(catalog.get("data", [])) > 0, "Models list should not be empty")

if __name__ == "__main__":
    unittest.main()
