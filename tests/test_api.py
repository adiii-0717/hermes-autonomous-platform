import unittest
from fastapi.testclient import TestClient
from server.main import app

class TestAPIEndpoints(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "online")
        self.assertIn("Hermes Agent Framework", data["framework"])

    def test_sessions_endpoint(self):
        # Create session
        res_create = self.client.post("/api/sessions", json={"session_name": "test_session_1"})
        self.assertEqual(res_create.status_code, 200)
        session_data = res_create.json()
        self.assertIn("session_id", session_data)

        # List sessions
        res_list = self.client.get("/api/sessions")
        self.assertEqual(res_list.status_code, 200)
        sessions_list = res_list.json()["sessions"]
        self.assertTrue(any(s["session_id"] == session_data["session_id"] for s in sessions_list))

    def test_workspace_endpoints(self):
        # 1. Get workspace info
        res_info = self.client.get("/api/workspace")
        self.assertEqual(res_info.status_code, 200)
        self.assertTrue(res_info.json()["exists"])

        # 2. List files
        res_files = self.client.get("/api/workspace/files")
        self.assertEqual(res_files.status_code, 200)
        self.assertIn("files", res_files.json())

    def test_chat_rest_endpoint(self):
        res = self.client.post("/api/chat", json={"session_id": "test_s1", "message": "List directory files"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["session_id"], "test_s1")
        self.assertIn("events", data)

if __name__ == "__main__":
    unittest.main()
