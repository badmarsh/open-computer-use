"""
OpenAI-compatible provider.
Supports custom `base_url` for self-hosted OpenAI-compatible endpoints.
"""

import json
import logging
from typing import Any, AsyncGenerator, Dict, List, Optional

from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAIProvider:
    """Provider for OpenAI-compatible chat completion endpoints."""

    def __init__(self):
        self.name = "openai"
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = settings.OPENAI_BASE_URL
        self.default_model = settings.OPENAI_DEFAULT_MODEL
        self.client: Optional[AsyncOpenAI] = None
        self.initialized = False

    def initialize(self, api_key: Optional[str] = None):
        """Initialize AsyncOpenAI client."""
        if self.initialized and self.client:
            return

        effective_key = api_key or self.api_key or "not-required"
        client_kwargs: Dict[str, Any] = {"api_key": effective_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        self.client = AsyncOpenAI(**client_kwargs)
        self.initialized = True
        logger.info(f"OpenAIProvider initialized (base_url={self.base_url or 'default'})")

    def get_available_models(self) -> List[str]:
        raw = settings.OPENAI_AVAILABLE_MODELS or self.default_model
        if isinstance(raw, str):
            return [m.strip() for m in raw.split(",") if m.strip()]
        return list(raw)

    async def stream_chat(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        max_steps: int = 1,  # kept for compatibility with existing executor calls
        temperature: Optional[float] = 1.0,
        max_tokens: Optional[int] = None,
        **_: Any,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream assistant text chunks from OpenAI-compatible endpoint."""
        del max_steps  # not used by OpenAI API directly

        if not self.client or not self.initialized:
            self.initialize()

        normalized_messages: List[Dict[str, Any]] = []
        for msg in messages or []:
            role = str(msg.get("role", "user"))
            if role not in {"system", "user", "assistant", "tool"}:
                role = "user"
            normalized_messages.append(
                {
                    "role": role,
                    "content": self._coerce_content(msg.get("content", "")),
                }
            )

        request_kwargs: Dict[str, Any] = {
            "model": model or self.default_model,
            "messages": normalized_messages,
            "stream": True,
        }
        if temperature is not None:
            request_kwargs["temperature"] = temperature
        if max_tokens is not None:
            request_kwargs["max_tokens"] = max_tokens
        if tools:
            request_kwargs["tools"] = tools

        stream = await self.client.chat.completions.create(**request_kwargs)
        async for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield {"type": "text", "content": delta.content}

        yield {"type": "finish", "finish_reason": "stop"}

    def _coerce_content(self, content: Any) -> str:
        """Normalize message content into a plain string for chat completions."""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            text_parts: List[str] = []
            for item in content:
                if isinstance(item, str):
                    text_parts.append(item)
                elif isinstance(item, dict):
                    if item.get("type") == "text":
                        text_parts.append(str(item.get("text", "")))
                    elif "content" in item:
                        text_parts.append(str(item.get("content", "")))
                    elif "text" in item:
                        text_parts.append(str(item.get("text", "")))
            return "\n".join(part for part in text_parts if part)
        if isinstance(content, dict):
            return json.dumps(content)
        return str(content)
