import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List

class DevTestingTools:
    def __init__(self, workspace_guard):
        self.guard = workspace_guard

    def run_tests(self, test_runner: Optional[str] = None) -> Dict[str, Any]:
        """Runs unit/integration test suite."""
        if not test_runner:
            if (self.guard.workspace_root / "pytest.ini").exists() or any(self.guard.workspace_root.rglob("test_*.py")):
                test_runner = "python3 -m unittest discover -s ."
            elif (self.guard.workspace_root / "package.json").exists():
                test_runner = "npm test"
            else:
                test_runner = "python3 -m unittest discover"

        risk_level, err_msg = self.guard.classify_command(test_runner)
        if risk_level == "BLOCKED":
            return {"success": False, "exit_code": -1, "stdout": "", "stderr": err_msg}

        try:
            res = subprocess.run(
                test_runner,
                shell=True,
                cwd=str(self.guard.workspace_root),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            classification = self.classify_test_failure(res.stderr, res.stdout) if res.returncode != 0 else "NONE"
            
            return {
                "success": res.returncode == 0,
                "exit_code": res.returncode,
                "stdout": res.stdout or "",
                "stderr": res.stderr or "",
                "failure_classification": classification
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "exit_code": -1, "stdout": "", "stderr": "Test execution timed out after 60s."}
        except Exception as e:
            return {"success": False, "exit_code": -1, "stdout": "", "stderr": str(e)}

    def run_linter(self, linter_cmd: Optional[str] = None) -> Dict[str, Any]:
        """Runs linter command on workspace."""
        if not linter_cmd:
            if (self.guard.workspace_root / "package.json").exists():
                linter_cmd = "npm run lint"
            else:
                linter_cmd = "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics"

        try:
            res = subprocess.run(
                linter_cmd,
                shell=True,
                cwd=str(self.guard.workspace_root),
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "success": res.returncode == 0,
                "exit_code": res.returncode,
                "stdout": res.stdout or "",
                "stderr": res.stderr or ""
            }
        except Exception as e:
            return {"success": False, "exit_code": -1, "stdout": "", "stderr": str(e)}

    def run_build(self, build_cmd: Optional[str] = None) -> Dict[str, Any]:
        """Runs build command on workspace."""
        if not build_cmd:
            if (self.guard.workspace_root / "package.json").exists():
                build_cmd = "npm run build"
            else:
                build_cmd = "python3 -m py_compile *.py"

        try:
            res = subprocess.run(
                build_cmd,
                shell=True,
                cwd=str(self.guard.workspace_root),
                capture_output=True,
                text=True,
                timeout=60
            )
            return {
                "success": res.returncode == 0,
                "exit_code": res.returncode,
                "stdout": res.stdout or "",
                "stderr": res.stderr or ""
            }
        except Exception as e:
            return {"success": False, "exit_code": -1, "stdout": "", "stderr": str(e)}

    def find_related_tests(self, target_file: str) -> List[str]:
        """Finds candidate test files associated with a target source file."""
        target_name = Path(target_file).stem.lower()
        candidates = []
        
        for path in self.guard.workspace_root.rglob("*"):
            if any(part in path.parts for part in [".git", "node_modules", "__pycache__", ".venv", "venv"]):
                continue
            if path.is_file() and ("test_" in path.name.lower() or "_test" in path.name.lower() or ".test." in path.name.lower()):
                if target_name in path.name.lower():
                    candidates.append(str(path.relative_to(self.guard.workspace_root)))
                    
        return candidates

    def classify_test_failure(self, stderr: str, stdout: str) -> str:
        """Classifies test failures into CODE_ERROR, TEST_ERROR, DEPENDENCY_ERROR, ENVIRONMENT_ERROR, or CONFIGURATION_ERROR."""
        text = (stderr + "\n" + stdout).lower()
        
        if "modulenotfounderror" in text or "cannot find module" in text or "importError" in text:
            return "DEPENDENCY_ERROR"
        elif "syntaxerror" in text or "indentationerror" in text or "nameerror" in text or "typeerror" in text:
            return "CODE_ERROR"
        elif "assertionerror" in text or "failed:" in text or "assert" in text:
            return "TEST_ERROR"
        elif "permission" in text or "eacces" in text or "connection refused" in text:
            return "ENVIRONMENT_ERROR"
        elif "config" in text or "invalid option" in text:
            return "CONFIGURATION_ERROR"
        return "UNKNOWN"
