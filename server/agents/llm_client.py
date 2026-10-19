import os
import re
import json
import time
import base64
import logging
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, List, Optional
from server.agents.provider_manager import provider_manager, ProviderStatus, ErrorClass, ProviderConfig

logger = logging.getLogger("agent.llm_client")


class LLMClient:
    """Unified LLM & Multimodal Vision client with automatic Gemini key rotation and APInex failover."""

    def __init__(self, model_config: Optional[Dict[str, str]] = None):
        self.explicit_config = bool(model_config)
        cfg = model_config or {}
        env_vars = self._load_env()
        self.cfg = cfg
        
        # Explicit provider config passed directly takes priority
        provider_candidate = (cfg.get("provider") or "").strip().lower()

        # Default provider priority: Gemini Key 1 (Primary) -> Gemini Key 2 -> Gemini Key 3 -> APInex -> Ollama
        if not provider_candidate:
            active = provider_manager.get_active_provider()
            if active:
                provider_candidate = active.provider
            elif os.getenv("GEMINI_API_KEY_1") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or env_vars.get("GEMINI_API_KEY"):
                provider_candidate = "google-gemini"
            elif os.getenv("APINEX_API_KEY") or env_vars.get("APINEX_API_KEY"):
                provider_candidate = "apinex"
            elif os.getenv("LLM_PROVIDER") or env_vars.get("LLM_PROVIDER"):
                provider_candidate = (os.getenv("LLM_PROVIDER") or env_vars.get("LLM_PROVIDER")).strip().lower()
            else:
                provider_candidate = "google-gemini"

        if provider_candidate in ["google-gemini", "gemini", "google", "google_gemini", "google-ai-studio"]:
            self.provider = "google-gemini"
            self.api_key = (
                cfg.get("api_key")
                or os.getenv("GEMINI_API_KEY_1")
                or os.getenv("GEMINI_API_KEY")
                or os.getenv("GOOGLE_API_KEY")
                or env_vars.get("GEMINI_API_KEY_1")
                or env_vars.get("GEMINI_API_KEY")
                or env_vars.get("GOOGLE_API_KEY")
                or ""
            )
            self.api_base = (
                cfg.get("api_base")
                or os.getenv("GEMINI_BASE_URL")
                or os.getenv("API_BASE_URL")
                or env_vars.get("GEMINI_BASE_URL")
                or "https://generativelanguage.googleapis.com/v1beta/openai/"
            ).rstrip("/") + "/"
            self.model_name = (
                cfg.get("model")
                or os.getenv("GEMINI_MODEL")
                or os.getenv("MODEL_NAME")
                or env_vars.get("GEMINI_MODEL")
                or env_vars.get("MODEL_NAME")
                or "gemini-2.5-flash"
            )
        elif provider_candidate in ["apinex", "apinex-ai", "apinex_bond", "apinex.bond"]:
            self.provider = "apinex"
            self.api_key = (
                cfg.get("api_key")
                or os.getenv("APINEX_API_KEY")
                or env_vars.get("APINEX_API_KEY")
                or ""
            )
            self.api_base = (
                cfg.get("api_base")
                or os.getenv("APINEX_BASE_URL")
                or env_vars.get("APINEX_BASE_URL")
                or "https://api.apinex.bond/v1/"
            ).rstrip("/") + "/"
            self.model_name = (
                cfg.get("model")
                or os.getenv("APINEX_MODEL")
                or env_vars.get("APINEX_MODEL")
                or "free/gemini-3.8-flash"
            )
        elif provider_candidate in ["groq", "groq-ai", "groq_ai"]:
            self.provider = "groq"
            self.api_key = (
                cfg.get("api_key")
                or os.getenv("GROQ_API_KEY")
                or env_vars.get("GROQ_API_KEY")
                or ""
            )
            self.api_base = (
                cfg.get("api_base")
                or os.getenv("GROQ_BASE_URL")
                or env_vars.get("GROQ_BASE_URL")
                or "https://api.groq.com/openai/v1/"
            ).rstrip("/") + "/"
            self.model_name = (
                cfg.get("model")
                or os.getenv("GROQ_MODEL")
                or env_vars.get("GROQ_MODEL")
                or "llama-3.3-70b-versatile"
            )
        elif provider_candidate in ["openrouter"]:
            self.provider = "openrouter"
            self.api_key = cfg.get("api_key") or os.getenv("OPENROUTER_API_KEY", "")
            self.api_base = (cfg.get("api_base") or os.getenv("API_BASE_URL", "https://openrouter.ai/api/v1/")).rstrip("/") + "/"
            self.model_name = cfg.get("model") or os.getenv("MODEL_NAME", "anthropic/claude-3.5-sonnet")
        elif provider_candidate in ["openai"]:
            self.provider = "openai"
            self.api_key = cfg.get("api_key") or os.getenv("OPENAI_API_KEY", "")
            self.api_base = (cfg.get("api_base") or os.getenv("API_BASE_URL", "https://api.openai.com/v1/")).rstrip("/") + "/"
            self.model_name = cfg.get("model") or os.getenv("MODEL_NAME", "gpt-4o")
        else:
            self.provider = "ollama"
            self.api_key = (
                cfg.get("api_key")
                or os.getenv("OLLAMA_API_KEY", "ollama")
                or env_vars.get("OLLAMA_API_KEY", "ollama")
            )
            self.api_base = (
                cfg.get("api_base")
                or os.getenv("OLLAMA_BASE_URL")
                or env_vars.get("OLLAMA_BASE_URL")
                or "http://localhost:11434/v1/"
            ).rstrip("/") + "/"
            self.model_name = (
                cfg.get("model")
                or os.getenv("OLLAMA_MODEL")
                or env_vars.get("OLLAMA_MODEL")
                or "gemma4:12b-hermes"
            )

    def _load_env(self) -> Dict[str, str]:
        env_dict: Dict[str, str] = {}
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
                    for line in p.read_text(encoding="utf-8").splitlines():
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            env_dict[k.strip()] = v.strip()
                except Exception:
                    pass
        return env_dict

    def is_configured(self) -> bool:
        if self.provider == "ollama":
            return True
        return bool(self.api_key)

    def _build_candidate_chain(self) -> List[Dict[str, str]]:
        """Builds list of provider configs to attempt, respecting priority and failover rules."""
        # If user explicitly passed an api_key in constructor (e.g. in test suite), use it as initial attempt
        chain = []
        if self.explicit_config and self.api_key:
            chain.append({
                "provider_id": "custom",
                "display_name": f"Configured {self.provider}",
                "provider": self.provider,
                "api_key": self.api_key,
                "api_base": self.api_base,
                "model": self.model_name
            })

        # Add providers from ProviderManager (Gemini Key 1 -> Key 2 -> Key 3 -> APInex)
        for p in provider_manager.get_ordered_providers():
            # Avoid duplicate if same key as custom
            if self.explicit_config and p.api_key == self.api_key:
                continue
            if p.is_available():
                chain.append({
                    "provider_id": p.provider_id,
                    "display_name": p.display_name,
                    "provider": p.provider,
                    "api_key": p.api_key,
                    "api_base": p.api_base,
                    "model": p.default_model
                })

        return chain

    def call_llm_json(
        self,
        system_prompt: str,
        user_prompt: str,
        image_paths: Optional[List[Path]] = None,
        temperature: float = 0.2
    ) -> Optional[Dict[str, Any]]:
        """Sends chat completion request (with optional multimodal images) and returns parsed JSON.
        Automatically fails over across Gemini Key 1 -> Gemini Key 2 -> Gemini Key 3 -> APInex.
        """
        chain = self._build_candidate_chain()
        if not chain:
            if not self.is_configured():
                logger.warning(f"LLMClient ({self.provider}): No API credentials configured. Cannot call LLM API.")
                return None
            chain = [{
                "provider_id": "default",
                "display_name": self.provider,
                "provider": self.provider,
                "api_key": self.api_key,
                "api_base": self.api_base,
                "model": self.model_name
            }]

        content_parts = [{"type": "text", "text": user_prompt}]
        if image_paths:
            for p in image_paths:
                p_path = Path(p)
                if p_path.exists() and p_path.is_file():
                    try:
                        b64_data = base64.b64encode(p_path.read_bytes()).decode("utf-8")
                        content_parts.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{b64_data}",
                                "detail": "high"
                            }
                        })
                        logger.info(f"LLMClient: Attached screenshot '{p_path.name}' ({p_path.stat().st_size} bytes)")
                    except Exception as img_err:
                        logger.warning(f"LLMClient: Failed to encode image '{p_path}': {img_err}")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content_parts if len(content_parts) > 1 else user_prompt}
        ]

        # Iterate through eligible providers in priority order
        last_exception = None
        for prov_idx, prov_cfg in enumerate(chain):
            p_id = prov_cfg["provider_id"]
            d_name = prov_cfg["display_name"]
            p_key = prov_cfg["api_key"]
            p_base = prov_cfg["api_base"]
            p_model = prov_cfg["model"]

            if prov_idx > 0:
                logger.info(f"LLMClient: Automatically failing over to backup provider [{d_name}] with model [{p_model}]")

            payload = {
                "model": p_model,
                "messages": messages,
                "temperature": temperature,
                "response_format": {"type": "json_object"}
            }

            url = f"{p_base}chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {p_key}",
                "User-Agent": "HermesAgent/1.0"
            }

            max_attempts = 2
            attempt_succeeded = False

            for attempt in range(1, max_attempts + 1):
                try:
                    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        raw_body = json.loads(resp.read().decode("utf-8"))
                        raw_content = raw_body["choices"][0]["message"]["content"]

                        raw_str = raw_content.strip()
                        if raw_str.startswith("```json"):
                            raw_str = raw_str[7:]
                        if raw_str.startswith("```"):
                            raw_str = raw_str[3:]
                        if raw_str.endswith("```"):
                            raw_str = raw_str[:-3]

                        parsed_result = json.loads(raw_str.strip())
                        if p_id != "custom" and p_id != "default":
                            provider_manager.mark_success(p_id)
                        attempt_succeeded = True
                        return parsed_result

                except urllib.error.HTTPError as http_err:
                    err_body = ""
                    try:
                        err_body = http_err.read().decode("utf-8", errors="ignore")
                    except Exception:
                        pass

                    sanitized_err = provider_manager.sanitize_text(f"HTTP {http_err.code} {http_err.reason}: {err_body[:250]}")
                    logger.warning(f"LLMClient [{d_name}] attempt {attempt}/{max_attempts} error: {sanitized_err}")

                    # Classification
                    err_class, _ = provider_manager.classify_error(http_err)
                    if p_id != "custom" and p_id != "default":
                        provider_manager.mark_failure(p_id, http_err)

                    # On permanent auth failure or quota limit, fail fast to next provider!
                    if http_err.code in (401, 403, 429) or err_class in (ErrorClass.AUTH_FAILURE, ErrorClass.QUOTA_EXHAUSTED):
                        logger.warning(f"LLMClient: Provider [{d_name}] hit {err_class}. Skipping remaining attempts on this provider.")
                        last_exception = http_err
                        break

                    # Transient server error (5xx)
                    if attempt < max_attempts:
                        time.sleep(1.0)
                    else:
                        last_exception = http_err

                except Exception as e:
                    sanitized_err = provider_manager.sanitize_text(str(e))
                    logger.warning(f"LLMClient [{d_name}] attempt {attempt}/{max_attempts} exception: {sanitized_err}")
                    if p_id != "custom" and p_id != "default":
                        provider_manager.mark_failure(p_id, e)
                    last_exception = e
                    if attempt < max_attempts:
                        time.sleep(1.0)

            if attempt_succeeded:
                break

        logger.error(f"LLMClient: All candidate providers in failover chain failed. Last error: {provider_manager.sanitize_text(last_exception)}")
        return None

    def call_llm_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        timeout: int = 60
    ) -> Optional[str]:
        """Sends chat completion request and returns text/code output.
        Automatically fails over across Gemini Key 1 -> Gemini Key 2 -> Gemini Key 3 -> APInex -> Ollama.
        """
        chain = self._build_candidate_chain()
        if not chain:
            if not self.is_configured():
                logger.warning(f"LLMClient ({self.provider}): No API credentials configured. Cannot call LLM API.")
                return None
            chain = [{
                "provider_id": "default",
                "display_name": self.provider,
                "provider": self.provider,
                "api_key": self.api_key,
                "api_base": self.api_base,
                "model": self.model_name
            }]

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        last_exception = None
        for prov_idx, prov_cfg in enumerate(chain):
            p_id = prov_cfg["provider_id"]
            d_name = prov_cfg["display_name"]
            p_key = prov_cfg["api_key"]
            p_base = prov_cfg["api_base"]
            p_model = prov_cfg["model"]

            if prov_idx > 0:
                logger.info(f"LLMClient: Automatically failing over to backup provider [{d_name}] with model [{p_model}]")

            payload = {
                "model": p_model,
                "messages": messages,
                "temperature": temperature
            }

            url = f"{p_base}chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {p_key}",
                "User-Agent": "HermesAgent/1.0"
            }

            max_attempts = 2
            for attempt in range(1, max_attempts + 1):
                try:
                    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
                    with urllib.request.urlopen(req, timeout=timeout) as resp:
                        raw_body = json.loads(resp.read().decode("utf-8"))
                        raw_content = raw_body["choices"][0]["message"]["content"]
                        text_content = raw_content.strip()

                        if p_id != "custom" and p_id != "default":
                            provider_manager.mark_success(p_id)
                        return text_content

                except urllib.error.HTTPError as http_err:
                    err_body = ""
                    try:
                        err_body = http_err.read().decode("utf-8", errors="ignore")
                    except Exception:
                        pass
                    sanitized_err = provider_manager.sanitize_text(f"HTTP {http_err.code} {http_err.reason}: {err_body[:250]}")
                    logger.warning(f"LLMClient [{d_name}] attempt {attempt}/{max_attempts} error: {sanitized_err}")

                    err_class, _ = provider_manager.classify_error(http_err)
                    if p_id != "custom" and p_id != "default":
                        provider_manager.mark_failure(p_id, http_err)

                    if http_err.code in (401, 403, 429) or err_class in (ErrorClass.AUTH_FAILURE, ErrorClass.QUOTA_EXHAUSTED):
                        logger.warning(f"LLMClient: Provider [{d_name}] hit {err_class}. Skipping remaining attempts.")
                        last_exception = http_err
                        break

                    if attempt < max_attempts:
                        time.sleep(1.0)
                    else:
                        last_exception = http_err

                except Exception as e:
                    sanitized_err = provider_manager.sanitize_text(str(e))
                    logger.warning(f"LLMClient [{d_name}] attempt {attempt}/{max_attempts} exception: {sanitized_err}")
                    if p_id != "custom" and p_id != "default":
                        provider_manager.mark_failure(p_id, e)
                    last_exception = e
                    if attempt < max_attempts:
                        time.sleep(1.0)

        logger.error(f"LLMClient: All candidate providers in failover chain failed for text completion. Last error: {provider_manager.sanitize_text(last_exception)}")
        return None
