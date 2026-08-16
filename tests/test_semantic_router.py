from laborlens.api.planner import (
    AskIntent,
)
from laborlens.api.semantic_router import (
    semantic_route,
)


def test_semantic_router_macro_paraphrase():
    route = semantic_route("Which series were doing most of the work in this classification?")

    assert route.intent == AskIntent.MACRO_EVIDENCE


def test_semantic_router_causal_paraphrase():
    route = semantic_route("Was government policy the underlying driver here?")

    assert route.intent == AskIntent.CAUSAL_ATTRIBUTION


def test_semantic_router_point_in_time():
    route = semantic_route("What stops December data from leaking into a September analysis?")

    assert route.intent == AskIntent.POINT_IN_TIME


def test_semantic_router_methodology():
    route = semantic_route("What happens mathematically before the skeptic sees a claim?")

    assert route.intent == AskIntent.METHODOLOGY
