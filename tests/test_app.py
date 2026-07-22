"""Tests for the harness API, exercised entirely through the offline mock
provider so they run without any API key or network access.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from harness.app import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_config_redacts_and_lists_providers():
    r = client.get("/config")
    assert r.status_code == 200
    names = {p["name"] for p in r.json()["providers"]}
    assert {"mock", "anthropic"} <= names
    mock = next(p for p in r.json()["providers"] if p["name"] == "mock")
    assert mock["configured"] is True
    assert mock["key_fingerprint"] is None


def test_models_and_scaffolds_listed():
    models = {m["id"] for m in client.get("/models").json()}
    assert "mock-model" in models
    assert "claude-opus-4-8" in models

    scaffolds = {s["name"] for s in client.get("/scaffolds").json()}
    assert {"direct", "cot", "self_critique", "plan_execute"} <= scaffolds


def test_run_direct_mock():
    r = client.post(
        "/run",
        json={"prompt": "What is 2+2?", "model": "mock-model", "scaffold": "direct"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["provider"] == "mock"
    assert body["error"] is None
    assert len(body["steps"]) == 1
    assert "What is 2+2?" in body["output"]


def test_two_call_scaffolds_make_two_steps():
    for scaffold in ("self_critique", "plan_execute"):
        r = client.post(
            "/run",
            json={"prompt": "Summarize AI.", "model": "mock-model", "scaffold": scaffold},
        )
        assert r.status_code == 200, scaffold
        assert len(r.json()["steps"]) == 2, scaffold


def test_run_reports_token_totals():
    r = client.post(
        "/run",
        json={"prompt": "hello", "model": "mock-model", "scaffold": "cot"},
    )
    body = r.json()
    assert body["total_input_tokens"] is not None
    assert body["total_output_tokens"] is not None
    assert body["latency_ms"] >= 0


def test_unknown_model_is_400():
    r = client.post(
        "/run",
        json={"prompt": "hi", "model": "does-not-exist", "scaffold": "direct"},
    )
    assert r.status_code == 400


def test_unknown_scaffold_is_400():
    r = client.post(
        "/run",
        json={"prompt": "hi", "model": "mock-model", "scaffold": "nope"},
    )
    assert r.status_code == 400


def test_compare_matrix_returns_one_row_per_cell():
    r = client.post(
        "/compare",
        json={
            "prompt": "Explain recursion.",
            "matrix": [
                {"model": "mock-model", "scaffold": "direct"},
                {"model": "mock-model", "scaffold": "cot"},
                {"model": "mock-model", "scaffold": "self_critique"},
            ],
        },
    )
    assert r.status_code == 200
    results = r.json()["results"]
    assert len(results) == 3
    assert [x["scaffold"] for x in results] == ["direct", "cot", "self_critique"]


def test_anthropic_cell_without_key_reports_error_not_crash():
    # In a no-key environment the anthropic provider is unavailable; the cell
    # should carry an error string rather than raising. If a key happens to be
    # configured, only assert the request itself doesn't crash.
    from harness.config import get_settings

    r = client.post(
        "/run",
        json={"prompt": "hi", "model": "claude-opus-4-8", "scaffold": "direct"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["provider"] == "anthropic"
    if not get_settings().anthropic_configured:
        assert body["error"] is not None
