from typing import Dict, Any
from server.project.project_analyzer import ProjectAnalyzer
from server.tools.dev_testing_tools import DevTestingTools
from server.tools.dev_git_tools import DevGitTools

class DevHealthTools:
    def __init__(self, workspace_guard):
        self.guard = workspace_guard
        self.analyzer = ProjectAnalyzer(self.guard.workspace_root)
        self.testing_tools = DevTestingTools(self.guard)
        self.git_tools = DevGitTools(self.guard)

    def check_project_health(self) -> Dict[str, Any]:
        """Runs a comprehensive health check across build, tests, linting, git, and manifest."""
        manifest = self.analyzer.generate_manifest()
        
        # Test health
        test_res = self.testing_tools.run_tests()
        
        # Lint health
        lint_res = self.testing_tools.run_linter()
        
        # Build health
        build_res = self.testing_tools.run_build()

        # Git health
        git_stat = self.git_tools.git_status()

        return {
            "project_name": manifest["name"],
            "languages": manifest["languages"],
            "frameworks": manifest["frameworks"],
            "build_healthy": build_res.get("success", False),
            "tests_healthy": test_res.get("success", False),
            "lint_healthy": lint_res.get("success", False),
            "git_status_preview": str(git_stat)[:300],
            "details": {
                "build": build_res,
                "tests": test_res,
                "lint": lint_res
            }
        }
