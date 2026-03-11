"""AI provider service wrapper."""

import os
import logging
from typing import Optional

from app.providers.provider_factory import ProviderFactory
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIProviderService:
    """Service for managing the configured provider."""

    def __init__(self):
        self._factory = ProviderFactory()

    def get_provider(self, model_id: str):
        """Get provider for a model."""
        return self._factory.get_provider(model_id)

    def is_model_available(self, model_id: str, user_id: Optional[str] = None) -> bool:
        """Check if configured credentials are available for the active provider."""
        provider_mode = (settings.LLM_PROVIDER or "bedrock").lower()
        if provider_mode == "openai":
            return bool(settings.OPENAI_API_KEY) or bool(settings.OPENAI_BASE_URL)
        if model_id in settings.FREE_MODELS:
            return True
        # Bedrock available if AWS credentials are configured
        return bool(os.environ.get("AWS_ACCESS_KEY_ID"))
