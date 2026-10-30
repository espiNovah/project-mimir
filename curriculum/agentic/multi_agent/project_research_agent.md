### Introduction

In this project you will build a web research agent that answers a question with a cited Markdown report, and then build it a second time as a multi-agent system. You'll run both on the same ten questions and measure which is better on citation accuracy, token use and speed.

The single-agent version plans sub-questions, searches, reads pages, keeps notes in a file outside its context window and writes the report within a step and cost budget. The multi-agent version uses an orchestrator that plans and writes, plus three read-only subagents that research in parallel and send back condensed findings. By the end you'll have your own evidence on the most argued-about design question in agent building: when are many agents worth it?

This builds on "The Agent That Remembers" (notes outside the context window) and on citations and grounding from the RAG section.

### Before you start

- Create a GitHub repository named `mimir-research-agent`.
- Pick a search and fetch approach. Options include the Claude [web search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool) and [web fetch tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool) (Claude features that run on Anthropic's servers; other providers offer their own), a search API with a free tier, or your own MCP server. Use the same tools in both versions. Whichever you choose, you'll also need a fetch function that runs on your own machine for the injection test.
- Choose any framework or your own loop. The Claude Agent SDK's subagents and the OpenAI Agents SDK both work well here.
- Write ten research questions in `questions.json` before you write any code. Mix narrow factual questions (one or two sources needed) with broad ones (many angles, for example "compare the main approaches to X"). Writing them first keeps you from choosing questions that flatter one design.
- Read your API keys from environment variables. Never commit them.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Build the single-agent version. Given a question, it should:
   - write a short plan of sub-questions to a `notes.md` file,
   - search and read pages, appending key facts with their source URLs to the notes file instead of keeping full pages in context,
   - write a final Markdown report in which every factual claim has a citation link to a page it actually read,
   - stop when it hits a step budget (for example, 30 tool calls) or a cost budget (for example, $0.50), and say in the report if it stopped early.
1. Build the multi-agent version:
   - an orchestrator that plans the sub-questions and writes the final report,
   - three subagents that run in parallel, each assigned one or more sub-questions,
   - subagents are read-only: they can search and fetch, but cannot write the report or each other's notes,
   - each subagent returns condensed findings (for example, at most 300 words) as a list of facts with source URLs,
   - the same total step and cost budget as the single-agent version, shared across all agents.
1. Write a citation checker. For each citation in a report, fetch the cited page and check that it supports the claim, using an LLM judge with a clear rubric (supported, partly supported, not supported), as in Citations and Grounding and Code Checks and LLM-as-Judge. Spot-check at least 20 of the judge's verdicts by hand and report how often you agreed with it.
1. Trace every run, as in Agent Tracing and Debugging. Give each subagent's spans a parent: the span of the delegation that started it, so you can see which delegation produced which finding.
1. Run both versions on all ten questions and record for each run: citation accuracy (share of citations judged supported), number of citations, total tokens, cost, wall-clock time and whether a budget was hit.
1. Put the results in a table in your README, broken down by narrow versus broad questions.
1. Write a one-page analysis called "When multi-agent was worth it". Use your numbers to say which kinds of questions benefited, which didn't, what the extra tokens bought you, and one failure that happened only in the multi-agent version.
1. Test both versions against a malicious web page. Write a page you serve yourself on `localhost` (for example with `uv run python -m http.server 8000` in a folder of test pages) that looks like a normal source for one of your questions but hides instructions in text a reader wouldn't see, such as an HTML comment or a hidden `div`. Give it two goals: make the report state a specific false claim that you can search for, and make the agent fetch a URL on a second local server (the logging server) with its notes in the query string. Hosted search won't find your page and hosted fetch tools can't reach your laptop, so for these runs make your search tool return the page as one of its results, and read it with a fetch function that runs on your machine. Run each version five times.
1. Push your project to GitHub with a README that explains what it does, how to run both versions and the evaluation, and what you learned.

#### Evidence

Your README must show:

- A passing GitHub Actions badge, and a workflow that runs `ruff check`, `ruff format --check` and `pytest` on every push. Pytest covers, with fakes and without calling a model or the web: pulling claims and cited URLs out of a report, the shared budget stopping every agent once it's used up, and the subagents' tool lists containing no tool that writes. (Linting, Formatting and CI)
- Traces: one committed trace per version for the same broad question, in which every subagent span has the delegation span that started it as its parent, plus the raw results file with one row per run. (Agent Tracing and Debugging, Subagents and Orchestration)
- The judge's quality on your hand labels: the agreement rate on at least 20 verdicts, and its TPR and TNR with confidence intervals, treating "not supported" as the failure the judge must catch, as in Code Checks and LLM-as-Judge. If you have fewer than five labels in a class, say so instead of reporting a rate for it.
- The results table: citation accuracy for each version with a 95% confidence interval, bootstrapped over the ten questions (Eval Statistics), and the difference between the versions with a paired bootstrap interval over the same questions. Next to these, the tokens, cost, wall-clock time and budget hits for each version, all split into narrow and broad questions. Ten questions gives wide intervals, so say plainly when the interval for the difference includes zero.
- The prompt-injection test: for each version and each goal, how many of the five runs the attack worked, detected from the environment (a request in the logging server's log, or the planted false claim appearing in the report), never from what the agent says. For the multi-agent version, say from the traces where the attack went: did it stay inside one subagent's findings, or did it reach the orchestrator and the report? If the leak worked even once, make a structural fix in code, such as letting the fetch tool open only URLs that came back from the search tool, never URLs the model built, and show the rerun. (Prompt Injection and the Lethal Trifecta)

#### Extra credit

- Make the orchestrator decide how many subagents to start (zero to five) based on the question, and compare it with the fixed design.
- Run each question three times per version and report how much the results vary.
- Add a final "fact-check" subagent that rereads the report against the notes before it's returned, and measure whether citation accuracy improves.

</div>

### Submitting your work

A strong submission includes the ten questions, every generated report, the raw results file, the comparison table and the injection results, so a reviewer can check any number. Show one report side by side from each version for the same broad question. Your analysis should reach a clear conclusion and be honest about its limits: ten questions is a small sample, and saying so is a sign of good judgment, not weakness.
