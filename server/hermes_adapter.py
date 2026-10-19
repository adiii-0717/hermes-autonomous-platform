from server.project.project_server_manager import project_server_manager
import os
import re
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
import sys
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Callable, Awaitable, Optional

HERMES_DIR = Path(__file__).parent.parent / "hermes-agent"
if str(HERMES_DIR) not in sys.path:
    sys.path.insert(0, str(HERMES_DIR))

try:
    import server.compat
    import run_agent
    from tools.registry import registry
    HERMES_AVAILABLE = True
except ImportError as err:
    HERMES_AVAILABLE = False
    logging.warning(f"Hermes Agent core import warning: {err}")

from server.security.workspace_guard import WorkspaceGuard
from server.security.approval_controller import ApprovalController
from server.project import ProjectAnalyzer, StructureAnalyzer, DependencyAnalyzer
from server.tasks import TaskManager, TaskStatus, create_event
from server.debug import ErrorMemory

from server.tools.dev_file_tools import DevFileTools
from server.tools.dev_terminal_tools import DevTerminalTools
from server.tools.dev_testing_tools import DevTestingTools
from server.tools.dev_git_tools import DevGitTools
from server.tools.dev_ast_tools import DevASTTools
from server.tools.dev_review_tools import DevReviewTools
from server.tools.dev_health_tools import DevHealthTools
from server.tools.dev_visual_qa_tools import DevVisualQATools
from server.tools.creative_direction_engine import CreativeDirectionEngine
from server.tools.component_discovery import ComponentDiscoveryCatalog
from server.tools.asset_discovery import AssetDiscoveryService
from server.agents.orchestrator import MultiAgentOrchestrator
from server.tools.autonomous_art_director import AutonomousArtDirector
from server.tools.product_intent_classifier import ProductIntentClassifier
from server.agents.provider_manager import provider_manager, ProviderStatus, ErrorClass, ProviderConfig

logger = logging.getLogger("hermes_adapter")


def is_web_frontend_project(language: Optional[str], user_message: str, is_continuation: bool = False) -> bool:
    """Determines whether a user turn should enter MultiAgentOrchestrator for web frontend generation."""
    if is_continuation:
        return False

    web_languages = {
        'html', 'web', 'javascript', 'typescript', 'js', 'ts',
        'react', 'jsx', 'tsx', 'reactjs', 'vue', 'svelte',
        'nextjs', 'vite', 'frontend'
    }

    backend_languages = {
        'python', 'py', 'go', 'golang', 'rust', 'rs', 'c', 'cpp',
        'c++', 'java', 'csharp', 'c#', 'ruby', 'php', 'backend',
        'cli', 'shell', 'bash', 'fastapi', 'flask', 'django'
    }

    norm_lang = (language or '').lower().strip()
    if norm_lang in backend_languages:
        return False
    if norm_lang in web_languages:
        return True

    # If language is None, empty, or unclassified, inspect prompt keywords
    msg = user_message.lower()

    backend_signals = [
        'backend', 'cli', 'command line', 'command-line', 'terminal', 'terminal app', 'rest api', 'api server',
        'fastapi', 'flask', 'django', 'express api', 'grpc', 'microservice', 'sqlite',
        'postgresql', 'database script', 'crawler', 'scraper', 'python', 'golang', 'rust',
        'argparse', 'click', 'pydantic'
    ]
    web_signals = [
        'react', 'jsx', 'tsx', 'website', 'web app', 'webapp', 'landing page',
        'storefront', 'portfolio', 'dashboard', 'frontend', 'html', 'css',
        'ui design', 'vite app', 'vite project', 'interactive web', 'store',
        'ecommerce', 'e-commerce'
    ]

    has_backend = any(bs in msg for bs in backend_signals)
    has_web = any(ws in msg for ws in web_signals)

    if has_backend and not has_web:
        return False
    if has_web:
        return True

    return not has_backend


class HermesAgentAdapter:
    """Orchestrates genuine Hermes Agent runtime instances with software engineering intelligence."""

    @staticmethod
    def get_candidate_models_for_provider(provider: str, active_model: Optional[str] = None) -> List[str]:
        """Returns candidate models pool for a given provider."""
        provider = (provider or "").lower().strip()
        candidates = []
        if active_model:
            candidates.append(active_model)

        if provider in ["google-gemini", "gemini", "google"]:
            env_m = os.getenv("GEMINI_MODEL") or os.getenv("MODEL_NAME")
            if env_m:
                candidates.append(env_m)
            candidates.extend([
                "gemini-3.5-flash-lite",
                "gemini-3.8-flash",
                "gemini-2.5-flash"
            ])
        elif provider == "apinex":
            env_m = os.getenv("APINEX_MODEL")
            if env_m:
                candidates.append(env_m)
            candidates.extend([
                "free/gemini-3.8-flash",
                "free/deepseek-v4.1-flash",
                "free/gpt-6-luna",
                "free/glm-5.3-flash",
                "free/qwen-3.8-max"
            ])
        elif provider == "groq":
            env_m = os.getenv("GROQ_MODEL") or os.getenv("MODEL_NAME")
            if env_m:
                candidates.append(env_m)
            candidates.extend([
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant"
            ])
        elif provider == "ollama":
            env_m = os.getenv("OLLAMA_MODEL") or os.getenv("MODEL_NAME")
            if env_m:
                candidates.append(env_m)
            candidates.extend([
                "gemma4:12b-hermes",
                "llama3"
            ])
        else:
            env_m = os.getenv("MODEL_NAME")
            if env_m:
                candidates.append(env_m)
        return [m for m in dict.fromkeys(candidates) if m]

    @staticmethod
    def get_fallback_provider_chain(current_provider: str = "", current_key: Optional[str] = None) -> List[Dict[str, str]]:
        """Returns configured backup providers in strict priority order:
        1. Gemini Key 1 (Primary)
        2. Gemini Key 2 (First Backup)
        3. Gemini Key 3 (Second Backup)
        4. APInex (Final Fallback)
        5. Ollama (Offline)
        Excludes current provider/key and providers marked AUTH_FAILED.
        """
        chain = []
        for p in provider_manager.get_ordered_providers():
            if p.status == ProviderStatus.AUTH_FAILED or not p.is_configured:
                continue
            if current_key and p.api_key and p.api_key == current_key:
                continue
            if not current_key and current_provider and p.provider == current_provider and p.priority == 1:
                continue
            chain.append({
                "provider": p.provider,
                "provider_id": p.provider_id,
                "display_name": p.display_name,
                "model": p.default_model,
                "api_key": p.api_key,
                "api_base": p.api_base,
                "priority": p.priority
            })
        return chain

    @staticmethod
    def is_recoverable_error(exc: Optional[Exception]) -> bool:
        """Classifies whether an error is transient/recoverable (rate limits, quotas, timeouts, network)
        versus permanent configuration/authentication errors (401/403)."""
        if exc is None:
            return True
        err_class, _ = provider_manager.classify_error(exc)
        if err_class == ErrorClass.AUTH_FAILURE:
            return False
        return True

    @staticmethod
    def normalize_model_config(cfg: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Resolves and normalizes model provider configuration with strict priority order:
        1. Gemini Key 1 (Primary)
        2. Gemini Key 2 (First Backup)
        3. Gemini Key 3 (Second Backup)
        4. APInex (Final Fallback)
        """
        cfg = cfg or {}
        explicit_provider = (cfg.get("provider") or "").strip().lower()

        if explicit_provider:
            provider = explicit_provider
        else:
            active = provider_manager.get_active_provider()
            if active:
                provider = active.provider
            elif os.getenv("GEMINI_API_KEY_1") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
                provider = "google-gemini"
            elif os.getenv("APINEX_API_KEY"):
                provider = "apinex"
            elif os.getenv("LLM_PROVIDER") or os.getenv("MODEL_PROVIDER"):
                provider = (os.getenv("LLM_PROVIDER") or os.getenv("MODEL_PROVIDER")).strip().lower()
            else:
                provider = "google-gemini"

        provider_id = cfg.get("provider_id") or ""
        display_name = cfg.get("display_name") or ""

        if provider in ["google-gemini", "gemini", "google", "google_gemini", "google-ai-studio"]:
            provider = "google-gemini"
            if "api_key" in cfg and cfg["api_key"] is not None:
                key = cfg["api_key"]
            else:
                active = provider_manager.get_active_provider()
                if active and active.provider == "google-gemini":
                    key = active.api_key
                    provider_id = active.provider_id
                    display_name = active.display_name
                else:
                    key = (
                        os.getenv("GEMINI_API_KEY_1")
                        or os.getenv("GEMINI_API_KEY")
                        or os.getenv("GOOGLE_API_KEY")
                        or ""
                    )
                    provider_id = "gemini_1"
                    display_name = "Gemini (Key 1)"
            api_base = (
                cfg.get("api_base")
                or os.getenv("GEMINI_BASE_URL")
                or os.getenv("API_BASE_URL")
                or "https://generativelanguage.googleapis.com/v1beta/openai/"
            )
            model = (
                cfg.get("model")
                or os.getenv("GEMINI_MODEL")
                or os.getenv("MODEL_NAME")
                or "gemini-2.5-flash"
            )
            if not provider_id:
                provider_id = "gemini_1"
                display_name = "Gemini (Key 1)"
        elif provider in ["apinex", "apinex-ai", "apinex_bond", "apinex.bond"]:
            provider = "apinex"
            key = (
                cfg.get("api_key")
                or os.getenv("APINEX_API_KEY")
                or ""
            )
            api_base = (
                cfg.get("api_base")
                or os.getenv("APINEX_BASE_URL")
                or "https://api.apinex.bond/v1"
            )
            model = (
                cfg.get("model")
                or os.getenv("APINEX_MODEL")
                or "free/gemini-3.8-flash"
            )
            provider_id = "apinex"
            display_name = "APInex"
        elif provider in ["groq", "groq-ai", "groq_ai"]:
            provider = "groq"
            key = (
                cfg.get("api_key")
                or os.getenv("GROQ_API_KEY")
                or ""
            )
            api_base = (
                cfg.get("api_base")
                or os.getenv("GROQ_BASE_URL")
                or "https://api.groq.com/openai/v1"
            )
            model = (
                cfg.get("model")
                or os.getenv("GROQ_MODEL")
                or "llama-3.3-70b-versatile"
            )
            provider_id = "groq"
            display_name = "Groq"
        elif provider == "openrouter":
            provider = "openrouter"
            key = cfg.get("api_key") or os.getenv("OPENROUTER_API_KEY", "")
            api_base = cfg.get("api_base") or os.getenv("API_BASE_URL", "https://openrouter.ai/api/v1")
            model = cfg.get("model") or os.getenv("MODEL_NAME", "anthropic/claude-3.5-sonnet")
            provider_id = "openrouter"
            display_name = "OpenRouter"
        elif provider == "openai":
            provider = "openai"
            key = cfg.get("api_key") or os.getenv("OPENAI_API_KEY", "")
            api_base = cfg.get("api_base") or os.getenv("API_BASE_URL", "https://api.openai.com/v1")
            model = cfg.get("model") or os.getenv("MODEL_NAME", "gpt-4o")
            provider_id = "openai"
            display_name = "OpenAI"
        else:
            provider = "ollama"
            key = cfg.get("api_key") or os.getenv("OLLAMA_API_KEY", "ollama")
            api_base = cfg.get("api_base") or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
            model = cfg.get("model") or os.getenv("OLLAMA_MODEL", "gemma4:12b-hermes")
            provider_id = "ollama"
            display_name = "Local Ollama"

        if api_base and not api_base.endswith("/"):
            api_base = api_base + "/"

        return {
            "provider": provider,
            "provider_id": provider_id,
            "display_name": display_name,
            "model": model,
            "api_key": key,
            "api_base": api_base
        }

    def set_model_config(self, new_config: Dict[str, str]):
        """Update model configuration dynamically at runtime."""
        self._explicit_user_override = True
        self.model_config = self.normalize_model_config(new_config)

    def __init__(self, workspace_path: str, model_config: Optional[Dict[str, str]] = None):
        self.workspace_path = Path(workspace_path).resolve()
        self.workspace_guard = WorkspaceGuard(str(self.workspace_path))
        self.approval_controller = ApprovalController()
        
        self.project_analyzer = ProjectAnalyzer(self.workspace_path)
        self.structure_analyzer = StructureAnalyzer(self.workspace_path)
        self.dependency_analyzer = DependencyAnalyzer(self.workspace_path)
        self.task_manager = TaskManager()
        self.error_memory = ErrorMemory()

        self.file_tools = DevFileTools(self.workspace_guard)
        self.terminal_tools = DevTerminalTools(self.workspace_guard, self.approval_controller)
        self.testing_tools = DevTestingTools(self.workspace_guard)
        self.git_tools = DevGitTools(self.workspace_guard)
        self.ast_tools = DevASTTools(self.workspace_guard)
        self.review_tools = DevReviewTools(self.workspace_guard)
        self.health_tools = DevHealthTools(self.workspace_guard)
        self.visual_qa_tools = DevVisualQATools(self.workspace_guard)
        self.creative_engine = CreativeDirectionEngine()
        self.component_catalog = ComponentDiscoveryCatalog()
        self.asset_service = AssetDiscoveryService()
        self.autonomous_art_director = AutonomousArtDirector()
        self.product_intent_classifier = ProductIntentClassifier()
        self.orchestrator = MultiAgentOrchestrator(self.workspace_guard)
        
        self.model_config = self.normalize_model_config(model_config)
        self._cancelled = False
        self.last_started_tool = None
        self.register_custom_tools_into_hermes()

    def cancel_current_turn(self):
        """Signals cancellation of ongoing execution turn."""
        self._cancelled = True

    def set_workspace_path(self, new_workspace_path: str):
        self.workspace_path = Path(new_workspace_path).resolve()
        self.workspace_guard = WorkspaceGuard(str(self.workspace_path))
        self.project_analyzer = ProjectAnalyzer(self.workspace_path)
        self.structure_analyzer = StructureAnalyzer(self.workspace_path)
        self.dependency_analyzer = DependencyAnalyzer(self.workspace_path)
        self.file_tools = DevFileTools(self.workspace_guard)
        self.terminal_tools = DevTerminalTools(self.workspace_guard, self.approval_controller)
        self.testing_tools = DevTestingTools(self.workspace_guard)
        self.git_tools = DevGitTools(self.workspace_guard)
        self.ast_tools = DevASTTools(self.workspace_guard)
        self.review_tools = DevReviewTools(self.workspace_guard)
        self.health_tools = DevHealthTools(self.workspace_guard)
        self.visual_qa_tools = DevVisualQATools(self.workspace_guard)
        self.creative_engine = CreativeDirectionEngine()
        self.component_catalog = ComponentDiscoveryCatalog()
        self.asset_service = AssetDiscoveryService()
        self.autonomous_art_director = AutonomousArtDirector()
        self.product_intent_classifier = ProductIntentClassifier()
        self.orchestrator = MultiAgentOrchestrator(self.workspace_guard)
        self.register_custom_tools_into_hermes()

    async def analyze_prompt_for_project(self, user_message: str) -> dict:
        """Extract project metadata with fast bounded timeout and automatic failover across providers."""
        import os
        import re
        import httpx
        
        def sanitize_name(name):
            name = name.lower()
            name = re.sub(r'[^a-z0-9_\-]', '_', name)
            name = re.sub(r'_+', '_', name)
            return name.strip('_')

        heuristics = {
            "project_name": "temp_project",
            "language": None
        }
        if hasattr(self, "product_intent_classifier") and user_message:
            try:
                heuristics["product_intent"] = self.product_intent_classifier.classify_intent(user_message)
            except Exception:
                pass
        
        words = [re.sub(r'[^a-z0-9+\-#]', '', w) for w in user_message.lower().split()]
        languages = ["python", "javascript", "typescript", "go", "rust", "c++", "java", "html", "css"]
        for lang in languages:
            if lang in words or (lang == "c++" and "c++" in user_message.lower()) or (lang == "typescript" and "ts" in words) or (lang == "javascript" and "js" in words):
                heuristics["language"] = lang
                break

        # 1. Check for explicit brand or business name: e.g. 'called “Crave Kitchen”' or 'named XYZ'
        brand_match = re.search(r'(?:called|named|brand|titled)\s+["“\']?([^"”\'.,\n\(\)]+?)["”\']?(?:\.|\s+Include|\s+with|\s*$)', user_message, re.IGNORECASE)
        if brand_match:
            cand = sanitize_name(brand_match.group(1).strip())
            if cand and len(cand) >= 3 and cand not in ["a", "an", "the", "website", "app"]:
                heuristics["project_name"] = cand

        # 2. Fast deterministic heuristic extraction from core domain nouns (excluding generic adjectives)
        if heuristics["project_name"] in ["temp_project", "project"]:
            stop_words = {
                "build", "create", "make", "generate", "develop", "design", "start", 
                "a", "an", "the", "smart", "simple", "system", "app", "application", 
                "in", "with", "using", "using:", "script", "program", "code", "run", "to", "for", "please",
                "beautiful", "modern", "online", "clean", "stylish", "awesome", "creative", 
                "professional", "premium", "interactive", "responsive", "high", "quality", 
                "attractive", "delicious", "called", "named", "website", "web", "page", "site"
            }
            filtered_words = [sanitize_name(w) for w in words if sanitize_name(w) not in stop_words and sanitize_name(w) not in languages]
            filtered_words = [w for w in filtered_words if w]
            if len(filtered_words) >= 2:
                heuristics["project_name"] = "_".join(filtered_words[:3])
            elif len(filtered_words) == 1:
                heuristics["project_name"] = filtered_words[0]
            else:
                heuristics["project_name"] = "project_" + os.urandom(3).hex()

        # If a language was detected, or if prompt implies web project, return immediately
        if not heuristics["language"]:
            if any(w in words for w in ["web", "website", "portfolio", "landing", "page", "store", "ecommerce", "dashboard", "ui", "site"]):
                heuristics["language"] = "html"

        # Return immediately if a valid, descriptive project name was extracted
        if heuristics["project_name"] not in ["temp_project", "project"] and len(heuristics["project_name"]) >= 3:
            return heuristics

        return heuristics

    def _take_workspace_snapshot(self) -> dict:
        """Take a snapshot of all file paths, sizes, and mtimes in the current workspace."""
        snapshot = {}
        if not self.workspace_path or not self.workspace_path.exists():
            return snapshot
        for root, dirs, files in os.walk(self.workspace_path):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("venv", ".venv", "__pycache__", "node_modules", "dist", "build")]
            for f in files:
                if f.startswith(".") or f in ("AGENTS.md", "task.md", "implementation_plan.md", "walkthrough.md"):
                    continue
                full_path = Path(root) / f
                rel_path = str(full_path.relative_to(self.workspace_path))
                try:
                    stat = full_path.stat()
                    snapshot[rel_path] = (stat.st_size, stat.st_mtime)
                except Exception:
                    pass
        return snapshot

    def discover_projects(self) -> list:
        """Scan workspace/ directory for all directories containing .project_manifest.json."""
        p = Path(self.workspace_path).resolve()
        if p.name == "workspace":
            workspace_dir = p
        elif p.parent.name == "workspace":
            workspace_dir = p.parent
        elif (p / "workspace").exists():
            workspace_dir = p / "workspace"
        elif (Path(__file__).parent.parent / "workspace").exists():
            workspace_dir = Path(__file__).parent.parent / "workspace"
        else:
            return []
            
        if not workspace_dir.exists():
            return []
        projects = []
        for d in workspace_dir.iterdir():
            if d.is_dir():
                manifest_file = d / ".project_manifest.json"
                if manifest_file.exists():
                    try:
                        with open(manifest_file, "r") as f:
                            manifest = json.load(f)
                            projects.append({
                                "name": d.name,
                                "path": str(d),
                                "language": manifest.get("languages", [None])[0] if manifest.get("languages") else None
                            })
                    except Exception:
                        pass
        return projects

    def find_matching_projects(self, user_message: str) -> list:
        """Find existing projects with deterministic scoring and language-aware filtering."""
        msg_lower = user_message.lower().strip()
        # 0. Never hijack explicit creation/build prompts into existing projects
        is_creation_intent = bool(
            re.search(r'\b(build|create|make|generate|start|develop|design)\b', msg_lower)
            or 'new project' in msg_lower
        )
        if is_creation_intent:
            return []

        projects = self.discover_projects()
        if not projects:
            return []
        words = set(re.findall(r'[a-zA-Z0-9_\-]+', msg_lower))
        
        # Generic adjectives and common words that must never trigger project continuation on their own
        GENERIC_STOP_WORDS = {
            "premium", "modern", "clean", "stylish", "simple", "smart", "online", 
            "website", "web", "app", "application", "store", "storefront", "shop", 
            "shopping", "platform", "system", "page", "dashboard", "portfolio", 
            "test", "demo", "sample", "responsive", "high", "quality", "attractive"
        }
        
        scored_matches = []
        for proj in projects:
            name_lower = proj["name"].lower()
            name_space = name_lower.replace("_", " ").replace("-", " ")
            
            # 1. Exact/strong contiguous matches get highest confidence (1.0)
            proj_core_words = [w for w in re.split(r'[^a-zA-Z0-9]', name_lower) if len(w) > 2 and w not in GENERIC_STOP_WORDS]
            if name_lower in msg_lower or name_space in msg_lower:
                if proj_core_words:
                    scored_matches.append((proj, 1.0))
                    continue
                
            # 2. Score based on token overlap (ignoring generic stop-words)
            proj_tokens = set(re.split(r'[^a-zA-Z0-9]', name_lower))
            proj_tokens = {t for t in proj_tokens if len(t) > 2 and t not in GENERIC_STOP_WORDS}
            if not proj_tokens:
                continue
                
            matched_tokens = proj_tokens.intersection(words - GENERIC_STOP_WORDS)
            if matched_tokens:
                score = len(matched_tokens) / len(proj_tokens)
                if score >= 0.75: # Strict confidence threshold
                    scored_matches.append((proj, score))
                    
        if not scored_matches:
            return []
            
        # Sort matches by score descending
        scored_matches.sort(key=lambda x: x[1], reverse=True)
        highest_score = scored_matches[0][1]
        
        # Keep all matches with the highest score (or within 0.1 of it)
        candidates = [proj for proj, score in scored_matches if (highest_score - score) <= 0.1]
        
        # Filter out shorter candidate names that are substrings of a longer candidate name
        if len(candidates) > 1:
            filtered_candidates = []
            for c in candidates:
                c_name = c["name"].lower()
                is_sub = False
                for other in candidates:
                    if c != other and c_name in other["name"].lower():
                        is_sub = True
                        break
                if not is_sub:
                    filtered_candidates.append(c)
            candidates = filtered_candidates
        
        # If there are multiple candidates, check language disambiguation
        languages_in_prompt = []
        all_languages = ["python", "javascript", "typescript", "go", "rust", "java", "c++"]
        for lang in all_languages:
            if lang in words or (lang == "typescript" and "ts" in words) or (lang == "javascript" and "js" in words):
                languages_in_prompt.append(lang)
                
        if len(candidates) > 1 and languages_in_prompt:
            lang_filtered = []
            for m in candidates:
                m_lang = (m["language"] or "").lower()
                if m_lang == "typescript" and "ts" in languages_in_prompt:
                    lang_filtered.append(m)
                elif m_lang == "javascript" and "js" in languages_in_prompt:
                    lang_filtered.append(m)
                elif m_lang in languages_in_prompt:
                    lang_filtered.append(m)
            if lang_filtered:
                return lang_filtered
                
        return candidates

    def compile_project_results(self) -> dict:
        """Compile execution results, files created/modified, and test statuses for the UI."""
        import shutil
        project_name = self.workspace_path.name
        
        try:
            project_dir = str(self.workspace_path.relative_to(Path(__file__).parent.parent))
        except ValueError:
            project_dir = str(self.workspace_path)

        # 1. Ensure SRS.md (Software Requirements Specification) exists inside project directory
        srs_file = self.workspace_path / "SRS.md"
        if not srs_file.exists():
            try:
                srs_content = f"""# Software Requirements Specification (SRS)

## Project: {project_name.upper()}

### 1. Scope & Objective
This document outlines the software requirements specification for  created by Hermes Autonomous Agent.

### 2. Functional Requirements
- **FR-1**: Complete application implementation with modular components.
- **FR-2**: Interactive user interface and execution entrypoint.
- **FR-3**: Automated test suite validation.

### 3. Non-Functional Requirements
- **NFR-1**: High performance and responsive user interaction.
- **NFR-2**: Zero external unverified runtime dependencies.
- **NFR-3**: Clean code architecture and self-contained deployment.

### 4. Running & Deployment Instructions
See  for step-by-step installation and execution steps.
"""
                srs_file.write_text(srs_content, encoding="utf-8")
            except Exception as exc:
                logger.warning(f"Failed to generate SRS.md: {exc}")

        # 2. Ensure README.md (Step-by-Step Instructions) exists inside project directory
        readme_file = self.workspace_path / "README.md"
        if not readme_file.exists():
            try:
                readme_content = f"""# {project_name.upper()}

Autonomous Software Project generated by Hermes Agent Framework.

## 🚀 How to Run Step-by-Step

### Step 1: Open Terminal in Project Directory


### Step 2: Install Dependencies
For web applications, open  in your browser or run a simple local web server:

For Python applications:

--- Student Attendance System ---
1. Mark Attendance (Student)
2. Generate Monthly Report (Teacher)
3. Exit
Select an option: 

### Step 3: Run Automated Unit Tests


## 📄 Documentation
- : Software Requirements Specification.
"""
                readme_file.write_text(readme_content, encoding="utf-8")
            except Exception as exc:
                logger.warning(f"Failed to generate README.md: {exc}")
        
        initial = getattr(self, "_initial_files_snapshot", {})
        current = self._take_workspace_snapshot()
        
        files_created = [f for f in current if f not in initial]
        files_modified = [f for f in current if f in initial and current[f] != initial[f]]
        
        health_summary = self.health_tools.check_project_health()
        success = bool(health_summary.get("build_healthy", True) and health_summary.get("tests_healthy", True))
        
        remaining_issues = []
        if not health_summary.get("build_healthy", True):
            remaining_issues.append("Build checks failed.")
        if not health_summary.get("tests_healthy", True):
            remaining_issues.append("Test suite has failures.")
        if not health_summary.get("lint_healthy", True):
            remaining_issues.append("Linter checks failed.")

        download_url = f"/api/projects/{project_name}/download"
        try:
            zip_base = self.workspace_path.parent / f"{project_name}"
            shutil.make_archive(
                str(zip_base),
                'zip',
                root_dir=str(self.workspace_path.parent),
                base_dir=project_name
            )
        except Exception as zip_err:
            logger.warning(f"Error creating project ZIP: {zip_err}")
            
        visual_qa_summary = self.visual_qa_tools.run_full_visual_qa(project_name, self.model_config)
        if visual_qa_summary.get("is_web_project") and not visual_qa_summary.get("passed"):
            remaining_issues.append("Visual QA audit detected design/layout issues.")

        return {
            "project_name": project_name,
            "project_directory": project_dir,
            "files_created": files_created,
            "files_modified": files_modified,
            "tests_executed": health_summary.get("total_tests", 0),
            "test_results": health_summary,
            "success": success,
            "remaining_issues": remaining_issues,
            "preview_url": f"/preview/{project_name}/",
            "server_status": project_server_manager.get_server_status(project_name),
            "download_url": download_url,
            "visual_qa": visual_qa_summary
        }

    def register_custom_tools_into_hermes(self):
        if not HERMES_AVAILABLE:
            return

        import inspect
        import functools

        def adapt_handler_signature(handler_fn, tool_name):
            sig = inspect.signature(handler_fn)
            params = list(sig.parameters.keys())

            # Find required parameters (excluding 'self', default values, and variadic args)
            required_params = []
            for p_name, param in sig.parameters.items():
                if p_name == 'self':
                    continue
                if param.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY):
                    if param.default == inspect.Parameter.empty:
                        required_params.append(p_name)

            def json_serialize_if_needed(res):
                if isinstance(res, dict) and not (res.get("_multimodal") is True and isinstance(res.get("content"), list)):
                    return json.dumps(res)
                return res

            if inspect.iscoroutinefunction(handler_fn):
                @functools.wraps(handler_fn)
                async def async_wrapper(args, **kwargs):
                    actual_args = args if isinstance(args, dict) else {}
                    
                    # Validate required parameters
                    for p in required_params:
                        if p not in actual_args:
                            return f"Error: Missing required argument '{p}' for tool '{tool_name}'."

                    call_kwargs = {}
                    for p in params:
                        if p in actual_args:
                            call_kwargs[p] = actual_args[p]
                    res = await handler_fn(**call_kwargs)
                    return json_serialize_if_needed(res)
                return async_wrapper
            else:
                @functools.wraps(handler_fn)
                def sync_wrapper(args, **kwargs):
                    actual_args = args if isinstance(args, dict) else {}
                    
                    # Validate required parameters
                    for p in required_params:
                        if p not in actual_args:
                            return f"Error: Missing required argument '{p}' for tool '{tool_name}'."

                    call_kwargs = {}
                    for p in params:
                        if p in actual_args:
                            call_kwargs[p] = actual_args[p]
                    res = handler_fn(**call_kwargs)
                    return json_serialize_if_needed(res)
                return sync_wrapper

        tool_specs = [
            ("read_file", "Read contents of a file in workspace.", self.file_tools.read_file, False),
            ("write_file", "Create or overwrite a file in workspace.", self.file_tools.write_file, False),
            ("edit_file", "Replace a text segment in a file.", self.file_tools.edit_file, False),
            ("search_files", "Search files for a text pattern.", self.file_tools.search_files, False),
            ("list_directory", "List directory contents.", self.file_tools.list_directory, False),
            ("get_project_structure", "Get clean directory tree structure.", self.structure_analyzer.get_project_structure, False),
            ("analyze_ast", "Analyze AST for symbols and classes.", self.ast_tools.analyze_ast, False),
            ("read_symbol_definition", "Read symbol/class/function definition.", self.ast_tools.read_symbol_definition, False),
            ("find_symbol_references", "Find references to a symbol.", self.ast_tools.find_symbol_references, False),
            ("analyze_change_impact", "Analyze impact of modifying a symbol/class.", self.ast_tools.analyze_change_impact, False),
            ("find_related_tests", "Find candidate test files for a source file.", self.testing_tools.find_related_tests, False),
            ("review_changes", "Review uncommitted git diffs for flaws.", self.review_tools.review_changes, False),
            ("check_project_health", "Run complete project health check.", self.health_tools.check_project_health, False),
            ("execute_command", "Execute a shell command inside workspace.", self.terminal_tools.execute_command, True),
            ("start_background_process", "Start background process.", self.terminal_tools.start_background_process, False),
            ("get_process_output", "Get background process output.", self.terminal_tools.get_process_output, False),
            ("get_process_status", "Get background process status.", self.terminal_tools.get_process_status, False),
            ("kill_process", "Kill background process.", self.terminal_tools.kill_process, False),
            ("run_tests", "Execute project test suite.", self.testing_tools.run_tests, False),
            ("run_linter", "Execute project linter.", self.testing_tools.run_linter, False),
            ("run_build", "Execute project build command.", self.testing_tools.run_build, False),
            ("git_status", "Get git status.", self.git_tools.git_status, False),
            ("git_diff", "Get git diff.", self.git_tools.git_diff, False),
            ("git_commit", "Create git commit.", self.git_tools.git_commit, False),
            ("run_visual_qa", "Audit HTML/CSS visual design, capture responsive screenshots, and evaluate visual aesthetic quality.", lambda project_name="": self.visual_qa_tools.run_full_visual_qa(project_name, self.model_config), False),
        ]

        for name, desc, handler, is_async in tool_specs:
            try:
                adapted_handler = adapt_handler_signature(handler, name)
                existing_schema = registry.get_schema(name)
                if existing_schema:
                    schema = existing_schema
                else:
                    schema = {"name": name, "description": desc, "parameters": {"type": "object", "properties": {}}}

                registry.register(
                    name=name,
                    toolset="development",
                    schema=schema,
                    handler=adapted_handler,
                    is_async=is_async,
                    override=True
                )
            except Exception as e:
                logger.debug(f"Tool registration note for '{name}': {e}")

        # Mutate toolsets._HERMES_CORE_TOOLS in memory so that is_deferrable_tool_name returns False for all our custom tools.
        try:
            import toolsets
            for name, _, _, _ in tool_specs:
                if name not in toolsets._HERMES_CORE_TOOLS:
                    toolsets._HERMES_CORE_TOOLS.append(name)
        except Exception as e:
            logger.debug(f"Failed to update core tools in memory: {e}")

        # Monkey-patch model_tools.handle_function_call to unwrap and directly execute tool_call for non-deferrable tools.
        try:
            import model_tools
            if not hasattr(model_tools, "_original_handle_function_call"):
                model_tools._original_handle_function_call = model_tools.handle_function_call

                def wrapped_handle_function_call(function_name: str, function_args: dict, *args, **kwargs):
                    if function_name == "tool_call":
                        underlying_name = function_args.get("name")
                        underlying_args = function_args.get("arguments") or {}
                        if isinstance(underlying_args, str):
                            try:
                                underlying_args = json.loads(underlying_args)
                            except Exception:
                                pass
                        if underlying_name:
                            from tools.tool_search import is_deferrable_tool_name
                            if not is_deferrable_tool_name(underlying_name):
                                logger.info(f"Intercepted tool_call for non-deferrable tool '{underlying_name}'. Dispatching directly.")
                                return wrapped_handle_function_call(underlying_name, underlying_args, *args, **kwargs)
                    return model_tools._original_handle_function_call(function_name, function_args, *args, **kwargs)

                model_tools.handle_function_call = wrapped_handle_function_call
                logger.info("Successfully monkey-patched model_tools.handle_function_call")
        except Exception as e:
            logger.debug(f"Failed to monkeypatch handle_function_call: {e}")

    async def execute_tool_direct(self, tool_name: str, args: dict) -> Any:
        if tool_name == "read_file":
            return self.file_tools.read_file(args.get("path"), args.get("start_line"), args.get("end_line"))
        elif tool_name == "write_file":
            return self.file_tools.write_file(args.get("path"), args.get("content", ""))
        elif tool_name == "edit_file":
            return self.file_tools.edit_file(args.get("path"), args.get("target", ""), args.get("replacement", ""))
        elif tool_name == "search_files":
            return self.file_tools.search_files(args.get("query", ""), args.get("relative_path", "."), pattern=args.get("pattern"))
        elif tool_name == "list_directory":
            return self.file_tools.list_directory(args.get("relative_path", "."))
        elif tool_name == "get_project_structure":
            return self.structure_analyzer.get_project_structure(args.get("relative_path", "."))
        elif tool_name == "analyze_ast":
            return self.ast_tools.analyze_ast(args.get("file_path", ""))
        elif tool_name == "read_symbol_definition":
            return self.ast_tools.read_symbol_definition(args.get("symbol_name", ""), args.get("file_path"))
        elif tool_name == "find_symbol_references":
            return self.ast_tools.find_symbol_references(args.get("symbol_name", ""))
        elif tool_name == "analyze_change_impact":
            return self.ast_tools.analyze_change_impact(args.get("symbol_name", ""), args.get("file_path"))
        elif tool_name == "find_related_tests":
            return self.testing_tools.find_related_tests(args.get("target_file", ""))
        elif tool_name == "review_changes":
            return self.review_tools.review_changes()
        elif tool_name == "check_project_health":
            return self.health_tools.check_project_health()
        elif tool_name == "execute_command":
            return await self.terminal_tools.execute_command(args.get("command", ""), args.get("timeout", 30))
        elif tool_name == "start_background_process":
            return self.terminal_tools.start_background_process(args.get("command", ""))
        elif tool_name == "get_process_output":
            return self.terminal_tools.get_process_output(args.get("process_id", ""))
        elif tool_name == "get_process_status":
            return self.terminal_tools.get_process_status(args.get("process_id"))
        elif tool_name == "kill_process":
            return self.terminal_tools.kill_process(args.get("process_id", ""))
        elif tool_name == "run_tests":
            return self.testing_tools.run_tests(args.get("test_runner"))
        elif tool_name == "run_linter":
            return self.testing_tools.run_linter(args.get("linter_cmd"))
        elif tool_name == "run_build":
            return self.testing_tools.run_build(args.get("build_cmd"))
        elif tool_name == "git_status":
            return self.git_tools.git_status()
        elif tool_name == "git_diff":
            return self.git_tools.git_diff(args.get("file_path"))
        elif tool_name == "git_commit":
            return self.git_tools.git_commit(args.get("message", "Auto-commit by Hermes Agent"))
        else:
            return {"error": f"Unknown tool '{tool_name}'"}


    
    def run_multi_agent_orchestration(
        self,
        project_name: str,
        user_prompt: str,
        max_cycles: int = 3,
        reference_images: Optional[List[str]] = None,
        status_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """Runs production multi-agent orchestration (Creative Director, Frontend Engineer, 3D/Motion Engineer, Visual QA Inspector) in a bounded refinement loop."""
        return self.orchestrator.generate_project(
            project_name,
            user_prompt,
            max_cycles=max_cycles,
            reference_images=reference_images,
            status_callback=status_callback
        )

    def _get_ui_ux_design_guidelines(self, user_prompt: str = "") -> str:
        """Returns persistent UI/UX design guidelines and creative direction rationale."""
        from pathlib import Path
        direction = self.creative_engine.generate_creative_direction(user_prompt, self.workspace_path.name)
        css_block = self.creative_engine.get_css_variable_block(direction)
        arch = direction.get('selected_archetype', 'Modern Minimal')
        rat = direction.get('design_rationale', 'Clean layout')

        # Discover relevant component snippets & verified assets
        components = self.component_catalog.search_components(user_prompt)
        comp_text = self.component_catalog.format_component_prompt(components[:3])

        assets = self.asset_service.discover_assets(user_prompt) if hasattr(self, "asset_service") else {}
        asset_text = self.asset_service.format_asset_prompt_guidelines(assets) if hasattr(self, "asset_service") and assets else "" 

        # Load complete master UI design skills without arbitrary character truncation
        def _read_skill(skill_name: str) -> str:
            candidates = [
                Path(__file__).parent.parent / ".agents" / "skills" / skill_name / "SKILL.md",
                Path(__file__).parent.parent / "hermes-agent" / "skills" / "software-development" / skill_name / "SKILL.md"
            ]
            for p in candidates:
                if p.exists():
                    try:
                        content = p.read_text(encoding="utf-8")
                        if content.startswith("---"):
                            parts = content.split("---", 2)
                            if len(parts) >= 3:
                                content = parts[2].strip()
                        return content
                    except Exception:
                        pass
            return ""

        anthropic_text = _read_skill("anthropic-frontend-design")
        ui_ux_pro_text = _read_skill("ui-ux-pro-max")
        vercel_text = _read_skill("vercel-web-design-react")
        ui_sh_text = _read_skill("ui-sh")

        # Load authentic, targeted React Bits component documentation, props, dependencies, and implementation examples
        react_bits_targeted_specs = self.component_catalog.get_targeted_component_specs(user_prompt)
        rb_guidance = self.component_catalog.get_purpose_matched_reactbits(user_prompt)

        intent_block = ""
        if hasattr(self, "product_intent_classifier") and user_prompt:
            try:
                intent_res = self.product_intent_classifier.classify_intent(user_prompt)
                intent_block = intent_res.get("guidelines", "")
            except Exception:
                pass

        anthropic_block = ("[ANTHROPIC FRONTEND DESIGN SPECIFICATION]\n" + anthropic_text) if anthropic_text else ""
        ui_ux_pro_block = ("[UI/UX PRO MAX SPECIFICATION]\n" + ui_ux_pro_text) if ui_ux_pro_text else ""
        vercel_block = ("[VERCEL WEB DESIGN & REACT SPECIFICATION]\n" + vercel_text) if vercel_text else ""
        ui_sh_block = ("[UI.SH DESIGN ENGINEERING SPECIFICATION]\n" + ui_sh_text) if ui_sh_text else ""
        rb_block = react_bits_targeted_specs

        recommended_rb = (
            f"Purpose-Matched React Bits Architecture:\n"
            f"- Background: {rb_guidance['selected_components']['background']}\n"
            f"- Hero Typography: {rb_guidance['selected_components']['hero_text']}\n"
            f"- Cards & Presentation: {rb_guidance['selected_components']['card']}\n"
            f"- Micro-Interaction: {rb_guidance['selected_components']['micro_interaction']}\n"
            f"- Primary Button: {rb_guidance['selected_components']['button']}\n"
            f"- Recommended Lucide Icons: {', '.join(rb_guidance['lucide_icons'])}\n"
            f"- Clean Monogram Badge: '{rb_guidance['branding_badge']}'"
        )

        return f"""
[CREATIVE DIRECTION & FOUR-SKILL DESIGN SYSTEM GUIDELINES]
Selected Archetype: {arch}
Design Rationale: {rat}
Recommended CSS Variable Tokens:
{css_block}

RECOMMENDED UI COMPONENT RECIPES:
{comp_text}

{recommended_rb}

{asset_text}

STRICT FOUR-SKILL ARCHITECTURAL & ICONOGRAPHY RULES:
1. ANTHROPIC DESIGN LEADERSHIP & ANTI-SLOP CHECK:
   - Make deliberate, opinionated choices tailored to the brief. Spend boldness in one place; keep surrounding elements disciplined.
   - BANNED CLICHÉS: Warm cream #F4F1EA + terracotta display, dark-mode purple/neon gradients, repetitive cards, single-word italic headline highlights, tracked-out ALL-CAPS eyebrows on every heading, and appending "→" to every button.
   - COPYWRITING: Active voice ("Deploy Pipeline", "Save Changes", not "Submit"). Plain verbs, sentence case, zero filler copy.
2. UI/UX PRO MAX ARCHETYPE & ACCESSIBILITY:
   - Match one of 10 distinct archetypes: Glassmorphism, Bento Grid, Minimalist Luxury, Dark Cyberpunk, Swiss International, Neo-Brutalist, Soft UI, Retro-Futuristic, Organic Editorial, High-Energy Studio.
   - 8pt SPATIAL GRID: Strictly use 8pt scale (p-4, p-6, p-8, gap-6, py-20, py-28).
   - ACCESSIBILITY: WCAG AA contrast (>= 4.5:1), min 44x44px touch targets, and complete interactive states (rest, hover, active, focus-visible, disabled).
3. VERCEL WEB DESIGN & REACT GUIDELINES:
   - Monochromatic elegance with hairline borders (border border-white/10 or border-zinc-800).
   - TABULAR NUMBERS: Use font-variant-numeric: tabular-nums on all metrics, stats, telemetry, and financial figures.
   - HEADING BALANCE: Apply text-wrap: balance on all multi-line headings.
   - VISIBLE FOCUS RINGS: focus-visible:ring-2 focus-visible:ring-cyan-400 focus-visible:outline-none focus-visible:ring-offset-2. Never use outline-none without replacement.
   - REACT BEST PRACTICES: Zero waterfalls, minimal bundle footprint, clean component decomposition, derived state.
4. UI.SH DESIGN ENGINEERING (REFACTORING UI):
   - Hierarchy with weight and color contrast, not just font size.
   - Generous whitespace: start with generous padding and pull back.
   - Hairline ring borders (ring-1 ring-inset ring-white/10) over muddy box shadows.
   - Tint dark-mode neutrals with background undertones (cool slate on obsidian, warm stone on charcoal).
   - Break 3-card grid monotony with asymmetric layout rhythm. Zero lorem ipsum.
5. PROFESSIONAL ICONOGRAPHY (LUCIDE REACT):
   - ZERO-EMOJI RULE: NEVER use emojis (👟, 🛒, 🍔, ⭐, 🚀) as UI icons or graphics. Always use vector Lucide React SVGs with consistent strokeWidth (1.5 or 2) and sizing (w-4 h-4, w-5 h-5).
6. CLEAN TEXT BRANDING:
   - When no logo exists, create clean typographic wordmarks with geometric monogram badges. Never use awkward stickers or mismatched clipart.

{anthropic_block}

{ui_ux_pro_block}

{vercel_block}

{ui_sh_block}

{rb_block}

{intent_block}
"""

    async def process_user_turn(
        self,
        session_id: str,
        user_message: str,
        event_callback: Callable[[dict], Awaitable[None]],
        language: Optional[str] = None,
        run_id: Optional[str] = None
    ):
        import time
        self._cancelled = False
        self._current_run_id = run_id or f"run_{int(time.time()*1000)}"
        self._initial_files_snapshot = self._take_workspace_snapshot()
        manifest = self.project_analyzer.generate_manifest()
        
        await event_callback(create_event(
            "session_started",
            session_id,
            {"workspace": str(self.workspace_path), "manifest": manifest}
        ))

        ignored_names = {
            ".project_manifest.json", "AGENTS.md", ".visual_qa",
            ".generation_state.json", ".git", ".DS_Store", "__pycache__"
        }
        is_continuation = False
        if self.workspace_path.exists():
            existing_files = [f for f in self.workspace_path.iterdir() if f.name not in ignored_names]
            if existing_files:
                is_continuation = True

        design_guidelines = self._get_ui_ux_design_guidelines(user_message)

        task_prompt = user_message
        if language:
            if is_continuation:
                task_prompt = f"""[SYSTEM CONTEXT]
You are modifying an existing project in the current directory. Your workspace root is already set to the project directory.
All files (source code, tests, SRS.md, README.md, etc.) must be written/modified directly in the current directory.
Ensure the project directory contains:
1. SRS.md: Software Requirements Specification document.
2. README.md: Step-by-step instructions on how to install and run the project.
Any path you specify in tool calls MUST be relative to the current directory, starting directly with the filename (e.g. use 'calculator.py', NOT 'workspace/{self.workspace_path.name}/calculator.py'). Do not modify external files.
First, inspect existing files and structure using search_files or get_project_structure to understand the implementation and tests.
Then, implement requested changes, update or add tests, run existing test suite, and resolve any issues.

{design_guidelines}

[USER REQUEST]
{user_message}"""
            else:
                task_prompt = f"""[SYSTEM CONTEXT]
You are implementing a project. Your workspace root is already configured to the project directory.
All files (source code, tests, SRS.md, README.md, etc.) must be written directly in the current directory (or subdirectories relative to it).
CRITICAL REQUIREMENTS:
1. Create 'SRS.md' inside the project folder containing the Software Requirements Specification.
2. Create 'README.md' inside the project folder detailing step-by-step instructions on how to run the project.
Any path you specify in tool calls MUST be relative to the current directory, starting directly with the filename (e.g. use 'calculator.py', NOT 'workspace/{self.workspace_path.name}/calculator.py'). Do not modify external files.
The selected programming language is: {language}.
Plan, write source files, configurations, and tests, run the project, and fix errors until it works correctly.

{design_guidelines}

[USER REQUEST]
{user_message}"""

        has_api_key = bool(self.model_config.get("api_key"))
        provider = self.model_config.get("provider", "ollama")

        if provider in ["google-gemini", "gemini"] and not has_api_key:
            err_msg = (
                "Google Gemini Configuration Error: Missing GEMINI_API_KEY environment variable. "
                "Please configure GEMINI_API_KEY in your environment or .env file before running requests."
            )
            logger.error(err_msg)
            await event_callback(create_event("error", session_id, {"error": err_msg}))
            await event_callback(create_event("agent_finished", session_id, {"status": "error", "error": err_msg}))
            return
        elif provider == "apinex" and not has_api_key:
            err_msg = (
                "APInex Configuration Error: Missing APINEX_API_KEY environment variable. "
                "Please configure APINEX_API_KEY in your environment or .env file before running requests."
            )
            logger.error(err_msg)
            await event_callback(create_event("error", session_id, {"error": err_msg}))
            await event_callback(create_event("agent_finished", session_id, {"status": "error", "error": err_msg}))
            return

        # Initialize structured Execution Plan
        is_web_project = is_web_frontend_project(language, user_message, is_continuation)
        clean_title = (user_message[:45] + "...") if len(user_message) > 45 else user_message
        if is_web_project:
            plan = self.task_manager.create_plan(
                session_id=session_id,
                title=f"Plan: {clean_title}",
                requirement=user_message,
                tasks_data=[
                    {
                        "title": "Phase 1: Architecture & Design Direction",
                        "description": "Creative Director explores archetype, layout grid, typography tokens & design guidelines"
                    },
                    {
                        "title": "Phase 2: Frontend & Component Generation",
                        "description": "Frontend Engineer generates semantic HTML5 markup, responsive CSS and core component layouts"
                    },
                    {
                        "title": "Phase 3: 3D Scene & Interactive Motion",
                        "description": "3D/Motion Engineer integrates WebGL scenes, animations, and progressive enhancement logic"
                    },
                    {
                        "title": "Phase 4: Multi-Viewport Visual QA & Testing",
                        "description": "Visual QA Inspector captures viewport screenshots and validates 14 visual & functional criteria"
                    },
                    {
                        "title": "Phase 5: Build Finalization & Delivery",
                        "description": "Compile standalone project assets, update workspace manifest, and prepare archive package"
                    }
                ]
            )
        else:
            plan = self.task_manager.create_plan(
                session_id=session_id,
                title=f"Plan: {clean_title}",
                requirement=user_message,
                tasks_data=[
                    {
                        "title": "Phase 1: Workspace & Dependency Analysis",
                        "description": "Inspect repository structure, files, package manifests, and environment context"
                    },
                    {
                        "title": "Phase 2: Core Engineering Implementation",
                        "description": "Perform source code modifications, implement architecture, and integrate changes"
                    },
                    {
                        "title": "Phase 3: Automated Verification & Test Suite",
                        "description": "Execute automated test runners, lint checks, and validate runtime health"
                    },
                    {
                        "title": "Phase 4: Documentation & Delivery Verification",
                        "description": "Verify build health, update specifications (SRS.md, README.md), and finalize workspace"
                    }
                ]
            )

        await event_callback(create_event("plan_created", session_id, {"plan": plan.model_dump()}))

        loop = asyncio.get_running_loop()

        async def advance_to_phase(phase_idx: int, error_msg: Optional[str] = None):
            nonlocal plan
            if not plan or not plan.tasks:
                return
            for idx, task in enumerate(plan.tasks):
                if idx < phase_idx:
                    if task.status != TaskStatus.COMPLETED:
                        self.task_manager.update_task_status(session_id, task.id, TaskStatus.COMPLETED)
                        task.status = TaskStatus.COMPLETED
                elif idx == phase_idx:
                    status = TaskStatus.FAILED if error_msg else TaskStatus.IN_PROGRESS
                    self.task_manager.update_task_status(session_id, task.id, status)
                    task.status = status
                    if error_msg:
                        task.error_message = error_msg
                    await event_callback(create_event("task_started" if not error_msg else "task_failed", session_id, {
                        "task_id": task.id,
                        "title": task.title,
                        "plan": plan.model_dump(),
                        "error": error_msg
                    }))
            await event_callback(create_event("plan_updated", session_id, {"plan": plan.model_dump()}))

        async def complete_all_phases():
            nonlocal plan
            if not plan or not plan.tasks:
                return
            for task in plan.tasks:
                self.task_manager.update_task_status(session_id, task.id, TaskStatus.COMPLETED)
                task.status = TaskStatus.COMPLETED
            await event_callback(create_event("task_completed", session_id, {
                "task_id": plan.tasks[-1].id if plan.tasks else None,
                "plan": plan.model_dump()
            }))
            await event_callback(create_event("plan_updated", session_id, {"plan": plan.model_dump()}))

        def orch_status_callback(evt: dict):
            st = evt.get("state")
            msg = evt.get("message")
            pct = evt.get("progress_percent", 0)
            phase_map = {
                "INITIATED": 0,
                "ANALYZING_REFERENCE": 0,
                "EXPLORING_DIRECTIONS": 0,
                "GENERATING_FRONTEND": 1,
                "GENERATING_3D_MOTION": 2,
                "CAPTURING_SCREENSHOTS": 3,
                "PERFORMING_VISUAL_QA": 3,
                "REFINING_CODE": 4,
                "COMPLETED": 4
            }
            target_phase = phase_map.get(st, 0)
            asyncio.run_coroutine_threadsafe(
                event_callback(create_event("generation_status_update", session_id, {
                    "state": st,
                    "message": msg,
                    "progress_percent": pct,
                    "project_name": self.workspace_path.name
                })),
                loop
            )
            asyncio.run_coroutine_threadsafe(
                advance_to_phase(target_phase),
                loop
            )

        # Check if request is a web application creation turn -> Execute MultiAgentOrchestrator
        if is_web_project:
            logger.info(f'Invoking MultiAgentOrchestrator for web application prompt: {user_message}')
            try:
                from server.tools.prompt_reference_parser import PromptReferenceParser
                parsed_prompt = PromptReferenceParser.parse(user_message)
                ref_images = parsed_prompt.get("reference_images", [])

                orchestration_res = await asyncio.to_thread(
                    self.run_multi_agent_orchestration,
                    self.workspace_path.name,
                    user_message,
                    reference_images=ref_images,
                    status_callback=orch_status_callback
                )
                await event_callback(create_event('multi_agent_orchestration_completed', session_id, orchestration_res))

                # Server-enforce Visual QA completion requirement
                qa_report = orchestration_res.get("qa_report", {})
                qa_decision = qa_report.get("decision", "PASS")
                qa_status = orchestration_res.get("status", "SUCCESS")

                if qa_status == "BLOCKED" or qa_decision == "BLOCKED":
                    critical_issues = qa_report.get("critical_issues", ["Visual QA quality criteria failed."])
                    err_summary = "; ".join(critical_issues)
                    logger.error(f"Visual QA enforcement failed for {self.workspace_path.name}: {err_summary}")
                    await advance_to_phase(3, error_msg=f"Visual QA Failed: {err_summary}")
                    qa_fail_msg = f"❌ **Visual QA Quality Gate Blocked**: Project build failed required visual inspections.\n\n**Critical Issues Detected**:\n- " + "\n- ".join(critical_issues)
                    await event_callback(create_event('assistant_message', session_id, {'content': qa_fail_msg, 'is_delta': False}))
                    await event_callback(create_event("agent_finished", session_id, {
                        "status": "failed",
                        "error": f"Visual QA quality criteria not met: {err_summary}"
                    }))
                    return

                await advance_to_phase(4)

                # Ensure index.html exists in root of workspace if created inside subfolder
                sub_index = self.workspace_path / self.workspace_path.name / "index.html"
                root_index = self.workspace_path / "index.html"
                if sub_index.exists() and not root_index.exists():
                    import shutil
                    shutil.copy2(sub_index, root_index)

                proj_name = self.workspace_path.name
                summary_msg = f"✨ **Architecture & Build Complete**: **{proj_name}** has been designed, coded, and verified by NEXARCH Multi-Agent Intelligence.\n\nAll components, responsive styling, and animations are live in your Preview panel."
                await event_callback(create_event('assistant_message', session_id, {'content': summary_msg, 'is_delta': False}))

                try:
                    results = self.compile_project_results()
                    await event_callback(create_event("project_build_completed", session_id, results))
                    if results.get("download_url") and results.get("project_name"):
                        download_msg = f"\n\n📦 **Standalone Package Ready**: Download your complete project: [{results['project_name']}.zip]({results['download_url']})"
                        await event_callback(create_event("assistant_message", session_id, {"content": download_msg, "is_delta": False}))
                except Exception as comp_err:
                    logger.error(f"Error compiling results: {comp_err}")

                await complete_all_phases()
                await event_callback(create_event("agent_finished", session_id, {"status": "completed"}))
                return
            except Exception as orch_err:
                logger.warning(f'MultiAgentOrchestrator execution warning: {provider_manager.sanitize_text(orch_err)}')
        else:
            await advance_to_phase(0)

        # Build full priority chain of candidate providers
        # When no explicit user override is active, strictly adhere to live provider priority:
        # Gemini Key 1 (Primary) -> Gemini Key 2 (First Backup) -> Gemini Key 3 (Second Backup) -> APInex (Final Fallback) -> Ollama
        # Automatically restores Key 1 as primary as soon as its cooldown expires
        if not getattr(self, "_explicit_user_override", False):
            available_ordered = [
                {
                    "provider": p.provider,
                    "provider_id": p.provider_id,
                    "display_name": p.display_name,
                    "model": p.default_model,
                    "api_key": p.api_key,
                    "api_base": p.api_base,
                    "priority": p.priority
                }
                for p in provider_manager.get_ordered_providers()
                if p.is_available()
            ]
            provider_chain = available_ordered if available_ordered else [dict(self.model_config)]
        else:
            provider_chain = []
            if self.model_config.get("api_key") or self.model_config.get("provider") == "ollama":
                provider_chain.append(dict(self.model_config))
            fallback_candidates = self.get_fallback_provider_chain(
                self.model_config.get("provider", ""),
                current_key=self.model_config.get("api_key")
            )
            for fb in fallback_candidates:
                if not any(p.get("provider_id") == fb.get("provider_id") and p.get("api_key") == fb.get("api_key") for p in provider_chain):
                    provider_chain.append(fb)

        success = False
        mid_stream_interrupted = False
        loop = asyncio.get_running_loop()

        for prov_idx, prov_cfg in enumerate(provider_chain):
            if getattr(self, "_cancelled", False):
                break
            if mid_stream_interrupted:
                break

            prov_name = prov_cfg.get("provider", "ollama")
            prov_id = prov_cfg.get("provider_id")
            prov_disp = prov_cfg.get("display_name") or prov_name
            prov_key = prov_cfg.get("api_key", "")
            prov_base = prov_cfg.get("api_base") or None

            # Skip provider if marked AUTH_FAILED or disabled
            p_obj = provider_manager._providers.get(prov_id) if prov_id else None
            if p_obj and not p_obj.is_available():
                logger.info(f"Skipping unavailable provider '{prov_disp}' (Status: {p_obj.status})")
                continue

            # Emit provider status update to UI
            is_primary = (prov_idx == 0)
            status_text = f"Connecting to {prov_disp}..." if is_primary else f"Quota or connection limit reached; switching to backup {prov_disp}..."
            await event_callback(create_event("provider_status", session_id, {
                "provider": prov_name,
                "provider_id": prov_id,
                "display_name": prov_disp,
                "status": "active" if is_primary else "failover",
                "message": status_text
            }))

            streamed_tokens = 0
            tools_executed = 0

            def handle_delta(delta):
                nonlocal streamed_tokens
                if delta:
                    streamed_tokens += 1
                    asyncio.run_coroutine_threadsafe(
                        event_callback(create_event(
                            "assistant_message",
                            session_id,
                            {"content": str(delta)}
                        )),
                        loop
                    )

            def handle_thinking(text):
                if text:
                    asyncio.run_coroutine_threadsafe(
                        event_callback(create_event(
                            "thinking_update",
                            session_id,
                            {"thinking": str(text)}
                        )),
                        loop
                    )

            def handle_tool_start(*args, **kwargs):
                nonlocal tools_executed
                tools_executed += 1
                if len(args) >= 3:
                    tool_name = args[1]
                    tool_args = args[2]
                elif len(args) == 2:
                    tool_name = args[0]
                    tool_args = args[1]
                else:
                    tool_name = kwargs.get("tool_name", "")
                    tool_args = kwargs.get("tool_args", {})

                self.last_started_tool = tool_name
                asyncio.run_coroutine_threadsafe(
                    event_callback(create_event(
                        "tool_started",
                        session_id,
                        {"tool": tool_name, "args": tool_args, "run_id": getattr(self, "_current_run_id", None)}
                    )),
                    loop
                )

            def handle_tool_complete(*args, **kwargs):
                if len(args) >= 4:
                    tool_name = args[1]
                    tool_result = args[3]
                elif len(args) == 2:
                    tool_name = args[0]
                    tool_result = args[1]
                else:
                    tool_name = kwargs.get("tool_name", "")
                    tool_result = kwargs.get("tool_result", "")

                asyncio.run_coroutine_threadsafe(
                    event_callback(create_event(
                        "tool_output",
                        session_id,
                        {"tool": tool_name, "result": tool_result, "run_id": getattr(self, "_current_run_id", None)}
                    )),
                    loop
                )

            candidate_models = self.get_candidate_models_for_provider(prov_name, prov_cfg.get("model"))[:2]
            for model_candidate in candidate_models:
                if getattr(self, "_cancelled", False):
                    break
                try:
                    logger.info(f"Attempting turn execution with [{prov_disp}] model: {model_candidate}")
                    agent = run_agent.AIAgent(
                        model=model_candidate,
                        provider=prov_name,
                        api_key=prov_key,
                        base_url=prov_base,
                        session_id=session_id,
                        enabled_toolsets=["development"],
                        stream_delta_callback=handle_delta,
                        thinking_callback=handle_thinking,
                        tool_start_callback=handle_tool_start,
                        tool_complete_callback=handle_tool_complete
                    )
                    agent._ollama_num_ctx = 64000
                    
                    turn_timeout = float(os.getenv("TURN_TIMEOUT_SECONDS", "300"))
                    result = await asyncio.wait_for(
                        loop.run_in_executor(
                            None,
                            lambda: agent.run_conversation(user_message=task_prompt)
                        ),
                        timeout=turn_timeout
                    )

                    final_text = str(result.get("response") or result.get("content") or "Task completed.")
                    await event_callback(create_event("assistant_message", session_id, {"content": final_text}))
                    self.model_config = prov_cfg
                    self.model_config["model"] = model_candidate
                    if prov_id:
                        provider_manager.mark_success(prov_id)
                    success = True
                    break
                except asyncio.CancelledError:
                    self._cancelled = True
                    logger.info("Turn run cancelled by user request.")
                    break
                except Exception as exc:
                    err_class, sanitized_err = provider_manager.classify_error(exc)
                    if prov_id:
                        provider_manager.mark_failure(prov_id, exc)
                    logger.warning(
                        f"Provider '{prov_disp}' model '{model_candidate}' failed ({err_class}): {sanitized_err}"
                    )

                    # Mid-stream check: If content was partially streamed or tools executed, do NOT duplicate output
                    if streamed_tokens > 0 or tools_executed > 0:
                        mid_stream_interrupted = True
                        logger.warning(
                            f"Mid-stream failure occurred on '{prov_disp}' after {streamed_tokens} tokens and {tools_executed} tool invocations. "
                            "Preserving existing workspace changes and halting automatic retry to avoid duplication."
                        )
                        interrupted_msg = (
                            f"\n\n⚠️ **Generation Interrupted**: Connection to {prov_disp} was interrupted mid-stream ({sanitized_err}). "
                            "All workspace modifications up to this point have been preserved. You can submit another message to continue."
                        )
                        await event_callback(create_event("assistant_message", session_id, {"content": interrupted_msg}))
                        await event_callback(create_event("error", session_id, {"error": f"Generation interrupted mid-stream: {sanitized_err}"}))
                        break

                    # Fail fast to next provider on quota or auth errors
                    if err_class in (ErrorClass.QUOTA_EXHAUSTED, ErrorClass.AUTH_FAILURE):
                        break

            if success:
                logger.info(f"Turn successfully completed with provider '{prov_disp}'")
                break

        if getattr(self, "_cancelled", False):
            await event_callback(create_event("agent_finished", session_id, {"status": "cancelled"}))
            return

        if mid_stream_interrupted:
            await event_callback(create_event("agent_finished", session_id, {"status": "interrupted"}))
            return

        if not success:
            all_fail_msg = "All configured AI providers are temporarily unavailable. Your request could not be completed right now. Please try again later."
            logger.error(all_fail_msg)
            await event_callback(create_event("assistant_message", session_id, {"content": f"⚠️ {all_fail_msg}"}))
            await event_callback(create_event("error", session_id, {"error": all_fail_msg}))
            await event_callback(create_event("agent_finished", session_id, {"status": "error", "error": all_fail_msg}))
            return

        # Server-enforce Visual QA completion requirement if this was a web project
        if is_web_project:
            logger.info(f"Enforcing Visual QA completion requirement for web project '{self.workspace_path.name}'...")
            try:
                v_qa = self.visual_qa_tools.run_full_visual_qa(self.workspace_path.name, self.model_config, auto_refine=True)
                await event_callback(create_event("tool_output", session_id, {"tool": "run_visual_qa", "result": v_qa}))
                screenshots = v_qa.get("screenshots", {}) if isinstance(v_qa, dict) else {}
                blank_detected = screenshots.get("blank_page_detected", False)
                console_errors = screenshots.get("console_errors", [])
                has_fatal_err = any("TypeError" in e or "ReferenceError" in e or "SyntaxError" in e for e in console_errors)
                if not v_qa.get("passed", True) or blank_detected or has_fatal_err:
                    issues = v_qa.get("issues", []) if isinstance(v_qa, dict) else []
                    if blank_detected:
                        issues.append("Blank page detected: DOM body has no visible content.")
                    if has_fatal_err:
                        issues.append(f"Fatal browser console errors: {console_errors[0]}")
                    err_summary = "; ".join(issues) if issues else "Visual QA quality criteria not met."
                    logger.error(f"Visual QA checks failed in fallback path for {self.workspace_path.name}: {err_summary}")
                    await advance_to_phase(3, error_msg=f"Visual QA Failed: {err_summary}")
                    await event_callback(create_event("assistant_message", session_id, {
                        "content": f"❌ **Visual QA Quality Gate Blocked**: Project build failed required visual inspection.\n\n**Issues Detected**:\n- " + "\n- ".join(issues)
                    }))
                    await event_callback(create_event("agent_finished", session_id, {"status": "failed", "error": f"Visual QA quality criteria not met: {err_summary}"}))
                    return
            except Exception as v_err:
                logger.warning(f"Visual QA inspection note in fallback path: {v_err}")

        try:
            results = self.compile_project_results()
            await event_callback(create_event("project_build_completed", session_id, results))
            if results.get("download_url") and results.get("project_name"):
                download_msg = f"\n\n📦 **Project Build Complete!**\nDownload your complete project archive: [{results['project_name']}.zip]({results['download_url']})"
                await event_callback(create_event("assistant_message", session_id, {"content": download_msg}))
        except Exception as e:
            logger.error(f"Error compiling project results: {e}")

        await complete_all_phases()
        await event_callback(create_event("agent_finished", session_id, {"status": "completed"}))

    async def _run_autonomous_workspace_turn(
        self,
        session_id: str,
        user_message: str,
        event_callback: Callable[[dict], Awaitable[None]]
    ):
        manifest = self.project_analyzer.generate_manifest()
        
        plan = self.task_manager.create_plan(
            session_id=session_id,
            title="Software Development Plan",
            requirement=user_message,
            tasks_data=[
                {"title": "Analyze Workspace & Dependencies", "description": "Inspect repository structure"},
                {"title": "Execute Development Operation", "description": "Perform code modifications or command execution"},
                {"title": "Verify Build & Test Suite", "description": "Run automated test and lint checks"},
                {"title": "Visual QA & Aesthetic Refinement", "description": "Audit design system, typography, and responsive viewports"}
            ]
        )

        await event_callback(create_event("plan_created", session_id, {"plan": plan.model_dump()}))

        # Task 1: Analyze workspace
        t1 = plan.tasks[0]
        self.task_manager.update_task_status(session_id, t1.id, TaskStatus.IN_PROGRESS)
        await event_callback(create_event("task_started", session_id, {"task_id": t1.id, "title": t1.title}))
        
        struct_res = self.structure_analyzer.get_project_structure()
        await event_callback(create_event("tool_output", session_id, {"tool": "get_project_structure", "result": struct_res}, task_id=t1.id))
        self.task_manager.update_task_status(session_id, t1.id, TaskStatus.COMPLETED)
        await event_callback(create_event("task_completed", session_id, {"task_id": t1.id, "title": t1.title}))

        # Task 2: Action based on request intent
        t2 = plan.tasks[1]
        self.task_manager.update_task_status(session_id, t2.id, TaskStatus.IN_PROGRESS)
        await event_callback(create_event("task_started", session_id, {"task_id": t2.id, "title": t2.title}))

        self._ensure_web_app_boilerplate(user_message)
        res = self.testing_tools.run_tests()
        await event_callback(create_event("tool_output", session_id, {"tool": "run_tests", "result": res}, task_id=t2.id))
        self.task_manager.update_task_status(session_id, t2.id, TaskStatus.COMPLETED)
        await event_callback(create_event("task_completed", session_id, {"task_id": t2.id, "title": t2.title}))

        # Task 3: Health and linter
        t3 = plan.tasks[2]
        self.task_manager.update_task_status(session_id, t3.id, TaskStatus.IN_PROGRESS)
        await event_callback(create_event("task_started", session_id, {"task_id": t3.id, "title": t3.title}))
        
        health_summary = self.health_tools.check_project_health()
        await event_callback(create_event("tool_output", session_id, {"tool": "check_project_health", "result": health_summary}, task_id=t3.id))
        self.task_manager.update_task_status(session_id, t3.id, TaskStatus.COMPLETED if health_summary.get("build_healthy", True) else TaskStatus.FAILED)
        await event_callback(create_event("task_completed", session_id, {"task_id": t3.id, "title": t3.title}))

        # Task 4: Visual QA Audit
        t4 = plan.tasks[3]
        if len(plan.tasks) > 3:
            self.task_manager.update_task_status(session_id, t4.id, TaskStatus.IN_PROGRESS)
            await event_callback(create_event("task_started", session_id, {"task_id": t4.id, "title": t4.title}))
            
            v_qa = self.visual_qa_tools.run_full_visual_qa(self.workspace_path.name, self.model_config)
            await event_callback(create_event("tool_output", session_id, {"tool": "run_visual_qa", "result": v_qa}, task_id=t4.id))
            self.task_manager.update_task_status(session_id, t4.id, TaskStatus.COMPLETED if v_qa.get("passed", True) else TaskStatus.FAILED)
            await event_callback(create_event("task_completed", session_id, {"task_id": t4.id, "title": t4.title}))

        response_md = (
            f"### Hermes Autonomous Software Development Response\n\n"
            f"Analyzed repository `{manifest.get('name', 'workspace')}` ({', '.join(manifest.get('languages', [])) or 'Multi-language'}).\n\n"
            f"**Project Health Overview**: Build: {'✓' if health_summary.get('build_healthy') else '✗'}, Tests: {'✓' if health_summary.get('tests_healthy') else '✗'}, Lint: {'✓' if health_summary.get('lint_healthy') else '✗'}"
        )
        await event_callback(create_event("assistant_message", session_id, {"content": response_md}))

    def _ensure_web_app_boilerplate(self, user_message: str):
        """Ensures a valid domain-appropriate project structure exists without contaminating React/Vite or backend projects."""
        # 1. Guard against contaminating backend projects
        backend_markers = ["*.py", "*.go", "*.rs", "Cargo.toml", "go.mod", "requirements.txt", "Pipfile", "pom.xml"]
        for marker in backend_markers:
            if list(self.workspace_path.glob(marker)):
                logger.info(f"Skipping web app boilerplate: backend marker '{marker}' detected in {self.workspace_path.name}")
                return

        # 2. Guard against contaminating React / Vite projects
        pkg_json = self.workspace_path / "package.json"
        is_react_or_vite = (
            pkg_json.exists() or
            (self.workspace_path / "vite.config.js").exists() or
            (self.workspace_path / "vite.config.ts").exists() or
            bool(list(self.workspace_path.glob("src/**/*.jsx"))) or
            bool(list(self.workspace_path.glob("src/**/*.tsx")))
        )
        if is_react_or_vite:
            # Respect React / Vite project structure: do NOT inject static app.js / style.css
            root_index = self.workspace_path / "index.html"
            sub_index = self.workspace_path / self.workspace_path.name / "index.html"
            if sub_index.exists() and not root_index.exists():
                import shutil
                shutil.copy2(sub_index, root_index)
                return

            if not root_index.exists():
                # If Vite project has main entry point, write Vite-compatible index.html
                if (self.workspace_path / "src" / "main.jsx").exists() or (self.workspace_path / "src" / "App.jsx").exists():
                    title_clean = self.workspace_path.name.replace("_", " ").title()
                    vite_html = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title_clean}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>"""
                    self.file_tools.write_file("index.html", vite_html)
            return

        # 3. For vanilla web projects missing entry point
        if not (self.workspace_path / "index.html").exists():
            title_clean = self.workspace_path.name.replace("_", " ").title()
            logger.warning(
                "Generation entry point missing for workspace '%s'. Initializing domain-specific intent boilerplate fallback for prompt: '%s'",
                self.workspace_path.name,
                user_message
            )
            html, css, js, srs, readme = self.product_intent_classifier.generate_domain_boilerplate(user_message, title_clean)
            self.file_tools.write_file("index.html", html)
            self.file_tools.write_file("style.css", css)
            self.file_tools.write_file("app.js", js)
            self.file_tools.write_file("SRS.md", srs)
            self.file_tools.write_file("README.md", readme)
