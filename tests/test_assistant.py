from datetime import date

from fastapi.testclient import TestClient

from laborlens.api.app import app
from laborlens.api.assistant import (
    demo_answer,
)

client = TestClient(app)


def test_demo_answer_is_grounded() -> None:
    result = demo_answer("Why was this detected on July 30?")

    assert "July 30" in result.answer
    assert "JTSHIR" in result.answer
    assert "JTSJOL" in result.answer


def test_demo_revision_answer() -> None:
    result = demo_answer("How did revisions change it?")

    assert "-0.446" in result.answer
    assert "-0.461" in result.answer


def test_meta_endpoint() -> None:
    response = client.get("/meta")

    assert response.status_code == 200

    payload = response.json()

    assert payload["name"] == "LaborLens"
    assert payload["ai_available"] is True
    assert payload["suggested_questions"]


def test_ask_schema_rejects_short_question() -> None:
    response = client.post(
        "/ask",
        json={
            "question": "x",
            "start_date": "2024-06-01",
        },
    )

    assert response.status_code == 422


def test_ask_request_model_date() -> None:
    from laborlens.api.schemas import (
        AskRequest,
    )

    request = AskRequest(
        question="Explain this episode",
        start_date=date(
            2024,
            6,
            1,
        ),
    )

    assert request.window == 24
