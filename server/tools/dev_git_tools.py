import subprocess
from typing import Optional

class DevGitTools:
    def __init__(self, workspace_guard):
        self.guard = workspace_guard

    def git_status(self) -> str:
        try:
            res = subprocess.run(
                "git status",
                shell=True,
                cwd=str(self.guard.workspace_root),
                capture_output=True,
                text=True,
                timeout=15
            )
            return res.stdout or res.stderr or "No git status output."
        except Exception as e:
            return f"Error executing git status: {str(e)}"

    def git_diff(self, file_path: Optional[str] = None) -> str:
        cmd = f"git diff {file_path}" if file_path else "git diff"
        try:
            res = subprocess.run(
                cmd,
                shell=True,
                cwd=str(self.guard.workspace_root),
                capture_output=True,
                text=True,
                timeout=20
            )
            return res.stdout or "No git diff changes detected."
        except Exception as e:
            return f"Error executing git diff: {str(e)}"

    def git_commit(self, message: str) -> str:
        try:
            res = subprocess.run(
                f'git add -A && git commit -m "{message}"',
                shell=True,
                cwd=str(self.guard.workspace_root),
                capture_output=True,
                text=True,
                timeout=30
            )
            return res.stdout or res.stderr or "Git commit completed."
        except Exception as e:
            return f"Error executing git commit: {str(e)}"
