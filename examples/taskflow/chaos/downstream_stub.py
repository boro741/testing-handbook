"""A tiny stand-in for a dependency. Used only by the fault-injection test.

Run by hand:  uvicorn downstream_stub:app --host 0.0.0.0 --port 9001   (from this folder)
(--host 0.0.0.0 lets a Docker container reach it. Local testing only.)
"""
from fastapi import FastAPI

app = FastAPI(title="downstream-stub")


@app.get("/ping")
def ping() -> dict[str, str]:
    return {"status": "ok", "service": "downstream-stub"}
