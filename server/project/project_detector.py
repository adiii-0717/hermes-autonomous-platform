import os
import json
from pathlib import Path
from typing import Dict, List, Set, Any

class ProjectDetector:
    """Detects languages, frameworks, package managers, databases, and testing tools in a workspace."""

    def __init__(self, workspace_root: Path):
        self.root = Path(workspace_root).resolve()

    def detect_languages(self) -> List[str]:
        languages: Set[str] = set()
        ext_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".jsx": "JavaScript",
            ".ts": "TypeScript",
            ".tsx": "TypeScript",
            ".go": "Go",
            ".rs": "Rust",
            ".java": "Java",
            ".php": "PHP",
            ".c": "C",
            ".cpp": "C++",
            ".h": "C/C++ Header"
        }

        for p in self.root.rglob("*"):
            if any(part in p.parts for part in [".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"]):
                continue
            if p.is_file() and p.suffix in ext_map:
                languages.add(ext_map[p.suffix])
                if len(languages) >= 6:
                    break

        return sorted(list(languages))

    def detect_frameworks(self) -> List[str]:
        frameworks: Set[str] = set()

        pyproject = self.root / "pyproject.toml"
        requirements = self.root / "requirements.txt"
        
        req_text = ""
        if requirements.exists():
            try:
                req_text += requirements.read_text(encoding="utf-8", errors="ignore").lower()
            except Exception:
                pass
        if pyproject.exists():
            try:
                req_text += pyproject.read_text(encoding="utf-8", errors="ignore").lower()
            except Exception:
                pass

        if "fastapi" in req_text:
            frameworks.add("FastAPI")
        if "django" in req_text:
            frameworks.add("Django")
        if "flask" in req_text:
            frameworks.add("Flask")

        pkg_json = self.root / "package.json"
        if pkg_json.exists():
            try:
                data = json.loads(pkg_json.read_text(encoding="utf-8"))
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                if "react" in deps:
                    frameworks.add("React")
                if "next" in deps:
                    frameworks.add("Next.js")
                if "express" in deps:
                    frameworks.add("Express")
                if "@nestjs/core" in deps:
                    frameworks.add("NestJS")
                if "vue" in deps:
                    frameworks.add("Vue")
            except Exception:
                pass

        return sorted(list(frameworks))

    def detect_package_managers(self) -> List[str]:
        managers: Set[str] = set()

        if (self.root / "package-lock.json").exists() or (self.root / "package.json").exists():
            managers.add("npm")
        if (self.root / "pnpm-lock.yaml").exists():
            managers.add("pnpm")
        if (self.root / "yarn.lock").exists():
            managers.add("yarn")
        if (self.root / "requirements.txt").exists() or (self.root / "setup.py").exists():
            managers.add("pip")
        if (self.root / "uv.lock").exists():
            managers.add("uv")
        if (self.root / "poetry.lock").exists():
            managers.add("poetry")
        if (self.root / "Cargo.toml").exists():
            managers.add("cargo")
        if (self.root / "pom.xml").exists():
            managers.add("maven")
        if (self.root / "build.gradle").exists():
            managers.add("gradle")
        if (self.root / "go.mod").exists():
            managers.add("go")

        return sorted(list(managers))

    def detect_databases(self) -> List[str]:
        databases: Set[str] = set()

        all_text = ""
        for fname in ["requirements.txt", "pyproject.toml", "package.json"]:
            fpath = self.root / fname
            if fpath.exists():
                try:
                    all_text += fpath.read_text(encoding="utf-8", errors="ignore").lower()
                except Exception:
                    pass

        if "psycopg" in all_text or "postgresql" in all_text or "asyncpg" in all_text or "pg" in all_text:
            databases.add("PostgreSQL")
        if "mysql" in all_text or "aiomysql" in all_text:
            databases.add("MySQL")
        if "sqlite" in all_text or "sqlite3" in all_text:
            databases.add("SQLite")
        if "mongodb" in all_text or "mongoose" in all_text or "pymongo" in all_text:
            databases.add("MongoDB")
        if "redis" in all_text or "ioredis" in all_text:
            databases.add("Redis")

        return sorted(list(databases))

    def detect_test_frameworks(self) -> List[str]:
        test_tools: Set[str] = set()

        if (self.root / "pytest.ini").exists() or any(self.root.rglob("test_*.py")):
            test_tools.add("pytest")
        if (self.root / "package.json").exists():
            try:
                data = json.loads((self.root / "package.json").read_text(encoding="utf-8"))
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                if "jest" in deps:
                    test_tools.add("Jest")
                if "vitest" in deps:
                    test_tools.add("Vitest")
            except Exception:
                pass
        if (self.root / "pom.xml").exists() or (self.root / "build.gradle").exists():
            test_tools.add("JUnit")

        return sorted(list(test_tools))
