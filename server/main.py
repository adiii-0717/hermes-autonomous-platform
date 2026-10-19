from dotenv import load_dotenv
load_dotenv()
import os
import sys
import time
import json
import httpx
import re
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional
import shutil
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query, Body, Request, Response
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from server.project.project_server_manager import project_server_manager
from server.hermes_adapter import HermesAgentAdapter
from server.agents.provider_manager import provider_manager
from server.tasks import create_event

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main_server")

app = FastAPI(
    title="Hermes Autonomous Software Development Platform",
    version="3.0.0",
    description="Software Development Agent product built around Hermes Agent engine."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WORKSPACE_DIR = os.getenv("HERMES_WORKSPACE", str(PROJECT_ROOT))
adapter = HermesAgentAdapter(WORKSPACE_DIR)

active_websockets: List[WebSocket] = []

# Persistent sessions DB
SESSIONS_DB_FILE = PROJECT_ROOT / ".sessions_db.json"
sessions_db: Dict[str, dict] = {}

if SESSIONS_DB_FILE.exists():
    try:
        sessions_db = json.loads(SESSIONS_DB_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning(f"Error loading persistent sessions DB: {e}")

def save_sessions_db():
    try:
        with open(SESSIONS_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(sessions_db, f, indent=2)
    except Exception as e:
        logger.warning(f"Error saving sessions DB: {e}")

async def broadcast_event(event: dict):
    for ws in list(active_websockets):
        try:
            await ws.send_json(event)
        except Exception:
            if ws in active_websockets:
                active_websockets.remove(ws)

adapter.approval_controller.register_broadcast_callback(broadcast_event)

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ApprovalResolveRequest(BaseModel):
    request_id: str
    approved: bool

class FileSaveRequest(BaseModel):
    path: str
    content: str

class ModelConfigRequest(BaseModel):
    provider: Optional[str] = None
    model: Optional[str] = None
    api_key: Optional[str] = None
    api_base: Optional[str] = None


@app.post("/api/providers/reload")
async def reload_providers():
    """Explicitly reload provider configuration from .env and restore healthy status for corrected keys."""
    provider_manager.reload_from_env()
    adapter.model_config = adapter.normalize_model_config()
    return {
        "status": "success",
        "message": "Providers reloaded from environment",
        "providers": provider_manager.get_summary()
    }

@app.get("/api/providers/status")
async def get_providers_status():
    """Diagnostic endpoint returning health, priority, and cooldown status of all configured LLM providers."""
    return {"providers": provider_manager.get_summary()}

@app.get("/api/health")
async def health_check():
    key = adapter.model_config.get("api_key", "")
    return {
        "status": "online",
        "framework": "Hermes Agent Framework (NousResearch/hermes-agent)",
        "workspace": str(adapter.workspace_path),
        "model_provider": adapter.model_config.get("provider"),
        "model_name": adapter.model_config.get("model"),
        "api_base": adapter.model_config.get("api_base"),
        "api_key_configured": bool(key)
    }

@app.get("/api/config")
async def get_model_config():
    cfg = adapter.model_config.copy()
    key = cfg.get("api_key", "")
    key_configured = bool(key)
    masked_key = (key[:4] + "..." + key[-4:]) if len(key) > 8 else ("***" if key else "Not set")
    cfg["api_key_configured"] = key_configured
    cfg["api_key_masked"] = masked_key
    cfg.pop("api_key", None)
    return cfg

@app.post("/api/config")
async def update_model_config(req: ModelConfigRequest):
    new_cfg = {}
    if req.provider is not None:
        new_cfg["provider"] = req.provider
    if req.model is not None:
        new_cfg["model"] = req.model
    if req.api_key is not None:
        new_cfg["api_key"] = req.api_key
    if req.api_base is not None:
        new_cfg["api_base"] = req.api_base

    merged = {**adapter.model_config, **new_cfg}
    adapter.set_model_config(merged)

    return {
        "status": "success",
        "message": "Model configuration updated",
        "provider": adapter.model_config.get("provider"),
        "model": adapter.model_config.get("model"),
        "api_base": adapter.model_config.get("api_base"),
        "api_key_configured": bool(adapter.model_config.get("api_key"))
    }

@app.get("/api/sessions")
async def get_sessions():
    return {"sessions": list(sessions_db.values())}

@app.post("/api/sessions")
async def create_session(session_name: str = Body(default="default_session", embed=True)):
    session_id = f"session_{len(sessions_db) + 1}_{os.urandom(4).hex()}"
    session_data = {
        "session_id": session_id,
        "name": session_name,
        "workspace": str(adapter.workspace_path),
        "created_at": str(asyncio.get_event_loop().time())
    }
    sessions_db[session_id] = session_data
    save_sessions_db()
    return session_data

@app.post("/api/chat")
async def chat_post_endpoint(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
        
    responses = []
    async def collect_events(evt: dict):
        responses.append(evt)
        await broadcast_event(evt)

    user_msg = req.message.strip()
    current_language = None
    current_workspace = None
    try:
        is_creation = bool(re.search(r'\b(build|create|make|generate|start|develop|design)\b', user_msg, re.IGNORECASE) or 'new project' in user_msg.lower())
        matches = [] if is_creation else adapter.find_matching_projects(user_msg)
        if len(matches) == 1:
            current_workspace = Path(matches[0]["path"])
            current_language = matches[0]["language"].lower() if matches[0]["language"] else None
            adapter.set_workspace_path(str(current_workspace))
        else:
            metadata = await adapter.analyze_prompt_for_project(user_msg)
            proj_name = metadata.get("project_name", "temp_project")
            detected_lang = metadata.get("language") or "html"
            current_language = detected_lang
            current_workspace = PROJECT_ROOT / "workspace" / proj_name
            current_workspace.mkdir(parents=True, exist_ok=True)
            adapter.set_workspace_path(str(current_workspace))

        run_id = f"run_{int(time.time()*1000)}"
        p_name = current_workspace.name if current_workspace else None
        await broadcast_event(create_event("run_started", req.session_id, {"run_id": run_id, "prompt": user_msg, "project_name": p_name}))

        await adapter.process_user_turn(req.session_id, user_msg, collect_events, language=current_language, run_id=run_id)
        await broadcast_event(create_event("run_completed", req.session_id, {"run_id": run_id, "status": "COMPLETED"}))
    except Exception as turn_exc:
        sanitized = provider_manager.sanitize_text(str(turn_exc))
        logger.error(f"Error in chat endpoint: {sanitized}")
        err_evt = create_event("error", req.session_id, {"error": sanitized})
        await broadcast_event(err_evt)
        responses.append(err_evt)
        await broadcast_event(create_event("agent_finished", req.session_id, {"status": "error"}))

    return {"session_id": req.session_id, "events": responses}

class WorkspaceRequest(BaseModel):
    path: str

@app.get("/api/workspace")
async def get_workspace_info():
    return {
        "workspace_root": str(adapter.workspace_path),
        "exists": adapter.workspace_path.exists(),
        "is_git_repo": (adapter.workspace_path / ".git").exists()
    }

@app.post("/api/workspace")
async def set_workspace_info(req: WorkspaceRequest):
    try:
        target = Path(req.path).resolve()
        if not target.exists():
            raise HTTPException(status_code=400, detail=f"Workspace path '{req.path}' does not exist.")
        adapter.set_workspace_path(str(target))
        return {
            "status": "updated",
            "workspace_root": str(target)
        }
    except HTTPException:
        raise
    except Exception as exc:
        import traceback
        trace = traceback.format_exc()
        print(f"Error in set_workspace_info:\n{trace}")
        raise HTTPException(status_code=500, detail=f"{type(exc).__name__}: {exc}")

@app.get("/api/workspace/manifest")
async def get_workspace_manifest():
    return adapter.project_analyzer.generate_manifest()

@app.get("/api/workspace/health")
async def get_project_health():
    return adapter.health_tools.check_project_health()

@app.get("/api/workspace/structure")
async def get_project_structure(path: str = "."):
    return {"structure": adapter.structure_analyzer.get_project_structure(path)}

@app.get("/api/workspace/review")
async def get_code_review():
    return adapter.review_tools.review_changes()

@app.get("/api/workspace/impact")
async def get_change_impact(symbol: str = Query(...), file: Optional[str] = Query(None)):
    return adapter.ast_tools.analyze_change_impact(symbol, file)

@app.get("/api/workspace/related_tests")
async def get_related_tests(file: str = Query(...)):
    return {"target_file": file, "related_tests": adapter.testing_tools.find_related_tests(file)}

@app.get("/api/tasks")
async def get_active_tasks(session_id: Optional[str] = Query(None)):
    if session_id:
        plan = adapter.task_manager.get_plan(session_id)
    else:
        plans = list(adapter.task_manager.active_plans.values())
        plan = plans[-1] if plans else None
    if not plan:
        return {"session_id": session_id, "plan": None}
    return {"session_id": session_id, "plan": plan.model_dump()}

@app.get("/api/workspace/files")
async def list_files(subpath: str = "."):
    valid, resolved, err = adapter.workspace_guard.validate_path(subpath)
    if not valid:
        raise HTTPException(status_code=403, detail=err)
        
    def build_tree(path: Path) -> List[dict]:
        items = []
        try:
            for entry in sorted(os.listdir(path)):
                if entry in [".git", "__pycache__", "node_modules", "venv", ".venv", "dist", "build"]:
                    continue
                full = path / entry
                rel = str(full.relative_to(adapter.workspace_path))
                if full.is_dir():
                    items.append({
                        "name": entry,
                        "path": rel,
                        "type": "directory",
                        "children": build_tree(full)
                    })
                else:
                    items.append({
                        "name": entry,
                        "path": rel,
                        "type": "file"
                    })
        except Exception as e:
            logger.error(f"Error listing directory {path}: {e}")
        return items

    tree = build_tree(resolved if resolved.is_dir() else resolved.parent)
    return {"workspace": str(adapter.workspace_path), "files": tree}

@app.get("/api/workspace/file")
async def get_file_content(path: str = Query(...)):
    valid, resolved, err = adapter.workspace_guard.validate_path(path)
    if not valid:
        raise HTTPException(status_code=403, detail=err)
        
    if not resolved.exists() or not resolved.is_file():
        raise HTTPException(status_code=404, detail=f"File '{path}' not found.")
        
    try:
        with open(resolved, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        return {"path": path, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/workspace/file")
async def save_file_content(req: FileSaveRequest):
    valid, resolved, err = adapter.workspace_guard.validate_path(req.path)
    if not valid:
        raise HTTPException(status_code=403, detail=err)
        
    try:
        resolved.parent.mkdir(parents=True, exist_ok=True)
        with open(resolved, "w", encoding="utf-8") as f:
            f.write(req.content)
        return {"status": "success", "path": req.path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects")
async def list_projects():
    workspace_dir = PROJECT_ROOT / "workspace"
    projects = []
    if workspace_dir.exists():
        dirs = [item for item in workspace_dir.iterdir() if item.is_dir() and not item.name.startswith(".")]
        dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)
        for item in dirs:
            projects.append({
                "name": item.name,
                "download_url": f"/api/projects/{item.name}/download",
                "preview_url": f"/preview/{item.name}/",
                "mtime": item.stat().st_mtime
            })
    return {"projects": projects}

@app.delete("/api/projects/{project_name}")
async def delete_project(project_name: str):
    valid, resolved, err = adapter.workspace_guard.validate_path(f"workspace/{project_name}")
    if not valid:
        if adapter.workspace_path.name == project_name:
            resolved = adapter.workspace_path
        else:
            raise HTTPException(status_code=403, detail=err)

    if not resolved.exists():
        raise HTTPException(status_code=404, detail=f"Project directory '{project_name}' not found.")

    try:
        # If currently active workspace is this project, reset to root workspace
        if adapter.workspace_path.resolve() == resolved.resolve():
            base_ws = PROJECT_ROOT / "workspace"
            adapter.set_workspace_path(str(base_ws))

        if resolved.is_dir():
            shutil.rmtree(resolved)
        elif resolved.is_file():
            resolved.unlink()

        zip_path = PROJECT_ROOT / "workspace" / f"{project_name}.zip"
        if zip_path.exists():
            zip_path.unlink()

        logger.info(f"Project '{project_name}' deleted successfully.")
        return {"success": True, "message": f"Project '{project_name}' deleted successfully."}
    except Exception as exc:
        logger.error(f"Failed to delete project '{project_name}': {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to delete project: {str(exc)}")





@app.api_route("/preview/{project_name}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"])
@app.api_route("/preview/{project_name}/", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"])
@app.api_route("/preview/{project_name}/{file_path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"])
async def preview_project_file(project_name: str, request: Request, file_path: str = ""):
    clean_file_path = file_path.lstrip("/")
    logger.info(f"PREVIEW REQUEST: project={project_name}, file_path={file_path}, clean={clean_file_path}")

    server_info = project_server_manager.ensure_project_server(project_name)
    if server_info.get("status") == "FAILED" or not server_info.get("port"):
        err_msg = server_info.get("error") or "Unknown server startup failure"
        logs_html = "<br>".join(server_info.get("logs", [])[-10:])
        return Response(
            content=f"""<!DOCTYPE html><html><head><title>Preview Error</title></head><body style="font-family:sans-serif;padding:2rem;background:#0d1117;color:#f85149;"><h2>Preview Server Failed to Start</h2><p>{err_msg}</p><pre style="background:#161b22;padding:1rem;border-radius:6px;color:#c9d1d9;">{logs_html}</pre></body></html>""",
            status_code=502,
            media_type="text/html"
        )

    port = server_info["port"]
    target_base = f"http://127.0.0.1:{port}"

    headers = dict(request.headers)
    headers.pop("host", None)
    headers.pop("accept-encoding", None)

    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        # Formulate candidate target URLs
        candidates = []
        if server_info.get("server_type") == "vite":
            candidates.append(f"{target_base}/preview/{project_name}/{clean_file_path}")
        candidates.append(f"{target_base}/{clean_file_path}")

        resp = None
        for target_url in candidates:
            try:
                resp = await client.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    params=dict(request.query_params),
                    content=await request.body()
                )
                if resp.status_code != 404:
                    break
            except Exception as exc:
                logger.error(f"Proxy request attempt to {target_url} failed: {exc}")

        if resp is None:
            # Fallback to local static file if available
            target_path = PROJECT_ROOT / "workspace" / project_name / (clean_file_path or "index.html")
            if target_path.exists() and target_path.is_file():
                return FileResponse(str(target_path))
            sub_target = PROJECT_ROOT / "workspace" / project_name / project_name / (clean_file_path or "index.html")
            if sub_target.exists() and sub_target.is_file():
                return FileResponse(str(sub_target))
            return Response(content="Proxy connection error", status_code=502)

    content_type = resp.headers.get("content-type", "")
    response_body = resp.content

    if "text/html" in content_type:
        try:
            html_text = resp.text
            prefix = f"/preview/{project_name}/"

            def rewrite_url(match):
                attr = match.group(1)
                quote = match.group(2)
                path = match.group(3)
                if path.startswith(prefix) or path.startswith("//") or path.startswith("http"):
                    return f"{attr}={quote}{path}{quote}"
                return f"{attr}={quote}{prefix}{path.lstrip('/')}{quote}"

            html_text = re.sub(r"""(src|href|action)=(["'])/(?!/)(.*?)\2""", rewrite_url, html_text)

            if "<head>" in html_text and f'base href="{prefix}"' not in html_text:
                html_text = html_text.replace("<head>", f'<head><base href="{prefix}">', 1)

            response_body = html_text.encode("utf-8")
        except Exception as e:
            logger.warning(f"HTML rewrite failed for {project_name}: {e}")

    resp_headers = {}
    for k, v in resp.headers.items():
        if k.lower() not in ("content-length", "content-encoding", "transfer-encoding"):
            resp_headers[k] = v

    return Response(
        content=response_body,
        status_code=resp.status_code,
        headers=resp_headers,
        media_type=content_type
    )

@app.get("/@vite/client")
@app.get("/@fs/{file_path:path}")
@app.get("/@id/{file_path:path}")
async def vite_fallback_assets(request: Request, file_path: str = ""):
    active_servers = [s for s in project_server_manager.servers.values() if s.get("status") == "READY"]
    if active_servers:
        target_base = f"http://127.0.0.1:{active_servers[-1]['port']}"
        target_url = f"{target_base}{request.url.path}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(target_url, params=dict(request.query_params))
                return Response(content=resp.content, status_code=resp.status_code, media_type=resp.headers.get("content-type"))
            except Exception:
                pass
    raise HTTPException(status_code=404, detail="Vite asset not found")


@app.get("/api/projects/{project_name}/download")
async def download_project_zip(project_name: str):
    valid, resolved, err = adapter.workspace_guard.validate_path(f"workspace/{project_name}")
    if not valid:
        if adapter.workspace_path.name == project_name:
            resolved = adapter.workspace_path
        else:
            raise HTTPException(status_code=403, detail=err)

    if not resolved.exists():
        raise HTTPException(status_code=404, detail=f"Project directory '{project_name}' not found.")

    zip_base = PROJECT_ROOT / "workspace" / f"{project_name}"
    zip_path = PROJECT_ROOT / "workspace" / f"{project_name}.zip"

    # Zip the project directory cleanly
    shutil.make_archive(
        str(zip_base),
        'zip',
        root_dir=str(resolved.parent),
        base_dir=resolved.name
    )

    return FileResponse(
        path=zip_path,
        filename=f"{project_name}.zip",
        media_type="application/zip"
    )

@app.get("/api/workspace/download")
async def download_current_workspace_zip():
    project_name = adapter.workspace_path.name
    return await download_project_zip(project_name)

class ApprovalRespondRequest(BaseModel):
    approved: bool

class ApprovalCreateRequest(BaseModel):
    action_type: str = "HIGH_RISK_TERMINAL_COMMAND"
    command: str = "rm -rf /tmp/test_dir"
    timeout: float = 10.0

@app.post("/api/approval/request")
async def create_approval_request(req: ApprovalCreateRequest):
    loop = asyncio.get_running_loop()
    task = loop.create_task(
        adapter.approval_controller.request_approval(
            action_type=req.action_type,
            details={"command": req.command, "workspace": str(adapter.workspace_path)},
            timeout=req.timeout
        )
    )
    await asyncio.sleep(0.1)
    pending_ids = list(adapter.approval_controller.pending_approvals.keys())
    if not pending_ids:
        raise HTTPException(status_code=500, detail="Failed to initiate approval request.")
    req_id = pending_ids[-1]
    return {"status": "created", "request_id": req_id}

@app.post("/api/approval/resolve")
async def resolve_approval(req: ApprovalResolveRequest):
    success = adapter.approval_controller.resolve_approval(req.request_id, req.approved)
    if not success:
        raise HTTPException(status_code=404, detail="Approval request not found or already resolved.")
    return {"status": "resolved", "request_id": req.request_id, "approved": req.approved}

@app.post("/api/approvals/{request_id}/respond")
async def respond_approval_endpoint(request_id: str, req: ApprovalRespondRequest):
    success = adapter.approval_controller.resolve_approval(request_id, req.approved)
    if not success:
        raise HTTPException(status_code=404, detail="Approval request not found or already resolved.")
    return {"status": "resolved", "request_id": request_id, "approved": req.approved}

class WebSocketKeepaliveContext:
    def __init__(self, session_id, event_handler):
        self.session_id = session_id
        self.event_handler = event_handler
        self.keepalive_active = False
        self.keepalive_task = None
        self.status = "working"

    async def __aenter__(self):
        self.keepalive_active = True
        self.keepalive_task = asyncio.create_task(self._send_keepalives())
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.keepalive_active = False
        if self.keepalive_task:
            self.keepalive_task.cancel()
            try:
                await self.keepalive_task
            except asyncio.CancelledError:
                pass

    async def _send_keepalives(self):
        start_time = time.monotonic()
        interval = float(os.getenv("HERMES_KEEPALIVE_INTERVAL", "15"))
        while self.keepalive_active:
            try:
                await asyncio.sleep(interval)
                if not self.keepalive_active:
                    break
                elapsed = int(time.monotonic() - start_time)
                if self.status == "analyzing_request":
                    payload = create_event(
                        "agent_heartbeat",
                        self.session_id,
                        {
                            "status": "analyzing_request",
                            "elapsed_seconds": elapsed,
                            "latest_tool": None
                        }
                    )
                else:
                    latest_tool = getattr(adapter, "last_started_tool", None)
                    payload = create_event(
                        "agent_heartbeat",
                        self.session_id,
                        {
                            "status": "working",
                            "elapsed_seconds": elapsed,
                            "latest_tool": latest_tool
                        }
                    )
                await self.event_handler(payload)
            except Exception as keepalive_err:
                logger.error(f"Keepalive failed: {keepalive_err}")
                break


@app.websocket("/ws")
@app.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    async def safe_send(ws: WebSocket, event: dict):
        try:
            await ws.send_json(event)
        except Exception:
            if ws in active_websockets:
                try:
                    active_websockets.remove(ws)
                except ValueError:
                    pass

    async def execute_turn_with_guard(session_id, prompt, event_handler, lang, run_id, ws):
        try:
            await adapter.process_user_turn(session_id, prompt, event_handler, language=lang, run_id=run_id)
            await broadcast_event(create_event("run_completed", session_id, {"run_id": run_id, "status": "COMPLETED"}))
        except asyncio.CancelledError:
            logger.info(f"Turn run {run_id} cancelled.")
            await broadcast_event(create_event("run_completed", session_id, {"run_id": run_id, "status": "CANCELLED"}))
            await broadcast_event(create_event("agent_finished", session_id, {"status": "cancelled"}))
        except Exception as turn_exc:
            sanitized = provider_manager.sanitize_text(str(turn_exc))
            logger.error(f"Error during turn processing for {run_id}: {sanitized}")
            await broadcast_event(create_event("error", session_id, {"error": f"Request processing failed: {sanitized}"}))
            await broadcast_event(create_event("run_completed", session_id, {"run_id": run_id, "status": "FAILED", "error": sanitized}))
            await broadcast_event(create_event("agent_finished", session_id, {"status": "error", "error": sanitized}))

    await websocket.accept()
    active_websockets.append(websocket)
    session_id = f"session_{id(websocket)}"
    
    current_workspace = None
    current_language = None
    
    try:
        await websocket.send_json(create_event(
            "session_started",
            session_id,
            {"workspace": str(adapter.workspace_path), "manifest": adapter.project_analyzer.generate_manifest()}
        ))
        
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type") or data.get("event")
            
            if message_type in ["user_message", "user_input"]:
                user_msg = data.get("content", "").strip() or data.get("data", {}).get("message", "").strip()
                original_prompt = user_msg
                if not user_msg:
                    continue
                
                async def event_handler(evt: dict):
                    await broadcast_event(evt)

                async with WebSocketKeepaliveContext(session_id, event_handler) as keepalive_ctx:
                    keepalive_ctx.status = "analyzing_request"
                    
                    is_creation = bool(re.search(r'\b(build|create|make|generate|start|develop|design)\b', user_msg, re.IGNORECASE) or 'new project' in user_msg.lower())
                    if is_creation or current_workspace is None:
                        # Discover and check for matching existing projects if not a fresh creation prompt
                        matches = [] if is_creation else adapter.find_matching_projects(user_msg)
                        if len(matches) == 1:
                            # Exact match: continue existing project
                            proj_name = matches[0]["name"]
                            current_workspace = Path(matches[0]["path"])
                            current_language = matches[0]["language"].lower() if matches[0]["language"] else None
                            adapter.set_workspace_path(str(current_workspace))
                        elif len(matches) > 1:
                            # Ambiguous: ask user to disambiguate
                            await broadcast_event(create_event(
                                "project_selection_required",
                                session_id,
                                {
                                    "projects": [m["name"] for m in matches],
                                    "prompt": user_msg
                                }
                            ))
                            continue
                        else:
                            # Run metadata extractor for new project creation
                            metadata = await adapter.analyze_prompt_for_project(user_msg)
                            proj_name = metadata.get("project_name", "temp_project")
                            detected_lang = metadata.get("language") or "html"
                            
                            current_language = detected_lang
                            current_workspace = PROJECT_ROOT / "workspace" / proj_name
                            current_workspace.mkdir(parents=True, exist_ok=True)
                            adapter.set_workspace_path(str(current_workspace))
                            
                    run_id = f"run_{int(time.time()*1000)}"
                    p_name = current_workspace.name if current_workspace else None
                    await broadcast_event(create_event("run_started", session_id, {"run_id": run_id, "prompt": original_prompt, "project_name": p_name}))
                    keepalive_ctx.status = "working"
                    await execute_turn_with_guard(session_id, original_prompt, event_handler, current_language, run_id, websocket)
                
            elif message_type == "project_selected":
                proj_name = data.get("project_name")
                original_prompt = data.get("content", "").strip()
                
                async def event_handler(evt: dict):
                    await broadcast_event(evt)

                async with WebSocketKeepaliveContext(session_id, event_handler) as keepalive_ctx:
                    keepalive_ctx.status = "analyzing_request"
                    
                    if proj_name == "_new_project_":
                        # Proceed with metadata extraction for new project
                        metadata = await adapter.analyze_prompt_for_project(original_prompt)
                        new_proj_name = metadata.get("project_name", "temp_project")
                        detected_lang = metadata.get("language") or "html"
                        
                        current_language = detected_lang
                        current_workspace = PROJECT_ROOT / "workspace" / new_proj_name
                        current_workspace.mkdir(parents=True, exist_ok=True)
                        adapter.set_workspace_path(str(current_workspace))
                    else:
                        # Select existing project
                        projects = adapter.discover_projects()
                        matched_proj = next((p for p in projects if p["name"] == proj_name), None)
                        if matched_proj:
                            current_workspace = Path(matched_proj["path"])
                            current_language = matched_proj["language"].lower() if matched_proj["language"] else None
                            adapter.set_workspace_path(str(current_workspace))
                        else:
                            current_workspace = PROJECT_ROOT / "workspace" / proj_name
                            current_workspace.mkdir(parents=True, exist_ok=True)
                            adapter.set_workspace_path(str(current_workspace))
                    
                    run_id = f"run_{int(time.time()*1000)}"
                    p_name = current_workspace.name if current_workspace else None
                    await broadcast_event(create_event("run_started", session_id, {"run_id": run_id, "prompt": original_prompt, "project_name": p_name}))
                    keepalive_ctx.status = "working"
                    await execute_turn_with_guard(session_id, original_prompt, event_handler, current_language, run_id, websocket)

            elif message_type == "language_selected":
                lang = data.get("language")
                proj_name = data.get("project_name", "temp_project")
                original_prompt = data.get("content", "").strip()
                
                current_language = lang
                current_workspace = PROJECT_ROOT / "workspace" / proj_name
                current_workspace.mkdir(parents=True, exist_ok=True)
                adapter.set_workspace_path(str(current_workspace))
                
                async def event_handler(evt: dict):
                    await broadcast_event(evt)
                    
                async with WebSocketKeepaliveContext(session_id, event_handler) as keepalive_ctx:
                    run_id = f"run_{int(time.time()*1000)}"
                    p_name = current_workspace.name if current_workspace else None
                    await broadcast_event(create_event("run_started", session_id, {"run_id": run_id, "prompt": original_prompt, "project_name": p_name}))
                    keepalive_ctx.status = "working"
                    await execute_turn_with_guard(session_id, original_prompt, event_handler, current_language, run_id, websocket)

            elif message_type in ["cancel", "stop", "stop_generation"]:
                adapter.cancel_current_turn()
                await broadcast_event(create_event("run_completed", session_id, {"status": "CANCELLED"}))
                await broadcast_event(create_event("agent_finished", session_id, {"status": "cancelled"}))

            elif message_type in ["approval_response", "approval_resolved"]:
                req_id = data.get("request_id") or data.get("data", {}).get("request_id")
                approved = data.get("approved", False) or data.get("data", {}).get("approved", False)
                adapter.approval_controller.resolve_approval(req_id, approved)
    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if websocket in active_websockets:
            active_websockets.remove(websocket)

from fastapi.staticfiles import StaticFiles

from fastapi.responses import FileResponse



client_dist = PROJECT_ROOT / "client" / "dist"
if client_dist.exists():
    app.mount("/", StaticFiles(directory=str(client_dist), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        ws_ping_interval=300,   # 5 min — local Ollama calls take ~100-140s
        ws_ping_timeout=300,    # 5 min — allow long waits without disconnect
    )
