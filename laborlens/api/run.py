from __future__ import annotations

import os

import uvicorn


def main() -> None:
    uvicorn.run(
        "laborlens.api.app:app",
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                "8000",
            )
        ),
        reload=False,
    )


if __name__ == "__main__":
    main()
