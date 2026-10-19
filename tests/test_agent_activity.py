import unittest
from fastapi.testclient import TestClient
from server.main import app, adapter
from server.tasks import TaskManager, TaskStatus, DevelopmentPlan, create_event

class TestAgentActivity(unittest.TestCase):
    """Tests agent activity tracking, lifecycle events, and task manager integration.
    Reflects the active Hermes Agent architecture (server.tasks & FastAPI event bus).
    """

    def setUp(self):
        self.client = TestClient(app)
        self.tm = TaskManager()

    def test_activity_event_schema(self):
        """Verify standard activity events conform to event schema."""
        evt = create_event(
            "agent_heartbeat",
            "session_test",
            {
                "status": "working",
                "elapsed_seconds": 15,
                "latest_tool": "dev_file_tools.write_file"
            }
        )
        self.assertEqual(evt["event"], "agent_heartbeat")
        self.assertEqual(evt["session_id"], "session_test")
        self.assertEqual(evt["data"]["status"], "working")
        self.assertEqual(evt["data"]["latest_tool"], "dev_file_tools.write_file")

    def test_task_plan_activity_lifecycle(self):
        """Verify task plan creation, status updates, and progress calculation."""
        plan = self.tm.create_plan(
            session_id="activity_session_1",
            title="Agent Engineering Plan",
            requirement="Build REST endpoints",
            tasks_data=[
                {"title": "Implement router", "description": "Add routes"},
                {"title": "Implement models", "description": "Add schemas"},
                {"title": "Run tests", "description": "Verify functionality"}
            ]
        )
        self.assertEqual(len(plan.tasks), 3)
        self.assertEqual(plan.progress_percentage(), 0.0)

        # Transition task 1 to in_progress
        t1 = plan.tasks[0]
        self.tm.update_task_status("activity_session_1", t1.id, TaskStatus.IN_PROGRESS)
        self.assertEqual(t1.status, TaskStatus.IN_PROGRESS)

        # Transition task 1 to completed
        self.tm.update_task_status("activity_session_1", t1.id, TaskStatus.COMPLETED)
        self.assertEqual(t1.status, TaskStatus.COMPLETED)
        self.assertAlmostEqual(plan.progress_percentage(), 33.3, places=1)

    def test_api_tasks_endpoint(self):
        """Verify /api/tasks returns plan for an active session."""
        session_id = "activity_session_api"
        adapter.task_manager.create_plan(
            session_id=session_id,
            title="API Activity Plan",
            requirement="Verify /api/tasks",
            tasks_data=[
                {"title": "Test Task", "description": "Validation"}
            ]
        )
        res = self.client.get(f"/api/tasks?session_id={session_id}")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["session_id"], session_id)
        self.assertIsNotNone(data["plan"])
        self.assertEqual(len(data["plan"]["tasks"]), 1)

    def test_api_sessions_activity_registry(self):
        """Verify /api/sessions tracks created sessions."""
        res = self.client.post("/api/sessions", json={"session_name": "Activity Test"})
        self.assertEqual(res.status_code, 200)
        sess = res.json()
        self.assertIn("session_id", sess)

        list_res = self.client.get("/api/sessions")
        self.assertEqual(list_res.status_code, 200)
        sessions = list_res.json().get("sessions", [])
        self.assertTrue(any(s["session_id"] == sess["session_id"] for s in sessions))

if __name__ == "__main__":
    unittest.main()
