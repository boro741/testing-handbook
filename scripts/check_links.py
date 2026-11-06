"""Check every unique external URL in docs/ and README.md.

Run: python3 scripts/check_links.py
Writes a report to /tmp/link-report.md (not the repo). Exit 0 always; read the report.
Status: OK, REDIRECT, BLOCKED (403/429/bot protection), DEAD (404/410/5xx/timeout).
"""
import concurrent.futures
import glob
import re
import ssl
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
URL_RE = re.compile(r"https?://[^\s)\]\"'<>`|]+")
UA = "Mozilla/5.0 (handbook link check; contact: repo owner)"


def collect():
    found = {}
    files = glob.glob(str(ROOT / "docs" / "**" / "*.mdx"), recursive=True) + [str(ROOT / "README.md")]
    for f in files:
        for url in URL_RE.findall(Path(f).read_text()):
            url = url.rstrip(".,;:")
            found.setdefault(url, set()).add(str(Path(f).relative_to(ROOT)))
    return found


def ssl_context():
    # python.org installs on macOS may lack root certificates; use certifi's bundle when present.
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


CTX = ssl_context()


def check(url):
    if url.startswith(("http://localhost", "http://127.0.0.1", "http://host.docker.internal")):
        return "LOCAL", "needs a running server; not checked"
    ctx = CTX
    last = ""
    for _ in range(2):
        for method in ("HEAD", "GET"):
            req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
            try:
                with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
                    final = r.geturl()
                    if final.rstrip("/") != url.rstrip("/"):
                        return "REDIRECT", f"{r.status} -> {final}"
                    return "OK", str(r.status)
            except urllib.error.HTTPError as e:
                last = str(e.code)
                if e.code in (403, 429):
                    return "BLOCKED", last
                if e.code == 405 and method == "HEAD":
                    continue
                if e.code == 404 or e.code == 410 or e.code >= 500:
                    if method == "GET":
                        return "DEAD", last
            except Exception as e:  # DNS, TLS, timeout
                last = type(e).__name__
    return "DEAD", last


def main():
    urls = collect()
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        futures = {ex.submit(check, u): u for u in urls}
        for fut in concurrent.futures.as_completed(futures):
            results[futures[fut]] = fut.result()
    lines = [f"# Link report: {len(urls)} unique URLs", ""]
    for status in ("DEAD", "BLOCKED", "REDIRECT", "LOCAL", "OK"):
        rows = [(u, d) for u, (s, d) in results.items() if s == status]
        lines.append(f"## {status} ({len(rows)})")
        for u, d in sorted(rows):
            pages = ", ".join(sorted(urls[u]))
            lines.append(f"- {u}  [{d}]  used in: {pages}")
        lines.append("")
    out = Path("/tmp/link-report.md")
    out.write_text("\n".join(lines))
    counts = {s: sum(1 for v in results.values() if v[0] == s) for s in ("OK", "REDIRECT", "BLOCKED", "DEAD", "LOCAL")}
    print(f"Wrote {out}: {counts}")


if __name__ == "__main__":
    main()
