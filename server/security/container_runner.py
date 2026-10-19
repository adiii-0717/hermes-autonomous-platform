import os
import shutil
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger('server.security.container_runner')

class ContainerRunner:
    """Isolated execution engine for generated user workloads.
    
    Provides containerized sandbox execution using Docker with strict resource
    and privilege limits. Enforces FAIL CLOSED security policy in production mode:
    host execution is strictly prohibited unless HERMES_ENV=development AND
    HERMES_ALLOW_HOST_FALLBACK=true.
    """

    def __init__(
        self,
        workspace_guard,
        docker_image: str = 'node:20-alpine',
        cpu_limit: str = '1.0',
        memory_limit: str = '512m',
        pids_limit: int = 64,
        network_mode: str = 'none',
        sandbox_runtime: str = 'runc'
    ):
        self.guard = workspace_guard
        self.docker_image = os.getenv('HERMES_DOCKER_IMAGE', docker_image)
        self.cpu_limit = os.getenv('HERMES_DOCKER_CPU_LIMIT', cpu_limit)
        self.memory_limit = os.getenv('HERMES_DOCKER_MEMORY_LIMIT', memory_limit)
        self.pids_limit = int(os.getenv('HERMES_DOCKER_PIDS_LIMIT', str(pids_limit)))
        self.network_mode = os.getenv('HERMES_DOCKER_NETWORK', network_mode)
        self.sandbox_runtime = os.getenv('HERMES_SANDBOX_RUNTIME', sandbox_runtime)
        self.enable_docker = os.getenv('HERMES_ENABLE_DOCKER', 'true').lower() in ('true', '1', 'yes')
        
        # Security Environment Controls
        self.env_mode = os.getenv('HERMES_ENV', 'production').lower()
        self.allow_host_fallback = os.getenv('HERMES_ALLOW_HOST_FALLBACK', 'false').lower() in ('true', '1', 'yes')

    def is_docker_available(self) -> bool:
        """Check if docker binary is present and daemon is responsive."""
        if not self.enable_docker:
            return False
        if not shutil.which('docker'):
            return False
        try:
            res = subprocess.run(
                ['docker', 'info'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=3
            )
            return res.returncode == 0
        except Exception:
            return False

    def build_docker_command(self, command: str, workspace_path: str) -> list:
        """Construct a secure, unprivileged docker run command invocation."""
        abs_workspace = os.path.realpath(workspace_path)
        
        cmd = [
            'docker', 'run', '--rm',
            '--cpus', self.cpu_limit,
            '--memory', self.memory_limit,
            '--pids-limit', str(self.pids_limit),
            '--network', self.network_mode,
            '--cap-drop', 'ALL',
            '--security-opt', 'no-new-privileges:true',
            '--read-only',
            '--tmpfs', '/tmp:rw,noexec,nosuid,size=64m',
            '-v', f'{abs_workspace}:/workspace:rw',
            '-w', '/workspace'
        ]

        if self.sandbox_runtime and self.sandbox_runtime != 'runc':
            cmd.extend(['--runtime', self.sandbox_runtime])

        cmd.extend([self.docker_image, 'sh', '-c', command])
        return cmd

    async def execute_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute command in isolated container or fail closed in production."""
        # 1. Enforce application-level WorkspaceGuard classification
        risk_level, err_msg = self.guard.classify_command(command)
        if risk_level == 'BLOCKED':
            return {
                'success': False,
                'exit_code': -1,
                'stdout': '',
                'stderr': err_msg,
                'isolation_mode': 'blocked_by_guard',
                'sandbox_profile': 'workspace_guard_blocked'
            }

        workspace_path = str(self.guard.workspace_root)

        # 2. Attempt Container Isolation if Docker daemon is available
        docker_ok = self.is_docker_available()
        if docker_ok:
            docker_cmd = self.build_docker_command(command, workspace_path)
            try:
                proc = subprocess.Popen(
                    docker_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = proc.communicate(timeout=timeout)
                
                if proc.returncode == 0:
                    return {
                        'success': True,
                        'exit_code': 0,
                        'stdout': stdout or '',
                        'stderr': stderr or '',
                        'isolation_mode': 'docker_container',
                        'sandbox_profile': f'unprivileged_container_cap_drop_all_{self.sandbox_runtime}',
                        'resource_limits': {
                            'cpu': self.cpu_limit,
                            'memory': self.memory_limit,
                            'pids_limit': self.pids_limit,
                            'timeout_s': timeout
                        }
                    }
                else:
                    # Container process exited with non-zero exit code or error
                    # If host fallback is prohibited, return the container failure
                    if not (self.env_mode == 'development' and self.allow_host_fallback):
                        return {
                            'success': False,
                            'exit_code': proc.returncode,
                            'stdout': stdout or '',
                            'stderr': stderr or f'Container execution failed with exit code {proc.returncode}',
                            'isolation_mode': 'docker_container_failed',
                            'sandbox_profile': 'fail_closed_production'
                        }
            except subprocess.TimeoutExpired:
                proc.kill()
                return {
                    'success': False,
                    'exit_code': -1,
                    'stdout': '',
                    'stderr': f'Container command timed out after {timeout} seconds.',
                    'isolation_mode': 'docker_container_timeout',
                    'sandbox_profile': 'docker_timeout'
                }
            except Exception as e:
                logger.error(f'Container execution error: {e}')
                if not (self.env_mode == 'development' and self.allow_host_fallback):
                    return {
                        'success': False,
                        'exit_code': -1,
                        'stdout': '',
                        'stderr': f'Security Error: Container creation or sandbox runtime execution failed ({str(e)}). Host execution is disabled in production.',
                        'isolation_mode': 'container_creation_failed_closed',
                        'sandbox_profile': 'fail_closed_production'
                    }

        # 3. Fail-Closed Check if Docker is unavailable
        if not docker_ok:
            if not (self.env_mode == 'development' and self.allow_host_fallback):
                logger.error('Fail-Closed Security Guard: Sandbox container runtime is unavailable and host fallback is disabled in production mode.')
                return {
                    'success': False,
                    'exit_code': -1,
                    'stdout': '',
                    'stderr': 'Security Error: Container sandbox execution is unavailable and host execution is strictly disabled in production mode.',
                    'isolation_mode': 'sandbox_unavailable_failed_closed',
                    'sandbox_profile': 'fail_closed_production'
                }
            logger.warning('Development Mode Active: Docker daemon unavailable, proceeding with explicit bounded host execution.')

        # 4. Permitted Development Bounded Host Fallback
        try:
            env = os.environ.copy()
            for key in ['GEMINI_API_KEY', 'OPENAI_API_KEY', 'SECRET_KEY', 'JWT_SECRET']:
                env.pop(key, None)

            proc = subprocess.Popen(
                command,
                shell=True,
                cwd=workspace_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            stdout, stderr = proc.communicate(timeout=timeout)
            return {
                'success': proc.returncode == 0,
                'exit_code': proc.returncode,
                'stdout': stdout or '',
                'stderr': stderr or '',
                'isolation_mode': 'host_bounded_development',
                'sandbox_profile': 'workspace_guard_bounded_dev',
                'resource_limits': {
                    'timeout_s': timeout
                }
            }
        except subprocess.TimeoutExpired:
            proc.kill()
            return {
                'success': False,
                'exit_code': -1,
                'stdout': '',
                'stderr': f'Command timed out after {timeout} seconds.',
                'isolation_mode': 'host_bounded_development',
                'sandbox_profile': 'host_timeout'
            }
        except Exception as e:
            return {
                'success': False,
                'exit_code': -1,
                'stdout': '',
                'stderr': str(e),
                'isolation_mode': 'host_bounded_development',
                'sandbox_profile': 'execution_error'
            }