import unittest
from fastapi.testclient import TestClient
from server.main import app

class TestServerAPI(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "online")
        self.assertIn("Hermes Agent", data["framework"])

    def test_sessions_lifecycle(self):
        create_res = self.client.post("/api/sessions", json={"session_name": "test_session"})
        self.assertEqual(create_res.status_code, 200)
        sess_data = create_res.json()
        self.assertIn("session_id", sess_data)

        list_res = self.client.get("/api/sessions")
        self.assertEqual(list_res.status_code, 200)
        sessions = list_res.json()["sessions"]
        self.assertTrue(any(s["session_id"] == sess_data["session_id"] for s in sessions))

    def test_workspace_endpoints(self):
        res = self.client.get("/api/workspace")
        self.assertEqual(res.status_code, 200)
        self.assertIn("workspace_root", res.json())

        manifest_res = self.client.get("/api/workspace/manifest")
        self.assertEqual(manifest_res.status_code, 200)
        self.assertIn("languages", manifest_res.json())

        health_res = self.client.get("/api/workspace/health")
        self.assertEqual(health_res.status_code, 200)
        self.assertIn("build_healthy", health_res.json())

        files_res = self.client.get("/api/workspace/files")
        self.assertEqual(files_res.status_code, 200)

    def test_chat_post_endpoint(self):
        chat_res = self.client.post("/api/chat", json={
            "session_id": "test_session_123",
            "message": "Inspect repository structure"
        })
        self.assertEqual(chat_res.status_code, 200)
        data = chat_res.json()
        self.assertEqual(data["session_id"], "test_session_123")
        self.assertGreater(len(data["events"]), 0)

if __name__ == "__main__":
    unittest.main()
