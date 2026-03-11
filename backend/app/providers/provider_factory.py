"""
Provider factory with support for Bedrock and OpenAI-compatible endpoints.
"""

import logging
from typing import Any, Dict

from app.core.config import settings
from app.providers.bedrock_provider import BedrockProvider
from app.providers.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)


class ProviderFactory:
    """Factory for model providers."""

    def __init__(self):
        self._providers: Dict[str, Any] = {}

    def get_provider(self, model_id: str):
        """Return provider for requested model/provider mode."""
        provider_name = self._resolve_provider_name(model_id)
        if provider_name not in self._providers:
            self._providers[provider_name] = self._create_provider(provider_name)
        return self._providers[provider_name]

    def _create_provider(self, provider: str):
        """Create provider instance by name."""
        provider_name = (provider or "").lower()
        if provider_name == "openai":
            return OpenAIProvider()
        if provider_name == "bedrock":
            return BedrockProvider()
        raise ValueError(f"Unsupported provider: {provider}")

    def _resolve_provider_name(self, model_id: str) -> str:
        """Resolve provider from config (preferred) or model id fallback."""
        configured = (settings.LLM_PROVIDER or "").strip().lower()
        if configured in {"bedrock", "openai"}:
            return configured

        if model_id and self._looks_like_openai_model(model_id):
            return "openai"
        return "bedrock"

    def get_default_model(self) -> str:
        """Get default model for active provider."""
        provider_name = self._resolve_provider_name("")
        if provider_name == "openai":
            return settings.OPENAI_DEFAULT_MODEL
        return settings.BEDROCK_DEFAULT_MODEL

    def resolve_model(self, requested_model: str) -> str:
        """Pick model id for current provider, with safe fallback."""
        provider_name = self._resolve_provider_name(requested_model)
        if provider_name == "openai":
            if requested_model and self._looks_like_openai_model(requested_model):
                return requested_model
            return settings.OPENAI_DEFAULT_MODEL

        if requested_model and not self._looks_like_openai_model(requested_model):
            return requested_model
        return settings.BEDROCK_DEFAULT_MODEL

    def get_all_models(self):
        """Return models for active provider."""
        provider_name = self._resolve_provider_name("")
        provider = self.get_provider(self.get_default_model())
        models = provider.get_available_models()
        return [{"id": model_id, "provider": provider_name} for model_id in models]

    def _looks_like_openai_model(self, model_id: str) -> bool:
        mid = (model_id or "").lower()
        return (
            mid.startswith("gpt-")
            or mid.startswith("o1")
            or mid.startswith("o3")
            or mid.startswith("o4")
            or mid.startswith("openai/")
        )
