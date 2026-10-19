"""
Comprehensive Automated Test Suite for Automatic Gemini API Failover in HermesProject.
Verifies all 14 required failover, recovery, safety, sanitization, and resilience scenarios.
Uses mocked API responses so tests do not consume real API quotas.
"""

import os
import sys
import time
import json
import asyncio
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from server.agents.provider_manager import (
    ProviderManager,
    ProviderConfig,
    ProviderStatus,
    ErrorClass,
    provider_manager
)
from server.agents.llm_client import LLMClient
from server.hermes_adapter import HermesAgentAdapter


class TestGeminiFailoverScenarios(unittest.TestCase):
    """Test suite verifying all 14 required Gemini failover and safety scenarios."""

    def setUp(self):
        self.workspace = PROJECT_ROOT / "workspace" / "test_failover_ws"
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.env_backup = os.environ.copy()

        # Reset provider_manager with controlled test state
        provider_manager.reload_from_env()
        # Set clean test providers
        provider_manager._providers["gemini_1"] = ProviderConfig(
            provider_id="gemini_1",
            provider="google-gemini",
            display_name="Gemini (Key 1)",
            api_key="dummy_gemini_key_1_mock",
            api_base="https://generativelanguage.googleapis.com/v1beta/openai/",
            default_model="gemini-2.5-flash",
            priority=1
        )
        provider_manager._providers["gemini_2"] = ProviderConfig(
            provider_id="gemini_2",
            provider="google-gemini",
            display_name="Gemini (Key 2)",
            api_key="dummy_gemini_key_2_mock",
            api_base="https://generativelanguage.googleapis.com/v1beta/openai/",
            default_model="gemini-2.5-flash",
            priority=2
        )
        provider_manager._providers["gemini_3"] = ProviderConfig(
            provider_id="gemini_3",
            provider="google-gemini",
            display_name="Gemini (Key 3)",
            api_key="dummy_gemini_key_3_mock",
            api_base="https://generativelanguage.googleapis.com/v1beta/openai/",
            default_model="gemini-2.5-flash",
            priority=3
        )
        provider_manager._providers["apinex"] = ProviderConfig(
            provider_id="apinex",
            provider="apinex",
            display_name="APInex",
            api_key="dummy_apinex_key_mock",
            api_base="https://api.apinex.bond/v1/",
            default_model="free/gemini-3.8-flash",
            priority=4
        )

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.env_backup)
        provider_manager.reload_from_env()

    # --------------------------------------------------------------------------
    # Scenario 1: Gemini Key 1 succeeds without fallback
    # --------------------------------------------------------------------------
    @patch("urllib.request.urlopen")
    def test_scenario_1_gemini_key_1_succeeds_without_fallback(self, mock_urlopen):
        """Scenario 1: Primary provider (Key 1) succeeds cleanly. No fallback occurs."""
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "choices": [{"message": {"content": json.dumps({"status": "ok", "provider": "gemini_1"})}}]
        }).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        client = LLMClient()
        res = client.call_llm_json("System", "Build app")

        self.assertIsNotNone(res)
        self.assertEqual(res.get("status"), "ok")
        self.assertEqual(mock_urlopen.call_count, 1)

        # Gemini 1 should be marked HEALTHY and failure count 0
        p1 = provider_manager._providers["gemini_1"]
        self.assertEqual(p1.status, ProviderStatus.HEALTHY)
        self.assertEqual(p1.failure_count, 0)

    # --------------------------------------------------------------------------
    # Scenario 2: Key 1 fails due to quota exhaustion; Key 2 succeeds
    # --------------------------------------------------------------------------
    @patch("urllib.request.urlopen")
    def test_scenario_2_key_1_quota_exhaustion_failover_to_key_2(self, mock_urlopen):
        """Scenario 2: Key 1 hits 429 Quota Exhausted; Hermes rotates to Key 2 and succeeds."""
        import urllib.error

        def side_effect(req, *args, **kwargs):
            auth_header = req.headers.get("Authorization", "")
            if "dummy_gemini_key_1_mock" in auth_header:
                fp = MagicMock()
                fp.read.return_value = b'{"error": {"code": 429, "message": "ResourceExhausted quota exceeded"}}'
                raise urllib.error.HTTPError(req.full_url, 429, "Too Many Requests", req.headers, fp)
            else:
                resp = MagicMock()
                resp.read.return_value = json.dumps({
                    "choices": [{"message": {"content": json.dumps({"status": "ok", "provider": "gemini_2"})}}]
                }).encode("utf-8")
                resp.__enter__.return_value = resp
                return resp

        mock_urlopen.side_effect = side_effect

        client = LLMClient()
        res = client.call_llm_json("System", "Build app")

        self.assertIsNotNone(res)
        self.assertEqual(res.get("provider"), "gemini_2")

        # Key 1 entered COOLDOWN
        p1 = provider_manager._providers["gemini_1"]
        p2 = provider_manager._providers["gemini_2"]
        self.assertEqual(p1.status, ProviderStatus.COOLDOWN)
        self.assertEqual(p2.status, ProviderStatus.HEALTHY)

    # --------------------------------------------------------------------------
    # Scenario 3: Keys 1 and 2 fail; Key 3 succeeds
    # --------------------------------------------------------------------------
    @patch("urllib.request.urlopen")
    def test_scenario_3_keys_1_and_2_fail_key_3_succeeds(self, mock_urlopen):
        """Scenario 3: Keys 1 and 2 both fail (429); Key 3 succeeds."""
        import urllib.error

        def side_effect(req, *args, **kwargs):
            auth = req.headers.get("Authorization", "")
            if "dummy_gemini_key_1_mock" in auth or "dummy_gemini_key_2_mock" in auth:
                fp = MagicMock()
                fp.read.return_value = b'{"error": {"code": 429, "message": "ResourceExhausted quota exceeded"}}'
                raise urllib.error.HTTPError(req.full_url, 429, "Too Many Requests", req.headers, fp)
            else:
                resp = MagicMock()
                resp.read.return_value = json.dumps({
                    "choices": [{"message": {"content": json.dumps({"status": "ok", "provider": "gemini_3"})}}]
                }).encode("utf-8")
                resp.__enter__.return_value = resp
                return resp

        mock_urlopen.side_effect = side_effect

        client = LLMClient()
        res = client.call_llm_json("System", "Build app")

        self.assertIsNotNone(res)
        self.assertEqual(res.get("provider"), "gemini_3")
        self.assertEqual(provider_manager._providers["gemini_1"].status, ProviderStatus.COOLDOWN)
        self.assertEqual(provider_manager._providers["gemini_2"].status, ProviderStatus.COOLDOWN)
        self.assertEqual(provider_manager._providers["gemini_3"].status, ProviderStatus.HEALTHY)

    # --------------------------------------------------------------------------
    # Scenario 4: All Gemini keys fail; APInex succeeds
    # --------------------------------------------------------------------------
    @patch("urllib.request.urlopen")
    def test_scenario_4_all_gemini_keys_fail_apinex_succeeds(self, mock_urlopen):
        """Scenario 4: All Gemini keys fail with quota exhaustion; final fallback APInex succeeds."""
        import urllib.error

        def side_effect(req, *args, **kwargs):
            auth = req.headers.get("Authorization", "")
            if "dummy_gemini" in auth:
                fp = MagicMock()
                fp.read.return_value = b'{"error": {"code": 429, "message": "Quota limit reached"}}'
                raise urllib.error.HTTPError(req.full_url, 429, "Too Many Requests", req.headers, fp)
            elif "dummy_apinex" in auth:
                resp = MagicMock()
                resp.read.return_value = json.dumps({
                    "choices": [{"message": {"content": json.dumps({"status": "ok", "provider": "apinex"})}}]
                }).encode("utf-8")
                resp.__enter__.return_value = resp
                return resp
            raise RuntimeError("Unexpected request")

        mock_urlopen.side_effect = side_effect

        client = LLMClient()
        res = client.call_llm_json("System", "Build app")

        self.assertIsNotNone(res)
        self.assertEqual(res.get("provider"), "apinex")
        self.assertEqual(provider_manager._providers["gemini_1"].status, ProviderStatus.COOLDOWN)
        self.assertEqual(provider_manager._providers["gemini_2"].status, ProviderStatus.COOLDOWN)
        self.assertEqual(provider_manager._providers["gemini_3"].status, ProviderStatus.COOLDOWN)
        self.assertEqual(provider_manager._providers["apinex"].status, ProviderStatus.HEALTHY)

    # --------------------------------------------------------------------------
    # Scenario 5: All providers fail; frontend receives controlled error
    # --------------------------------------------------------------------------
    def test_scenario_5_all_providers_fail_controlled_error(self):
        """Scenario 5: Every provider fails; exact controlled error is emitted to client."""
        # Mark all providers in cooldown or disabled
        for p in provider_manager._providers.values():
            p.status = ProviderStatus.COOLDOWN
            p.cooldown_until = time.time() + 9999

        adapter = HermesAgentAdapter(str(self.workspace))
        events = []

        async def mock_callback(evt):
            events.append(evt)

        asyncio.run(adapter.process_user_turn("s1", "Build app", mock_callback))

        # Check for exact required error message
        expected_msg = "All configured AI providers are temporarily unavailable. Your request could not be completed right now. Please try again later."
        error_events = [e for e in events if e.get("event") == "error"]
        finish_events = [e for e in events if e.get("event") == "agent_finished"]

        self.assertTrue(len(error_events) > 0, "Must emit error event")
        self.assertIn(expected_msg, error_events[0]["data"]["error"])
        self.assertTrue(len(finish_events) > 0, "Must emit agent_finished event to stop frontend loading")
        self.assertEqual(finish_events[0]["data"]["status"], "error")

    # --------------------------------------------------------------------------
    # Scenario 6: Missing backup keys do not break application
    # --------------------------------------------------------------------------
    def test_scenario_6_missing_backup_keys_graceful_handling(self):
        """Scenario 6: Missing optional backup keys (Key 2, Key 3) are handled gracefully."""
        # Key 2 and Key 3 empty
        provider_manager._providers["gemini_2"].api_key = ""
        provider_manager._providers["gemini_2"].status = ProviderStatus.DISABLED
        provider_manager._providers["gemini_3"].api_key = ""
        provider_manager._providers["gemini_3"].status = ProviderStatus.DISABLED

        ordered = provider_manager.get_ordered_providers()
        ordered_ids = [p.provider_id for p in ordered]

        self.assertIn("gemini_1", ordered_ids)
        self.assertNotIn("gemini_2", ordered_ids)
        self.assertNotIn("gemini_3", ordered_ids)
        self.assertIn("apinex", ordered_ids)

        # Fallover chain directly links Key 1 -> APInex without error
        chain = provider_manager.get_failover_chain("gemini_1")
        self.assertEqual(chain[0].provider_id, "apinex")

    # --------------------------------------------------------------------------
    # Scenario 7: Authentication failures handled appropriately
    # --------------------------------------------------------------------------
    @patch("urllib.request.urlopen")
    def test_scenario_7_auth_failure_classification_and_failover(self, mock_urlopen):
        """Scenario 7: 401/403 Invalid API key marks key AUTH_FAILED and fails over cleanly."""
        import urllib.error

        def side_effect(req, *args, **kwargs):
            auth = req.headers.get("Authorization", "")
            if "dummy_gemini_key_1_mock" in auth:
                fp = MagicMock()
                fp.read.return_value = b'{"error": {"code": 401, "message": "API key not valid"}}'
                raise urllib.error.HTTPError(req.full_url, 401, "Unauthorized", req.headers, fp)
            else:
                resp = MagicMock()
                resp.read.return_value = json.dumps({
                    "choices": [{"message": {"content": json.dumps({"status": "ok", "provider": "gemini_2"})}}]
                }).encode("utf-8")
                resp.__enter__.return_value = resp
                return resp

        mock_urlopen.side_effect = side_effect

        client = LLMClient()
        res = client.call_llm_json("System", "Build app")

        self.assertIsNotNone(res)
        self.assertEqual(res.get("provider"), "gemini_2")

        # Key 1 is permanently AUTH_FAILED
        p1 = provider_manager._providers["gemini_1"]
        self.assertEqual(p1.status, ProviderStatus.AUTH_FAILED)
        self.assertFalse(p1.is_available())

    # --------------------------------------------------------------------------
    # Scenario 8: Invalid model and request errors classified correctly
    # --------------------------------------------------------------------------
    def test_scenario_8_error_classification(self):
        """Scenario 8: Error types are classified correctly into normalized categories."""
        c1, _ = provider_manager.classify_error(Exception("HTTP 429: ResourceExhausted quota exceeded"))
        self.assertEqual(c1, ErrorClass.QUOTA_EXHAUSTED)

        c2, _ = provider_manager.classify_error(Exception("HTTP 401: Invalid API Key"))
        self.assertEqual(c2, ErrorClass.AUTH_FAILURE)

        c3, _ = provider_manager.classify_error(Exception("HTTP 403: PermissionDenied"))
        self.assertEqual(c3, ErrorClass.AUTH_FAILURE)

        c4, _ = provider_manager.classify_error(Exception("HTTP 400: model_not_found does not exist"))
        self.assertEqual(c4, ErrorClass.INVALID_MODEL)

        c5, _ = provider_manager.classify_error(Exception("HTTP 503: Service Unavailable backend overloaded"))
        self.assertEqual(c5, ErrorClass.SERVER_ERROR)

        c6, _ = provider_manager.classify_error(Exception("ConnectTimeout: connection timed out after 30s"))
        self.assertEqual(c6, ErrorClass.TIMEOUT)

        c7, _ = provider_manager.classify_error(Exception("socket.error: Connection refused"))
        self.assertEqual(c7, ErrorClass.NETWORK_ERROR)

    # --------------------------------------------------------------------------
    # Scenario 9: Network failures and timeouts terminate within configured bounds
    # --------------------------------------------------------------------------
    @patch("urllib.request.urlopen")
    def test_scenario_9_timeout_and_network_failure_handling(self, mock_urlopen):
        """Scenario 9: Network failure / timeout fails over without indefinite stalling."""
        import socket
        # Gemini 1 raises socket timeout, Gemini 2 succeeds
        def side_effect(req, *args, **kwargs):
            auth = req.headers.get("Authorization", "")
            if "dummy_gemini_key_1_mock" in auth:
                raise socket.timeout("timed out")
            else:
                resp = MagicMock()
                resp.read.return_value = json.dumps({
                    "choices": [{"message": {"content": json.dumps({"status": "ok", "provider": "gemini_2"})}}]
                }).encode("utf-8")
                resp.__enter__.return_value = resp
                return resp

        mock_urlopen.side_effect = side_effect

        start = time.time()
        client = LLMClient()
        res = client.call_llm_json("System", "Build app")
        elapsed = time.time() - start

        self.assertIsNotNone(res)
        self.assertEqual(res.get("provider"), "gemini_2")
        self.assertLess(elapsed, 10.0, "Timeout handling must not hang indefinitely")

    # --------------------------------------------------------------------------
    # Scenario 10: Providers recover and return to original priority
    # --------------------------------------------------------------------------
    def test_scenario_10_automatic_provider_recovery(self):
        """Scenario 10: Provider in cooldown recovers automatically when cooldown expires."""
        p1 = provider_manager._providers["gemini_1"]
        # Set cooldown in the past
        p1.status = ProviderStatus.COOLDOWN
        p1.cooldown_until = time.time() - 5.0

        # Checking availability should trigger recovery
        self.assertTrue(p1.is_available())
        self.assertEqual(p1.status, ProviderStatus.HEALTHY)

        active = provider_manager.get_active_provider()
        self.assertEqual(active.provider_id, "gemini_1")
        self.assertEqual(active.priority, 1)

    # --------------------------------------------------------------------------
    # Scenario 11: User cancellation stops retries
    # --------------------------------------------------------------------------
    def test_scenario_11_user_cancellation_stops_retries(self):
        """Scenario 11: Cancelling turn halts execution and does not continue retrying."""
        adapter = HermesAgentAdapter(str(self.workspace))
        adapter._cancelled = True

        events = []
        async def mock_callback(evt):
            events.append(evt)

        asyncio.run(adapter.process_user_turn("s_cancel", "Build app", mock_callback))

        cancel_events = [e for e in events if e.get("data", {}).get("status") == "cancelled"]
        self.assertTrue(len(cancel_events) > 0, "Must emit cancelled status event")

    # --------------------------------------------------------------------------
    # Scenario 12: Mid-stream failures do not duplicate generated content
    # --------------------------------------------------------------------------
    @patch("run_agent.AIAgent")
    def test_scenario_12_mid_stream_failure_safety(self, mock_aiagent_cls):
        """Scenario 12: Mid-stream failure stops chain to prevent duplicate content or repeated tool changes."""
        mock_agent_instance = MagicMock()

        def agent_init(*args, **kwargs):
            mock_agent_instance.stream_delta_callback = kwargs.get("stream_delta_callback")
            return mock_agent_instance

        mock_aiagent_cls.side_effect = agent_init

        def fake_run(user_message):
            # Simulate streaming tokens before failing
            if getattr(mock_agent_instance, "stream_delta_callback", None):
                mock_agent_instance.stream_delta_callback("Here is part 1 of the app...")
            raise RuntimeError("Stream disconnected mid-response")

        mock_agent_instance.run_conversation.side_effect = fake_run

        adapter = HermesAgentAdapter(str(self.workspace))
        events = []
        async def mock_callback(evt):
            events.append(evt)

        asyncio.run(adapter.process_user_turn("s_mid", "Build app", mock_callback))

        # Must have assistant_message with partial token, then notice, and NOT retry blindly
        messages = [e for e in events if e.get("event") == "assistant_message"]
        interrupted_events = [m for m in messages if "Generation Interrupted" in m["data"]["content"]]
        self.assertTrue(len(interrupted_events) > 0, "Must emit generation interrupted notice")
        
        # Verify provider loop stopped (only 1 provider attempted)
        self.assertEqual(mock_aiagent_cls.call_count, 1)

    # --------------------------------------------------------------------------
    # Scenario 13: API keys never appear in logs or user-facing errors
    # --------------------------------------------------------------------------
    def test_scenario_13_credential_sanitization(self):
        """Scenario 13: Keys and authorization tokens are strictly redacted from logs and errors."""
        secret_key_1 = "dummy_gemini_key_1_mock"
        secret_key_2 = "AIzaSyDummySyntheticKeyForSanitizationX"
        bearer_token = "Bearer AQ.DummySyntheticBearerTokenForTestingX"

        raw_err = f"Failed to call endpoint with key {secret_key_1} and {secret_key_2} and header {bearer_token}"
        sanitized = provider_manager.sanitize_text(raw_err)

        self.assertNotIn(secret_key_1, sanitized)
        self.assertNotIn(secret_key_2, sanitized)
        self.assertNotIn("AQ.DummySyntheticBearerTokenForTestingX", sanitized)
        self.assertIn("[REDACTED_API_KEY]", sanitized)

    # --------------------------------------------------------------------------
    # Scenario 14: Existing agent, provider, and frontend functionality remains intact
    # --------------------------------------------------------------------------
    def test_scenario_14_existing_functionality_intact(self):
        """Scenario 14: Runtime configuration, tool registration, and existing features work."""
        adapter = HermesAgentAdapter(str(self.workspace))
        
        # Verify dynamic model switching
        adapter.set_model_config({"provider": "google-gemini", "model": "gemini-2.0-flash", "api_key": "k_custom"})
        self.assertEqual(adapter.model_config["provider"], "google-gemini")
        self.assertEqual(adapter.model_config["model"], "gemini-2.0-flash")
        self.assertEqual(adapter.model_config["api_key"], "k_custom")

        # Verify fallback chain computation
        fb_chain = adapter.get_fallback_provider_chain("google-gemini", current_key="k_custom")
        self.assertTrue(len(fb_chain) > 0)
        self.assertTrue(any(p["provider"] == "apinex" for p in fb_chain))


if __name__ == "__main__":
    unittest.main()
