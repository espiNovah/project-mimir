<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

A multi-agent system splits work between several model instances, each with its own instructions, tools and context window. The most common shape is an orchestrator, a lead agent that breaks a task into parts and hands each one to a subagent. Subagents work in parallel and return short summaries. Done well, this lets a system cover more ground than one context window can hold. Done badly, it multiplies cost and creates agents that work from different, conflicting assumptions. Practitioners disagree in public about when it is worth it, and this lesson has you read both sides.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The orchestrator-worker pattern applied to agents.
- Why subagents help: separate context windows and parallel work.
- Why they hurt: lost context, conflicting decisions and token cost.
- Writing good delegation instructions.
- Condensed results: what a subagent should send back.
- Subagents in the Claude Agent SDK.

### Key ideas

- **A subagent is a fresh context window.** The lead agent writes a task description, and the subagent starts with only that (plus its own system prompt and tools). It can read many pages or files and return a few hundred tokens of findings, which keeps the lead agent's context clean.
- **Parallel work pays off for broad, read-heavy tasks.** Research that branches into independent questions is the best case. Anthropic's research system beat a single agent on such tasks, but used several times more tokens. Multi-agent is a way to spend more tokens usefully, not a way to save them.
- **Parallel writers conflict.** When several agents make decisions, such as editing the same code or writing parts of one document, each one makes assumptions the others can't see. Cognition's "Don't Build Multi-Agents" argues for a single thread with full context for this reason. Keep subagents read-only, or give them tasks that truly don't overlap.
- **Delegation is a prompt-writing job.** Each subagent needs an objective, the output format, which tools and sources to use, clear boundaries and a budget. Vague tasks lead to duplicated or off-target work.
- **Return condensed, structured findings.** Ask for key facts with sources, not raw page dumps. For large outputs, have subagents write to files and return a pointer.
- **Scale effort to the task.** Simple questions need one agent and a few tool calls. Only spawn many subagents when the task is clearly broad. Put this rule in the orchestrator's prompt.
- **Evaluate the whole system.** Measure final quality, tokens and latency against a single-agent baseline. Without the baseline, you can't tell whether the extra agents helped.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read Anthropic's [How we built our multi-agent research system](https://www.anthropic.com/research/multi-agent-research-system).
   - Focus on the prompting principles for the lead agent, the token cost discussion and the evaluation section.
1. Read Cognition's [Don't Build Multi-Agents](https://cognition.com/blog/dont-build-multi-agents), then their follow-up [Multi-Agents: What's Actually Working](https://cognition.com/blog/multi-agents-working).
   - Write a paragraph on where the two companies actually disagree and where they agree once you account for the kinds of tasks they build for.
1. Read the [Claude Agent SDK subagents guide](https://code.claude.com/docs/en/agent-sdk/subagents).
   - Note how a subagent's tools are restricted and how its result returns to the parent.
1. Build a tiny orchestrator: a lead agent that splits a question into three sub-questions and runs three read-only subagents in parallel, each returning at most 200 words with sources. Compare its token use with one agent answering the same question.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Claude Code subagents](https://code.claude.com/docs/en/sub-agents) shows how a coding agent uses subagents to keep its main context clean.
