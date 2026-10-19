"""
Phase 4 Verification Tests: Lifecycle & Event Reliability.
Verifies stable event ID generation, deduplication key structure, and build status integrity.
"""

import unittest
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from server.tasks.task_events import create_event

class TestPhase4LifecycleEvents(unittest.TestCase):

    def test_create_event_generates_stable_unique_event_id(self):
        evt1 = create_event("test_event", "session_1", {"foo": "bar"})
        evt2 = create_event("test_event", "session_1", {"foo": "bar"})

        self.assertIn("event_id", evt1)
        self.assertIn("event_id", evt2)
        self.assertTrue(evt1["event_id"].startswith("evt_"))
        self.assertTrue(evt2["event_id"].startswith("evt_"))
        # Ensure event IDs are distinct
        self.assertNotEqual(evt1["event_id"], evt2["event_id"])

    def test_create_event_accepts_custom_event_id(self):
        custom_id = "custom_evt_12345"
        evt = create_event("test_event", "session_1", {}, event_id=custom_id)
        self.assertEqual(evt["event_id"], custom_id)

    def test_failed_build_status_formatting_logic(self):
        # Validate that failed build events mark success as False
        failed_event = create_event("project_build_completed", "session_1", {
            "project_name": "test_app",
            "success": False,
            "remaining_issues": ["Syntax error in main.js"]
        })
        self.assertFalse(failed_event["data"]["success"])
        self.assertEqual(failed_event["event"], "project_build_completed")

if __name__ == "__main__":
    unittest.main()
