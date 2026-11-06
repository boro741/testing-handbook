"""Gate for handbook pages. Exit 0 = clean, 1 = problems found.

Run: python3 scripts/check_docs.py          (from the repo root; needs PyYAML)
Checks every docs/**/*.mdx page for the rules in templates/AGENT-BRIEF.md.
"""
import glob
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = (ROOT / "templates" / "CHAPTER-MANIFEST.md").read_text()
REQUIRED = ["title", "description", "part", "summary", "reading_time"]
# Word bounds do not apply to these folders.
NO_WORD_BOUNDS = ("98-templates", "99-appendices", "00-start-here")
# External-link cap does not apply to these folders.
NO_LINK_CAP = ("99-appendices", "00-start-here")

# Words that describe how a page was written (tools, "I ran this") do not belong in reader-facing text.
PROCESS_RE = re.compile(
    r"opened, ok|Context7|\bWebFetch\b|\bwe opened\b"
    r"|(?:^|[ (.\"*_])I (?:checked|ran|re-implemented|wrote|opened|verified|tried|used|found|did|saw|got|confirmed|took|started)\b"
)
# A quiz with one letter holding more than this share of the correct answers is easy to guess.
MAX_QUIZ_LETTER_SHARE = 0.35

problems = []


def problem(path, msg):
    problems.append(f"{path.relative_to(ROOT)}: {msg}")


for path in sorted(glob.glob(str(ROOT / "docs" / "**" / "*.mdx"), recursive=True)):
    p = Path(path)
    text = p.read_text()
    folder = p.parent.name
    if not text.startswith("---"):
        problem(p, "no front matter")
        continue
    parts = text.split("---", 2)
    if len(parts) < 3:
        problem(p, "front matter not closed")
        continue
    try:
        fm = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as e:
        problem(p, f"front matter does not parse: {str(e).splitlines()[0]}")
        continue
    body = parts[2]

    for key in REQUIRED:
        if key not in fm:
            problem(p, f"front matter missing '{key}'")
    if "id" in fm:
        problem(p, "front matter must not have 'id' (the file name is the id)")

    if "<TLDR>" not in body:
        problem(p, "no <TLDR> block")

    if "](/docs/" in body or re.search(r'"/docs/', parts[1]):
        problem(p, "link starts with /docs/ (site serves docs at the root)")

    if re.search(r"\b[Cc]hapters? \d+", body):
        problem(p, "plain-text 'chapter N' reference (use a link by title)")

    if body.count("```") % 2:
        problem(p, "unbalanced code fence")

    prose = re.sub(r"```.*?```", "", body, flags=re.S)
    words = len(prose.split())
    if not folder.startswith(NO_WORD_BOUNDS):
        if words < 300:
            problem(p, f"too short: {words} words (min 300)")
        if words > 1200:
            problem(p, f"too long: {words} words (max 1200)")

    if not folder.startswith(NO_LINK_CAP):
        ext = len(re.findall(r"\]\(https?://", body))
        if ext > 3:
            problem(p, f"{ext} external links (max 3)")

    if p.name not in MANIFEST:
        problem(p, "file name not listed in templates/CHAPTER-MANIFEST.md")

    if p.name != "sources.mdx":
        in_code = False
        for n, line in enumerate(body.splitlines(), 1):
            if line.lstrip().startswith("```"):
                in_code = not in_code
                continue
            if in_code or "What I tried" in line:  # the exploratory session template is first person on purpose
                continue
            if PROCESS_RE.search(line):
                problem(p, f"process language on body line {n}: {line.strip()[:70]}")

    # Self-check quiz: the correct letters must be spread out.
    if p.name == "self-check-quizzes.mdx":
        letters = re.findall(r"<summary>Show the answer</summary>\s*\n\s*\*\*([A-D])\.\*\*", body)
        if letters:
            top = max(letters.count(c) for c in "ABCD")
            if top / len(letters) > MAX_QUIZ_LETTER_SHARE:
                problem(p, f"quiz answers are skewed: {dict((c, letters.count(c)) for c in 'ABCD')}")

# Leftover backup files from `sed -i` on macOS.
for stray in sorted(glob.glob(str(ROOT / "docs" / "**" / "*"), recursive=True)):
    if stray.endswith(("-E", ".bak", ".orig")):
        problem(Path(stray), "stray backup file (delete it)")

for path in sorted(glob.glob(str(ROOT / "docs" / "*" / "_category_.json"))):
    import json
    try:
        json.loads(Path(path).read_text())
    except json.JSONDecodeError as e:
        problem(Path(path), f"bad JSON: {e}")

if problems:
    print(f"{len(problems)} problem(s):")
    for line in problems:
        print("  -", line)
    sys.exit(1)
print("check_docs: clean")
