import unittest
from server.debug import ErrorMemory

class TestErrorMemory(unittest.TestCase):

    def setUp(self):
        self.em = ErrorMemory()

    def test_record_and_retrieve_error_history(self):
        self.em.record_error(
            session_id="s1",
            error_text="ModuleNotFoundError: No module named 'jwt'",
            root_cause="Missing PyJWT dependency",
            attempted_fix="pip install pyjwt",
            result="Resolved"
        )

        history = self.em.get_error_history("s1")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["error_text"], "ModuleNotFoundError: No module named 'jwt'")

        formatted = self.em.format_history_for_context("s1")
        self.assertIn("Missing PyJWT dependency", formatted)

if __name__ == "__main__":
    unittest.main()
