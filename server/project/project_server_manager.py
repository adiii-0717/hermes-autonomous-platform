import os
import sys
import time
import socket
import json
import signal
import threading
import subprocess
import urllib.request
import urllib.error
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger('project_server_manager')

class ProjectServerManager:
    """Centralized lifecycle manager for generated project development and preview servers."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ProjectServerManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, workspace_root: Optional[Path] = None):
        if self._initialized:
            if workspace_root:
                self.workspace_root = Path(workspace_root).resolve()
            return

        self._initialized = True
        self.workspace_root = Path(workspace_root or (Path(__file__).parent.parent.parent / 'workspace')).resolve()
        self.servers: Dict[str, Dict[str, Any]] = {}
        self.port_range_start = 8090
        self.port_range_end = 8190

    def find_free_port(self) -> int:
        for port in range(self.port_range_start, self.port_range_end):
            if any(s.get('port') == port and s.get('status') in ['STARTING', 'READY'] for s in self.servers.values()):
                continue
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                try:
                    sock.bind(('0.0.0.0', port))
                    return port
                except OSError:
                    continue
        raise RuntimeError('No free port available in range 8090-8190.')

    def detect_server_cmd(self, project_dir: Path, port: int) -> tuple[str, str]:
        pkg_json_path = project_dir / 'package.json'
        dist_html = project_dir / 'dist' / 'index.html'
        build_html = project_dir / 'build' / 'index.html'

        if pkg_json_path.exists():
            try:
                pkg_data = json.loads(pkg_json_path.read_text(encoding='utf-8'))
                scripts = pkg_data.get('scripts', {})
                deps = {**pkg_data.get('dependencies', {}), **pkg_data.get('devDependencies', {})}

                if dist_html.exists():
                    return f'python3 -m http.server {port} --directory dist', 'static_dist'
                elif build_html.exists():
                    return f'python3 -m http.server {port} --directory build', 'static_dist'
                elif 'vite' in deps or 'dev' in scripts:
                    return f'npx -y vite --host 127.0.0.1 --port {port} --strictPort --base /preview/{project_dir.name}/', 'vite'
                elif 'start' in scripts:
                    return f'PORT={port} npm start', 'node'
            except Exception as e:
                logger.warning(f'Error parsing package.json for {project_dir.name}: {e}')

        if (project_dir / 'index.html').exists():
            return f'python3 -m http.server {port}', 'static_html'

        if (project_dir / 'main.py').exists():
            return f'python3 main.py', 'python'

        return f'python3 -m http.server {port}', 'static_fallback'


    def ensure_styling_and_build(self, project_dir: Path) -> None:
        pkg_json = project_dir / "package.json"
        index_css_files = list(project_dir.glob("src/**/*.css")) + list(project_dir.glob("*.css"))
        uses_tailwind = False

        if pkg_json.exists():
            try:
                pkg_data = json.loads(pkg_json.read_text(encoding="utf-8"))
                deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}
                if "tailwindcss" in deps:
                    uses_tailwind = True
            except Exception:
                pass

        if not uses_tailwind:
            for css_file in index_css_files:
                if "node_modules" not in str(css_file):
                    try:
                        text = css_file.read_text(encoding="utf-8")
                        if "@tailwind" in text or "@apply" in text:
                            uses_tailwind = True
                            break
                    except Exception:
                        pass

        if uses_tailwind:
            postcss_cfg = project_dir / "postcss.config.js"
            tailwind_cfg = project_dir / "tailwind.config.js"

            if not postcss_cfg.exists():
                logger.info(f"Generating missing postcss.config.js for {project_dir.name}...")
                postcss_cfg.write_text("export default {\n  plugins: {\n    tailwindcss: {},\n    autoprefixer: {},\n  },\n}\n", encoding="utf-8")

            if not tailwind_cfg.exists():
                logger.info(f"Generating missing tailwind.config.js for {project_dir.name}...")
                tailwind_cfg.write_text("/** @type {import('tailwindcss').Config} */\nexport default {\n  content: [\n    './index.html',\n    './src/**/*.{js,ts,jsx,tsx,html}',\n  ],\n  theme: {\n    extend: {},\n  },\n  plugins: [],\n}\n", encoding="utf-8")

            dist_css_files = list(project_dir.glob("dist/**/*.css"))
            needs_rebuild = False
            if not dist_css_files:
                needs_rebuild = True
            else:
                for css in dist_css_files:
                    try:
                        css_text = css.read_text(encoding="utf-8")
                        if "@tailwind" in css_text or "@apply" in css_text or len(css_text) < 500:
                            needs_rebuild = True
                            break
                    except Exception:
                        needs_rebuild = True

            if needs_rebuild and pkg_json.exists():
                logger.info(f"Rebuilding project {project_dir.name} with processed Tailwind CSS...")
                try:
                    res = subprocess.run("npm run build", shell=True, cwd=str(project_dir), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120, text=True)
                    if res.returncode != 0:
                        logger.warning(f"Build error: {res.stderr}")
                except Exception as exc:
                    logger.error(f"Rebuild failed for {project_dir.name}: {exc}")

    def ensure_dependencies(self, project_dir: Path) -> bool:
        pkg_json = project_dir / 'package.json'
        node_modules = project_dir / 'node_modules'

        if pkg_json.exists() and not node_modules.exists():
            logger.info(f'Installing dependencies for {project_dir.name}...')
            try:
                res = subprocess.run(
                    'npm install',
                    shell=True,
                    cwd=str(project_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=120,
                    text=True
                )
                if res.returncode != 0:
                    logger.warning(f'npm install warnings/errors: {res.stderr}')
            except Exception as exc:
                logger.error(f'Failed to execute npm install in {project_dir.name}: {exc}')
                return False
        return True

    def ensure_project_server(self, project_name: str, force_restart: bool = False) -> Dict[str, Any]:
        project_dir = self.workspace_root / project_name
        if not project_dir.exists() and (self.workspace_root / project_name).exists():
            project_dir = self.workspace_root / project_name

        if not project_dir.exists():
            return {
                'success': False,
                'status': 'FAILED',
                'error': f'Project directory "{project_name}" does not exist in workspace.'
            }

        existing = self.servers.get(project_name)
        if existing and not force_restart:
            if self.is_server_alive(project_name):
                return existing

        if existing:
            self.stop_project_server(project_name)

        self.ensure_dependencies(project_dir)
        self.ensure_styling_and_build(project_dir)

        port = self.find_free_port()
        cmd, server_type = self.detect_server_cmd(project_dir, port)
        logger.info(f'Starting server for "{project_name}" on port {port} using command: {cmd}')

        logs = []

        try:
            proc = subprocess.Popen(
                cmd,
                shell=True,
                cwd=str(project_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                start_new_session=True
            )

            server_info = {
                'project_name': project_name,
                'project_dir': str(project_dir),
                'port': port,
                'process': proc,
                'pid': proc.pid,
                'status': 'STARTING',
                'server_type': server_type,
                'command': cmd,
                'url': f'http://127.0.0.1:{port}',
                'logs': logs,
                'error': None,
                'start_time': time.time()
            }
            self.servers[project_name] = server_info

            def log_reader():
                try:
                    for line in iter(proc.stdout.readline, ''):
                        if line:
                            logs.append(line.strip())
                            if len(logs) > 200:
                                logs.pop(0)
                except Exception:
                    pass

            thread = threading.Thread(target=log_reader, daemon=True)
            thread.start()

            ready = self.poll_readiness(port, timeout_seconds=15)
            if ready:
                server_info['status'] = 'READY'
                logger.info(f'Server for "{project_name}" is READY on port {port} (PID {proc.pid})')
            else:
                if proc.poll() is not None:
                    server_info['status'] = 'FAILED'
                    server_info['error'] = f'Process exited prematurely with code {proc.returncode}. Logs: ' + ' '.join(logs[-5:])
                    logger.error(server_info['error'])
                else:
                    server_info['status'] = 'READY'
                    logger.info(f'Server process running on port {port}, proceeding.')

            return server_info

        except Exception as err:
            logger.error(f'Failed to start server for "{project_name}": {err}')
            return {
                'success': False,
                'status': 'FAILED',
                'error': str(err)
            }

    def poll_readiness(self, port: int, timeout_seconds: int = 15) -> bool:
        start = time.time()
        url = f'http://127.0.0.1:{port}/'
        while time.time() - start < timeout_seconds:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'HermesReadinessCheck/1.0'})
                with urllib.request.urlopen(req, timeout=2) as response:
                    if response.status in [200, 301, 302, 304, 404]:
                        return True
            except (urllib.error.HTTPError, urllib.error.URLError, socket.timeout, ConnectionRefusedError):
                pass
            time.sleep(0.5)
        return False

    def is_server_alive(self, project_name: str) -> bool:
        server = self.servers.get(project_name)
        if not server:
            return False
        proc = server.get('process')
        if not proc or proc.poll() is not None:
            server['status'] = 'STOPPED'
            return False
        return True

    def stop_project_server(self, project_name: str):
        server = self.servers.get(project_name)
        if not server:
            return
        proc = server.get('process')
        if proc and proc.poll() is None:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                proc.wait(timeout=3)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        server['status'] = 'STOPPED'

    def get_server_status(self, project_name: str) -> Dict[str, Any]:
        server = self.servers.get(project_name)
        if not server:
            return {'status': 'NOT_FOUND', 'url': None, 'port': None}
        alive = self.is_server_alive(project_name)
        return {
            'project_name': project_name,
            'status': server['status'] if alive else 'STOPPED',
            'port': server['port'],
            'url': server['url'],
            'server_type': server['server_type'],
            'pid': server['pid'],
            'error': server.get('error'),
            'logs': server.get('logs', [])[-10:]
        }


project_server_manager = ProjectServerManager()
