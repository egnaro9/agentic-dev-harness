"""The model registry.

Maps each known model id to the provider that serves it. Live Claude ids are
the current defaults; the mock provider registers a stand-in so the whole
matrix can be exercised offline.
"""

from __future__ import annotations

from .schemas import ModelInfo

_MODELS: dict[str, ModelInfo] = {
    m.id: m
    for m in (
        ModelInfo(
            id="mock-model",
            provider="mock",
            display_name="Mock Model",
            description="Deterministic offline model for testing scaffolds.",
        ),
        ModelInfo(
            id="claude-opus-4-8",
            provider="anthropic",
            display_name="Claude Opus 4.8",
            description="Most capable Opus-tier model.",
        ),
        ModelInfo(
            id="claude-sonnet-5",
            provider="anthropic",
            display_name="Claude Sonnet 5",
            description="Balanced speed and intelligence.",
        ),
        ModelInfo(
            id="claude-haiku-4-5",
            provider="anthropic",
            display_name="Claude Haiku 4.5",
            description="Fastest, most cost-effective.",
        ),
    )
}


def get_model(model_id: str) -> ModelInfo:
    try:
        return _MODELS[model_id]
    except KeyError:
        raise KeyError(f"unknown model: {model_id!r}") from None


def all_models() -> list[ModelInfo]:
    return list(_MODELS.values())
