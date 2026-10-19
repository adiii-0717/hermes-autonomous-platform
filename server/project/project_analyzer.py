import os
import json
from pathlib import Path
from typing import Dict, Any, List
from server.project.project_detector import ProjectDetector

class ProjectAnalyzer:
    """Generates structured Project Manifests for the workspace."""

    def __init__(self, workspace_root: Path):
        self.root = Path(workspace_root).resolve()
        self.detector = ProjectDetector(self.root)

    def generate_manifest(self) -> Dict[str, Any]:
        languages = self.detector.detect_languages()
        frameworks = self.detector.detect_frameworks()
        package_managers = self.detector.detect_package_managers()
        databases = self.detector.detect_databases()
        test_frameworks = self.detector.detect_test_frameworks()

        entry_points: List[str] = []
        for candidate in ["app.py", "main.py", "server.py", "index.js", "src/index.js", "src/main.jsx", "src/App.jsx"]:
            if (self.root / candidate).exists():
                entry_points.append(candidate)

        config_files: List[str] = []
        for candidate in ["package.json", "pyproject.toml", "requirements.txt", "vite.config.js", "pytest.ini", "tsconfig.json", "AGENTS.md"]:
            if (self.root / candidate).exists():
                config_files.append(candidate)

        manifest = {
            "project_id": self.root.name,
            "name": self.root.name,
            "languages": languages,
            "frameworks": frameworks,
            "package_managers": package_managers,
            "databases": databases,
            "test_frameworks": test_frameworks,
            "entry_points": entry_points,
            "configuration_files": config_files,
            "workspace_root": str(self.root),
            "git_repository": (self.root / ".git").exists()
        }

        # Save project_manifest.json in workspace
        try:
            manifest_file = self.root / ".project_manifest.json"
            with open(manifest_file, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)
        except Exception:
            pass

        return manifest
