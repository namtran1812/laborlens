from __future__ import annotations

import httpx
from fastapi import FastAPI, HTTPException

from laborlens.api.assistant import ollama_answer
from laborlens.api.grounded_answer import (
    deterministic_answer,
)
from laborlens.api.planner import plan_question
from laborlens.api.schemas import (
    AskRequest,
    AskResponse,
)
from laborlens.config import get_settings
from laborlens.services.research_pipeline import (
    ResearchPipeline,
)
from laborlens.storage.clickhouse import (
    ClickHouseStore,
)

app = FastAPI(
    title="LaborLens",
    description=(
        "Revision-aware labor-market research engine using point-in-time FRED/ALFRED and QCEW data."
    ),
    version="0.1.0",
)

settings = get_settings()


def pipeline() -> ResearchPipeline:
    return ResearchPipeline(ClickHouseStore(get_settings()))


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "laborlens",
    }


@app.post(
    "/ask",
    response_model=AskResponse,
)
def ask(
    request: AskRequest,
) -> AskResponse:
    plan = plan_question(
        request.question,
        explicit_area=request.area,
    )

    if plan.needs_qcew and plan.area_fips is None:
        raise HTTPException(
            status_code=422,
            detail=(
                "This question requires a geography. "
                "Include a supported geography such as "
                "'Florida' in the question or provide "
                "the QCEW area FIPS code in 'area'."
            ),
        )

    try:
        bundle = pipeline().build(
            start_date=request.start_date,
            window=request.window,
            min_confidence=(request.min_confidence),
            as_of_date=request.as_of,
            qcew_area_fips=(plan.area_fips if plan.needs_qcew else None),
            qcew_industry_level=(request.industry_level),
            qcew_context_limit=(request.context_limit),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    if plan.deterministic_answer:
        result = deterministic_answer(
            plan=plan,
            bundle=bundle,
        )

    elif settings.laborlens_llm_provider == "ollama":
        try:
            result = ollama_answer(
                question=request.question,
                bundle=bundle,
                settings=settings,
            )

        except (
            httpx.HTTPError,
            RuntimeError,
        ):
            #
            # Local generation is optional.
            # Availability of the research API must not
            # depend on Ollama being reachable.
            #
            result = deterministic_answer(
                plan=plan,
                bundle=bundle,
            )

    else:
        #
        # Unsupported or unavailable generation providers
        # degrade to the verified deterministic engine.
        #
        result = deterministic_answer(
            plan=plan,
            bundle=bundle,
        )

    return AskResponse(
        answer=result.answer,
        mode=result.mode,
        model=result.model,
        sources=list(result.sources),
        caveat=result.caveat,
    )
