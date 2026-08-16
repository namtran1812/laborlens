from datetime import date

from fastapi.testclient import TestClient

from laborlens.api.app import app

client = TestClient(app)


def test_ask_schema_rejects_short_question() -> None:
    response = client.post("/ask", json={"question": "x", "start_date": "2024-06-01"})
    assert response.status_code == 422


def test_ask_request_model_date() -> None:
    from laborlens.api.schemas import AskRequest

    request = AskRequest(question="Explain this episode", start_date=date(2024, 6, 1))
    assert request.window == 24


def test_ask_falls_back_when_ollama_is_unavailable(monkeypatch) -> None:
    import httpx

    import laborlens.api.app as app_module
    from laborlens.api.assistant import AssistantAnswer
    from laborlens.api.planner import AskIntent, AskPlan

    class FakePipeline:
        def build(self, **kwargs):
            return object()

    def fake_plan_question(question, explicit_area=None):
        return AskPlan(
            intent=AskIntent.GENERAL_RESEARCH,
            area_fips=explicit_area,
            needs_qcew=False,
            needs_macro=True,
            deterministic_answer=False,
        )

    def failing_ollama_answer(**kwargs):
        raise httpx.ConnectError("Ollama unavailable")

    def fake_deterministic_answer(*, plan, bundle):
        assert plan.intent == AskIntent.GENERAL_RESEARCH
        return AssistantAnswer(
            answer="Verified deterministic fallback answer.",
            mode="deterministic-research",
            model="laborlens-rules",
            sources=("verified-source",),
            caveat="Answer generated only from verified LaborLens research outputs.",
        )

    monkeypatch.setattr(app_module, "plan_question", fake_plan_question)
    monkeypatch.setattr(app_module, "pipeline", lambda: FakePipeline())
    monkeypatch.setattr(app_module, "ollama_answer", failing_ollama_answer)
    monkeypatch.setattr(app_module, "deterministic_answer", fake_deterministic_answer)
    response = client.post(
        "/ask",
        json={
            "question": "Give me a nuanced interpretation of this episode.",
            "start_date": "2024-06-01",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"] == "Verified deterministic fallback answer."
    assert payload["mode"] == "deterministic-research"
    assert payload["model"] == "laborlens-rules"
    assert payload["sources"] == ["verified-source"]
