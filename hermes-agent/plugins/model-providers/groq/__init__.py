"""Groq provider profile.

Groq offers fast LPU inference via an OpenAI-compatible endpoint at https://api.groq.com/openai/v1.
"""

from providers import register_provider
from providers.base import ProviderProfile

groq = ProviderProfile(
    name="groq",
    aliases=("groq-ai", "groq_ai"),
    display_name="Groq",
    description="Groq — High-speed inference for open models (Llama, Gemma, Mixtral)",
    signup_url="https://console.groq.com/keys",
    env_vars=("GROQ_API_KEY", "GROQ_BASE_URL", "GROQ_MODEL"),
    base_url="https://api.groq.com/openai/v1",
    auth_type="api_key",
    supports_vision=True,
    default_aux_model="llama-3.3-70b-versatile",
    fallback_models=(
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
    ),
)

register_provider(groq)
