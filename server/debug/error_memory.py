import time
from typing import Dict, List, Any, Optional

class ErrorMemory:
    """Maintains error classification and fix attempt history for active development sessions."""

    def __init__(self):
        self.session_errors: Dict[str, List[Dict[str, Any]]] = {}

    def record_error(
        self,
        session_id: str,
        error_text: str,
        root_cause: str,
        attempted_fix: str,
        result: str
    ) -> Dict[str, Any]:
        entry = {
            "timestamp": time.time(),
            "error_text": error_text,
            "root_cause": root_cause,
            "attempted_fix": attempted_fix,
            "result": result
        }
        if session_id not in self.session_errors:
            self.session_errors[session_id] = []
        self.session_errors[session_id].append(entry)
        return entry

    def get_error_history(self, session_id: str) -> List[Dict[str, Any]]:
        return self.session_errors.get(session_id, [])

    def format_history_for_context(self, session_id: str) -> str:
        history = self.get_error_history(session_id)
        if not history:
            return "No previous error attempts recorded for this session."

        lines = ["Previous Failure & Fix Attempts Log:"]
        for idx, item in enumerate(history, 1):
            lines.append(f"{idx}. Error: {item['error_text']}\n   Root Cause: {item['root_cause']}\n   Attempted Fix: {item['attempted_fix']}\n   Result: {item['result']}")
        return "\n".join(lines)
