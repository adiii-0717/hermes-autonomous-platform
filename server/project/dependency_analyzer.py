import os
import json
from pathlib import Path
from typing import Dict, Any, List

class DependencyAnalyzer:
    """Analyzes declared and installed dependencies prior to package installation."""

    def __init__(self, workspace_root: Path):
        self.root = Path(workspace_root).resolve()

    def get_declared_dependencies(self) -> Dict[str, Any]:
        dependencies: Dict[str, List[str]] = {
            "python": [],
            "javascript": []
        }

        # Check Python requirements.txt
        req_file = self.root / "requirements.txt"
        if req_file.exists():
            try:
                lines = req_file.read_text(encoding="utf-8").splitlines()
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        pkg = line.split("==")[0].split(">=")[0].split("<=")[0].strip()
                        dependencies["python"].append(pkg)
            except Exception:
                pass

        # Check JS package.json
        pkg_json = self.root / "package.json"
        if pkg_json.exists():
            try:
                data = json.loads(pkg_json.read_text(encoding="utf-8"))
                deps = list({**data.get("dependencies", {}), **data.get("devDependencies", {})}.keys())
                dependencies["javascript"] = deps
            except Exception:
                pass

        return dependencies

    def is_dependency_installed(self, package_name: str, language: str = "python") -> bool:
        deps = self.get_declared_dependencies()
        pkg_lower = package_name.lower()
        if language.lower() in ["python", "py"]:
            return any(d.lower() == pkg_lower for d in deps["python"])
        elif language.lower() in ["javascript", "js", "typescript", "ts"]:
            return any(d.lower() == pkg_lower for d in deps["javascript"])
        return False
