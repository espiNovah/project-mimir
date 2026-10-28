### Introduction

Every Core project so far told you what to build. The Messy-Text Extractor named the schema's job, the LLM-Powered API listed its endpoints, and Chat With Your Docs said which retrieval steps to use. This one doesn't. You get a business problem and the bar the solution has to clear, and nothing else. You decide what the system does, what the schema looks like, which endpoints exist, how you'll measure it, and what the user sees.

That is what the job is actually like. A product manager or a client says "our support team drowns in tickets" or "nobody can find anything in our policy documents", and maybe adds "it has to be right nearly every time, and fast". Turning that into a design, a measurable definition of "good" and a working, deployed feature is the core skill of an AI engineer. It's also the strongest portfolio piece you can have at this point, because nobody else will have built the same thing.

You've already learned everything you need. If you get stuck, the answer is in a Core lesson you've done, and the requirements below say which one. How you put the pieces together is up to you.

### Before you start

#### Choose a problem

Pick one of the briefs below, or write your own in the same shape. A brief is a problem, a user and a bar: a few success criteria with numbers. A problem you or someone you know actually has is the best choice, because you'll have real inputs and a real person to show it to.

1. **Support ticket triage.** A small software company gets a few hundred support emails a week. The support lead wants each one tagged with a category and an urgency, and the customer's account or order number pulled out, so urgent tickets get answered first. **The bar:** macro-F1 on category at least 0.85 and clearly above a non-LLM baseline; recall on urgent tickets at least 0.95; the extracted ID is correct on at least 95% of tickets that contain one; under $0.01 per ticket.
1. **Policy answers for tenants.** A tenants' association has a stack of PDFs: the lease template, building rules, city housing regulations. Members keep asking the same questions. **The bar:** at least 80% of answerable questions answered correctly, every answer cites the document and page, at least 90% of out-of-scope questions get "I don't know", and a reviewer can check any answer in under a minute.
1. **Receipts for a bookkeeper.** A freelance bookkeeper receives photos and PDFs of receipts from clients and types them into a spreadsheet. **The bar:** merchant, date, total and tax correct on at least 95% of receipts, including photos; every low-confidence receipt is flagged for review instead of guessed; a batch of 50 receipts finishes in under five minutes.
1. **Meeting notes to action items.** A volunteer group records its meetings as text notes and forgets half of what it agreed to do. **The bar:** recall on action items at least 0.90 and precision at least 0.80 against your hand labels; each item has an owner and a due date when the notes give one, and never an invented one.
1. **Your own.** Write a brief like the ones above for a problem you choose. It needs a named user, a problem in their words, and three to five success criteria with numbers you can measure. At least one criterion must be about quality, and one about cost or speed.

Whichever you choose, the system must use a model to do real work, and either retrieval with citations (as in the RAG section) or validated structured outputs (as in the Structured Outputs section), or both.

#### Design it on paper first

Create a new repository named `mimir-<your-project-name>` and write a `DESIGN.md` before any code. Answer these in plain language:

1. **The brief.** Copy it in, then restate the problem in your own words. What would the user do today without your system?
1. **What does using it look like?** Describe two or three real interactions from the user's side, with example inputs and the output you expect.
1. **Success criteria.** Turn each bar into a metric you can compute: which cases, which grader (code, human or judge), and how many examples you'll need to tell a pass from a fail with a confidence interval of a useful width. (Eval Statistics)
1. **The simplest baseline.** What would a regex, a keyword search, a classic classifier or a single plain prompt score? You'll measure it, because a system that doesn't beat a cheap baseline isn't worth its cost. (Overfitting and Baselines)
1. **Prompt, RAG or fine-tuning?** Which problem do you have, knowledge or behavior, and why does your choice fit it? (Fine-Tune, Prompt or RAG?)
1. **The design.** The data model, the endpoints, the schema or retrieval pipeline, and the screens. A box-and-arrow sketch is enough.
1. **What can go wrong?** Bad or hostile inputs, model failures, timeouts, cost blowups, and what the user sees in each case.
1. **Non-goals.** What you will deliberately not build.

Commit `DESIGN.md` before you write any code. It's normal for the design to change. When it does, update the file and say what changed and why in your README.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Keep the scope small

Aim for three to four weeks of work. One user, one main flow and a handful of screens that work, fail gracefully and are measured beat a sprawling app that half works. Put extra ideas under a "Next steps" heading in your README.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

There is no step-by-step guide for this project. These are the requirements your finished system must meet; how you meet them is up to you.

#### Evals first

1. Build a golden dataset before you tune anything: at least 50 cases drawn from real inputs where you can get them, and synthetic inputs where you can't, including edge cases and inputs your system should refuse or flag. Label them yourself, with written labeling guidelines. (Why Evals Matter, Error Analysis and Labeling)
1. Write a grader for every success criterion. Use code checks wherever they can work. If a criterion needs an LLM judge, validate it against your own labels and report its true positive and true negative rates before you trust it. (Code Checks and LLM-as-Judge)
1. Measure your baseline on the same cases, then your first working version. Run error analysis on the failures, name the categories and count them, and make at least one change aimed at the largest category. Show the before-and-after scores with a paired comparison. (Error Analysis and Labeling, Eval Statistics)
1. Run your evals with one command. Reusing your RAG Eval Harness with a new adapter is the fastest way, and a good test of its design. (Evaluating RAG and Catching Regressions)

#### The system

1. Build the model-powered core as a tested Python package: prompts with version IDs, Pydantic validation of every structured output, and citations checked in code if you use retrieval. If your inputs include images, PDFs or audio, handle them as in Images, PDFs and Audio. (Structured Outputs, Embeddings & Retrieval)
1. Wrap it in a FastAPI backend with Postgres via SQLModel, tables created by Alembic migrations, user accounts, and each user seeing only their own data. (Backend for AI Apps)
1. Make it resilient: a timeout on every model call, retries with backoff for errors that can fix themselves, a per-user rate limit, and an input size limit. If any request takes more than a few seconds, run it as a job, as in Job Queues and Workers and Deploying Your API. (Timeouts, Retries and Rate Limits)
1. Treat every outside input as untrusted. If your system reads documents or text that someone else wrote, add at least one case with an injected instruction to your golden set and show that the system doesn't follow it. Display model output as text, never as raw HTML. (Citations and Grounding, Streaming in the Browser)
1. Build a UI that fits your user. If the users are outside your team, build it in React and TypeScript calling your backend, as in the Docs Chatbot UI project. If the brief's users are genuinely internal, a Streamlit or Gradio app is acceptable, but justify it in the README with the criteria from Prototyping with Streamlit and Gradio. Stream responses if the user waits on generated text. (Frontend for AI Apps)
1. Deploy it to a public URL for free, with a public `GET /health`, as in Deploying Your API. Protect your API key with a spending limit and the rate limit above.

#### The write-up

1. Write tests that need neither a network nor a model, with fakes and dependency overrides, for the core logic, the graders, the auth rules and the failure paths. (Testing with pytest, User Accounts and Auth)
1. Push your project to GitHub with a README that explains the problem, who it's for, how to run it, the live link, and what you learned. Include the design decisions that changed while you built it.

#### Evidence

- A GitHub Actions workflow runs `ruff check`, `ruff format --check` and `pytest` on every push (and `npm run build` if you built a TypeScript front end), and the latest run on `main` passes. Show its status badge at the top of the README. (Linting, Formatting and CI)
- Traces: every model call writes one trace, as a JSONL line or a database row, with a trace ID, the prompt version, the model, the input, the output, token counts and latency. Commit a sample of at least 20 traces with private data removed. (Why Evals Matter)
- A success-criteria table: each criterion from your brief, its target, the measured value with a 95% confidence interval and `n`, and whether you met it. Include the baseline's scores, and the prompt version the scores belong to. Report misses honestly; a clear "we missed the bar on photos, and here's why" is worth more than a vague pass. (Eval Statistics)
- Your judge's TPR and TNR with confidence intervals, if you used one.
- A before-and-after table for the change you made on purpose, with a paired confidence interval for the difference.
- A live link, a short GIF or video of the main flow, and a transcript against the deployed URL: `GET /health`, one real request, and the same request without a token getting `401`.
- Your measured cost per request (or per batch) from the traces' token counts, compared with the cost criterion in your brief. (Tokens, Cost and Rate Limits)

#### Extra credit

- Put a real user in front of it. Watch them use it without your help, write down where they got stuck, and fix the worst problem.
- Run your evals in GitHub Actions on every pull request, with your API key as a repository secret, and fail the build when a score drops below its bar. Link a failed run from a deliberately bad pull request. (Evaluating RAG and Catching Regressions)
- Compare two models on your success criteria and cost per request, and say which one you'd ship and why.
- Write a public post about the project, as in Learning in Public: the problem, the bar, and what it took to clear it.

</div>

### Submitting your work

A strong submission reads like a short case study. The first screen of the README states the problem and the user in one or two sentences, shows the live link and the CI badge, and puts the success-criteria table right there, met and missed. Below it, a reviewer finds the architecture, the design decisions that changed (from `DESIGN.md`), the baseline you had to beat, the failure categories you found and the change you made because of them.

Hiring managers see many chatbots built from tutorials. They rarely see someone who took a vague problem, defined what "good" meant with numbers, and showed honestly how close they got. In an interview, "the bar was 95% recall on urgent tickets, my first version got 81% with a confidence interval from 72% to 88%, and here's what I changed" is the kind of answer that gets you the next round. Keep this repo; you'll point to it often.
