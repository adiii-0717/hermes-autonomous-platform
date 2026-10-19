"""Centralized LLM Provider & Key Failover Manager for Hermes Dev Studio.

Maintains strict provider priority:
1. Gemini API Key 1 (Primary)
2. Gemini API Key 2 (First Backup)
3. Gemini API Key 3 (Second Backup)
4. APInex (Final Fallback)

Provides:
- Thread-safe state tracking (HEALTHY, COOLDOWN, AUTH_FAILED, DISABLED)
- Automatic recovery without server restart when cooldown expires
- Accurate error classification (QUOTA, AUTH, TIMEOUT, NETWORK, SERVER_ERROR, INVALID_MODEL)
- Strict credential sanitization in all logs, error messages, and payloads
- Project-level quota coordination
"""

import os
import re
import time
import logging
import threading
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger("server.provider_manager")


class ProviderStatus:
    HEALTHY = "HEALTHY"
    COOLDOWN = "COOLDOWN"
    AUTH_FAILED = "AUTH_FAILED"
    DISABLED = "DISABLED"


class ErrorClass:
    QUOTA_EXHAUSTED = "QUOTA_EXHAUSTED"
    AUTH_FAILURE = "AUTH_FAILURE"
    TIMEOUT = "TIMEOUT"
    NETWORK_ERROR = "NETWORK_ERROR"
    SERVER_ERROR = "SERVER_ERROR"
    INVALID_MODEL = "INVALID_MODEL"
    INVALID_REQUEST = "INVALID_REQUEST"
    UNKNOWN = "UNKNOWN"


class ProviderConfig:
    def __init__(
        self,
        provider_id: str,
        provider: str,
        display_name: str,
        api_key: str,
        api_base: str,
        default_model: str,
        priority: int,
        is_cloud: bool = True
    ):
        self.provider_id = provider_id
        self.provider = provider
        self.display_name = display_name
        self.api_key = api_key.strip() if api_key else ""
        self.api_base = api_base.rstrip("/") + "/" if api_base else ""
        self.default_model = default_model
        self.priority = priority
        self.is_cloud = is_cloud
        
        self.status = ProviderStatus.HEALTHY if (self.api_key or not self.is_cloud) else ProviderStatus.DISABLED
        self.cooldown_until: float = 0.0
        self.failure_count: int = 0
        self.last_error: str = ""
        self.last_error_type: str = ""
        self.last_used_timestamp: float = 0.0
        self.project_id: Optional[str] = None

    @property
    def is_configured(self) -> bool:
        if not self.is_cloud:
            return True
        return bool(self.api_key)

    def is_available(self) -> bool:
        if not self.is_configured or self.status in (ProviderStatus.DISABLED, ProviderStatus.AUTH_FAILED):
            return False
        if self.status == ProviderStatus.COOLDOWN:
            if time.time() >= self.cooldown_until:
                # Cooldown expired -> automatic recovery!
                self.status = ProviderStatus.HEALTHY
                self.failure_count = 0
                logger.info(f"Provider '{self.display_name}' cooldown expired. Restored to priority.")
                return True
            return False
        return True

    def to_dict(self, mask_key: bool = True) -> Dict[str, Any]:
        key_masked = "Not configured"
        if self.api_key:
            if mask_key:
                if len(self.api_key) > 8:
                    key_masked = f"{self.api_key[:4]}...{self.api_key[-4:]}"
                else:
                    key_masked = "***"
            else:
                key_masked = self.api_key
        return {
            "provider_id": self.provider_id,
            "provider": self.provider,
            "display_name": self.display_name,
            "api_base": self.api_base,
            "model": self.default_model,
            "priority": self.priority,
            "status": self.status,
            "is_configured": self.is_configured,
            "api_key_masked": key_masked,
            "cooldown_remaining_sec": max(0, int(self.cooldown_until - time.time())) if self.status == ProviderStatus.COOLDOWN else 0,
            "failure_count": self.failure_count,
            "last_error_type": self.last_error_type
        }


class ProviderManager:
    """Singleton manager controlling LLM provider prioritization, automatic failover, and recovery."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ProviderManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        with self._lock:
            if self._initialized:
                return
            self._providers: Dict[str, ProviderConfig] = {}
            self._cooldown_seconds = int(os.getenv("GEMINI_COOLDOWN_SECONDS", "60"))
            self._short_cooldown_seconds = int(os.getenv("GEMINI_SHORT_COOLDOWN_SECONDS", "30"))
            self.reload_from_env()
            self._initialized = True

    def reload_from_env(self):
        """Reads configuration and API keys from environment and active .env."""
        env_dict = self._read_env_files()

        def get_val(key: str, default: str = "") -> str:
            return os.getenv(key) or env_dict.get(key) or default

        # Provider 1: Gemini Key 1 (Primary)
        key_1 = (
            get_val("GEMINI_API_KEY_1")
            or get_val("GEMINI_API_KEY")
            or get_val("GOOGLE_API_KEY")
        )
        base_gemini = get_val("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
        model_gemini = get_val("GEMINI_MODEL") or get_val("MODEL_NAME") or "gemini-2.5-flash"

        self._providers["gemini_1"] = ProviderConfig(
            provider_id="gemini_1",
            provider="google-gemini",
            display_name="Gemini (Key 1)",
            api_key=key_1,
            api_base=base_gemini,
            default_model=model_gemini,
            priority=1,
            is_cloud=True
        )

        # Provider 2: Gemini Key 2 (First Backup)
        key_2 = get_val("GEMINI_API_KEY_2")
        self._providers["gemini_2"] = ProviderConfig(
            provider_id="gemini_2",
            provider="google-gemini",
            display_name="Gemini (Key 2)",
            api_key=key_2,
            api_base=base_gemini,
            default_model=model_gemini,
            priority=2,
            is_cloud=True
        )

        # Provider 3: Gemini Key 3 (Second Backup)
        key_3 = get_val("GEMINI_API_KEY_3")
        self._providers["gemini_3"] = ProviderConfig(
            provider_id="gemini_3",
            provider="google-gemini",
            display_name="Gemini (Key 3)",
            api_key=key_3,
            api_base=base_gemini,
            default_model=model_gemini,
            priority=3,
            is_cloud=True
        )

        # Provider 4: APInex (Final Fallback)
        key_apinex = get_val("APINEX_API_KEY")
        base_apinex = get_val("APINEX_BASE_URL", "https://api.apinex.bond/v1/")
        model_apinex = get_val("APINEX_MODEL", "free/gemini-3.8-flash")
        self._providers["apinex"] = ProviderConfig(
            provider_id="apinex",
            provider="apinex",
            display_name="APInex",
            api_key=key_apinex,
            api_base=base_apinex,
            default_model=model_apinex,
            priority=4,
            is_cloud=True
        )

        # Optional offline fallback: Ollama
        base_ollama = get_val("OLLAMA_BASE_URL", "http://localhost:11434/v1/")
        model_ollama = get_val("OLLAMA_MODEL", "gemma4:12b-hermes")
        self._providers["ollama"] = ProviderConfig(
            provider_id="ollama",
            provider="ollama",
            display_name="Local Ollama",
            api_key="ollama",
            api_base=base_ollama,
            default_model=model_ollama,
            priority=5,
            is_cloud=False
        )

    def _read_env_files(self) -> Dict[str, str]:
        env_dict = {}
        max_mtime = 0.0
        env_candidates = [
            Path(os.getenv("HERMES_ENV_PATH", "")),
            Path(".env"),
            Path(__file__).resolve().parent.parent.parent / ".env"
        ]
        seen_paths = set()
        for p in env_candidates:
            if str(p) and p.exists() and p.resolve() not in seen_paths:
                seen_paths.add(p.resolve())
                try:
                    mt = p.stat().st_mtime
                    if mt > max_mtime:
                        max_mtime = mt
                    for line in p.read_text(encoding="utf-8").splitlines():
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            env_dict[k.strip()] = v.strip()
                except Exception:
                    pass
        self._last_env_mtime = max_mtime
        return env_dict

    def sanitize_text(self, text: Any) -> str:
        """Strictly redacts all configured API keys and authorization tokens from strings."""
        if not text:
            return ""
        s = str(text)
        # Redact specific configured keys
        for p in self._providers.values():
            if p.api_key and len(p.api_key) > 4:
                s = s.replace(p.api_key, "[REDACTED_API_KEY]")
        # Redact common token and key patterns
        s = re.sub(r'Bearer\s+[A-Za-z0-9_\-\.]{10,}', 'Bearer [REDACTED_TOKEN]', s, flags=re.IGNORECASE)
        s = re.sub(r'AIza[0-9A-Za-z\-_]{35}', '[REDACTED_GEMINI_KEY]', s)
        s = re.sub(r'AQ\.[A-Za-z0-9_\-]{30,}', '[REDACTED_GEMINI_KEY]', s)
        s = re.sub(r'sk-[A-Za-z0-9_\-]{20,}', '[REDACTED_API_KEY]', s)
        return s

    def classify_error(self, exc: Any) -> Tuple[str, str]:
        """Classifies an exception into a normalized error category and sanitized description."""
        if exc is None:
            return ErrorClass.UNKNOWN, "Unknown error"
        err_str = self.sanitize_text(str(exc))
        lower = err_str.lower()

        # Quota / Rate limit
        if any(w in lower for w in [
            "429", "resource_exhausted", "resourceexhausted", "quota", "rate_limit", "ratelimit",
            "tpm", "rpm", "too many requests", "insufficient_quota", "402", "credit", "exceeded your current quota"
        ]):
            return ErrorClass.QUOTA_EXHAUSTED, err_str

        # Authentication / Permission
        if any(w in lower for w in [
            "401", "403", "unauthorized", "forbidden", "invalid_api_key", "invalid api key",
            "api_key_invalid", "permission_denied", "permissiondenied", "api key not valid"
        ]):
            return ErrorClass.AUTH_FAILURE, err_str

        # Timeout
        if any(w in lower for w in [
            "timeout", "timed out", "deadline_exceeded", "deadlineexceeded", "read timeout", "connect timeout"
        ]):
            return ErrorClass.TIMEOUT, err_str

        # Network failures
        if any(w in lower for w in [
            "connection refused", "connection reset", "dns", "name resolution",
            "network is unreachable", "remote disconnected", "socket"
        ]):
            return ErrorClass.NETWORK_ERROR, err_str

        # Model not found / invalid
        if any(w in lower for w in ["model_not_found", "model not found", "does not exist", "invalid model"]):
            return ErrorClass.INVALID_MODEL, err_str

        # Malformed request
        if "400" in lower or "bad request" in lower:
            return ErrorClass.INVALID_REQUEST, err_str

        # Server outages (5xx)
        if any(w in lower for w in ["500", "502", "503", "504", "bad gateway", "service unavailable", "overloaded"]):
            return ErrorClass.SERVER_ERROR, err_str

        return ErrorClass.UNKNOWN, err_str

    def get_ordered_providers(self) -> List[ProviderConfig]:
        """Returns all configured providers ordered by priority."""
        with self._lock:
            env_candidates = [
                Path(os.getenv("HERMES_ENV_PATH", "")),
                Path(".env"),
                Path(__file__).resolve().parent.parent.parent / ".env"
            ]
            for p_path in env_candidates:
                if str(p_path) and p_path.exists():
                    try:
                        if p_path.stat().st_mtime > getattr(self, "_last_env_mtime", 0.0):
                            self.reload_from_env()
                            break
                    except Exception:
                        pass

            # Check for cooldown expiration -> automatically restore original priority!
            for p in self._providers.values():
                if p.status == ProviderStatus.COOLDOWN and time.time() >= p.cooldown_until:
                    p.status = ProviderStatus.HEALTHY
                    p.failure_count = 0
                    logger.info(f"Provider '{p.display_name}' cooldown expired. Restored to priority {p.priority}.")

            return sorted(
                [p for p in self._providers.values() if p.is_configured and p.status != ProviderStatus.DISABLED],
                key=lambda x: x.priority
            )

    def get_active_provider(self) -> Optional[ProviderConfig]:
        """Returns the highest-priority provider that is currently available."""
        providers = self.get_ordered_providers()
        for p in providers:
            if p.is_available():
                return p
        # If all cloud providers are in cooldown, but not permanently auth-failed, return the one with shortest remaining cooldown
        cooldown_pool = [p for p in providers if p.status == ProviderStatus.COOLDOWN]
        if cooldown_pool:
            cooldown_pool.sort(key=lambda x: x.cooldown_until)
            return cooldown_pool[0]
        return None

    def get_failover_chain(self, current_provider_id: Optional[str] = None) -> List[ProviderConfig]:
        """Returns ordered list of fallback providers excluding current provider and auth-failed providers."""
        providers = self.get_ordered_providers()
        chain = []
        for p in providers:
            if current_provider_id and p.provider_id == current_provider_id:
                continue
            if p.status == ProviderStatus.AUTH_FAILED:
                continue
            chain.append(p)
        return chain

    def mark_failure(
        self,
        provider_id: str,
        exc: Any,
        retry_after: Optional[float] = None
    ) -> str:
        """Records a provider failure, sets appropriate cooldown, and returns error classification."""
        with self._lock:
            provider = self._providers.get(provider_id)
            if not provider:
                return ErrorClass.UNKNOWN

            err_class, sanitized_err = self.classify_error(exc)
            provider.last_error = sanitized_err
            provider.last_error_type = err_class
            provider.failure_count += 1

            if err_class == ErrorClass.AUTH_FAILURE:
                # Permanent credential failure for this key
                provider.status = ProviderStatus.AUTH_FAILED
                logger.error(
                    f"Provider '{provider.display_name}' marked AUTH_FAILED: {sanitized_err}. "
                    "Skipping this key until credentials are corrected."
                )
            elif err_class == ErrorClass.QUOTA_EXHAUSTED:
                # Rate limit / Quota limit -> Cooldown
                cooldown_dur = retry_after if retry_after and retry_after > 0 else self._cooldown_seconds
                provider.status = ProviderStatus.COOLDOWN
                provider.cooldown_until = time.time() + cooldown_dur
                logger.warning(
                    f"Provider '{provider.display_name}' quota exhausted. "
                    f"Entering {cooldown_dur}s cooldown until {time.strftime('%H:%M:%S', time.localtime(provider.cooldown_until))}."
                )
            elif err_class in (ErrorClass.TIMEOUT, ErrorClass.NETWORK_ERROR, ErrorClass.SERVER_ERROR):
                # Transient network/server error -> Short cooldown
                cooldown_dur = self._short_cooldown_seconds
                provider.status = ProviderStatus.COOLDOWN
                provider.cooldown_until = time.time() + cooldown_dur
                logger.warning(
                    f"Provider '{provider.display_name}' transient failure ({err_class}). "
                    f"Entering {cooldown_dur}s cooldown."
                )
            else:
                # Unknown / other error -> short cooldown
                provider.status = ProviderStatus.COOLDOWN
                provider.cooldown_until = time.time() + self._short_cooldown_seconds

            return err_class

    def mark_success(self, provider_id: str):
        """Records a successful call and restores provider to healthy state."""
        with self._lock:
            provider = self._providers.get(provider_id)
            if provider:
                provider.status = ProviderStatus.HEALTHY
                provider.failure_count = 0
                provider.cooldown_until = 0.0
                provider.last_used_timestamp = time.time()

    def get_summary(self) -> List[Dict[str, Any]]:
        """Returns diagnostic list of all provider states with masked keys."""
        with self._lock:
            return [p.to_dict(mask_key=True) for p in sorted(self._providers.values(), key=lambda x: x.priority)]


# Global singleton access
provider_manager = ProviderManager()
