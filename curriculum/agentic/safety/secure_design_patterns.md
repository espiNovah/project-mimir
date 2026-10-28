<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

You can't make a model immune to prompt injection, but you can design the system around it so that a fooled model can't do much damage. This lesson covers structural defenses, meaning things enforced by your code and infrastructure rather than by asking the model nicely. It also covers the habits of responsible deployment: rolling an agent out gradually and keeping the ability to see and stop what it does.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Least privilege: the fewest tools and narrowest permissions that do the job.
- Sandboxing and egress control as security boundaries.
- Design patterns that constrain what an agent can do after reading untrusted input.
- Input and output guardrails, and what they can't do.
- Defense in depth for browser and coding agents.
- Responsible deployment: staged rollout, monitoring and a kill switch.

### Key ideas

- **Least privilege comes first.** Give each agent only the tools its task needs, scoped as narrowly as possible: read-only database access, one folder, one email recipient, one API with a limited token. Every tool you remove is an attack that can't happen.
- **Break the trifecta structurally.** Block outbound network traffic except allowlisted hosts, keep secrets out of the agent's reach, or keep untrusted content away from agents that hold private data. These are enforced by your system, not the model.
- **Plan then execute.** Have the agent commit to a plan of tool calls before it reads any untrusted content. Content read later can change the details, but can't add new actions to the plan.
- **Separate the privileged and the quarantined.** In the dual-LLM pattern, a privileged model that can call tools never sees untrusted text directly. A quarantined model reads that text and returns only constrained values, such as a label or a variable, that the privileged model handles without reading. Other patterns from the same paper include action selectors, map-reduce over untrusted documents and context minimization.
- **Guardrails are useful tripwires.** Input and output checks, such as a small classifier that flags injected instructions or blocks a response containing secrets, catch many attacks and are cheap to add. Never rely on them alone.
- **Watch the actions, not just the words.** Log every tool call, alert on unusual ones and have a classifier or rules review risky actions before they run. Anthropic's Claude Code auto mode works this way.
- **Deploy responsibly.** Start with read-only or draft-only access, roll out to a few users, monitor real traces, keep a kill switch that disables tools instantly, and tell users plainly what the agent can and can't do.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Design Patterns for Securing LLM Agents against Prompt Injections](https://arxiv.org/abs/2506.08837).
   - Read the introduction and the section describing the six patterns. Skim the case studies.
   - For each pattern, write one sentence on which of your past projects it would fit.
1. Read Anthropic's [Mitigating prompt injection in browser use](https://www.anthropic.com/research/prompt-injection-defenses) to see layered defenses in a real product.
1. Read [How we built Claude Code auto mode](https://www.anthropic.com/research/claude-code-auto-mode) for an example of reviewing actions before they run.
1. Read the [OpenAI Agents SDK guardrails docs](https://openai.github.io/openai-agents-python/guardrails/).
   - Note the difference between input and output guardrails, when each one runs and what happens when one trips.
1. Take an agent you've built and write a one-page threat model: its tools, which ones form a trifecta and two structural changes that would break it.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Simon Willison's write-up of CaMeL](https://simonwillison.net/2025/Apr/11/camel/) explains a research design that separates control flow from untrusted data.
