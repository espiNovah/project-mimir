<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

"Design a customer-support agent for our product" is now one of the most common prompts in AI engineering interviews. There's no single right answer. The interviewer wants to see how you structure an open-ended problem, which tradeoffs you notice, and whether you think about evaluation, safety and cost without being prompted. You've built every piece of this system somewhere in the curriculum. This lesson teaches you to assemble them out loud, in 45 minutes.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- A repeatable structure for a 45-minute AI system design interview.
- Clarifying requirements and defining success metrics.
- Choosing between a workflow, a single agent and multiple agents.
- Designing the core architecture: retrieval, tools, memory and model choice.
- Evals, guardrails and human escalation.
- Cost, latency and scaling estimates.
- Communicating tradeoffs clearly.

### Key ideas

- **Use a time-boxed structure.** Roughly: clarify requirements (5 minutes), define success metrics (5), sketch the high-level architecture (10), go deep on two or three components (15), then cover evals, safety, cost and what you'd do next (10). Say the structure out loud at the start.
- **Clarify before designing.** Who are the users? What channels? What can the agent do (answer questions, look up orders, issue refunds)? What volume? What happens when it's wrong? Requirements drive every later choice.
- **Define success with numbers.** Resolution rate without human handoff, answer accuracy on a test set, customer satisfaction, cost per conversation, and response latency. Name how you'd measure each.
- **Start with the simplest design that could work.** Often that's a router plus retrieval plus a small set of well-designed tools, as in Workflows vs Agents. Add agentic loops or multiple agents only where the problem needs them, and explain why.
- **Treat evals as part of the design, not an afterthought.** An offline test set built from real tickets, code checks and LLM-as-judge for answer quality, tracing in production, and turning failures into new test cases, as you did in From Traces to Evals.
- **Design for safety and escalation.** Prompt injection from customer messages, least-privilege tools, human approval for refunds or account changes, PII handling, and a clean handoff to a human agent with context.
- **Do the cost math.** Estimate tokens per conversation, multiply by volume and price, and show how caching, smaller models for easy routes, and batching bring it down. Interviewers notice when you can do this on the spot.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Chip Huyen's Building A Generative AI Platform](https://huyenchip.com/2024/07/25/genai-platform.html), which walks through the components of a production generative AI system step by step.
   - Use it as a checklist of components to mention: context construction, guardrails, model routing, caching, and observability.
1. Read [Eugene Yan's Patterns for Building LLM-based Systems and Products](https://eugeneyan.com/writing/llm-patterns/) for the vocabulary of patterns interviewers expect.
   - Focus on the sections on evals, guardrails, defensive UX and collecting user feedback.
1. Reread [Anthropic's Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) and practice explaining, in two minutes, when you'd choose a workflow over an agent for customer support.
1. Do one untimed practice design of a support agent for a product you know well. Write it up on one page with a diagram, covering requirements, metrics, architecture, evals, safety and cost. You'll do a timed version in Project: Mock Interview Loop.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The System Design Primer](https://github.com/donnemartin/system-design-primer) is the classic free guide to general system design (load balancers, caches, databases), which many interview loops still include alongside AI design.
- [What We've Learned From A Year of Building with LLMs](https://applied-llms.org/) is full of practical lessons that make strong talking points in design interviews.
