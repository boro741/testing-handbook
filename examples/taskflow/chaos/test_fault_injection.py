"""Fault injection with Toxiproxy, using its HTTP API.

The client talks to Toxiproxy on localhost:22220, which forwards to the
stub on port 9001. Toxiproxy adds latency. The tests skip when Toxiproxy
is not running on localhost:8474.
"""
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest

HERE = Path(__file__).parent
TOXIPROXY_API = "http://localhost:8474"
PROXY_NAME = "downstream_ping"
PROXY_LISTEN = "0.0.0.0:22220"
CLIENT_URL = "http://localhost:22220/ping"
# host.docker.internal lets the Toxiproxy container reach the stub on the host.
UPSTREAM = "host.docker.internal:9001"
STUB_PORT = 9001


def _toxiproxy_reachable() -> bool:
    try:
        return httpx.get(f"{TOXIPROXY_API}/version", timeout=1).status_code == 200
    except httpx.HTTPError:
        return False


requires_toxiproxy = pytest.mark.skipif(
    not _toxiproxy_reachable(),
    reason="Toxiproxy is not reachable at localhost:8474. Start it with docker run (see the fault-injection chapter).",
)


@pytest.fixture
def stub():
    proc = subprocess.Popen(
        # --host 0.0.0.0 so the Toxiproxy container can reach the stub. On Linux, a container
        # reaches the host through the host gateway, not through 127.0.0.1. Local testing only.
        [sys.executable, "-m", "uvicorn", "downstream_stub:app", "--host", "0.0.0.0", "--port", str(STUB_PORT)],
        cwd=HERE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(50):
            try:
                if httpx.get(f"http://127.0.0.1:{STUB_PORT}/ping", timeout=0.2).status_code == 200:
                    break
            except httpx.HTTPError:
                time.sleep(0.1)
        else:
            raise RuntimeError("downstream stub did not start on port 9001")
        yield
    finally:
        proc.terminate()
        proc.wait(timeout=5)


@pytest.fixture
def proxy(stub):
    httpx.post(f"{TOXIPROXY_API}/reset")  # clear toxics left by an earlier run
    httpx.delete(f"{TOXIPROXY_API}/proxies/{PROXY_NAME}")
    created = httpx.post(
        f"{TOXIPROXY_API}/proxies",
        json={"name": PROXY_NAME, "listen": PROXY_LISTEN, "upstream": UPSTREAM},
    )
    created.raise_for_status()
    yield PROXY_NAME
    httpx.post(f"{TOXIPROXY_API}/reset")
    httpx.delete(f"{TOXIPROXY_API}/proxies/{PROXY_NAME}")


def _add_latency(proxy_name: str, ms: int) -> None:
    resp = httpx.post(
        f"{TOXIPROXY_API}/proxies/{proxy_name}/toxics",
        json={
            "name": "latency_down",
            "type": "latency",
            "stream": "downstream",
            "toxicity": 1.0,
            "attributes": {"latency": ms},
        },
    )
    resp.raise_for_status()


@requires_toxiproxy
def test_latency_toxic_adds_about_300ms(proxy):
    _add_latency(proxy, 300)

    start = time.perf_counter()
    resp = httpx.get(CLIENT_URL, timeout=5)
    elapsed = time.perf_counter() - start

    assert resp.status_code == 200
    assert resp.json()["service"] == "downstream-stub"
    assert elapsed >= 0.28, f"expected at least ~300 ms, got {elapsed:.3f} s"


@requires_toxiproxy
def test_timeout_of_100ms_fails_cleanly_under_latency(proxy):
    _add_latency(proxy, 300)

    start = time.perf_counter()
    with pytest.raises(httpx.TimeoutException):
        httpx.get(CLIENT_URL, timeout=0.1)
    elapsed = time.perf_counter() - start

    # The client gave up in well under the injected 300 ms.
    assert elapsed < 1.0, f"client waited {elapsed:.3f} s after a 100 ms timeout"
