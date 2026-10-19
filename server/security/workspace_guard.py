import os
import re
from pathlib import Path
from typing import Tuple

class WorkspaceGuard:
    """Security Boundary for Hermes Agent execution.
    
    Guarantees strict workspace containment, path traversal prevention,
    symlink escape blocking, and command risk classification.
    """
    
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root).resolve()
        self.real_workspace_root = os.path.realpath(str(self.workspace_root))
        os.makedirs(self.real_workspace_root, exist_ok=True)
        
    def validate_path(self, target_path: str) -> Tuple[bool, Path, str]:
        """Validate if target path is strictly within workspace boundaries, resolving symlinks."""
        if not target_path or not str(target_path).strip():
            return True, Path(self.real_workspace_root), ""
            
        try:
            import urllib.parse
            # 1. Decode URL percent encoding (%2F -> /)
            clean_path = urllib.parse.unquote(str(target_path))
            
            # 2. Collapse multi-slashes and multi-dots (e.g. ....//....//)
            clean_path = re.sub(r"/+", "/", clean_path)
            clean_path = re.sub(r"\.\.+", "..", clean_path)
            
            # 3. Join workspace root with target path
            combined = os.path.join(self.real_workspace_root, clean_path)
            
            # 4. Resolve canonical realpath (follows and resolves all symlinks)
            real_target = os.path.realpath(combined)
            
            # 5. Verify real_target starts with real_workspace_root
            if real_target == self.real_workspace_root or real_target.startswith(self.real_workspace_root + os.sep):
                return True, Path(real_target), ""
            else:
                return False, Path(self.real_workspace_root), f"Security Boundary Violation: Path '{target_path}' (resolving to '{real_target}') escapes workspace '{self.real_workspace_root}'"
        except Exception as e:
            return False, Path(self.real_workspace_root), f"Invalid path specification: {str(e)}"

    def classify_command(self, command: str) -> Tuple[str, str]:
        """Classifies shell command risk level.
        
        Returns:
            ("BLOCKED", reason)
            ("REQUIRE_APPROVAL", reason)
            ("ALLOWED", "")
        """
        cmd_clean = command.strip()
        
        # P0 Forbidden Commands
        forbidden_patterns = [
            r"rm\s+-rf\s+/",
            r"mkfs",
            r"dd\s+if=",
            r":\(\){\s*:\|:&\s*};:",
            r"chmod\s+-R\s+777\s+/",
            r"shutdown",
            r"reboot",
            r"\bsudo\b",
            r"\bsu\b",
            r"cat\s+/etc/passwd",
            r"cat\s+/etc/shadow"
        ]
        
        for pattern in forbidden_patterns:
            if re.search(pattern, cmd_clean, re.IGNORECASE):
                return "BLOCKED", f"Security Policy Error: Command contains forbidden pattern '{pattern}'"
                
        # Command navigation escape checks
        if "cd .." in cmd_clean or "cd /" in cmd_clean or "cd ~" in cmd_clean:
            return "REQUIRE_APPROVAL", "Command involves directory navigation outside workspace boundary."
            
        # High Risk Mutation Commands Requiring User Approval
        approval_keywords = ["rm ", "mv ", "git commit", "git push", "npm install", "pip install", "kill ", "pkill "]
        for kw in approval_keywords:
            if kw in cmd_clean:
                return "REQUIRE_APPROVAL", f"High-risk operation detected: '{kw.strip()}'"
                
        return "ALLOWED", ""
