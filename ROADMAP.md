# Curriculum improvement roadmap

This roadmap turns the October 2026 curriculum review into work that can ship in small pull requests. The goal is a curriculum that takes a true beginner to a hireable AI engineer in 2026. That takes more than covering the right topics. Every lesson has to teach, every lesson has to be practiced, and skills employers check have to show up early and come back often.

**Status key:** `NEW` = a file to create, `MOVE` = an existing file that changes path or section, `EDIT` = a change to an existing file, `CUT` = merge or remove.

## Guiding principles

1. **Teach before linking.** Every lesson needs written explanation and code in its custom sections. A lesson that is only links is unfinished.
1. **Practice every lesson.** Each lesson gets a knowledge check, and most get an exercise with tests.
1. **Thread core habits through every project.** Tests, CI, traces and a small eval appear from Foundations onward. From the first agent project on, add one prompt-injection test.
1. **Teach a skill before a project needs it.** A project may only require skills taught earlier in the path.
1. **Stay provider-neutral where it matters.** Use Claude for examples, but name provider-specific features as such, and have learners run at least one project on a second provider or an open model.
1. **Give honest hours.** Every path's estimate is checked against what it actually assigns.

## Phases at a glance

| Phase | What | Depends on | Size |
| --- | --- | --- | --- |
| 0 | Fix verified bugs | none | ~1 day |
| 1 | Infrastructure: templates, validator, models page, aliases, exercises repo | none | ~1 week |
| 2 | Restructure `curriculum.json` (new order, moves, stubs) | 1 | ~1 week |
| 3 | Write the 15 lessons projects depend on | 1 | ~4–6 weeks |
| 4 | Write the new required lessons | 2 | ~8–10 weeks |
| 5 | Upgrade project briefs | 2, ideally 3 | ~2–3 weeks |
| 6 | Production, Capstone and Hired deepening | 2 | ~4 weeks |
| 7 | Rescope the electives | 2 | ~2 weeks |
| 8 | Write the remaining outlines and backfill knowledge checks | 3, 4 | ongoing |

Phases 3–7 can run in parallel once Phase 2 has merged. Sizes assume one focused maintainer. Contributors shorten them.

---

## Phase 0: Fix verified bugs

One PR. Each fix below was confirmed by reading the file.

- [ ] **EDIT** `curriculum/foundations/web/api_keys_and_secrets.md:23`: remove Anthropic from the `Authorization: Bearer` line, and add an `x-api-key` line that names Anthropic.
- [ ] **EDIT** `curriculum/foundations/web/project_weather_cli.md:21`: `tap_weather_cli:main` becomes `mimir_weather_cli:main`.
- [ ] **EDIT** `curriculum/foundations/git/git_basics.md:131`: before the first push, add a fallback. Run `git status`, and if it reports "not a git repository", run `git init`. Then always run `git branch -M main`.
- [ ] **EDIT** `curriculum/foundations/first_llm_app/tokens_cost_and_rate_limits.md:68`: add `encoding="utf-8"` to `open()`.
- [ ] **EDIT** `curriculum/foundations/llms/context_windows_and_sampling.md:100`: state plainly which current models reject non-default sampling parameters, instead of "some".
- [ ] **EDIT** `curriculum/core/prompting/thinking_and_prompt_chaining.md:44`: fix the "chapter 6 … if you skipped it" reference. The previous lesson already assigns chapters 1–7.
- [ ] **EDIT** `curriculum/core/rag/hybrid_search_and_reranking.md:44`: replace the unmaintained `rank_bm25` with `bm25s` (and mention Postgres full-text search).
- [ ] **VERIFY then fix**:
  - [ ] the `mcp run … --transport streamable-http` flag in `agentic/mcp/mcp_transports_and_security.md:43`
  - [ ] the τ³-bench naming in `agentic/agent_evals/simulated_users_and_benchmarks.md:30`
  - [ ] the promptfoo acquisition claim in `core/evals/evaluating_rag_and_regressions.md:42` (cite a source or remove it)
  - [ ] the Pydantic docs URLs in `core/structured_outputs/json_schema_and_pydantic.md:40-44`
  - [ ] the `CliffWalking-v1` version in `research/reinforcement_learning/project_train_an_rl_agent.md:36`
  - [ ] the Microsoft Research link in `research/research_skills/writing_up_research.md:39`
  - [ ] the truncated sentence in `research/planning/project_llm_vs_classical_planner.md:12`
- [ ] **EDIT** `production/reliability/prompt_versioning_and_ci_evals.md:38,40`: update the two redirected GitHub Docs URLs.
- [ ] **EDIT** the three Skilljar course links in `foundations/first_llm_app/`: mark them optional, because they require a sign-up.

**Done when:** `python3 scripts/validate.py --links` passes and every item is checked off.

---

## Phase 1: Infrastructure

These changes make every later phase cheaper and keep it enforced.

### 1.1 Knowledge checks
- [ ] **EDIT** `LAYOUT_STYLE_GUIDE.md`: add `### Knowledge check` to the lesson layout, after Assignment and before Additional resources.
  - It holds 4–7 questions.
  - Each question links to the heading anchor that answers it, for example `[What is a chunk?](#chunking)`. This is how The Odin Project does it.
- [ ] **EDIT** `templates/lesson-template.md`: add the section.

### 1.2 Project evidence checklist
- [ ] **EDIT** `templates/project-template.md` and the style guide: add an `#### Evidence` block that lists what proves the project works.
- [ ] Set the default evidence by stage:
  - **Foundations onward:** tests plus CI.
  - **Core onward:** traces plus an eval score with a confidence interval.
  - **From the Agent Loop project onward:** one prompt-injection test.

### 1.3 Validator
- [ ] **EDIT** `scripts/validate.py`:
  - Require `### Knowledge check` in non-project lessons that don't carry the "Outline lesson" banner. Outlines stay exempt until Phase 8.
  - Fail on any hard-coded model ID (regex `claude-(haiku|sonnet|opus|fable)-\d`) outside `curriculum/models.md`.
  - Check that every `requires` path id (see 1.5) exists.
    - Print an outline count per path, so progress shows up in CI logs.

### 1.4 Moving lessons
Not needed before launch: the site isn't live, so no learner has saved progress or shared links. **After launch**, progress keys and URLs are both `path-id/lesson-id` (`assets/js/app.js`), so moving a lesson between paths would need an alias field that redirects old routes and migrates saved progress.

### 1.5 Path prerequisites
- [ ] Add an optional `"requires": ["ml"]` field on paths, and render "Requires: ML Foundations" on the path page in `app.js`.

### 1.6 Current models page
- [ ] **NEW** `curriculum/models.md`, rendered like `about.md`, with a nav link.
  - It lists the current cheap development model, the default capable model, and an open-weight option, with prices and a "last checked" date.
  - Lessons say "use the cheapest current model (see Current Models)" instead of an ID.
- [ ] **EDIT** about 30 files: replace hard-coded `claude-haiku-5-5` / `claude-sonnet-5-5`. The validator from 1.3 enforces this.
- [ ] **EDIT** `scripts/validate.py`: exempt `models.md` from the "not listed in curriculum.json" check, as it does for `about.md`.

### 1.7 Exercises repo
- [ ] **NEW** folder `exercises/` in this repo (it can move to its own repo later). Each exercise is a folder with a `README.md`, a starter file, a failing test file and a reference solution in `solution/`. `scripts/check_exercises.py` checks in CI that every solution passes and every starter fails.
- [ ] Seed it with the exercise sets lessons will link to:
  - `python-basics/` (10)
  - `pythonic-python/` (8)
  - `debugging/` (8 bugged scripts)
  - `regex/` (6)
  - `apis/` (5, with recorded HTTP fixtures)
  - `data/` (5, pandas)
  - `tool-schemas/` (5)
  - `evals/` (5, compute P/R/F1 and bootstrap CIs)

### 1.8 Contributor workflow
- [ ] **EDIT** `CONTRIBUTING.md`: link this roadmap, explain the "claim a lesson" convention (one issue per lesson, labeled `write-lesson`), and add a definition of done for a written lesson:
  - at least 900 words of the learner's own explanation
  - at least one runnable code example where the topic is code
  - a knowledge check
  - the Assignment includes a practice step
  - the "Outline lesson" banner is removed
- [ ] Open one GitHub issue per item in Phases 3, 4 and 8, using a label for each phase.

**Done when:**
- the validator enforces 1.3 in CI;
- a moved test lesson keeps its progress and redirects correctly in the browser;
- the exercises repo has at least 20 exercises.

---

## Phase 2: Restructure the sequence

One PR that changes only `curriculum.json`, moves files with `git mv` and creates **stub files** for every `NEW` lesson. Each stub carries the outline banner plus an Introduction, a Lesson overview and an Assignment, so the validator passes. Writing the content happens in Phases 3–8.

Below is the target order. Unmarked items stay where they are.

### Foundations (~260 h, was 200)

1. **Introduction**: unchanged.
1. **Your Setup**
   - command line basics
   - **NEW** `shell_scripting_and_your_environment` (env vars, `$PATH`, `which`, permissions, processes, `find`/`xargs`, a first bash script)
   - installing Python and VS Code
   - virtual environments and uv
   - project Hello, uv (**EDIT**: the learner extends a provided `main.py` instead of writing one from scratch)
1. **Git & GitHub**
   - introduction to Git
   - Git basics
   - **NEW** `undoing_mistakes_in_git` (restore, reset, revert, stash, reflog, with a practice lab)
   - branches and PRs
   - README
   - project Hello, GitHub
1. **Python Fundamentals**
   - variables
   - conditionals
   - functions
   - data structures
   - **NEW** `pythonic_python` (comprehensions, generators and `yield`, `zip`/`enumerate`, lambda with `sorted(key=)`, `*args`/`**kwargs`, context managers)
   - files and JSON
   - **NEW** `regular_expressions`
   - project CLI Quiz Game
   - errors and exceptions
   - **NEW** `debugging_and_logging` (VS Code debugger, `breakpoint()`, minimal reproductions, bisecting, the `logging` module; links `exercises/debugging`)
   - modules and packages
   - **NEW** `command_line_apps` (`argparse`, `datetime`, exit codes)
   - classes
   - type hints
   - testing with pytest (**EDIT**: add fakes, `monkeypatch` and dependency injection)
   - **NEW** `linting_formatting_and_ci` (ruff, pre-commit, a GitHub Actions pytest workflow)
   - project Expense Tracker (**EDIT**: CI and ruff required)
   - **NEW** `complexity_and_core_data_structures` (Big-O, hash maps, stacks and queues, sorting and searching)
   - **NEW** `reading_code_and_docs`
   - **NEW** `working_with_ai_coding_assistants` (an agent on a branch, specs first, tests as guardrails, reviewing a diff line by line, AGENTS.md/CLAUDE.md)
   - **NEW** `project_pair_with_an_agent`: add a feature to the Expense Tracker through an agent-written PR, review it, and log every place the agent was wrong
1. **NEW section: Working with Data**
   - **NEW** `notebooks_and_colab` (Jupyter, Colab, opening a GitHub repo in Colab)
   - **NEW** `numpy_and_pandas_basics` (CSV, filtering, groupby, joins)
   - **NEW** `plotting_with_matplotlib` (including error bars)
   - **NEW** `project_data_explorer`: analyze a real CSV and produce a short report with charts
1. **The Web for AI Builders**: unchanged order. Project Weather CLI (**EDIT**: CI, ruff and logging required).
1. **NEW** `project_your_own_cli` (open brief): any CLI that calls a public API, with tests and CI. The learner designs it with no step-by-step guidance.
1. **How LLMs Work**: unchanged. **EDIT** `why_models_hallucinate` to add a first look at untrusted model output and prompt injection.
1. **Your First LLM App**: unchanged. **EDIT** project Terminal Chatbot: put the model call behind a small `ChatBackend` interface. A second backend is extra credit.

### AI Engineering Core (~380 h, was 300)

1. **Prompt & Context Engineering**: unchanged.
1. **NEW section: Measuring Quality**
   - **MOVE** `core/evals/why_evals_matter`
   - **NEW** `error_analysis_and_labeling` (open coding, axial coding, rubrics, a tiny labeling app in Streamlit, synthetic inputs)
   - **NEW** `eval_statistics` (confusion matrix, precision/recall/F1, standard error of a pass rate, bootstrap CIs, paired comparisons, how many examples you need; links `exercises/evals`)
   - Practice: re-score Prompt Lab with CIs.
1. **Structured Outputs**
   - JSON Schema and Pydantic
   - getting structured output
   - **NEW** `multimodal_inputs` (images and PDFs to the model, audio transcription)
   - project Messy-Text Extractor (**EDIT**: include image or PDF inputs, and report scores with CIs)
1. **NEW section: ML Essentials for AI Engineers**
   - **MOVE** `ml/classic_ml/supervised_learning`
   - **MOVE** `ml/classic_ml/overfitting_and_baselines`
   - **MOVE** `ml/classic_ml/project_beat_the_baseline` (**EDIT**: frame it as "a classic classifier vs. an LLM classifier on cost, latency and macro-F1")
1. **Backend for AI Apps**
   - SQL fundamentals (**EDIT**: deepen with indexes, transactions and joins practice)
   - FastAPI basics
   - **MOVE** `production/deployment/docker_for_python` → `core/backend/docker_and_compose` (**EDIT**: add Compose with Postgres)
   - persisting data (**EDIT**: Postgres by default; SQLite only for tests)
   - **NEW** `migrations_with_alembic`
   - **CUT** `auth_and_background_jobs`, split into **NEW** `user_auth` (sessions/JWT or a hosted provider, per-user data) and **NEW** `job_queues_and_workers` (arq or RQ with Redis, retries, idempotency)
   - **NEW** `timeouts_retries_and_rate_limits`
   - **NEW** `deploying_your_api` (Render or Fly with a managed Postgres, a `/health` endpoint, environment config)
   - project LLM-Powered API (**EDIT**: see Phase 5)
1. **Embeddings & Retrieval (RAG)**
   - **MOVE** `ml/math/vectors_and_similarity`
   - what embeddings are (**EDIT**: model choice, dimensions, query/document prefixes, Matryoshka, re-embedding)
   - **NEW** `document_parsing` (pypdf/pymupdf, docling or unstructured, trafilatura, tables, OCR and vision parsing)
   - chunking and vector databases (**EDIT**: pgvector by default)
   - hybrid search and reranking (**EDIT**: Postgres FTS + RRF)
   - citations and grounding (**EDIT**: indirect injection through retrieved documents)
   - **MOVE** `ml/fine_tuning/fine_tune_prompt_or_rag`
   - project Chat With Your Docs (**EDIT**: at least one PDF source, pgvector, incremental re-indexing)
1. **Evals in Practice** (was Evals)
   - code checks and LLM-as-judge
   - evaluating RAG and regressions
   - project RAG Eval Harness (**EDIT**: generic, so it evaluates the extractor and RAG with CIs; judge TPR/TNR required)
1. **Frontend for AI Apps** (was Minimal Frontend)
   - **CUT** `html_css_js_essentials`, split into **NEW** `html_and_css_essentials` and **NEW** `javascript_fundamentals`
   - **NEW** `typescript_basics`
   - **NEW** `react_essentials`
   - **NEW** `nextjs_and_the_ai_sdk`
   - streaming in the browser
   - rapid UIs (reframed as prototyping)
   - project Docs Chatbot UI (**EDIT**: a TS/React front end with login is required; Streamlit is only the prototype step)
1. **NEW section: Career Groundwork**
   - **MOVE** `hired/job_landscape/ai_roles_explained`
   - **MOVE** `hired/portfolio/learning_in_public` (**EDIT**: require one public post per path from here on)
   - **MOVE** `hired/job_landscape/project_role_map`
1. **NEW** `project_core_open_brief`: a business problem and evaluation criteria only. The learner designs the schema, API, evals and UI.

### Agentic Systems (~300 h, unchanged total and rebalanced)

1. **What Is an Agent?**
   - workflows vs agents
   - the agent loop
   - project Workflow or Agent? (**EDIT**: decision memo and cost math only; remove the mini loop)
1. **Tool Use**
   - function calling
   - designing tools
   - tool errors and parallel calls (**EDIT**: argument validation and repair, timeouts, backoff)
   - **MOVE** `agentic/safety/prompt_injection` (lethal trifecta)
   - **NEW** `agent_tracing_and_debugging` (OpenTelemetry GenAI conventions, Langfuse or Phoenix, replaying a failed run)
   - **MOVE** `agentic/agent_evals/agent_eval_fundamentals` (tasks, trials, environment graders, pass^k)
   - scaling to many tools (**EDIT**: label provider-specific features)
   - project Agent Loop From Scratch (**EDIT**: see Phase 5)
1. **Workflow Patterns**
   - chaining and routing
   - parallelization
   - evaluator-optimizer
   - **NEW** `agent_cost_and_latency` (per-run budgets, caching in loops, model routing per step)
   - project Support Ticket Pipeline
1. **MCP**: unchanged. **EDIT** `mcp_architecture`: add Elicitation and the other current primitives.
1. **Memory & Context**
   - **NEW** `context_engineering_for_agents` (tool-result shaping, just-in-time retrieval, agentic search vs vector RAG)
   - short- and long-term memory
   - compaction
   - long-running agents
   - **NEW** `durable_execution` (checkpointers, Temporal or Inngest, queue workers, idempotent side effects, resuming after a crash)
   - project The Agent That Remembers (**EDIT**: must survive a process restart)
1. **Frameworks, SDKs & Skills**
   - Claude Agent SDK
   - other agent frameworks (**EDIT** → "LangGraph and the Wider Ecosystem": LangGraph in depth, one comparison read for the rest)
   - agent skills (**EDIT**: gains the Skill practice removed from the project)
   - **MOVE** `ml/fine_tuning/running_open_models`
   - when frameworks help
   - project Port Your Agent (**EDIT**: port to LangGraph *and* run on an open model or a second provider; drop the Skill requirement)
1. **Coding, Browser & Computer-Use Agents**
   - how coding agents work
   - sandboxing (Docker is now taught earlier)
   - browser and computer use (**EDIT**: measured reliability and cost per step against a plain API)
   - **NEW (optional)** `voice_and_realtime_agents`
   - project Sandboxed Coding & Browser Agent
1. **Multi-Agent Systems**
   - subagents and orchestration (**EDIT**: fold in handoffs; A2A moves to Additional resources)
   - **CUT** `handoffs_and_a2a` (folded into subagents)
   - project Research Agent
1. **Safety & Human-in-the-Loop**
   - secure design patterns
   - **NEW** `guardrails_in_production` (input/output classifiers, PII redaction, policy engines)
   - approvals and permissions (**EDIT**: agent UX, approvals in a web UI)
   - project Break Your Own Agent
1. **Evaluating Agents at Scale** (was Evaluating Agents)
   - simulated users and benchmarks
   - project Workflow Automation Agent (**EDIT**: the approval survives a restart and shows in a UI)

### Production & LLMOps (~180 h, was 120)

1. **Deployment**
   - **NEW** `one_real_cloud` (Cloud Run or AWS App Runner, IAM, a secrets manager; Render stays as the free fallback)
   - deploying to the cloud (**EDIT** → "Environments and Releases": staging vs prod, rollbacks; adds a practice step)
   - **NEW (optional)** `a_server_of_your_own` (VPS, SSH, systemd)
   - project Hello, Production
1. **NEW section: Data in Production**
   - **NEW** `managed_postgres_and_backups`
   - **NEW** `feature_flags_and_ab_tests`
1. **Observability**
   - logging and tracing (**EDIT**: PII redaction in traces)
   - traces to evals
   - **NEW** `alerting_and_incidents` (alerts, on-call basics, postmortems)
   - project Trace Detective
1. **Cost & Latency**
   - caching and model choice
   - batching, rate limits and fallbacks (**EDIT**: LiteLLM or OpenRouter gateway)
   - **NEW** `load_testing` (Locust, p95 under concurrency)
   - project Cut the Bill (**EDIT**: cross-provider fallback and a p95 load-test result required)
1. **Reliability, Security & CI**
   - prompt versioning and CI evals
   - security review (**EDIT**: GDPR basics, data retention)
   - **NEW** `code_review` (reviewing human and AI diffs, giving and receiving review)
   - project Ship It (**EDIT**: an alert fired on purpose, a rollback exercised)

### Final Capstone (~120 h, was 100)

- finding a real problem
- **NEW** `working_in_a_team` (PR etiquette, issue tracking, async communication)
- writing a spec
- project Capstone (**EDIT**: see Phase 6)

### Getting Hired (~100 h, was 80)

1. **Portfolio & Writing**
   - case studies and demos
   - project Portfolio Site
1. **Open Source**: unchanged.
1. **NEW section: Running the Search**
   - **NEW** `networking_and_referrals`
   - **NEW** `project_outreach_sprint` (20 targeted messages, logged)
   - **NEW** `running_a_job_search` (pipeline tracker, weekly targets, handling rejection)
   - **NEW** `freelance_and_contract_work`
1. **Resume & Interviews**
   - resume
   - **NEW** `coding_interviews` (a NeetCode-style Easy/Medium set in Python, timed practical builds, AI-assisted interview rounds)
   - **NEW** `behavioral_interviews` (STAR, six stories drawn from your projects)
   - **NEW** `system_design_basics` (general: load balancers, caches, queues, databases)
   - AI system design
   - **NEW** `offers_and_negotiation`
   - project Mock Interview Loop (**EDIT**: add a live coding round and an AI-assisted round)

### ML Foundations elective (~120 h, rescoped)

- **Just Enough Math**
  - **NEW** `math_you_need` (a checklist with Khan Academy links)
  - matrices and probability (**EDIT**: replace MML chapter 6 with Khan Academy or Seeing Theory)
  - project Similarity by Hand
- **Neural Networks & Transformers**: unchanged.
- **Open Models & Fine-Tuning**
  - LoRA fine-tuning
  - **NEW** `serving_open_models` (Ollama → vLLM, batching, throughput)
  - **NEW** `distillation_and_synthetic_data`
  - **NEW** `fine_tuning_embeddings`
  - project Fine-Tune a Small Model (**EDIT**: measure batched throughput for the cost estimate)
  - **NEW (extra)** `project_preference_tuning` (a small DPO run)

### Research Track elective (~500 h honest, `"requires": ["ml"]`)

- **EDIT**:
  - state the prerequisites in each lesson's Introduction;
  - move Boyd, Roughgarden and the full 18.06 problem sets to Additional resources;
  - replace repeated readings (3Blue1Brown, Bayes, ReAct/ToT/Generative Agents) with cross-references.
- **EDIT** the description in `curriculum.json`: "pre-master's preparation, not required for applied roles."

### Site-wide copy

- [ ] **EDIT** hours in `curriculum.json`, `curriculum/about.md`, the FAQ in `scripts/build.py`, and `README.md`. The new core total is about 1,340 h, roughly 15–20 months at 15–20 h/week. Then run `python3 scripts/build.py` to regenerate `index.html`.

**Done when:**
- the validator and `build.py --check` pass;
- every `NEW` stub exists with a full Assignment, so the path is usable even before the prose is written.

---

## Phase 3: Write the project-critical lessons

Projects depend on these lessons, which currently teach only through bullets and links. Each one must meet the definition of done (1.8) and include **a 30–60 line annotated code walkthrough**. Work in this order:

| # | Lesson | The walkthrough must show |
| --- | --- | --- |
| 1 | `agentic/tool_use/function_calling` | a full `tool_use` → `tool_result` message round trip |
| 2 | `agentic/what_is_an_agent/the_agent_loop` | a minimal loop with a step limit and stop reasons |
| 3 | `agentic/tool_use/tool_errors_and_parallel_calls` | structured errors, `is_error`, results matched by ID |
| 4 | `core/structured_outputs/getting_structured_output` | a retry-with-`ValidationError` loop |
| 5 | `core/backend/fastapi_basics` | routes, Pydantic models, `TestClient` tests |
| 6 | `core/backend/persisting_data` | the `get_session` dependency, CRUD against Postgres |
| 7 | `core/backend/docker_and_compose` | a Dockerfile and a Compose file with Postgres |
| 8 | `core/rag/chunking_and_vector_databases` | an ingestion script into pgvector |
| 9 | `core/rag/hybrid_search_and_reranking` | an RRF function, Postgres FTS |
| 10 | `core/evals/why_evals_matter` | a JSONL trace logger and an error-analysis notebook |
| 11 | `core/evals/code_checks_and_llm_as_judge` | a binary judge plus TPR/TNR validation |
| 12 | `core/frontend/streaming_in_the_browser` | an SSE generator in FastAPI plus a `fetch` reader |
| 13 | `agentic/safety/prompt_injection` | a working injection against a toy agent and its fix |
| 14 | `agentic/agent_evals/agent_eval_fundamentals` | an environment-state grader, pass^k |
| 15 | `production/reliability/prompt_versioning_and_ci_evals` | a GitHub Actions workflow that fails on an eval drop |

Every lesson also gets its knowledge check and a practice step in the Assignment.

**Done when:** all 15 have no outline banner and pass review by a second person who works through the code.

---

## Phase 4: Write the new required lessons

These are the `NEW` stubs from Phase 2 in the required paths, about 45 lessons. Write them in priority order, by how much each one affects hireability:

1. **Highest:**
   - `working_with_ai_coding_assistants` + `project_pair_with_an_agent`
   - `eval_statistics`
   - `error_analysis_and_labeling`
   - `complexity_and_core_data_structures`
   - `coding_interviews`
1. **Gaps that projects depend on:**
   - `pythonic_python`
   - `debugging_and_logging`
   - `command_line_apps`
   - `linting_formatting_and_ci`
   - the Working with Data section
   - `document_parsing`
   - `migrations_with_alembic`
   - `deploying_your_api`
1. **Stack modernity:**
   - `javascript_fundamentals`
   - `typescript_basics`
   - `react_essentials`
   - `nextjs_and_the_ai_sdk`
   - `user_auth`
   - `job_queues_and_workers`
1. **Agent depth:**
   - `agent_tracing_and_debugging`
   - `durable_execution`
   - `context_engineering_for_agents`
   - `agent_cost_and_latency`
   - `guardrails_in_production`
1. **Production:**
   - `one_real_cloud`
   - `managed_postgres_and_backups`
   - `alerting_and_incidents`
   - `load_testing`
   - `feature_flags_and_ab_tests`
   - `code_review`
1. **Career:**
   - `networking_and_referrals`
   - `behavioral_interviews`
   - `running_a_job_search`
   - `system_design_basics`
   - `freelance_and_contract_work`
   - `offers_and_negotiation`
   - `working_in_a_team`
1. **The rest**, including the optional `voice_and_realtime_agents` and `a_server_of_your_own`.

Each lesson meets the definition of done, and where it is a coding topic it links an exercise set in `exercises/`.

---

## Phase 5: Upgrade project briefs

Apply the evidence checklist (1.2) to every project, plus these specific changes:

- [ ] **Hello, uv**: provide the starter `main.py`, so the learner only extends it.
- [ ] **Expense Tracker**, **Weather CLI**: GitHub Actions running ruff and pytest is required, with a badge in the README.
- [ ] **Terminal Chatbot**: a `ChatBackend` interface is required.
- [ ] **Messy-Text Extractor**: image or PDF inputs; scores with bootstrap CIs.
- [ ] **LLM-Powered API**:
  - Postgres via Compose
  - Alembic migrations
  - user auth
  - a queue worker for long jobs
  - 429 handling and timeouts
  - JSONL traces with prompt version IDs
  - an extractor eval in CI
  - deployed with a public `/health`
- [ ] **Chat With Your Docs**: a PDF source, pgvector, hybrid search, incremental re-index, one indirect-injection test document.
- [ ] **RAG Eval Harness**: generic across the extractor and RAG; judge TPR/TNR; CIs; runs in CI.
- [ ] **Docs Chatbot UI**: Next.js or React with TypeScript, login, streaming. Streamlit is only the prototype step.
- [ ] **Agent Loop From Scratch**: OpenTelemetry-compatible traces, required rather than extra credit; a 10-task eval with pass^3; one prompt-injection test (a poisoned web page tries to exfiltrate through `write_file` or search).
- [ ] **Every later agentic project**: a small required eval and one injection case, carried forward.
- [ ] **The Agent That Remembers**, **Workflow Automation Agent**: state survives a process restart, and approvals show in a UI.
- [ ] **Port Your Agent**: LangGraph plus an open model or a second provider, with a comparison table.
- [ ] **Fine-Tune a Small Model**: batched or vLLM throughput for the cost estimate.

---

## Phase 6: Capstone and Getting Hired

- [ ] **EDIT** `capstone/capstone/project_capstone.md`:
  - every change goes through a PR that a peer reviews;
  - the learner reviews two other learners' capstone PRs;
  - at least two weeks of real use;
  - at least 30 real tasks;
  - one online metric (acceptance rate, edits or retention) reported next to the offline eval;
  - an optional 2–3 person team track.
- [ ] **EDIT** `hired/interviews/project_mock_interview_loop.md`: add a 45-minute live coding round and an AI-assisted build round.
- [ ] **EDIT** `hired/job_landscape/ai_roles_explained.md`: note that AI product engineer roles expect TypeScript and React.
- [ ] Set up a peer-review venue, such as a GitHub Discussions category or a Discord channel, so the peer review requirements are possible. Link it from `asking_for_help.md`.

---

## Phase 7: Rescope the electives

- [ ] Apply the ML and Research changes from Phase 2. Confirm the honest-hours estimates by listing every assigned lecture and problem set with its time.
- [ ] Add "Requires ML Foundations" to the first lesson of each Research section.
- [ ] Dedupe repeated readings with cross-references.
- [ ] Add a free-GPU fallback note (Kaggle, Lightning AI, or a CPU-only path) to the tiny-GPT and fine-tuning projects.

---

## Phase 8: Write the remaining outlines and backfill knowledge checks

- [ ] Write every remaining "Outline lesson" in path order, so learners hit finished content first. This is about 75 files after Phase 3, minus any cut ones.
- [ ] Backfill knowledge checks into all 34 Foundations lessons (this can start right after Phase 1).
- [ ] Once the outline count reaches zero, make the knowledge-check validator rule apply to every lesson.
- [ ] Rebalance repeated readings: Building Effective Agents is cited about 10 times and Chip Huyen's platform post 5 times. Swap in fresh material, for example the Google SRE book chapters and real postmortems.

**Done when:** the validator reports 0 outlines and every lesson has a knowledge check.

---

## Hours re-budget

| Path | Before | After | Main reason |
| --- | --- | --- | --- |
| Foundations | 200 | 260 | Pythonic Python, debugging, CI, DSA, AI assistants, Working with Data |
| AI Engineering Core | 300 | 380 | eval statistics, ML essentials, Postgres/Docker/auth/queues, TS/React |
| Agentic Systems | 300 | 300 | tracing, durable execution and cost added; frameworks and multi-agent trimmed |
| Production & LLMOps | 120 | 180 | cloud, data in prod, alerting, load testing, code review |
| Final Capstone | 100 | 120 | team practice, longer real use |
| Getting Hired | 80 | 100 | coding interviews, networking, job-search process |
| **Required total** | **1,100** | **1,340** | |
| ML Foundations (elective) | 150 | 120 | classic ML and vectors moved to Core |
| Research Track (elective) | 200 | ~500 | honest estimate; now requires ML |

## Suggested PR sequence

1. `fix/phase-0-bugs`
1. `infra/knowledge-checks-and-templates` (1.1, 1.2)
1. `infra/validator` (1.3)
1. `infra/requires-field` (1.5)
1. `infra/current-models-page` (1.6)
1. `restructure/curriculum-json` (Phase 2, all moves and stubs in one PR so the order never half-changes)
1. `docs/hours-and-copy` (site-wide copy plus `build.py`)
1. Then one PR per lesson or project from Phases 3–8, each linked to its issue.

## Risks and how to handle them

- **Phase 2 is a large PR.** Keep it mechanical (JSON, `git mv`, stubs) with no prose changes.
- **Scope creep in the new lessons.** Hold to the definition of done. A lesson can always be extended later.
- **AI tooling goes stale fast.** Keep the Current Models page, run the weekly link check, and put a "last checked" date on time-sensitive claims such as free tiers and pricing.
- **Peer review needs a community.** Until one exists, a learner may substitute a recorded self-review with an AI reviewer, but must say so in the README.

---

## Finishing plan (from 2026-10-28)

Phases 0–3 are done, and Phase 4 is partly done. This plan finishes the required paths in batches. **What's left:** 72 required lessons that are still outlines and 31 required project briefs without an `#### Evidence` section. The electives (26 lessons, 8 briefs) are optional and come last.

**Done when** every lesson in a required path meets the definition of done, every project brief has Evidence, `scripts/validate.py` and `scripts/check_exercises.py` both pass, and every item under [Deferred verification](#deferred-verification) is checked.

### How each batch runs

- About 6 writer agents per batch, usually 2 lessons each, all following the writer brief.
- Each agent saves a complete draft to disk before checking links, so an interrupted run never loses work.
- After each batch: audit (validator, exercise checker, scope, consistency between lessons), then commit, merge to `main` and push.
- Order follows the learner's path. Lessons are written before the project briefs that depend on them, so each brief matches what was taught.

### Batches

| # | Lessons | Briefs and fix-ups |
| --- | --- | --- |
| 4. Core | User Accounts and Auth, Job Queues and Workers, Timeouts/Retries/Rate Limits, Images/PDFs/Audio, JavaScript, TypeScript, React, Next.js and the AI SDK, HTML and CSS, Rapid UIs, Citations and Grounding, Supervised Learning, Overfitting and Baselines, Fine-Tune/Prompt/RAG (14) | JavaScript must cover `fetch` and async/await. Images/PDFs/Audio must cover the base64 document block. Job Queues must fit the `submit_job`/`INLINE_JOBS` pattern in Deploying Your API |
| 5. Core briefs, Agentic I | Workflows vs Agents, Designing Tools, Agent Tracing and Debugging, Scaling to Many Tools, Chaining and Routing, Parallelization and Orchestrators (6) | Write the Core Open Brief project. Add Evidence to 5 Core and 7 Foundations briefs. Chat With Your Docs ingests `records.jsonl` so citations keep page numbers |
| 6. Agentic II | Evaluator-Optimizer, Agent Cost and Latency, MCP Architecture, Building an MCP Server, MCP Transports and Security, Context Engineering, Short- and Long-Term Memory, Compaction, Long-Running Agents, Durable Execution, Claude Agent SDK, Other Frameworks (12) | none |
| 7. Agentic III | Agent Skills, Running Open Models, When Frameworks Help, How Coding Agents Work, Sandboxing, Browser and Computer Use, Subagents and Orchestration, Secure Design Patterns, Guardrails in Production, Approvals and Permissions, Simulated Users and Benchmarks, Voice (optional) (12) | none |
| 8. Agentic briefs, Production I | One Real Cloud, Deploying to the Cloud, Managed Postgres and Backups, Feature Flags and A/B Tests, Logging and Tracing, Traces to Evals, Alerting and Incidents, Load Testing (8) | Evidence for all 10 Agentic briefs, each with a prompt-injection test |
| 9. Production II, Capstone | Caching and Model Choice, Batching/Rate Limits/Fallbacks, Security Review, Code Review, A Server of Your Own (optional), Finding a Real Problem, Writing a Spec, Working in a Team, Resume for AI Roles, Case Studies and Demos (10) | Evidence for 4 Production briefs and the Capstone |
| 10. Getting Hired | Your First Contribution, Networking and Referrals, Running a Job Search, Freelance and Contract Work, Behavioral Interviews, Offers and Negotiation, System Design Basics, AI System Design (8) | Write the Outreach Sprint project. Evidence for 3 Hired briefs |
| 11. Final review | none | A consistency pass across the curriculum. Recheck each path's hour estimate against what it assigns. Tick off the checkboxes in this roadmap |
| 12–13. Electives (optional) | ML: 8 lessons. Research: 17 lessons | ML: 4 briefs. Research: 5 briefs |

Each batch takes about 20–30 minutes of agent time plus review.

### Open decisions

- [x] **Lesson length.** Decided: the target for a lesson's own explanation is now 1,500–2,200 words, which matches the finished lessons. No trimming.
- [x] **One Real Cloud vs Deploying to the Cloud.** Decided: the Batch 8 agent first recommends whether to merge or split them, then writes them.
- [x] **Electives.** Decided: write them after the required paths (Batches 12–13).

### Deferred verification

Agents work without API keys, Docker or a Render account, so some code has only run against fakes. Test these by hand before calling the curriculum finished. Each batch adds its items here.

- [ ] Run the Claude API examples with a real key: The Agent Loop, Function Calling, Tool Errors and Parallel Calls, Prompt Injection, Agent Eval Fundamentals, Streaming in the Browser, Error Analysis and Labeling (`synth.py`), and Document Parsing (`vision_parse.py`).
- [ ] Build the Dockerfile and `compose.yaml` from Docker and Docker Compose, and the pgvector Compose file from Chunking and Vector Databases.
- [ ] Run the Compose `migrate` service from Migrations with Alembic.
- [ ] Deploy the LLM-Powered API's free `render.yaml` to Render once, with inline jobs.
- [ ] Run `uv lock` in `exercises/`; numpy was added to `uv.lock` by hand.
- [ ] Browser checks: the Meta hiring-process page says candidates use only its built-in AI assistant (Coding Interviews), and the Runestone pythonds3 chapter names match the Complexity lesson.
