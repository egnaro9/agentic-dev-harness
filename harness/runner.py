"""Orchestration: run one model/scaffold combination against a prompt."""

from __future__ import annotations

import time

from .config import get_settings
from .providers import ProviderError, get_provider
from .registry import get_model
from .scaffolds import get_scaffold
from .schemas import RunResult


def run_cell(
    *,
    prompt: str,
    model_id: str,
    scaffold_name: str,
    system: str | None = None,
    effort: str | None = None,
    max_tokens: int | None = None,
) -> RunResult:
    """Execute a single (model, scaffold) combination.

    Never raises for provider/model errors — those are captured onto the
    ``error`` field so a compare matrix returns one row per cell regardless of
    individual failures. Unknown model or scaffold names raise ``KeyError`` (a
    client mistake, surfaced as a 400 by the API layer).
    """
    model = get_model(model_id)  # KeyError -> 400
    scaffold = get_scaffold(scaffold_name)  # KeyError -> 400
    provider = get_provider(model.provider)
    tokens = max_tokens or get_settings().default_max_tokens

    started = time.monotonic()
    try:
        output, steps = scaffold.run(
            provider=provider,
            model=model.id,
            prompt=prompt,
            system=system,
            max_tokens=tokens,
            effort=effort,
        )
        error = None
    except ProviderError as exc:
        output, steps, error = "", [], str(exc)

    latency_ms = int((time.monotonic() - started) * 1000)

    def _sum(field: str) -> int | None:
        vals = [getattr(s, field) for s in steps if getattr(s, field) is not None]
        return sum(vals) if vals else None

    return RunResult(
        provider=model.provider,
        model=model.id,
        scaffold=scaffold.name,
        output=output,
        steps=steps,
        total_input_tokens=_sum("input_tokens"),
        total_output_tokens=_sum("output_tokens"),
        latency_ms=latency_ms,
        error=error,
    )
