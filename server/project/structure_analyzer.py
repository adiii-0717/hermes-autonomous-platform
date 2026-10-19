import os
from pathlib import Path
from typing import Dict, Any, List, Optional

class StructureAnalyzer:
    """Generates clean workspace structure trees with intelligent directory exclusions."""

    def __init__(self, workspace_root: Path):
        self.root = Path(workspace_root).resolve()
        self.default_excludes = {
            ".git", "node_modules", "__pycache__", ".venv", "venv",
            "dist", "build", "target", "coverage", ".next", ".nuxt"
        }

    def get_project_structure(self, relative_path: str = ".", max_depth: int = 4) -> str:
        target = (self.root / relative_path).resolve()
        if not target.exists():
            return f"Error: Path '{relative_path}' does not exist."

        lines: List[str] = [f"Workspace Structure: {self.root.name}/"]

        def _build_tree(dir_path: Path, prefix: str = "", depth: int = 0):
            if depth >= max_depth:
                return

            try:
                entries = sorted(os.listdir(dir_path))
            except Exception as e:
                lines.append(f"{prefix}└── [Error reading dir: {e}]")
                return

            visible_entries = [e for e in entries if e not in self.default_excludes and not e.startswith(".project_manifest")]
            count = len(visible_entries)

            for idx, name in enumerate(visible_entries):
                is_last = (idx == count - 1)
                connector = "└── " if is_last else "├── "
                child_prefix = "    " if is_last else "│   "

                child_path = dir_path / name
                if child_path.is_dir():
                    lines.append(f"{prefix}{connector}{name}/")
                    _build_tree(child_path, prefix + child_prefix, depth + 1)
                else:
                    lines.append(f"{prefix}{connector}{name}")

        _build_tree(target)
        return "\n".join(lines)
