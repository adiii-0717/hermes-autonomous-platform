import unittest
import shutil
from pathlib import Path
from server.security.workspace_guard import WorkspaceGuard
from server.tools.dev_visual_qa_tools import DevVisualQATools

class TestMilestone2VisualQATools(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path('workspace/test_visual_qa_project')
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.guard = WorkspaceGuard(Path.cwd())
        self.tools = DevVisualQATools(self.guard)

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_technical_qa_web_project(self):
        html_file = self.test_dir / 'index.html'
        css_file = self.test_dir / 'style.css'

        html_file.write_text('<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><link rel="stylesheet" href="style.css"></head><body><h1>Test</h1></body></html>')
        css_file.write_text(':root { --bg-primary: #ffffff; } button:hover { opacity: 0.8; } @import url("https://fonts.googleapis.com/css2?family=Inter");')

        res = self.tools.run_technical_visual_qa('test_visual_qa_project')
        self.assertTrue(res['passed'])
        self.assertTrue(res['is_web_project'])
        self.assertTrue(res['viewport_configured'])
        self.assertTrue(res['css_tokens_found'])
        self.assertTrue(res['interactive_states_found'])

    def test_technical_qa_non_web_project(self):
        py_file = self.test_dir / 'script.py'
        py_file.write_text('print("Hello CLI")')

        res = self.tools.run_technical_visual_qa('test_visual_qa_project')
        self.assertTrue(res['passed'])
        self.assertFalse(res['is_web_project'])

    def test_screenshot_capture(self):
        html_file = self.test_dir / 'index.html'
        html_file.write_text('<!DOCTYPE html><html><head><title>Test</title></head><body><h1>Hello World</h1></body></html>')
        res = self.tools.capture_responsive_screenshots('test_visual_qa_project')
        self.assertTrue(res['success'])
        self.assertTrue(Path(self.test_dir / '.visual_qa' / 'desktop.png').exists())
        self.assertTrue(Path(self.test_dir / '.visual_qa' / 'mobile.png').exists())

    def test_honest_status_separation(self):
        res = self.tools.run_full_visual_qa('test_visual_qa_project', model_config={'provider': 'ollama'})
        self.assertIn('technical_qa', res)
        self.assertIn('evaluated', res)
        self.assertFalse(res['evaluated']) # Ollama without vision returns evaluated: False honestly

if __name__ == '__main__':
    unittest.main()
