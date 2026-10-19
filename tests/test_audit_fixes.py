import os
import sys
import shutil
import tempfile
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from server.hermes_adapter import is_web_frontend_project, HermesAgentAdapter
from server.tools.component_discovery import ComponentDiscoveryCatalog
from server.tools.product_intent_classifier import ProductIntentClassifier
from server.agents.creative_director_agent import CreativeDirectorAgent
from server.agents.visual_qa_inspector_agent import VisualQAInspectorAgent
from server.agents.schemas import AgentContext
from server.security.workspace_guard import WorkspaceGuard


def test_routing_web_frontend_project():
    """Validates Priority 1: Web-project detection handles React, JSX, HTML, JS, TS, and excludes backend/continuations."""
    print("Running test_routing_web_frontend_project...")

    # 1. React, JSX, TSX variations must enter web orchestrator
    assert is_web_frontend_project("react", "Build a customer dashboard") is True
    assert is_web_frontend_project("React", "Build a customer dashboard") is True
    assert is_web_frontend_project("jsx", "Create a product landing page") is True
    assert is_web_frontend_project("tsx", "Build an analytics panel") is True
    assert is_web_frontend_project("reactjs", "Build a storefront") is True

    # 2. Standard web languages must enter web orchestrator
    assert is_web_frontend_project("html", "Create a landing page") is True
    assert is_web_frontend_project("javascript", "Build an interactive widget") is True
    assert is_web_frontend_project("typescript", "Build a web app") is True
    assert is_web_frontend_project("web", "Build a website") is True
    assert is_web_frontend_project("vue", "Build a dashboard") is True
    assert is_web_frontend_project("nextjs", "Build an e-commerce site") is True

    # 3. Backend-only languages must NOT enter web orchestrator
    assert is_web_frontend_project("python", "Create a data pipeline") is False
    assert is_web_frontend_project("Python", "Build a CLI tool") is False
    assert is_web_frontend_project("py", "Build a scraper") is False
    assert is_web_frontend_project("golang", "Build a microservice") is False
    assert is_web_frontend_project("go", "Create a concurrent worker") is False
    assert is_web_frontend_project("rust", "Create a high-speed parser") is False
    assert is_web_frontend_project("c", "Write a memory allocator") is False
    assert is_web_frontend_project("cpp", "Build a game engine backend") is False
    assert is_web_frontend_project("fastapi", "Create a REST API") is False

    # 4. Language None / empty: Inspect prompt keywords
    assert is_web_frontend_project(None, "Build a React website with 3D shoes") is True
    assert is_web_frontend_project(None, "Create a modern landing page for an AI studio") is True
    assert is_web_frontend_project(None, "Develop an interactive web storefront") is True
    assert is_web_frontend_project(None, "Write a Python CLI calculator with argparse") is False
    assert is_web_frontend_project(None, "Build a backend REST API with SQLite database") is False
    assert is_web_frontend_project(None, "Create a terminal command line tool in Go") is False

    # 5. Continuations must NOT enter web orchestrator (preserves interactive file modification)
    assert is_web_frontend_project("react", "Add checkout button", is_continuation=True) is False
    assert is_web_frontend_project("html", "Fix CSS layout bug", is_continuation=True) is False
    assert is_web_frontend_project(None, "Update README.md", is_continuation=True) is False

    print("✓ test_routing_web_frontend_project PASSED")


def test_skill_delivery_untruncated_and_targeted():
    """Validates Priority 2: Complete skill loading without 1,000-char truncation, delivering real React Bits APIs."""
    print("Running test_skill_delivery_untruncated_and_targeted...")

    tmp_dir = Path(tempfile.mkdtemp())
    try:
        adapter = HermesAgentAdapter(str(tmp_dir), model_config={"provider": "ollama"})

        guidelines = adapter._get_ui_ux_design_guidelines("Build a React luxury fashion boutique called Velour")

        # 1. Must NOT be truncated to 1,000 characters
        assert len(guidelines) > 5000, f"Guidelines length {len(guidelines)} is unexpectedly short; check truncation!"

        # 2. Master skills must be delivered with complete substantive sections
        assert "[ANTHROPIC FRONTEND DESIGN SPECIFICATION]" in guidelines
        assert "The Anti-Slop Check (Banned Clichés)" in guidelines
        assert "Spend boldness in one place" in guidelines

        assert "[UI/UX PRO MAX SPECIFICATION]" in guidelines
        assert "8pt Spatial Spacing System" in guidelines
        assert "Accessibility Quality Gates (WCAG AA/AAA)" in guidelines

        assert "[VERCEL WEB DESIGN & REACT SPECIFICATION]" in guidelines
        assert "Tabular Numbers" in guidelines
        assert "Eliminating Data Waterfalls" in guidelines

        assert "[UI.SH DESIGN ENGINEERING SPECIFICATION]" in guidelines
        assert "Hierarchy with Weight & Color Contrast" in guidelines
        assert "Hairline Borders & Rings Over Muddy Box Shadows" in guidelines

        # 3. Authentic React Bits specification with real component documentation
        assert "[AUTHENTIC REACT BITS ARCHITECTURE SPECIFICATION" in guidelines
        assert "\"framer-motion\":" in guidelines
        assert "\"lucide-react\":" in guidelines
        assert "SpotlightCard" in guidelines or "TiltedCard" in guidelines
        assert "ZERO-EMOJI RULE" in guidelines

        # 4. Check targeted component catalog retrieval directly
        catalog = ComponentDiscoveryCatalog()
        targeted_specs = catalog.get_targeted_component_specs("Build a high-performance distributed streaming dashboard")
        assert "Squares" in targeted_specs or "DecryptedText" in targeted_specs
        assert "code_sample" not in targeted_specs  # formatted code block, not raw dict key
        assert "```jsx" in targeted_specs
        assert "package.json" in targeted_specs

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    print("✓ test_skill_delivery_untruncated_and_targeted PASSED")


def test_boilerplate_protection():
    """Validates Priority 4: Legacy boilerplate trap is eradicated, protects React/Vite and backend projects."""
    print("Running test_boilerplate_protection...")

    classifier = ProductIntentClassifier()

    # 1. Boilerplate must have ZERO emojis
    b_html, b_css, b_js, _, _ = classifier.generate_domain_boilerplate("Create a sneaker store", "Aura Shoes")
    assert "👟" not in b_html, "Found emoji 👟 in boilerplate HTML!"
    assert "🛒" not in b_html, "Found emoji 🛒 in boilerplate HTML!"
    assert "🏀" not in b_js, "Found emoji 🏀 in boilerplate JS!"
    assert "👟" not in b_js, "Found emoji 👟 in boilerplate JS!"

    dash_html, _, _, _, _ = classifier.generate_domain_boilerplate("Create student dashboard", "Nexus")
    assert "📊" not in dash_html, "Found emoji 📊 in dashboard boilerplate HTML!"

    # 2. Protection against contaminating React / Vite projects
    tmp_react = Path(tempfile.mkdtemp())
    try:
        adapter = HermesAgentAdapter(str(tmp_react), model_config={"provider": "ollama"})

        # Simulate a React project with package.json and src/App.jsx
        (tmp_react / "package.json").write_text('{"name": "my-react-app", "dependencies": {"react": "^18.3.1"}}')
        src_dir = tmp_react / "src"
        src_dir.mkdir(parents=True)
        (src_dir / "App.jsx").write_text("export default function App() { return <div>React App</div>; }")

        # Run boilerplate check
        adapter._ensure_web_app_boilerplate("Build a React store")

        # Must NOT generate static app.js or vanilla style.css
        assert not (tmp_react / "app.js").exists(), "Contaminated React project with static app.js!"
        assert not (tmp_react / "style.css").exists(), "Contaminated React project with static style.css!"

    finally:
        shutil.rmtree(tmp_react, ignore_errors=True)

    # 3. Protection against contaminating backend projects
    tmp_backend = Path(tempfile.mkdtemp())
    try:
        adapter = HermesAgentAdapter(str(tmp_backend), model_config={"provider": "ollama"})

        # Simulate a Python backend project
        (tmp_backend / "server.py").write_text("print('Python API Server')")

        adapter._ensure_web_app_boilerplate("Build a Python backend service")

        assert not (tmp_backend / "index.html").exists(), "Contaminated Python project with index.html!"
        assert not (tmp_backend / "style.css").exists(), "Contaminated Python project with style.css!"
        assert not (tmp_backend / "app.js").exists(), "Contaminated Python project with app.js!"

    finally:
        shutil.rmtree(tmp_backend, ignore_errors=True)

    print("✓ test_boilerplate_protection PASSED")


def test_visual_qa_enforcement_and_gates():
    """Validates Priority 3: Server enforces visual inspection and blocks blank pages or fatal runtime errors."""
    print("Running test_visual_qa_enforcement_and_gates...")

    tmp_dir = Path(tempfile.mkdtemp())
    try:
        guard = WorkspaceGuard(str(tmp_dir))
        qa_agent = VisualQAInspectorAgent(guard)

        context = AgentContext(
            project_name="test_proj",
            user_prompt="Build a React storefront",
            workspace_root=str(tmp_dir),
            max_refinement_cycles=3
        )
        context.attempt_number = 1

        # Test Case 1: Blank page defect detected
        blank_screenshot_res = {
            "success": False,
            "visual_inspection_executed": True,
            "blank_page_detected": True,
            "has_fatal_runtime_error": False,
            "desktop": None,
            "mobile": None,
            "console_errors": []
        }
        report_blank = qa_agent.run(context, screenshot_result=blank_screenshot_res)
        assert report_blank["decision"] in ["NEEDS_REFINEMENT", "NEEDS_RETRY"], f"Unexpected decision {report_blank['decision']}"
        assert any("BLANK PAGE" in issue for issue in report_blank["critical_issues"])

        # Test Case 2: Max attempts reached on blank page -> MUST BE BLOCKED
        context.attempt_number = 3
        report_blocked = qa_agent.run(context, screenshot_result=blank_screenshot_res)
        assert report_blocked["decision"] == "BLOCKED", f"Expected BLOCKED on attempt 3, got {report_blocked['decision']}"

        # Test Case 3: Fatal runtime errors in console
        context.attempt_number = 1
        fatal_screenshot_res = {
            "success": False,
            "visual_inspection_executed": True,
            "blank_page_detected": False,
            "has_fatal_runtime_error": True,
            "desktop": None,
            "mobile": None,
            "console_errors": ["Uncaught TypeError: Cannot read property 'map' of undefined at App.jsx:42"]
        }
        report_fatal = qa_agent.run(context, screenshot_result=fatal_screenshot_res)
        assert report_fatal["decision"] in ["NEEDS_REFINEMENT", "NEEDS_RETRY"]
        assert any("FATAL RUNTIME ERROR" in issue for issue in report_fatal["critical_issues"])

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    print("✓ test_visual_qa_enforcement_and_gates PASSED")


def test_creative_director_variety_and_anti_patterns():
    """Validates Priority 5: Creative Director formulates project-specific directions without default purple templates."""
    print("Running test_creative_director_variety_and_anti_patterns...")

    cd = CreativeDirectorAgent()

    # 1. Test deterministic domain baseline directions
    ctx_fashion = AgentContext(project_name="velour_store", user_prompt="Editorial haute couture fashion boutique", workspace_root="/tmp")
    fallback_fashion = cd.get_fallback_output(ctx_fashion, "test")
    assert fallback_fashion["color_tokens"]["accent_primary"] == "#4A1525"
    assert fallback_fashion["color_tokens"]["bg_primary"] == "#FDFBF7"

    ctx_food = AgentContext(project_name="osteria_terra", user_prompt="Artisanal dining and farm to table restaurant", workspace_root="/tmp")
    fallback_food = cd.get_fallback_output(ctx_food, "test")
    assert fallback_food["color_tokens"]["accent_primary"] == "#283618"
    assert fallback_food["color_tokens"]["bg_primary"] == "#F6F4EE"

    ctx_agency = AgentContext(project_name="nexus_arch", user_prompt="High contrast architectural studio and creative portfolio", workspace_root="/tmp")
    fallback_agency = cd.get_fallback_output(ctx_agency, "test")
    assert fallback_agency["color_tokens"]["accent_primary"] == "#1E40AF"
    assert fallback_agency["color_tokens"]["bg_primary"] == "#0A0A0C"

    ctx_stream = AgentContext(project_name="vortex_stream", user_prompt="Distributed streaming engine telemetry devtool", workspace_root="/tmp")
    fallback_stream = cd.get_fallback_output(ctx_stream, "test")
    assert fallback_stream["color_tokens"]["accent_primary"] == "#38bdf8"

    # 2. Test live run() outputs ensure diversity and zero banned clichés
    res_fashion = cd.run(ctx_fashion)
    res_food = cd.run(ctx_food)
    res_agency = cd.run(ctx_agency)
    res_gen = cd.run(AgentContext(project_name="modern_project", user_prompt="Build a clean modern business tool", workspace_root="/tmp"))

    fashion_accent = res_fashion["color_tokens"]["accent_primary"].lower()
    food_accent = res_food["color_tokens"]["accent_primary"].lower()
    agency_accent = res_agency["color_tokens"]["accent_primary"].lower()
    gen_accent = res_gen["color_tokens"]["accent_primary"].lower()

    # Verify colors across domains are varied and not all identical
    distinct_accents = {fashion_accent, food_accent, agency_accent}
    assert len(distinct_accents) >= 2, f"Expected varied color accents across domains, got {distinct_accents}"

    # Verify default / generic fallback must NOT use generic purple (#4F46E5 / #6366F1)
    banned_purples = ["#4f46e5", "#6366f1"]
    for accent in [fashion_accent, food_accent, agency_accent, gen_accent]:
        assert accent not in banned_purples, f"Banned purple cliché {accent} found in creative director output!"

    # Verify anti-patterns list is present and enforced
    assert len(res_fashion["anti_patterns"]) >= 5
    assert any("emoji" in ap.lower() for ap in res_fashion["anti_patterns"])

    print("✓ test_creative_director_variety_and_anti_patterns PASSED")


if __name__ == "__main__":
    test_routing_web_frontend_project()
    test_skill_delivery_untruncated_and_targeted()
    test_boilerplate_protection()
    test_visual_qa_enforcement_and_gates()
    test_creative_director_variety_and_anti_patterns()
    print("\nALL ROOT-CAUSE AUDIT REGRESSION TESTS PASSED SUCCESSFULLY! (5/5)")
