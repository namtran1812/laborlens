from __future__ import annotations

import httpx

from laborlens.research.research_bundle import ResearchBundle
from laborlens.writer.prompt import (
    SYSTEM_INSTRUCTIONS,
    build_writer_input,
)


class OllamaWriter:
    def __init__(
        self,
        *,
        host: str,
        model: str,
        timeout: float = 180.0,
    ) -> None:
        self.host = host.rstrip("/")
        self.model = model
        self.timeout = timeout

    def write(
        self,
        bundle: ResearchBundle,
    ) -> str:
        response = httpx.post(
            f"{self.host}/api/generate",
            json={
                "model": self.model,
                "system": SYSTEM_INSTRUCTIONS,
                "prompt": build_writer_input(bundle),
                "stream": False,
                "think": False,
                "options": {
                    "temperature": 0.2,
                },
            },
            timeout=self.timeout,
        )

        response.raise_for_status()

        payload = response.json()

        article = payload.get(
            "response",
            "",
        ).strip()

        if not article:
            raise RuntimeError("Ollama returned an empty response")

        return article
