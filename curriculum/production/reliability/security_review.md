<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

You learned about prompt injection and secure design patterns in the Human-in-the-Loop and Safety section. Before you put an agent in front of real users, you need to check the whole system methodically, not just the parts you remember. A security review is that check: you walk through a known list of risks, decide which apply to your app, and write down what you did about each one. This lesson uses the OWASP Top 10 for LLM Applications as the checklist, plus the newer OWASP list for agentic applications.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What OWASP is and how to use its Top 10 lists as a checklist.
- Prompt injection defenses that work in practice.
- Sensitive data exposure and output handling.
- Excessive agency: limiting what tools and agents can do.
- Unbounded consumption and protecting your bill.
- Writing a security review document for your own app.

### Key ideas

- **OWASP lists are checklists, not theory.** OWASP is a nonprofit that publishes widely used security guidance. Its Top 10 for LLM Applications names the most common risks, such as prompt injection, sensitive information disclosure, improper output handling, excessive agency, system prompt leakage and unbounded consumption. The agentic list adds risks such as goal hijacking, tool misuse and identity abuse. For each item, write whether it applies, how you mitigate it, and how you tested that.
- **Assume prompt injection will happen.** Any text the model reads (a web page, an email, a retrieved document, a tool result) can contain instructions. No prompt reliably stops this, so defend in layers: keep untrusted content clearly separated and labeled in the prompt, give the agent the fewest tools and permissions it needs, require human approval for risky actions (sending, deleting, paying), and avoid the "lethal trifecta" of private data, untrusted content and a way to send data out, all in one agent.
- **Treat model output as untrusted input.** Never pass it straight into SQL, shell commands, `eval` or HTML. Validate it against a schema, escape it before rendering, and use parameterized queries.
- **Limit agency.** Scope API keys and database users to the minimum. Use allowlists for tools, domains and file paths. Run code execution in a sandbox, as in the Sandboxing Agents lesson.
- **Protect secrets and user data.** Keep keys in the host's secret store, don't put secrets in system prompts (assume the prompt will leak), and mask personal data in traces and logs.
- **Cap consumption.** Require authentication, add per-user rate limits, cap the number of agent steps and output tokens per request, and set a spend limit with your provider. Otherwise one script can run up your bill overnight.
- **Test your defenses.** Keep a set of attack prompts (from your Break Your Own Agent project) in your eval suite so a future change can't quietly reopen a hole.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/) and open each of the ten risk pages.
   - For each one, write one sentence on whether it applies to an agent you've built.
1. Read the [OWASP entry on prompt injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) closely, especially its prevention and mitigation strategies.
1. Read the [OWASP Top 10 for Agentic Applications (2026)](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) for the risks specific to agents that use tools and act on their own.
   - Focus on the risks that the LLM list doesn't already cover.
1. Reread Simon Willison's [The lethal trifecta for AI agents](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) and check whether any agent you've built combines all three ingredients.
1. Practice: write a one-page security review for your Workflow Automation Agent.
   - Make a table with one row per OWASP LLM Top 10 item: applies (yes or no), mitigation, and how you tested it.
   - Add at least three attack prompts to the agent's eval set and record whether they succeed.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Mitigating jailbreaks and prompt injections](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks) in the Claude docs gives concrete techniques such as harmlessness screens and input validation.
- [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) is a good reminder that the simplest design is usually the easiest one to secure.
