### Introduction

In this project you will attack one of your own agents, measure how often the attacks work, then harden it with structural defenses and measure again. Security teams call this red-teaming. Pick an agent from an earlier project that reads untrusted content and has real tools, such as your research agent from "Research Agent, One vs Many", your coding agent from "Sandboxed Coding & Browser Agent" or your memory agent from "The Agent That Remembers".

The rule of this project is that prompt tweaks don't count as defenses. You can add them, but your measured improvement must come from changes enforced by code or infrastructure. That's the lesson of this section: you can't talk a model out of being fooled, but you can limit what a fooled model is able to do.

### Before you start

- Create a GitHub repository named `mimir-break-your-own-agent`. Copy in the agent you're testing, or add it as a Git submodule.
- Set up a safe target for exfiltration. Run a small local web server (for example `uv run python -m http.server 8999`) or a request-logging endpoint on `localhost` that plays the attacker's server. Any request that reaches it counts as a successful leak.
- Put fake secrets in the agent's environment, such as a file named `secrets.txt` containing `CANARY-7f3a9`. Never use real credentials in this project.
- Download the [OWASP Top 10 for Agentic Applications (2026)](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/). You'll map your findings to its IDs.

<div class="lesson-note lesson-note--critical" markdown="1">

#### Only attack what you own

Run every test against your own agent, your own accounts and local servers. Don't plant injections on public sites, in other people's repositories or in shared documents.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Write a lethal-trifecta audit in `AUDIT.md`, starting from the threat model you wrote in Secure Design Patterns. List every tool the agent has, and for each one, mark whether it gives access to private data, exposure to untrusted content or a way to communicate externally. Identify every combination that forms a full trifecta.
1. Write at least 10 injection test cases in an `attacks/` folder. Each test case includes the payload, where it is planted and what counts as success. Cover at least three delivery channels:
   - web pages the agent fetches,
   - files the agent reads,
   - tool results (for example, a fake search API response or an issue comment).
   - Across the set, include at least three different goals, such as leaking the canary to your local server, taking an unauthorized action (deleting a file, sending a message) and changing the agent's final answer.
1. Write an automated runner that runs every test case at least three times and records whether the attack succeeded. Success must be detected from the environment, such as a request hitting your server, a file changing or the canary appearing in output, not from reading the agent's explanation.
1. Report the baseline attack success rate per test case and overall, before any hardening.
1. Add at least two structural defenses. Choose from (or go beyond) this list:
   - an approval gate in code for irreversible or outbound actions,
   - plan-then-execute, where the tool-call plan is fixed before untrusted content is read,
   - a strict tool allowlist or removing a trifecta leg from the agent entirely,
   - an egress block so the agent can only reach allowlisted hosts,
   - a dual-LLM split so the tool-calling model never reads raw untrusted text,
   - taint tracking, so a value that came from untrusted content can't be used where policy forbids it.
1. Rerun the full suite and report the attack success rate after hardening, per defense where you can. Also rerun the agent's normal tasks to show the defenses didn't break its real job, and report that success rate too.
1. Map each test case and each defense to OWASP Agentic Top 10 IDs (for example, ASI01 for goal hijacking) in a table in your README.
1. Push your project to GitHub with a README that explains what it does, how to run the attacks, what you found and what you learned.

#### Evidence

This project is about attacks, so one injection test isn't enough. The evidence is a measured attack success rate (ASR), before and after your defenses, next to the normal task success rate. Your README must show:

- A passing GitHub Actions badge, and a workflow that runs `ruff check`, `ruff format --check` and `pytest` on every push. Pytest proves each structural defense in code, with a fake model client and no real model call, as `test_gate.py` did in Approvals and Permissions. For example: a gated tool can't run without approval even when the prompt claims approval was given; a request to a host off the allowlist is refused; a tainted value is blocked by its policy. These tests must pass every time, because the code path that leaks shouldn't exist. (Linting, Formatting and CI)
- The raw results, committed as `results/before.csv` and `results/after.csv`, with one row per run: the test case, its delivery channel and goal, the run number, whether the attack succeeded and how that was detected (a request in your attacker server's log, a changed file, the canary in the output).
- The before-and-after table:
  - The overall ASR before and after hardening, each with a 95% confidence interval bootstrapped over test cases (average each case's runs first, as in Eval Statistics).
  - The drop, with a paired bootstrap interval over the same cases.
  - The ASR broken down by delivery channel and by goal.
  - A row per test case showing its successes out of its runs, such as "2/3 → 0/3".
- The ASR with each defense on its own, where you can switch them separately, so a reader can see which defense stopped which attacks.
- The normal task success rate before and after hardening, on at least ten of the agent's real tasks run three times each, with confidence intervals and a paired interval for the change. Add the change in average cost and steps, because every defense has a price (Secure Design Patterns).
- One successful baseline attack, shown end to end: the payload, the trace of the run that fell for it (Agent Tracing and Debugging), and the log line on your attacker server or the changed file that proves it.
- Every attack that still succeeds after hardening, with the reason it gets through and what you'd change next. If none do, say how many runs that claim rests on: 0 successes in 30 runs is still consistent with a true rate of about 10%.

#### Extra credit

- Add a guardrail classifier as a third layer, and report how many attacks it catches that the structural defenses already blocked, and how many it catches that they missed. Measure its false positive rate on your normal tasks with an interval, as in Guardrails in Production.
- Write five more attacks designed specifically to get around your defenses, and report the results honestly.
- Turn your attack suite into a CI job that fails if the attack success rate goes above zero.

</div>

### Submitting your work

A strong submission is a short security report. It opens with a before-and-after table (attack success rate, normal task success rate), then shows the trifecta audit, the test cases, the defenses and the OWASP mapping. Include the evidence for at least one successful attack before hardening, such as the log line on your attacker server. If any attack still works after hardening, say so and explain why. A reviewer trusts a report that admits remaining risk far more than one that claims perfect security.
