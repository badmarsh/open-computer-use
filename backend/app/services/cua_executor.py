"""
Compatibility wrapper for legacy CUA executor imports.

This repository currently ships the consolidated multi-agent executor, while
some routes still import ``CUAExecutor`` directly. Keep that import path valid
so the backend can start in deployments built from this checkout.
"""

from app.services.multi_agent_executor import MultiAgentExecutor


class CUAExecutor(MultiAgentExecutor):
    """Backward-compatible alias for the consolidated executor."""

