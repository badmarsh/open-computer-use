"""
Amazon Bedrock provider — single provider replacing all previous AI providers.
Uses boto3 bedrock-runtime client with AWS credentials from settings.
"""

import logging
from typing import Any, AsyncGenerator, Dict, List, Optional

import boto3

from app.core.config import settings

logger = logging.getLogger(__name__)


class BedrockProvider:
    """Single provider that routes all model calls through Amazon Bedrock."""

    def __init__(self):
        self.name = "bedrock"
        self.api_key = None  # Not used — AWS credentials from settings
        self.client = None
        self.initialized = False
        # Expose AWS credentials so CUA executor can read them
        self.aws_access_key_id = settings.AWS_ACCESS_KEY_ID
        self.aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
        self.aws_region = settings.AWS_REGION

    def initialize(self, api_key: Optional[str] = None):
        """Create boto3 bedrock-runtime client using settings credentials."""
        if not self.aws_access_key_id or not self.aws_secret_access_key:
            logger.warning("AWS credentials not set in settings — BedrockProvider will rely on boto3 default credential chain")

        self.client = boto3.client(
            "bedrock-runtime",
            region_name=self.aws_region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )
        self.initialized = True
        logger.info(f"BedrockProvider initialized (region={self.aws_region})")

    def get_available_models(self) -> List[str]:
        """Return configured Bedrock models."""
        return settings.get_bedrock_models_list()

    async def stream_chat(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        max_steps: int = 1,
        temperature: Optional[float] = 1.0,
        max_tokens: Optional[int] = None,
        **_: Any,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Bedrock streaming is not implemented in this branch."""
        del messages, model, tools, max_steps, temperature, max_tokens
        raise NotImplementedError(
            "Bedrock stream_chat is not implemented in this branch. "
            "Set LLM_PROVIDER=openai with OPENAI_BASE_URL/OPENAI_API_KEY to use a custom endpoint."
        )
