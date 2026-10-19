import unittest
from server.tasks import TaskManager, TaskStatus, DevelopmentPlan, create_event

class TestTaskManager(unittest.TestCase):

    def setUp(self):
        self.tm = TaskManager()

    def test_create_plan_and_update_status(self):
        plan = self.tm.create_plan(
            session_id="s1",
            title="Add Auth",
            requirement="Implement JWT auth",
            tasks_data=[
                {"title": "Install pyjwt", "description": "Add dependency"},
                {"title": "Implement auth middleware", "description": "Token check"},
                {"title": "Write unit tests", "description": "Verify token decoding"}
            ]
        )

        self.assertEqual(len(plan.tasks), 3)
        self.assertEqual(plan.progress_percentage(), 0.0)

        t1 = plan.tasks[0]
        self.tm.update_task_status("s1", t1.id, TaskStatus.IN_PROGRESS)
        self.assertEqual(t1.status, TaskStatus.IN_PROGRESS)

        self.tm.update_task_status("s1", t1.id, TaskStatus.COMPLETED)
        self.assertEqual(t1.status, TaskStatus.COMPLETED)
        self.assertAlmostEqual(plan.progress_percentage(), 33.3, places=1)

    def test_event_schema_creation(self):
        event = create_event("task_started", "s1", {"task_id": "t1", "title": "Setup DB"})
        self.assertEqual(event["event"], "task_started")
        self.assertEqual(event["session_id"], "s1")
        self.assertEqual(event["data"]["title"], "Setup DB")

if __name__ == "__main__":
    unittest.main()
