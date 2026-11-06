# Software Testing Handbook

A TL;DR handbook for testers and SDETs: 81 short chapters, diagrams, and examples that all use one
fictional app, TaskFlow. Parts cover fundamentals, test design, automation, performance and load testing,
AWS ECS capacity, and AI in testing. Plus a problem-based index, playbooks and copy-paste templates.

Built with Docusaurus 3, with Mermaid diagrams and local search. Node 22 is recommended (`nvm use`).

## Run the site

```bash
npm install
npm start            # dev server at http://localhost:3000/
npm run build        # production build; fails on any broken link
npm run serve        # serve the production build
```

To publish on a GitHub Pages project site, build with the repo path: `BASE_URL=/<repo>/ npm run build`.
The site is a single docs site: the sidebar lists all parts, the top bar has search only.

## Run the examples

| Folder | What it is | How to run |
|---|---|---|
| `examples/taskflow/` | Runnable local TaskFlow API, UI, 94 offline tests plus UI, visual, load, Postman and Pact examples | See its README |
| `examples/ecs-capacity/` | Capacity calculator, HTML report generator and Terraform for an ECS test environment (no AWS calls; Terraform is syntax-checked only, never applied) | See its README |

## Repo layout

```
docs/                 chapters, one folder per part (NN- prefixes are removed from URLs)
templates/            chapter template, manifest, and the brief for writing agents
examples/             runnable code used by the chapters
src/                  custom components (TL;DR box) and a small d3 fix for Mermaid
```

Writing rules and the full specification: `templates/CHAPTER-MANIFEST.md`, `templates/AGENT-BRIEF.md`.

## Ground rules

- Nothing in this handbook was measured on a real AWS account. Sample numbers are labelled **Illustrative data**.
- Tool facts carry an "as of" date and a source link. Facts that could not be verified were left out.
- Replace `your-org` in `docusaurus.config.ts` before you publish.
