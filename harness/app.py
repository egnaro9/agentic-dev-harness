"""FastAPI application: the model & scaffolding testing harness.

Run locally with:

    uvicorn harness.app:app --reload

Interactive docs are served at /docs.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from . import __version__
from .config import get_settings
from .registry import all_models
from .runner import run_cell
from .scaffolds import all_scaffolds
from .schemas import (
    CompareRequest,
    CompareResult,
    ModelInfo,
    RunRequest,
    RunResult,
    ScaffoldInfo,
)

app = FastAPI(
    title="Model & Scaffolding Harness",
    version=__version__,
    description=(
        "A configuration tool for testing LLM models across different "
        "scaffoldings. Uses API keys to run a prompt through a matrix of "
        "model/scaffold combinations and compare the results."
    ),
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": __version__}


@app.get("/config")
def config() -> dict:
    """Show provider configuration with secrets redacted."""
    settings = get_settings()
    return {
        "default_max_tokens": settings.default_max_tokens,
        "providers": [pc.__dict__ for pc in settings.provider_configs()],
    }


@app.get("/models", response_model=list[ModelInfo])
def models() -> list[ModelInfo]:
    return all_models()


@app.get("/scaffolds", response_model=list[ScaffoldInfo])
def scaffolds() -> list[ScaffoldInfo]:
    return [
        ScaffoldInfo(name=s.name, description=s.description, calls=s.calls)
        for s in all_scaffolds()
    ]


@app.post("/run", response_model=RunResult)
def run(req: RunRequest) -> RunResult:
    try:
        return run_cell(
            prompt=req.prompt,
            model_id=req.model,
            scaffold_name=req.scaffold,
            system=req.system,
            effort=req.effort,
            max_tokens=req.max_tokens,
        )
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/compare", response_model=CompareResult)
def compare(req: CompareRequest) -> CompareResult:
    results = []
    for cell in req.matrix:
        try:
            results.append(
                run_cell(
                    prompt=req.prompt,
                    model_id=cell.model,
                    scaffold_name=cell.scaffold,
                    system=req.system,
                    effort=req.effort,
                    max_tokens=req.max_tokens,
                )
            )
        except KeyError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    return CompareResult(prompt=req.prompt, results=results)
