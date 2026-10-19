import subprocess
from typing import Dict, Any, List

class DevReviewTools:
    def __init__(self, workspace_guard):
        self.guard = workspace_guard

    def review_changes(self) -> Dict[str, Any]:
        """Analyzes uncommitted workspace diffs for security issues, missing tests, and potential bugs."""
        try:
            res = subprocess.run(
                "git diff",
                shell=True,
                cwd=str(self.guard.workspace_root),
                capture_output=True,
                text=True,
                timeout=15
            )
            diff_text = res.stdout or ""
            
            if not diff_text.strip():
                return {
                    "has_changes": False,
                    "summary": "No uncommitted git changes found to review.",
                    "findings": []
                }

            findings: List[str] = []
            
            # Static check patterns
            if "api_key" in diff_text.lower() or "secret" in diff_text.lower() or "password" in diff_text.lower():
                findings.append("SECURITY WARNING: Potential hardcoded secret or API key detected in git diff!")
            if "eval(" in diff_text or "exec(" in diff_text:
                findings.append("SECURITY WARNING: Dynamic evaluation (`eval` / `exec`) introduced in changes.")
            if "print(" in diff_text or "console.log(" in diff_text:
                findings.append("CODE QUALITY: Debug logging statements (`print` / `console.log`) present in diff.")
                
            modified_files = [line.split("b/")[-1] for line in diff_text.splitlines() if line.startswith("+++ b/")]
            has_tests = any("test" in f.lower() for f in modified_files)
            if modified_files and not has_tests:
                findings.append("TEST COVERAGE: Code modified without corresponding test file updates.")

            return {
                "has_changes": True,
                "modified_files": modified_files,
                "summary": f"Reviewed {len(modified_files)} modified file(s). Found {len(findings)} review note(s).",
                "findings": findings,
                "raw_diff_preview": diff_text[:1500]
            }
        except Exception as e:
            return {"error": f"Error performing code review: {str(e)}"}
