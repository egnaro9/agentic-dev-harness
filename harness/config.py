"""Configuration for the harness.

API keys and provider settings are read from the environment so nothing
sensitive lives in the repo. The mock provider needs no key, which is what
lets the service (and its tests) run with zero configuration.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


def _redact(secret: str | None) -> str | None:
    """Return a display-safe fingerprint of a secret, never the secret itself."""
    if not secret:
        return None
    if len(secret) <= 8:
        return "****"
    return f"{secret[:4]}…{secret[-4:]}"


@dataclass(frozen=True)
class ProviderConfig:
    """Static, non-secret description of a provider's availability."""

    name: str
    configured: bool
    key_fingerprint: str | None
    note: str


@dataclass
class Settings:
    """Runtime settings resolved from the environment.

    Read once at import time via :func:`get_settings`. The Anthropic key is the
    only real credential; the mock provider is always available.
    """

    anthropic_api_key: str | None = field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY")
    )
    # Default output cap for a single model call. Kept modest so ad-hoc runs
    # stay cheap; callers can override per request.
    default_max_tokens: int = field(
        default_factory=lambda: int(os.getenv("HARNESS_MAX_TOKENS", "1024"))
    )

    @property
    def anthropic_configured(self) -> bool:
        return bool(self.anthropic_api_key)

    def provider_configs(self) -> list[ProviderConfig]:
        return [
            ProviderConfig(
                name="mock",
                configured=True,
                key_fingerprint=None,
                note="Offline deterministic provider. No API key required.",
            ),
            ProviderConfig(
                name="anthropic",
                configured=self.anthropic_configured,
                key_fingerprint=_redact(self.anthropic_api_key),
                note=(
                    "Live Claude models via the Anthropic API. "
                    "Set ANTHROPIC_API_KEY to enable."
                ),
            ),
        ]


_settings: Settings | None = None


def get_settings() -> Settings:
    """Return the process-wide settings, resolving the environment once."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
