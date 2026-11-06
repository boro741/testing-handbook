# Brief for chapter-writing agents

Repo: /Users/pavan.boro/Documents/GitHub/temp/testing-handbook (Docusaurus 3 site). You write content only for your assigned files.

## Read first
1. `/Users/pavan.boro/Documents/GitHub/temp/HANDBOOK_PROMPT.md` sections 0, 1, 2, 3, 4 and 6 (writing rules, template, TaskFlow, reality rules, content details).
2. `templates/CHAPTER-MANIFEST.md`: exact file path, chapter number and title for each chapter.
3. `templates/chapter-template.mdx`: the front matter and section layout to copy.
4. `docs/00-start-here/taskflow-reference.mdx` (the fixed TaskFlow architecture and API) and `docs/00-start-here/glossary.mdx` (do NOT edit the glossary; list any new terms in your final report).
5. Existing `examples/taskflow/` (runnable local TaskFlow: FastAPI API, UI, 19 pytest tests, Locust script).

## Format rules
- Front matter: `title`, `sidebar_position` (= the chapter number from the manifest), `description`, `part` (number), `summary`, `tags`, `reading_time`, `related` (list of URL paths, may be empty). Do NOT add an `id` field.
- Every chapter starts with a `<TLDR>...</TLDR>` block, then the sections from the template, in order.
- Playbook chapters (44–48) use a checklist format instead of "What and why / How it works / When to use".
- Length: 400–900 words of prose (code not counted). Never over 1,200 words.
- Plain English. Short sentences. Explain jargon the first time.
- Diagrams: Mermaid (```mermaid blocks) only where a picture explains faster than text. Keep labels simple; quote labels that contain brackets, colons or parentheses, for example `A["Load generator (k6)"]`.
- Callouts: Docusaurus admonitions, for example `:::tip`, `:::warning`, `:::info[Illustrative data]`.
- Internal links: `/<folder-without-number>/<slug>`, for example `/fundamentals/what-is-software-testing`. The site serves docs at the root and Docusaurus strips the `NN-` prefix, so `/docs/...` and `/01-fundamentals/...` both break the build. Link only to pages that exist in the manifest. Always link by page title; NEVER write chapter numbers ("chapter 61") in text, because the sidebar shows no numbers.

## Facts and links (important)
- Never invent statistics, benchmark numbers, company case studies, or tool features.
- External links: open each one with WebFetch first and keep it only if it loads. Prefer official docs. Maximum 3 external links per chapter. Drop any link you cannot open.
- Tool facts (versions, licences, stars, release dates, company usage) must carry "as of 2026-11-06" and a source link you opened. If you cannot verify a fact, leave it out.
- Classify tool claims as: documented production use / community recommendation / individual experiment / vendor marketing.
- Recommendations are labelled "Recommendation", not presented as standards.

## Code rules
- Before showing code for a library (Playwright, Locust, k6, pytest plugins, Pact, Schemathesis, boto3, Docusaurus, etc.), use the Context7 tools (`mcp__context7__resolve-library-id`, then `mcp__context7__query-docs`) to get current syntax. Mention the version you checked.
- Keep each code block under ~30 lines.
- Where possible, use real TaskFlow endpoints from the reference page. Do not add endpoints that the local app does not have.
- Real code that you add under `examples/` must run. Run it with the existing venv `examples/taskflow/.venv` (install into it only with `--index-url https://pypi.org/simple`). Do not run `npm` or `npm run build`.

## Reality rules
- Nobody deploys to AWS from this handbook. Never say you measured something on a real system.
- Any sample results, reports or numbers must carry a visible `:::info[Illustrative data]` callout.
- One topic lives in one chapter. Other chapters link to it in one sentence.

## Scope
- Write only your assigned files. Do not edit other chapters, the glossary, the config, or the manifest.
- Do not run `npm run build`; the lead runs it after all agents finish.

## Final report (keep under 250 words)
- Files written, with approximate word counts.
- External URLs used, each with the result of WebFetch (ok or not).
- New glossary terms as `Term: definition`.
- Anything you could not verify or finish, and why.


## Round 2 rules (new pages and examples)
- Your files are listed in the "Additions" table of `templates/CHAPTER-MANIFEST.md`. Use the exact path and the `sidebar_position` shown there (decimals are fine). Do not edit any file that is not yours.
- Existing pages you may link to are in the first table of the manifest. Links to other NEW pages are allowed (they are all in the Additions table), but do not rely on their content.
- Do NOT edit `examples/taskflow/requirements*.txt` or `examples/taskflow/app/`. If you need a package, create your own venv: `python3 -m venv /tmp/venv-<yourname>`, then `/tmp/venv-<yourname>/bin/pip install --index-url https://pypi.org/simple -r examples/taskflow/requirements-dev.txt <extra packages>`. In your final report list each extra package with its exact installed version, so the lead can add it to the requirements.
- Running a TaskFlow server: use your own port and your own database file, so parallel agents do not collide. Ports: agent1=8101, agent2=8102, agent3=8103, agent4=8104, agent5=8105. Example: `cd examples/taskflow && DATABASE_URL=sqlite:////tmp/<yourname>.db /tmp/venv-<yourname>/bin/uvicorn app.main:app --port <port>`. Stop your server when done.
- Tests you add must pass. Run them and report the real result. If something cannot run here, label it clearly as "not run" on the page and say why in your report.
- Do not leave scratch files, `.db` files or `__pycache__` in the repo.
- New glossary terms: list them in your report. Do not edit the glossary.
- Content must be NEW. Do not repeat what an existing chapter already explains. Link to it in one sentence.

## Round 3 rules (Haiku agents)
- Your file list is in the "round 3" table of `templates/CHAPTER-MANIFEST.md`. Create only those files, and only the example paths named for your group. Do not edit any other file.
- Max 5 pages each. Each page: the template sections (TL;DR, What and why, When to use, TaskFlow example, Do this, Avoid this, Further reading). Practice pages and playbooks have their own layout (see your brief).
- Before you write about TaskFlow, read `docs/00-start-here/taskflow-reference.mdx` and `examples/taskflow/app/main.py`. Every claim about TaskFlow must match the code. If you are not sure, leave the claim out.
- Front matter: double-quote any `description` or `summary` value that contains a colon, or the build breaks.
- Exercises use this exact pattern (leave a blank line after `<details>` and after `</summary>`):

```
<details>
<summary>Show the answer</summary>

Answer text here.

</details>
```

- Run `python3 scripts/check_docs.py` before you report. Fix every problem it reports for YOUR files. Problems in other people's files are not yours.
- Commands: run each command you describe. Report the real output or the real error. NEVER invent output. If a command fails, say so, keep the page honest ("not run: <reason>"), and stop that part.
- Python only. Use pytest for tests. Use a venv at `/tmp/venv-<yourname>` installed from public PyPI only (`--index-url https://pypi.org/simple`). Use your own port and database file if you start a server.
- Do not add packages to `examples/taskflow/requirements-dev.txt`. The lead does that. List each extra package with its exact version in your report.
- Do not leave scratch files, `.db` files, `__pycache__`, `.pytest_cache` or `.hypothesis` in the repo. Delete them before reporting.
- New glossary terms: list them in your report as `Term: definition`. Do not edit the glossary.
- Final report under 200 words: files written, commands run with real results, what was not run and why, extra packages with versions, glossary terms.

## Seeded bugs (fixed catalogue, round 3)
The practice project uses eight bugs in `examples/taskflow/app/main.py`. They are switched on by the environment variable `TASKFLOW_BUGS` (comma list of IDs, or `all`). Unset or empty = the bug-free app. The check is made on every request, so tests can switch bugs on and off.

| ID | What the bug does | Real behaviour when on |
|---|---|---|
| B01 | Title length not checked | A 101-character title is accepted (201) |
| B02 | Status step skipped | TODO to DONE is allowed (200) |
| B03 | Read without membership check | Non-member gets 200 on GET /api/tasks/{id} |
| B04 | Assign without member check | Assigning a non-member gets 200 |
| B05 | Delete keeps the row | DELETE returns 204, but a later GET still returns 200 |
| B06 | Wrong password accepted for bob | Any password works for user bob |
| B07 | List ignores project | GET /api/tasks returns tasks from every project |
| B08 | Priority not checked | Priority "URGENT" is accepted (201) |

Project pages and the answer key use these IDs. Do not rename them. The bug-hunt script `examples/taskflow/bug-hunt/verify_bugs_detectable.py` proves each bug fails at least one existing test.
