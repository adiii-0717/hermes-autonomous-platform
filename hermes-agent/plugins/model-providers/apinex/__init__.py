"""APInex provider profile.

APInex provides an OpenAI-compatible API endpoint at https://api.apinex.bond/v1.
Supports chat completions, streaming, and tool calling with free-tier and premium models.
"""

from providers import register_provider
from providers.base import ProviderProfile

apinex = ProviderProfile(
    name="apinex",
    aliases=("apinex-ai", "apinex-bond", "apinex_bond"),
    display_name="APInex",
    description="APInex — OpenAI-compatible API gateway (https://api.apinex.bond/v1)",
    signup_url="https://apinex.bond/models",
    env_vars=("APINEX_API_KEY", "APINEX_BASE_URL", "APINEX_MODEL"),
    base_url="https://api.apinex.bond/v1",
    auth_type="api_key",
    supports_vision=True,
    default_headers={
        "User-Agent": "HermesAgent/1.0",
    },
    default_aux_model="free/gemini-3.8-flash",
    fallback_models=(
        "free/gemini-3.8-flash",
        "free/deepseek-v4.1-flash",
        "free/gpt-6-luna",
        "free/glm-5.3-flash",
        "free/qwen-3.8-max",
    ),
)

register_provider(apinex)
