<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Not everything has an API. Many tasks still happen in web pages and desktop apps: filling in a form, checking that a page renders, clicking through an old admin panel. Browser and computer-use agents operate these interfaces directly. They either read a structured description of the page (an accessibility snapshot) or look at screenshots, then click, type and scroll. This lesson explains both approaches, when to use which, and why these agents need extra care.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Scripted browser automation with Playwright, and when you don't need an agent at all.
- Accessibility snapshots versus screenshots as the agent's view of a page.
- Driving a browser through Playwright MCP.
- Model-provided browser and computer-use tools.
- Why these agents are slower, costlier and less reliable than API-based ones.
- The extra security risks of agents that read arbitrary web pages.

### Key ideas

- **Script it if you can.** If the steps are known in advance, a plain Playwright script is faster, cheaper and deterministic. Use an agent when the page or the task varies too much to script.
- **Snapshots are text, screenshots are pixels.** An accessibility snapshot lists the page's elements (buttons, links, fields) with their roles and labels, so a text model can act on them precisely and cheaply. Screenshots work on anything visible, including desktop apps and canvas-heavy pages, but need a vision model and cost more tokens per step.
- **Playwright MCP gives any MCP client a browser.** It exposes actions such as navigate, click, type and snapshot as MCP tools, using accessibility snapshots by default. This is often the quickest way to add browsing to an agent you already have.
- **Computer use is the most general and the most fragile.** The model receives screenshots and returns mouse and keyboard actions with screen coordinates. Your code carries out each action in a virtual display and sends back a new screenshot. Run it in a VM or container, never on your main desktop.
- **Every step is a chance to drift.** Pages load slowly, pop-ups appear, layouts change. Keep step budgets, wait for elements explicitly, and verify the end state, such as "the confirmation text is visible", rather than trusting the agent's claim.
- **Every page is untrusted input.** A web page can contain hidden text telling the agent to do something else. Browser agents are a prime target for prompt injection, which the safety section covers in depth. Limit which sites they can visit and require approval for purchases, submissions or messages.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Work through the [Playwright for Python](https://playwright.dev/python/) getting started pages, from installation through writing and running your first test.
   - Install it with `uv add playwright` and then `uv run playwright install chromium`.
1. Read the README of [Playwright MCP](https://github.com/microsoft/playwright-mcp).
   - Connect it to an MCP client you used in the MCP section, and ask the agent to open a page and report its main heading.
1. Read the Claude docs on the [browser use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool) and the [computer use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool).
   - Focus on how the action loop works and on the security considerations sections.
1. Read Anthropic's [Mitigating prompt injection in browser use](https://www.anthropic.com/research/prompt-injection-defenses) to see why browsing agents need layered defenses.
1. Do the same small task three ways: a Playwright script, an agent with Playwright MCP, and (optionally) computer use in a container. Record time, tokens and success over five runs each.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [OpenAI's computer use guide](https://developers.openai.com/api/docs/guides/tools-computer-use) shows the same idea with another provider's API.
