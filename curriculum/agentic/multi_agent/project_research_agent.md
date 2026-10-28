### Introduction

In this project you will build a web research agent that answers a question with a cited Markdown report, and then build it a second time as a multi-agent system. You'll run both on the same ten questions and measure which is better on citation accuracy, token use and speed.

The single-agent version plans sub-questions, searches, reads pages, keeps notes in a file outside its context window and writes the report within a step and cost budget. The multi-agent version uses an orchestrator that plans and writes, plus three read-only subagents that research in parallel and send back condensed findings. By the end you'll have your own evidence on the most argued-about design question in agent building: when are many agents worth it?

This builds on "The Agent That Remembers" (notes outside the context window) and on citations and grounding from the RAG section.

### Before you start

- Create a GitHub repository named `mimir-research-agent`.
- Pick a search and fetch approach. Options include the Claude [web search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool) and [web fetch tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool), a search API with a free tier, or your own MCP server. Use the same tools in both versions.
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
1. Write a citation checker. For each citation in a report, fetch the cited page and check that it supports the claim, using an LLM judge with a clear rubric (supported, partly supported, not supported). Spot-check at least 20 of the judge's verdicts by hand and report how often you agreed with it.
1. Run both versions on all ten questions and record for each run: citation accuracy (share of citations judged supported), number of citations, total tokens, cost, wall-clock time and whether a budget was hit.
1. Put the results in a table in your README, broken down by narrow versus broad questions.
1. Write a one-page analysis called "When multi-agent was worth it". Use your numbers to say which kinds of questions benefited, which didn't, what the extra tokens bought you, and one failure that happened only in the multi-agent version.
1. Push your project to GitHub with a README that explains what it does, how to run both versions and the evaluation, and what you learned.

#### Extra credit

- Make the orchestrator decide how many subagents to start (zero to five) based on the question, and compare it with the fixed design.
- Run each question three times per version and report how much the results vary.
- Add a final "fact-check" subagent that rereads the report against the notes before it's returned, and measure whether citation accuracy improves.

</div>

### Submitting your work

A strong submission includes the ten questions, every generated report, the raw results file and the comparison table, so a reviewer can check any number. Show one report side by side from each version for the same broad question. Your analysis should reach a clear conclusion and be honest about its limits: ten questions is a small sample, and saying so is a sign of good judgment, not weakness.
