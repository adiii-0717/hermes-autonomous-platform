import time
import uuid
from typing import Dict, Any, Optional

def create_event(
    event_type: str,
    session_id: str,
    data: Optional[Dict[str, Any]] = None,
    task_id: Optional[str] = None,
    event_id: Optional[str] = None
) -> Dict[str, Any]:
    """Creates a standardized real-time event dictionary for WebSocket consumption with a stable unique event_id."""
    return {
        "event_id": event_id or f"evt_{uuid.uuid4().hex[:12]}",
        "event": event_type,
        "session_id": session_id,
        "task_id": task_id,
        "timestamp": time.time(),
        "data": data or {}
    }
