# Writer brief: Project Mímir lessons

You are writing lessons for **Project Mímir**, a free curriculum at `/Users/mac/Desktop/vibe coding/project-mimir`. It takes a learner with **zero coding experience** to a job as an AI engineer or agent engineer. It copies The Odin Project's method:
- written lessons that actually teach;
- the best free resources, each with a reason to read it;
- frequent projects that need evidence they work;
- a knowledge check at the end of every lesson.

Today is the date the batch is launched; the person launching it updates this line or states the date in the agent prompt.

## Read these first

1. `LAYOUT_STYLE_GUIDE.md`, the rules. Pay particular attention to Knowledge check, the evidence ladder, the definition of a "written" lesson, and model IDs.
1. `templates/lesson-template.md` and `templates/project-template.md`.
1. `curriculum/curriculum.json`, the order of everything. A lesson may only assume what comes **before** it in this order.
1. Two reference lessons for tone and depth: `curriculum/foundations/python/testing_with_pytest.md` and `curriculum/foundations/first_llm_app/your_first_api_call.md`. Match them.
1. `ROADMAP.md`, for why the curriculum is changing. Phase 5 lists project changes.

## What "done" means for a lesson

- **Remove the "Outline lesson" warning box.**
- Structure: `### Introduction`, `### Lesson overview`, then **custom teaching sections** (`### Your heading`), then `### Assignment`, `### Knowledge check`, and `### Additional resources` (optional).
- **Teach in prose.** Write about 1,500–2,200 words of your own explanation, with concrete examples. If the file has a `### Key ideas` bullet list, turn it into real teaching sections and remove the `Key ideas` heading. Keep the ideas.
- **Show code.** When the topic involves code, include short, **runnable**, annotated examples, usually 1–3 blocks of 10–60 lines. Use Python 3.12 with `uv` unless the topic is JS/TS/SQL/bash. Code must be correct for current library versions.
  - Before writing any Claude API or Anthropic SDK code, load the `claude-api` skill with the Skill tool and follow it.
- **Practice.** The Assignment has 3–6 numbered items. Each says why it's there and which parts to read. At least one item is a hands-on practice task, and it can point to an exercise set (see below).
- **Knowledge check.** 4–7 questions, each a link to the `###` heading that answers it, formatted as in the template. An anchor is the heading text lowercased, with runs of characters other than letters and digits replaced by `-`, for example `### Why chunk size matters` → `#why-chunk-size-matters`. The validator checks every anchor, so keep headings free of code and punctuation surprises.
- Define jargon the first time it appears. Use plain, direct American English, and write for someone who started from zero a few months ago.

## What "done" means for a project brief

- Keep the existing structure: Introduction, optional Before you start, Assignment, Submitting your work.
- Add an `#### Evidence` subsection inside the Assignment panel, before `#### Extra credit`, that follows the evidence ladder in the style guide:
  - **From the Expense Tracker on:** CI with ruff and pytest.
  - **From the LLM-Powered API on:** traces plus an eval score with a confidence interval.
  - **From the Agent Loop From Scratch on:** at least one prompt-injection test.
- Apply any project changes assigned to you.
- A project may only require skills taught before it. If it needs something untaught, either cut the requirement or say which earlier lesson covers it.
- If a project file is a stub, write the full brief at the same depth as `curriculum/agentic/tool_use/project_agent_loop_from_scratch.md`.

## Links

- **Free resources only.** No paywalls, and no required sign-ups when a free alternative exists.
- **Keep the existing curated links** unless they're broken or outdated. They were chosen with care.
- **Verify every new URL before using it**, with `curl -s -o /dev/null -w '%{http_code}' -L --max-time 20 URL`. It should return 200; a 403 is acceptable for realpython.com, openai.com, medium.com, coursera.org and runestone.academy. **A 403 is not proof a link is broken.** Many sites sit behind a bot filter such as Cloudflare that blocks scripts but not browsers. Check with `curl -sI URL | grep -i -E 'cf-mitigated|server: cloudflare'`. If it's a bot challenge, keep a good resource and list the URL in your final report under "needs a browser check" instead of dropping it. **Never invent a URL.** If you can't find a good free resource, write the explanation yourself.
- Prefer official docs, then well-known free courses and books, then respected practitioner writing.

## Provider neutrality

Code examples use the Anthropic SDK by default, so learners see one consistent API. But the curriculum must not make learners Claude-only: employers use OpenAI, Gemini and open models too.

- **Every lesson with model-calling code gets an `### On other providers` section**, placed after the teaching sections and before `### Assignment`. Write 3–8 sentences on what carries over and what differs on other providers: the names and shapes of messages, tool calls, structured output, streaming, caching, or whatever your lesson uses. You may add one short snippet (15 lines at most) showing the same call with the OpenAI SDK or a local open model through Ollama's OpenAI-compatible API. Link the matching OpenAI docs page and one open-model option, and verify every URL.
- **Label provider-specific features** the first time they appear, for example "(a Claude feature)", and say what to do on other providers. Never present one provider's behavior or limits as universal.
- **Where a project compares models, allow or encourage a second provider.**

## Model IDs

- Never put a model ID in prose. Write "the [cheap model](#/models)" or "the [capable model](#/models)" instead.
- In code, use this pattern: `MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")`.

## Where things now live

Fix any stale cross-references you find in your files.

- **Foundations** now also teaches:
  - Shell Scripting and Your Environment; Undoing Mistakes in Git
  - Pythonic Python (generators, lambda/`sorted(key=)`, `*args`, context managers); Regular Expressions
  - Debugging and Logging (`logging` module); Command-Line Apps (`argparse`, `datetime`)
  - Linting, Formatting and CI (ruff, pre-commit, GitHub Actions)
  - Complexity and Core Data Structures (Big-O)
  - Reading Code and Docs; Working With AI Coding Assistants
  - a **Working with Data** section: Jupyter/Colab, NumPy/pandas, matplotlib
  - `testing_with_pytest` covers fakes, `monkeypatch` and dependency injection.
- **Core order:**
  1. Prompting
  1. **Measuring Quality**: Why Evals Matter, Error Analysis and Labeling, Eval Statistics (P/R/F1, CIs, bootstrap)
  1. Structured Outputs, including Images, PDFs and Audio
  1. **ML Essentials** (moved from the ML elective): Supervised Learning, Overfitting and Baselines, Beat the Baseline
  1. **Backend**: SQL, FastAPI, **Docker and Docker Compose** (moved from Production), Postgres via SQLModel (Postgres is the default database from here on), Alembic migrations, User Accounts and Auth, Job Queues and Workers (Redis + arq/RQ), Timeouts/Retries/Rate Limits, Deploying Your API (Render or Fly + managed Postgres), Project LLM-Powered API
  1. **RAG**: Vectors and Similarity (moved from ML), Embeddings, Document Parsing, Chunking (**pgvector is the default store**), Hybrid Search (Postgres FTS or `bm25s` + RRF), Citations and Grounding, Fine-Tune/Prompt/RAG (moved from ML), project
  1. **Evals in Practice**: judges, RAG evals, harness
  1. **Frontend**: HTML/CSS, JavaScript, TypeScript, React, Next.js + Vercel AI SDK, Streaming in the Browser, Prototyping with Streamlit/Gradio, Docs Chatbot UI (TS/React required)
  1. **Career Groundwork** (moved from Getting Hired): AI Roles Explained, Reading Job Postings, Learning in Public, Role Map
  1. **Open Brief** project
- **Agentic order:**
  1. What Is an Agent
  1. **Tool Use**: function calling, designing tools, tool errors, **Prompt Injection** (moved here from Safety), **Agent Tracing and Debugging** (new), **Agent Eval Fundamentals** (moved here from Agent Evals), scaling to many tools, Agent Loop project
  1. Workflow Patterns, plus **Agent Cost and Latency**
  1. MCP
  1. Memory, plus **Context Engineering for Agents** and **Durable Execution**
  1. Frameworks: Claude Agent SDK, **LangGraph and the Wider Ecosystem**, Agent Skills, **Running Open Models** (moved from ML), When Frameworks Help
  1. Coding/Browser agents, plus optional Voice
  1. Multi-Agent: Subagents and Orchestration (**handoffs and A2A are folded in here**; the separate A2A lesson was removed)
  1. Safety: Secure Design Patterns, **Guardrails in Production**, Approvals
  1. Evaluating Agents at Scale
- **Production:**
  - Deployment: One Real Cloud (Cloud Run), Environments and Releases, an optional VPS lesson
  - **Data in Production**: managed Postgres and backups, feature flags and A/B tests
  - Observability, plus Alerting and Incidents
  - Cost and Latency, plus Load Testing
  - Reliability, plus **Code Review**
- **Capstone** adds Working in a Team.
- **Hired:** Portfolio; Open Source; **Running the Search** (networking, job search, freelance, Outreach Sprint project); Interviews (resume, **Coding Interviews**, **Behavioral**, **System Design Basics**, AI System Design, **Offers**, Mock Interview Loop).
- **ML elective:** Math You Need, Matrices and Probability, Similarity by Hand; neural nets and tiny GPT; LoRA, Serving Open Models (vLLM), Distillation and Synthetic Data, Fine-Tuning Embeddings, Fine-Tune project, optional Preference Tuning (DPO) project.
- **Research:** requires ML Foundations.

## Exercise sets

These sets live in the repo at `exercises/<set>/`. Link a set as `https://github.com/espiNovah/project-mimir/tree/main/exercises/<set>`. Only these sets exist, so don't link any other name:

`python-basics`, `pythonic-python`, `regex`, `debugging`, `cli-apps`, `complexity`, `data`, `evals`, `javascript`, `typescript`

Each exercise is a starter file plus failing tests. The learner makes the tests pass with `uv run pytest <set>/<exercise>` from the `exercises/` folder (the set README shows the setup), or `npm test` for the JS/TS sets.

## Rules of engagement

- Only edit the files assigned to you. **Don't edit `curriculum/curriculum.json`.** If a title or description should change, say so in your final report.
- Don't run git commands that change state.
- When you finish, run `python3 scripts/validate.py`. Errors in other people's files are expected, but **none may be in yours**.
- **Final report** (under 300 words):
  - each file with its approximate word count;
  - suggested `curriculum.json` changes;
  - URLs you wanted but couldn't verify;
  - anything that conflicts with other lessons.
