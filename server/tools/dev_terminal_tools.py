import uuid
import subprocess
import asyncio
import time
from typing import Optional, Dict, Any
from server.security.container_runner import ContainerRunner

class DevTerminalTools:
    def __init__(self, workspace_guard, approval_controller):
        self.guard = workspace_guard
        self.approval = approval_controller
        self.container_runner = ContainerRunner(workspace_guard=workspace_guard)
        self.background_processes: Dict[str, Dict[str, Any]] = {}

    async def execute_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        risk_level, err_msg = self.guard.classify_command(command)
        
        if risk_level == "BLOCKED":
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": err_msg,
                "isolation_mode": "blocked_by_guard"
            }
            
        if risk_level == "REQUIRE_APPROVAL" and self.approval:
            approved = await self.approval.request_approval(
                action_type="terminal_command",
                details={"command": command, "workspace": str(self.guard.workspace_root)}
            )
            if not approved:
                return {
                    "success": False,
                    "exit_code": -1,
                    "stdout": "",
                    "stderr": "Security Error: Command execution rejected by developer sign-off policy.",
                    "isolation_mode": "rejected_by_policy"
                }

        return await self.container_runner.execute_command(command, timeout=timeout)

    def start_background_process(self, command: str) -> Dict[str, Any]:
        risk_level, err_msg = self.guard.classify_command(command)
        if risk_level == "BLOCKED":
            return {"success": False, "process_id": "", "error": err_msg}
            
        try:
            proc_id = str(uuid.uuid4())[:8]
            proc = subprocess.Popen(
                command,
                shell=True,
                cwd=str(self.guard.workspace_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.background_processes[proc_id] = {
                "process": proc,
                "command": command,
                "pid": proc.pid,
                "start_time": time.time(),
                "workspace": str(self.guard.workspace_root)
            }
            return {
                "success": True,
                "process_id": proc_id,
                "pid": proc.pid,
                "command": command,
                "message": f"Background process '{proc_id}' started with PID {proc.pid}."
            }
        except Exception as e:
            return {"success": False, "process_id": "", "error": str(e)}

    def get_process_output(self, process_id: str) -> Dict[str, Any]:
        if process_id not in self.background_processes:
            return {"success": False, "error": f"Process ID '{process_id}' not found."}
            
        info = self.background_processes[process_id]
        proc = info["process"]
        
        poll_status = proc.poll()
        is_running = (poll_status is None)
        
        stdout_text = ""
        stderr_text = ""
        if not is_running:
            stdout_text, stderr_text = proc.communicate()
            
        return {
            "success": True,
            "process_id": process_id,
            "running": is_running,
            "exit_code": poll_status,
            "stdout": stdout_text,
            "stderr": stderr_text
        }

    def get_process_status(self, process_id: Optional[str] = None) -> Dict[str, Any]:
        """Returns status for a specific background process or all running processes."""
        if process_id:
            if process_id not in self.background_processes:
                return {"success": False, "error": f"Process ID '{process_id}' not found."}
            info = self.background_processes[process_id]
            proc = info["process"]
            poll_status = proc.poll()
            return {
                "success": True,
                "process_id": process_id,
                "command": info["command"],
                "pid": info["pid"],
                "running": (poll_status is None),
                "exit_code": poll_status,
                "uptime_seconds": round(time.time() - info["start_time"], 1)
            }

        processes_list = []
        for pid_key, info in self.background_processes.items():
            proc = info["process"]
            poll_status = proc.poll()
            processes_list.append({
                "process_id": pid_key,
                "command": info["command"],
                "pid": info["pid"],
                "running": (poll_status is None),
                "exit_code": poll_status,
                "uptime_seconds": round(time.time() - info["start_time"], 1)
            })

        return {
            "success": True,
            "total_processes": len(processes_list),
            "processes": processes_list
        }

    def kill_process(self, process_id: str) -> Dict[str, Any]:
        """Terminates a running background process."""
        if process_id not in self.background_processes:
            return {"success": False, "error": f"Process ID '{process_id}' not found."}

        info = self.background_processes[process_id]
        proc = info["process"]
        try:
            proc.kill()
            proc.wait(timeout=2.0)
            return {
                "success": True,
                "process_id": process_id,
                "message": f"Process '{process_id}' (PID {info['pid']}) successfully terminated."
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to kill process '{process_id}': {str(e)}"}