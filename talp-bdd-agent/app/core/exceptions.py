"""Domain exceptions used across API and service layers."""

from __future__ import annotations


class UpstreamRateLimitError(RuntimeError):
    """Raised when an upstream LLM provider rejects requests due to rate limits."""
