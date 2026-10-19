import os
import glob
from pathlib import Path
from typing import Optional, List

class DevFileTools:
    def __init__(self, workspace_guard):
        self.guard = workspace_guard

    def read_file(self, path: str, start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
        valid, resolved, err = self.guard.validate_path(path)
        if not valid:
            return f"Error: {err}"
        
        if not resolved.exists():
            return f"Error: File '{path}' does not exist."
            
        try:
            with open(resolved, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
                
            total_lines = len(lines)
            s_idx = max(0, (start_line - 1)) if start_line else 0
            e_idx = min(total_lines, end_line) if end_line else total_lines
            
            selected = lines[s_idx:e_idx]
            formatted = "".join([f"{i + s_idx + 1:4d} | {line}" for i, line in enumerate(selected)])
            return f"File: {path} (Lines {s_idx + 1}-{e_idx} of {total_lines}):\n{formatted}"
        except Exception as e:
            return f"Error reading file '{path}': {str(e)}"

    def write_file(self, path: str, content: str) -> str:
        valid, resolved, err = self.guard.validate_path(path)
        if not valid:
            return f"Error: {err}"
            
        try:
            resolved.parent.mkdir(parents=True, exist_ok=True)
            with open(resolved, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Successfully wrote {len(content)} characters to '{path}'."
        except Exception as e:
            return f"Error writing to file '{path}': {str(e)}"

    def edit_file(self, path: str, target: str, replacement: str) -> str:
        valid, resolved, err = self.guard.validate_path(path)
        if not valid:
            return f"Error: {err}"
            
        if not resolved.exists():
            return f"Error: File '{path}' does not exist."
            
        try:
            with open(resolved, "r", encoding="utf-8") as f:
                content = f.read()
                
            if target not in content:
                return f"Error: Target text segment not found in '{path}'."
                
            new_content = content.replace(target, replacement, 1)
            with open(resolved, "w", encoding="utf-8") as f:
                f.write(new_content)
            return f"Successfully updated '{path}'."
        except Exception as e:
            return f"Error editing file '{path}': {str(e)}"

    def list_directory(self, relative_path: str = ".") -> str:
        valid, resolved, err = self.guard.validate_path(relative_path)
        if not valid:
            return f"Error: {err}"
            
        if not resolved.exists():
            return f"Error: Directory '{relative_path}' does not exist."
            
        try:
            entries = os.listdir(resolved)
            items = []
            for name in sorted(entries):
                if name.startswith(".git"):
                    continue
                p = resolved / name
                kind = "DIR " if p.is_dir() else "FILE"
                items.append(f"{kind}  {name}")
            return f"Directory listing for '{relative_path}':\n" + "\n".join(items)
        except Exception as e:
            return f"Error listing directory '{relative_path}': {str(e)}"

    def search_files(self, query: str = "", relative_path: str = ".", pattern: Optional[str] = None) -> str:
        valid, resolved, err = self.guard.validate_path(relative_path)
        if not valid:
            return f"Error: {err}"
            
        search_term = query or pattern or ""
        results = []
        try:
            # Check if this looks like a filename/glob search rather than text search
            import fnmatch
            is_filename_search = False
            clean_term = search_term.strip()
            if any(c in clean_term for c in "*?[]") or clean_term.endswith(".py") or clean_term.endswith(".txt") or clean_term.endswith(".json") or clean_term == "*":
                is_filename_search = True

            if is_filename_search:
                # Search by filename
                for root, dirs, files in os.walk(resolved):
                    if ".git" in dirs:
                        dirs.remove(".git")
                    if "node_modules" in dirs:
                        dirs.remove("node_modules")
                    if "__pycache__" in dirs:
                        dirs.remove("__pycache__")
                    for file in files:
                        match = False
                        if fnmatch.fnmatch(file.lower(), clean_term.lower()):
                            match = True
                        elif fnmatch.fnmatch(file.lower(), f"*{clean_term.lower()}*"):
                            match = True
                        if match:
                            file_path = Path(root) / file
                            rel = file_path.relative_to(self.guard.workspace_root)
                            results.append(f"File: {rel}")
                if not results:
                    return f"No files matching filename pattern '{search_term}' found."
                return f"Files matching pattern '{search_term}':\n" + "\n".join(results)

            # Standard content text search
            for root, dirs, files in os.walk(resolved):
                if ".git" in dirs:
                    dirs.remove(".git")
                if "node_modules" in dirs:
                    dirs.remove("node_modules")
                if "__pycache__" in dirs:
                    dirs.remove("__pycache__")
                    
                for file in files:
                    file_path = Path(root) / file
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            for idx, line in enumerate(f, 1):
                                if search_term in line:
                                    rel = file_path.relative_to(self.guard.workspace_root)
                                    results.append(f"{rel}:{idx}: {line.strip()}")
                                    if len(results) >= 100:
                                        break
                    except Exception:
                        continue
            if not results:
                return f"No matches found for '{search_term}'."
            return f"Matches for '{search_term}' (up to 100):\n" + "\n".join(results)
        except Exception as e:
            return f"Error searching files: {str(e)}"
