# Model & Scaffolding Harness

A small FastAPI configuration tool for **testing LLM models across different
scaffoldings**. You give it a prompt and a matrix of `model × scaffold`
combinations; it runs each one through the configured provider (using your API
keys) and returns the outputs, per-call traces, token usage, and latency side by
side.

It ships with an offline **mock provider** so the whole service — and its test
suite — runs with **zero configuration and no API key**. Add
`ANTHROPIC_API_KEY` to test live Claude models.

## Concepts

- **Provider** — turns a `(system, messages)` pair into a completion.
  - `mock`: deterministic, offline, no key required.
  - `anthropic`: live Claude models via the official SDK.
- **Model** — a registered id bound to a provider (`mock-model`,
  `claude-opus-4-8`, `claude-sonnet-5`, `claude-haiku-4-5`).
- **Scaffold** — a strategy for wrapping a model around a task:
  - `direct` — one call, prompt straight through.
  - `cot` — one call with a chain-of-thought instruction.
  - `self_critique` — draft, then critique-and-revise (2 calls).
  - `plan_execute` — plan, then execute (2 calls).

## Run it

```bash
pip install -r requirements.txt
uvicorn harness.app:app --reload      # docs at http://127.0.0.1:8000/docs
export ANTHROPIC_API_KEY=sk-ant-...   # optional: enables live Claude models
```

## Endpoints

| Method | Path         | Purpose                                        |
| ------ | ------------ | ---------------------------------------------- |
| GET    | `/health`    | Liveness check.                                |
| GET    | `/config`    | Provider configuration (API keys redacted).    |
| GET    | `/models`    | Registered models.                             |
| GET    | `/scaffolds` | Available scaffolds.                           |
| POST   | `/run`       | Run one `model × scaffold` against a prompt.   |
| POST   | `/compare`   | Run a matrix of combinations against a prompt. |

### Example: compare scaffolds offline

```bash
curl -s localhost:8000/compare -H 'content-type: application/json' -d '{
  "prompt": "Explain recursion to a beginner.",
  "matrix": [
    {"model": "mock-model", "scaffold": "direct"},
    {"model": "mock-model", "scaffold": "cot"},
    {"model": "mock-model", "scaffold": "self_critique"}
  ]
}'
```

Swap `mock-model` for `claude-sonnet-5` (with a key set) to test a live model,
and add `"effort": "high"` to the request to control Claude's reasoning depth.

## Tests

```bash
pytest        # runs fully offline via the mock provider
```
