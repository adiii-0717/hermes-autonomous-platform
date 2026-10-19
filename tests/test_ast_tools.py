import os
import tempfile
import unittest
from pathlib import Path
from server.security.workspace_guard import WorkspaceGuard
from server.tools.dev_ast_tools import DevASTTools

class TestASTTools(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root_path = Path(self.temp_dir.name).resolve()
        self.guard = WorkspaceGuard(str(self.root_path))
        self.ast_tools = DevASTTools(self.guard)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_python_ast_analysis(self):
        code = """import os
import sys

class Calculator:
    def add(self, a, b):
        return a + b

    async def async_mult(self, a, b):
        return a * b

def helper_fn():
    pass
"""
        (self.root_path / "calc.py").write_text(code)

        res = self.ast_tools.analyze_ast("calc.py")
        self.assertEqual(res["language"], "Python")
        self.assertEqual(len(res["classes"]), 1)
        self.assertEqual(res["classes"][0]["name"], "Calculator")
        self.assertIn("add", res["classes"][0]["methods"])
        self.assertIn("async_mult", res["classes"][0]["methods"])

    def test_js_ast_analysis(self):
        code = """import React from 'react';

class UserCard extends React.Component {
    render() { return <div>User</div>; }
}

function processUser(id) {
    return id;
}
"""
        (self.root_path / "UserCard.jsx").write_text(code)

        res = self.ast_tools.analyze_ast("UserCard.jsx")
        self.assertEqual(res["language"], "JavaScript/TypeScript")
        self.assertEqual(len(res["classes"]), 1)
        self.assertEqual(res["classes"][0]["name"], "UserCard")

    def test_read_symbol_definition(self):
        code = "def target_func(x, y):\n    return x + y\n"
        (self.root_path / "util.py").write_text(code)

        def_res = self.ast_tools.read_symbol_definition("target_func")
        self.assertIn("target_func", def_res)
        self.assertIn("util.py", def_res)

    def test_find_symbol_references(self):
        (self.root_path / "mod1.py").write_text("def shared_fn(): pass\n")
        (self.root_path / "mod2.py").write_text("from mod1 import shared_fn\nshared_fn()\n")

        ref_res = self.ast_tools.find_symbol_references("shared_fn")
        self.assertIn("mod1.py", ref_res)
        self.assertIn("mod2.py", ref_res)

if __name__ == "__main__":
    unittest.main()
