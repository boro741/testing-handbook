# Chapter manifest

The single source of truth for chapter numbers, file paths and titles.
Write a chapter at exactly the path shown. Link to other pages with `/<folder-without-number>/<slug>`, for example `/fundamentals/what-is-software-testing`. The site serves docs at the root and Docusaurus removes the `NN-` prefix from URLs, so `/docs/...` and `/01-fundamentals/...` are WRONG and break the build.

Front matter: do NOT add an `id` field. The file name is the id.

| # | File (under `docs/`) | Title |
|---|---|---|
| 1 | 01-fundamentals/what-is-software-testing.mdx | What is software testing |
| 2 | 01-fundamentals/verification-vs-validation.mdx | Verification vs validation, QA vs QC |
| 3 | 01-fundamentals/sdlc-and-stlc.mdx | SDLC and STLC |
| 4 | 01-fundamentals/test-levels-and-types.mdx | Test levels and test types |
| 5 | 01-fundamentals/manual-vs-automated.mdx | Manual vs automated testing |
| 6 | 02-planning-strategy/requirements-and-testability.mdx | Requirements and testability |
| 7 | 02-planning-strategy/test-strategy-vs-plan.mdx | Test strategy vs test plan |
| 8 | 02-planning-strategy/risk-based-testing.mdx | Risk-based testing |
| 9 | 02-planning-strategy/test-coverage.mdx | Test coverage |
| 10 | 02-planning-strategy/entry-and-exit-criteria.mdx | Entry and exit criteria |
| 11 | 02-planning-strategy/defect-management.mdx | Defect management and the bug life cycle |
| 12 | 03-test-design/equivalence-partitioning-and-boundaries.mdx | Equivalence partitioning and boundary values |
| 13 | 03-test-design/decision-tables.mdx | Decision table testing |
| 14 | 03-test-design/state-transition-testing.mdx | State transition testing |
| 15 | 03-test-design/use-case-and-scenario-testing.mdx | Use case and scenario testing |
| 16 | 03-test-design/pairwise-testing.mdx | Pairwise testing |
| 17 | 03-test-design/exploratory-testing.mdx | Exploratory testing |
| 18 | 03-test-design/negative-and-edge-cases.mdx | Negative and edge-case testing |
| 19 | 04-testing-by-layer/ui-testing.mdx | UI testing |
| 20 | 04-testing-by-layer/api-testing.mdx | API testing |
| 21 | 04-testing-by-layer/backend-and-database-testing.mdx | Backend and database testing |
| 22 | 04-testing-by-layer/integration-and-contract-testing.mdx | Integration and contract testing |
| 23 | 04-testing-by-layer/end-to-end-testing.mdx | End-to-end testing |
| 24 | 04-testing-by-layer/microservices-and-event-driven-testing.mdx | Microservices and event-driven testing |
| 25 | 04-testing-by-layer/mobile-app-testing.mdx | Mobile app testing |
| 26 | 05-automation-engineering/test-automation-pyramid.mdx | The test automation pyramid |
| 27 | 05-automation-engineering/automation-framework-design.mdx | Designing an automation framework |
| 28 | 05-automation-engineering/design-patterns.mdx | Design patterns for test code |
| 29 | 05-automation-engineering/test-data-management.mdx | Test data management |
| 30 | 05-automation-engineering/flaky-tests.mdx | Flaky tests |
| 31 | 05-automation-engineering/parallel-and-distributed-execution.mdx | Parallel and distributed execution |
| 32 | 05-automation-engineering/reporting-and-logging.mdx | Reporting and logging |
| 33 | 05-automation-engineering/ci-cd-and-continuous-testing.mdx | CI/CD and continuous testing |
| 34 | 05-automation-engineering/maintaining-automation.mdx | Maintaining automation suites |
| 35 | 06-other-non-functional/security-testing.mdx | Security testing fundamentals |
| 36 | 06-other-non-functional/accessibility-testing.mdx | Accessibility testing |
| 37 | 06-other-non-functional/compatibility-testing.mdx | Compatibility testing |
| 38 | 06-other-non-functional/reliability-and-chaos.mdx | Reliability, resilience and chaos engineering |
| 39 | 07-modern-quality-engineering/shift-left-and-shift-right.mdx | Shift-left and shift-right |
| 40 | 07-modern-quality-engineering/observability-for-testers.mdx | Observability for testers |
| 41 | 07-modern-quality-engineering/testing-in-production.mdx | Testing in production |
| 42 | 07-modern-quality-engineering/test-environments.mdx | Test environments |
| 43 | 07-modern-quality-engineering/quality-metrics.mdx | Quality metrics and KPIs |
| 44 | 08-playbooks/how-to-test-a-new-feature.mdx | How to test a new feature |
| 45 | 08-playbooks/how-to-test-a-rest-api.mdx | How to test a REST API |
| 46 | 08-playbooks/how-to-test-a-microservice.mdx | How to test a microservice |
| 47 | 08-playbooks/how-to-investigate-a-production-defect.mdx | How to investigate a production defect |
| 48 | 08-playbooks/how-to-write-a-test-strategy.mdx | How to write a test strategy |
| 49 | 09-performance-fundamentals/performance-testing-types.mdx | Performance testing types |
| 50 | 09-performance-fundamentals/performance-metrics.mdx | Performance metrics |
| 51 | 09-performance-fundamentals/performance-requirements-and-slos.mdx | Performance requirements and SLOs |
| 52 | 09-performance-fundamentals/workload-modelling.mdx | Workload modelling |
| 53 | 09-performance-fundamentals/finding-bottlenecks.mdx | Finding bottlenecks (USE and RED) |
| 54 | 09-performance-fundamentals/performance-strategy-and-ci.mdx | Performance strategy and regression testing in CI |
| 55 | 10-performance-by-layer/frontend-performance.mdx | Frontend performance |
| 56 | 10-performance-by-layer/mobile-performance.mdx | Mobile performance |
| 57 | 10-performance-by-layer/backend-api-performance.mdx | Backend API performance |
| 58 | 10-performance-by-layer/microservices-performance.mdx | Microservices performance |
| 59 | 10-performance-by-layer/database-performance.mdx | Database performance |
| 60 | 11-load-testing-tools/choosing-a-tool.mdx | Choosing a load testing tool |
| 61 | 11-load-testing-tools/locust-with-pytest.mdx | Hands-on: Locust with pytest |
| 62 | 11-load-testing-tools/k6.mdx | Hands-on: k6 |
| 63 | 11-load-testing-tools/distributed-load-and-dashboards.mdx | Distributed load and dashboards |
| 64 | 12-ecs-performance/ecs-architecture.mdx | ECS performance architecture |
| 65 | 12-ecs-performance/metrics-that-matter.mdx | Metrics that matter for ECS |
| 66 | 12-ecs-performance/running-a-load-test-on-ecs.mdx | Running a load test against ECS safely |
| 67 | 12-ecs-performance/per-task-capacity-and-task-count.mdx | Per-task capacity and task count |
| 68 | 12-ecs-performance/auto-scaling.mdx | Auto scaling |
| 69 | 12-ecs-performance/soak-tests-and-memory-leaks.mdx | Soak tests and memory leaks |
| 70 | 12-ecs-performance/right-sizing-and-cost.mdx | Right-sizing and cost |
| 71 | 12-ecs-performance/performance-report.mdx | The performance report |
| 72 | 13-ai-in-testing/ai-testing-landscape.mdx | The AI testing landscape |
| 73 | 13-ai-in-testing/ai-test-generation.mdx | AI-assisted test generation |
| 74 | 13-ai-in-testing/browser-agents.mdx | Agentic and exploratory testing with browser agents |
| 75 | 13-ai-in-testing/self-healing-tests.mdx | Self-healing tests |
| 76 | 13-ai-in-testing/ai-failure-triage.mdx | AI for failure triage |
| 77 | 13-ai-in-testing/ai-performance-analysis.mdx | AI for performance analysis |
| 78 | 13-ai-in-testing/testing-llm-and-rag-apps.mdx | Testing LLM and RAG applications |
| 79 | 13-ai-in-testing/testing-ai-agents-and-security.mdx | Testing AI agents and AI security |
| 80 | 13-ai-in-testing/limits-and-risks-of-ai.mdx | Limits and risks of AI in testing |
| 81 | 14-capstone/taskflow-quality-platform.mdx | TaskFlow Quality & Performance Platform |
| Appendix | 99-appendices/tool-directory.mdx | Tool directory (AI and performance tools, verified) |
| Appendix | 99-appendices/cheat-sheets.mdx | Cheat sheets |
| Appendix | 99-appendices/sources.mdx | Sources |
| Start | 00-start-here/how-to-use.mdx, taskflow-reference.mdx, glossary.mdx | Written by the lead |


## Additions (round 2)

Existing chapter numbers are NOT changed. New pages have no number; `sidebar_position` is a decimal that slots them in.
Front matter `part` = the part number of the folder (98 for templates).

| Agent | File (under `docs/`) | Title | sidebar_position |
|---|---|---|---|
| 1 | 01-fundamentals/regression-retest-smoke-sanity.mdx | Regression, retest, smoke and sanity testing | 4.5 |
| 1 | 02-planning-strategy/writing-test-cases.mdx | Writing test cases and traceability | 6.5 |
| 1 | 04-testing-by-layer/unit-testing-and-tdd.mdx | Unit testing and TDD | 18.5 |
| 1 | 04-testing-by-layer/other-api-styles.mdx | Testing GraphQL, gRPC and WebSocket | 20.7 |
| 1 | 04-testing-by-layer/acceptance-testing-and-bdd.mdx | Acceptance testing and BDD | 23.5 |
| 2 | 05-automation-engineering/test-doubles-and-service-virtualization.mdx | Test doubles and service virtualization | 28.5 |
| 2 | 05-automation-engineering/mutation-and-property-based-testing.mdx | Mutation and property-based testing | 30.5 |
| 2 | 05-automation-engineering/visual-regression-testing.mdx | Visual regression testing | 31.5 |
| 2 | 07-modern-quality-engineering/static-analysis-and-code-review.mdx | Static analysis and code review | 39.5 |
| 3 | 06-other-non-functional/api-security-and-injection.mdx | API security and injection | 35.5 |
| 3 | 06-other-non-functional/usability-and-localization-testing.mdx | Usability and localization testing | 37.5 |
| 3 | 98-templates/bug-report.mdx | Template: bug report | 1 |
| 3 | 98-templates/test-case.mdx | Template: test case | 2 |
| 3 | 98-templates/test-plan.mdx | Template: test plan | 3 |
| 3 | 98-templates/performance-test-plan.mdx | Template: performance test plan | 4 |
| 3 | 98-templates/traceability-matrix.mdx | Template: traceability matrix | 5 |
| 3 | 98-templates/test-summary-report.mdx | Template: test summary report | 6 |
| 4 | 04-testing-by-layer/api-testing-with-postman-cli.mdx | API testing with the Postman CLI | 20.5 |
| 6 | 04-testing-by-layer/device-farms-and-real-devices.mdx | Device farms and real devices | 25.5 |
| 4 | 05-automation-engineering/choosing-test-tools.mdx | Choosing UI and API test tools | 27.5 |
| 5 | 08-playbooks/how-to-run-a-load-test-end-to-end.mdx | How to run a load test end to end | 48.1 |
| 5 | 08-playbooks/how-to-triage-a-flaky-test.mdx | How to triage a flaky test | 48.2 |
| 5 | 08-playbooks/how-to-set-up-a-ci-test-pipeline.mdx | How to set up a CI test pipeline | 48.3 |
| 5 | 08-playbooks/how-to-test-a-mobile-app-release.mdx | How to test a mobile app release | 48.4 |
| 5 | 08-playbooks/how-to-run-an-accessibility-audit.mdx | How to run an accessibility audit | 48.5 |
| 5 | 08-playbooks/how-to-test-login-and-authentication.mdx | How to test login and authentication | 48.6 |
| 5 | 08-playbooks/how-to-size-an-ecs-service.mdx | How to size an ECS service | 48.7 |
| 6 | 12-ecs-performance/infrastructure-as-code.mdx | Setting up the ECS test environment with Terraform | 64.5 |
| 6 | 12-ecs-performance/alarms-and-dashboards.mdx | CloudWatch alarms and dashboards | 65.5 |
| lead | 00-start-here/find-by-problem.mdx | Find what you need | 1.5 |

Example code owners: agent 2 = `examples/taskflow/tests/test_properties.py`; agent 3 = `examples/taskflow/tests/test_security.py`;
agent 4 = `examples/taskflow/ui-tests/`, `examples/taskflow/contract/`, and the Postman files under `examples/taskflow/postman/`;
agent 1 = `examples/taskflow/bdd/` (pytest-bdd feature and steps); agent 6 = `examples/ecs-capacity/infra/terraform/`; agent 1 also owns `examples/taskflow/unit/`; agent 2 also owns `examples/taskflow/doubles/` and `examples/taskflow/visual/`.
Agent 4 also adds rows to `99-appendices/tool-directory.mdx` and `99-appendices/sources.mdx` (only agent 4 edits those two files).

## Additions (round 3)

Same rules as round 2. Decimal `sidebar_position` values slot pages into existing parts. `part` = folder number.
Front matter values that contain a colon MUST be double-quoted.

| Agent | File (under `docs/`) | Title | sidebar_position |
|---|---|---|---|
| P1 | 97-practice/learning-paths.mdx | Learning paths | 97.1 |
| P1 | 97-practice/exercises-fundamentals-and-design.mdx | Exercises: fundamentals and design | 97.2 |
| P1 | 97-practice/exercises-automation-and-layers.mdx | Exercises: automation and layers | 97.3 |
| P2 | 97-practice/exercises-nonfunctional-and-performance.mdx | Exercises: non-functional and performance | 97.4 |
| P2 | 97-practice/exercises-modern-and-ai.mdx | Exercises: modern practice and AI | 97.5 |
| P2 | 97-practice/self-check-quizzes.mdx | Self-check quizzes | 97.6 |
| P3 | 97-practice/project-overview.mdx | Capstone project: overview | 97.7 |
| P3 | 97-practice/project-1-requirements-and-risk.mdx | Project 1: requirements and risk | 97.8 |
| P3 | 97-practice/project-2-design-tests.mdx | Project 2: design the tests | 97.9 |
| P4 | 97-practice/project-3-automate-the-api.mdx | Project 3: automate the API | 97.10 |
| P4 | 97-practice/project-4-automate-the-ui.mdx | Project 4: automate the UI | 97.11 |
| P4 | 97-practice/project-5-performance-and-capacity.mdx | Project 5: performance and capacity | 97.12 |
| P5 | 97-practice/project-6-report-and-retro.mdx | Project 6: report and retrospective | 97.13 |
| P5 | 97-practice/project-bug-answer-key.mdx | Project answer key (spoilers) | 97.14 |
| T1 | 15-working-in-teams/testing-in-agile-teams.mdx | Testing in agile teams | 15.1 |
| T1 | 15-working-in-teams/test-estimation-in-practice.mdx | Test estimation in practice | 15.2 |
| T1 | 15-working-in-teams/bug-triage-meetings.mdx | Bug triage meetings | 15.3 |
| T2 | 15-working-in-teams/test-management-tools.mdx | Test management tools | 15.4 |
| T2 | 15-working-in-teams/communicating-quality-and-risk.mdx | Communicating quality and risk | 15.5 |
| T2 | 98-templates/bug-triage-agenda.mdx | Template: bug triage agenda | 7 |
| T2 | 98-templates/estimation-worksheet.mdx | Template: estimation worksheet | 8 |
| T2 | 98-templates/sprint-test-checklist.mdx | Template: sprint test checklist | 9 |
| D1 | 16-other-domains/data-and-etl-testing.mdx | Data and ETL testing | 16.1 |
| D1 | 16-other-domains/testing-machine-learning-models.mdx | Testing machine learning models | 16.2 |
| D2 | 16-other-domains/desktop-app-testing.mdx | Desktop app testing | 16.3 |
| D2 | 16-other-domains/embedded-and-iot-testing.mdx | Embedded and IoT testing | 16.4 |
| D2 | 16-other-domains/game-testing.mdx | Game testing | 16.5 |
| D2 | 16-other-domains/enterprise-platform-testing.mdx | Enterprise platform testing | 16.6 |
| S1 | 06-other-non-functional/threat-modelling-for-testers.mdx | Threat modelling for testers | 35.7 |
| S1 | 06-other-non-functional/dependency-and-secrets-scanning.mdx | Dependency and secrets scanning | 35.8 |
| S2 | 06-other-non-functional/fault-injection-hands-on.mdx | Fault injection, hands on | 38.5 |
| S2 | 07-modern-quality-engineering/testing-on-kubernetes.mdx | Testing on Kubernetes | 43.5 |
| S2 | 04-testing-by-layer/serverless-testing.mdx | Serverless testing | 25.8 |

Example code owners (round 3):
- P1: nothing runnable beyond the practice files. Practice answers must be checked against the real app.
- D1: `examples/data-testing/` (pytest, sqlite3, csv). `examples/ml-testing/` is owned by D1 too.
- D2: no code. Concepts only, state "nothing run".
- S1: `examples/taskflow/` dependency scan only (pip-audit, run against requirements.txt). No new app code.
- S2: `examples/taskflow/chaos/` (Toxiproxy via Docker, run if Docker works). Kubernetes page has no code run.
- S3 (serverless): `examples/serverless/` (moto, no AWS calls).
- B1 (seeded bugs): the only owner of `examples/taskflow/app/main.py` and `examples/taskflow/bug-hunt/`.
- TF: the only owner of `examples/ecs-capacity/infra/terraform/` and the Terraform wording in three pages.
