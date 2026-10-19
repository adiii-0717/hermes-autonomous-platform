import ast
import re
from pathlib import Path
from typing import Optional, Dict, Any, List

class DevASTTools:
    def __init__(self, workspace_guard):
        self.guard = workspace_guard

    def analyze_ast(self, file_path: str) -> Dict[str, Any]:
        valid, resolved, err = self.guard.validate_path(file_path)
        if not valid:
            return {"error": err}

        if not resolved.exists():
            return {"error": f"File '{file_path}' not found."}

        suffix = resolved.suffix.lower()
        if suffix in [".py"]:
            return self._analyze_python_ast(resolved, file_path)
        elif suffix in [".js", ".jsx", ".ts", ".tsx"]:
            return self._analyze_js_ast(resolved, file_path)
        else:
            return {"error": f"AST analysis not supported for extension '{suffix}'."}

    def _analyze_python_ast(self, resolved: Path, rel_path: str) -> Dict[str, Any]:
        try:
            source = resolved.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source, filename=str(resolved))

            classes = []
            functions = []
            imports = []

            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                    classes.append({
                        "name": node.name,
                        "line": node.lineno,
                        "methods": methods
                    })
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions.append({
                        "name": node.name,
                        "line": node.lineno,
                        "is_async": isinstance(node, ast.AsyncFunctionDef)
                    })
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")

            return {
                "file": rel_path,
                "language": "Python",
                "classes": classes,
                "functions": functions,
                "imports": imports
            }
        except Exception as e:
            return {"file": rel_path, "error": f"Python AST parse error: {str(e)}"}

    def _analyze_js_ast(self, resolved: Path, rel_path: str) -> Dict[str, Any]:
        try:
            source = resolved.read_text(encoding="utf-8", errors="replace")
            classes = []
            functions = []
            imports = []

            class_matches = re.findall(r"class\s+([A-Za-z0-9_]+)", source)
            for cls in class_matches:
                classes.append({"name": cls})

            fn_matches = re.findall(r"(?:function\s+([A-Za-z0-9_]+)|const\s+([A-Za-z0-9_]+)\s*=\s*(?:async\s*)?\(|export\s+default\s+function\s+([A-Za-z0-9_]+))", source)
            for match in fn_matches:
                fn_name = next((m for m in match if m), "")
                if fn_name:
                    functions.append({"name": fn_name})

            import_matches = re.findall(r"import\s+.*?from\s+['\"](.*?)['\"]", source)
            imports.extend(import_matches)

            return {
                "file": rel_path,
                "language": "JavaScript/TypeScript",
                "classes": classes,
                "functions": functions,
                "imports": imports
            }
        except Exception as e:
            return {"file": rel_path, "error": f"JS AST parse error: {str(e)}"}

    def read_symbol_definition(self, symbol_name: str, file_path: Optional[str] = None) -> str:
        if file_path:
            valid, resolved, err = self.guard.validate_path(file_path)
            if not valid:
                return f"Error: {err}"
            files_to_search = [resolved]
        else:
            files_to_search = list(self.guard.workspace_root.rglob("*.py")) + list(self.guard.workspace_root.rglob("*.js")) + list(self.guard.workspace_root.rglob("*.jsx")) + list(self.guard.workspace_root.rglob("*.ts")) + list(self.guard.workspace_root.rglob("*.tsx"))

        for path in files_to_search:
            if any(part in path.parts for part in [".git", "node_modules", "__pycache__", ".venv", "venv"]):
                continue
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
                lines = content.splitlines()

                for idx, line in enumerate(lines):
                    if f"def {symbol_name}" in line or f"class {symbol_name}" in line or f"const {symbol_name}" in line or f"function {symbol_name}" in line:
                        start = max(0, idx - 2)
                        end = min(len(lines), idx + 35)
                        snippet = "\n".join([f"{i+1:4d} | {lines[i]}" for i in range(start, end)])
                        rel = path.relative_to(self.guard.workspace_root)
                        return f"Symbol '{symbol_name}' found in {rel} (Lines {start+1}-{end}):\n{snippet}"
            except Exception:
                continue

        return f"Symbol '{symbol_name}' definition not found in workspace."

    def find_symbol_references(self, symbol_name: str) -> str:
        results = []
        for path in self.guard.workspace_root.rglob("*"):
            if any(part in path.parts for part in [".git", "node_modules", "__pycache__", ".venv", "venv", "dist"]):
                continue
            if path.is_file() and path.suffix in [".py", ".js", ".jsx", ".ts", ".tsx"]:
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        for idx, line in enumerate(f, 1):
                            if symbol_name in line:
                                rel = path.relative_to(self.guard.workspace_root)
                                results.append(f"{rel}:{idx}: {line.strip()}")
                                if len(results) >= 50:
                                    break
                except Exception:
                    continue

        if not results:
            return f"No references found for symbol '{symbol_name}'."
        return f"Symbol '{symbol_name}' references (up to 50):\n" + "\n".join(results)

    def analyze_change_impact(self, symbol_name: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Analyzes impact of changing a symbol/class across workspace modules, services, controllers, and tests."""
        affected_files = []
        affected_tests = []
        
        for path in self.guard.workspace_root.rglob("*"):
            if any(part in path.parts for part in [".git", "node_modules", "__pycache__", ".venv", "venv", "dist"]):
                continue
            if path.is_file() and path.suffix in [".py", ".js", ".jsx", ".ts", ".tsx"]:
                try:
                    content = path.read_text(encoding="utf-8", errors="ignore")
                    if symbol_name in content:
                        rel = str(path.relative_to(self.guard.workspace_root))
                        if "test" in rel.lower():
                            affected_tests.append(rel)
                        else:
                            affected_files.append(rel)
                except Exception:
                    continue

        return {
            "target_symbol": symbol_name,
            "target_file": file_path,
            "impact_summary": f"Changing symbol '{symbol_name}' impacts {len(affected_files)} source file(s) and {len(affected_tests)} test file(s).",
            "affected_source_files": affected_files,
            "affected_test_files": affected_tests
        }
