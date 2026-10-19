import uuid
import time
import asyncio
from typing import Dict, Any, Optional, Callable

class ApprovalController:
    """Manages human-in-the-loop approval requests for high-risk system operations."""

    def __init__(self):
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}
        self.broadcast_callback: Optional[Callable[[dict], Any]] = None

    def register_broadcast_callback(self, callback: Callable[[dict], Any]):
        self.broadcast_callback = callback

    async def request_approval(
        self,
        action_type: str,
        details: Dict[str, Any],
        timeout: float = 60.0
    ) -> bool:
        request_id = f"appr_{str(uuid.uuid4())[:8]}"
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        # Format rich risk metadata for the UI approval modal
        risk_info = {
            "request_id": request_id,
            "action_type": action_type,
            "command": details.get("command", ""),
            "workspace_root": details.get("workspace", ""),
            "risk_level": "HIGH-RISK OPERATION",
            "reason": "Execution of terminal command requires human developer sign-off policy.",
            "risk_details": f"Command '{details.get('command')}' executes inside workspace shell.",
            "safety_recommendation": "Inspect command parameters before granting execution approval.",
            "created_at": time.time(),
            "timeout_seconds": timeout,
            "status": "PENDING"
        }

        self.pending_approvals[request_id] = {
            "future": future,
            "data": risk_info
        }

        if self.broadcast_callback:
            event = {
                "event": "approval_required",
                "type": "approval_required",
                "timestamp": time.time(),
                "data": risk_info
            }
            if asyncio.iscoroutinefunction(self.broadcast_callback):
                await self.broadcast_callback(event)
            else:
                self.broadcast_callback(event)

        try:
            approved = await asyncio.wait_for(future, timeout=timeout)
            return approved
        except asyncio.TimeoutError:
            self.pending_approvals.pop(request_id, None)
            return False

    def resolve_approval(self, request_id: str, approved: bool) -> bool:
        if request_id in self.pending_approvals:
            item = self.pending_approvals.pop(request_id)
            future = item["future"]
            if not future.done():
                future.set_result(approved)
                return True
        return False
