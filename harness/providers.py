"""Provider adapters.

A provider turns a (system, messages) pair into a text completion plus token
usage. Two providers ship:

- ``mock``: deterministic, offline, no key. Used for tests and for exercising
  scaffolds without spending money.
- ``anthropic``: live Claude models via the official SDK.

The Anthropic SDK is imported lazily so the service (and the test suite) runs
even when the package or key is absent.
"""

from __future__ import annotations

from dataclasses import dataclass

from .config import get_settings


@dataclass
class Completion:
    text: str
    input_tokens: int | None = None
    output_tokens: int | None = None


class ProviderError(RuntimeError):
    """Raised when a provider cannot service a request."""


class Provider:
    name: str = "base"

    def available(self) -> bool:
        raise NotImplementedError

    def complete(
        self,
        *,
        model: str,
        system: str | None,
        messages: list[dict],
        max_tokens: int,
        effort: str | None = None,
    ) -> Completion:
        raise NotImplementedError


class MockProvider(Provider):
    """Deterministic provider for offline runs and tests.

    It echoes a compact, structured view of what it was asked, which makes
    scaffold behaviour (extra calls, system prompts, message threading)
    observable without a network round-trip.
    """

    name = "mock"

    def available(self) -> bool:
        return True

    def complete(
        self,
        *,
        model: str,
        system: str | None,
        messages: list[dict],
        max_tokens: int,
        effort: str | None = None,
    ) -> Completion:
        last_user = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"),
            "",
        )
        parts = [f"[mock:{model}]"]
        if system:
            parts.append(f"(system: {system.strip()[:60]})")
        if effort:
            parts.append(f"(effort={effort})")
        parts.append(f"answer to: {last_user.strip()[:200]}")
        text = " ".join(parts)
        # Cheap, stable token estimates (~4 chars/token).
        in_tokens = sum(len(m["content"]) for m in messages) // 4
        if system:
            in_tokens += len(system) // 4
        return Completion(
            text=text,
            input_tokens=in_tokens,
            output_tokens=len(text) // 4,
        )


class AnthropicProvider(Provider):
    """Live Claude models via the Anthropic Messages API."""

    name = "anthropic"

    def __init__(self) -> None:
        self._client = None

    def available(self) -> bool:
        return get_settings().anthropic_configured

    def _get_client(self):
        if self._client is not None:
            return self._client
        settings = get_settings()
        if not settings.anthropic_configured:
            raise ProviderError(
                "anthropic provider is not configured (set ANTHROPIC_API_KEY)"
            )
        try:
            import anthropic  # imported lazily; optional dependency
        except ImportError as exc:  # pragma: no cover - depends on env
            raise ProviderError(
                "the 'anthropic' package is not installed; run "
                "'pip install anthropic'"
            ) from exc
        self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        return self._client

    def complete(
        self,
        *,
        model: str,
        system: str | None,
        messages: list[dict],
        max_tokens: int,
        effort: str | None = None,
    ) -> Completion:
        client = self._get_client()
        kwargs: dict = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages,
        }
        if system:
            kwargs["system"] = system
        if effort:
            kwargs["output_config"] = {"effort": effort}
        try:
            resp = client.messages.create(**kwargs)
        except Exception as exc:  # surface a clean error to the API layer
            raise ProviderError(str(exc)) from exc
        text = "".join(
            block.text for block in resp.content if getattr(block, "type", None) == "text"
        )
        return Completion(
            text=text,
            input_tokens=getattr(resp.usage, "input_tokens", None),
            output_tokens=getattr(resp.usage, "output_tokens", None),
        )


_PROVIDERS: dict[str, Provider] = {
    "mock": MockProvider(),
    "anthropic": AnthropicProvider(),
}


def get_provider(name: str) -> Provider:
    try:
        return _PROVIDERS[name]
    except KeyError:
        raise ProviderError(f"unknown provider: {name!r}") from None


def provider_names() -> list[str]:
    return list(_PROVIDERS)
