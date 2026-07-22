"""Pydantic request/response models for the harness API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Effort = Literal["low", "medium", "high", "xhigh", "max"]


class ModelInfo(BaseModel):
    id: str
    provider: str
    display_name: str
    description: str = ""


class ScaffoldInfo(BaseModel):
    name: str
    description: str
    # How many model calls the scaffold makes for one run.
    calls: int


class RunRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="The task to run.")
    model: str = Field(..., description="A model id from GET /models.")
    scaffold: str = Field("direct", description="A scaffold name from GET /scaffolds.")
    system: str | None = Field(
        None, description="Optional system prompt prepended by the scaffold."
    )
    effort: Effort | None = Field(
        None, description="Reasoning effort (Anthropic models only)."
    )
    max_tokens: int | None = Field(
        None, gt=0, description="Override the per-call output token cap."
    )


class Step(BaseModel):
    """One model call within a scaffold run."""

    label: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    output: str


class RunResult(BaseModel):
    provider: str
    model: str
    scaffold: str
    output: str
    steps: list[Step]
    total_input_tokens: int | None = None
    total_output_tokens: int | None = None
    latency_ms: int
    error: str | None = None


class Cell(BaseModel):
    """One model/scaffold combination to evaluate in a compare matrix."""

    model: str
    scaffold: str = "direct"


class CompareRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    matrix: list[Cell] = Field(..., min_length=1, description="Combinations to run.")
    system: str | None = None
    effort: Effort | None = None
    max_tokens: int | None = Field(None, gt=0)


class CompareResult(BaseModel):
    prompt: str
    results: list[RunResult]
