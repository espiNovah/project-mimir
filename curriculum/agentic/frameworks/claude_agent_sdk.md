<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

In the "Agent Loop From Scratch" project you wrote every piece of an agent yourself: the `while` loop, the tool dispatch, the message history, the stop condition. That was the right way to learn. But production agents need much more than that loop, such as file and shell tools, permission checks, context compaction, subagents and session resumption. The Claude Agent SDK packages the same harness that powers Claude Code as a Python (and TypeScript) library, so you get all of that without writing it again.

This lesson shows you what the SDK does for you, which parts of your hand-built loop map onto it, and where you still have to make the decisions.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What an agent harness is, and how the Claude Agent SDK relates to Claude Code.
- How the SDK's loop maps onto the loop you wrote by hand.
- Built-in tools versus custom tools you register yourself.
- Permission modes, allowed tools and hooks as control points.
- Sessions, context compaction and subagents provided out of the box.
- When the SDK is the wrong fit compared to calling the Messages API directly.

### Key ideas

- **A harness is everything around the model.** The model only decides the next step. The harness runs tools, enforces permissions, manages context and decides when to stop. The Agent SDK is Claude Code's harness exposed as a library, so `query()` starts a full agent loop, not a single API call.
- **Your hand-built loop is still inside.** The SDK still sends messages, receives tool-use requests, runs tools and appends results. You now consume a stream of messages (assistant text, tool calls, results, and a final result with cost and turn counts) instead of writing the loop.
- **Built-in tools come first.** File reading and editing, shell commands, search and web fetch are already there. You add your own tools as in-process MCP tools, which reuses what you learned in the MCP section.
- **Control lives in options, not prompts.** Allowed and disallowed tool lists, permission modes, a working directory, a maximum number of turns and a system prompt are configuration. Hooks let your code run before or after a tool call to log it, block it or change it.
- **Context is managed for you, but not for free.** Automatic compaction and subagents keep long tasks inside the context window. You still pay in tokens, and you still need to know what got summarized away when a run goes wrong.
- **Give the agent a computer, then constrain it.** The SDK's design idea is that agents work best with the same tools a person uses at a terminal. The price is that you must sandbox it and scope its permissions, which later sections cover.
- **Reach for the raw API when you need total control.** A tiny, single-purpose tool loop, a non-Claude model or an unusual control flow can be simpler without a harness.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [Claude Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview) to see what the SDK includes and how it relates to Claude Code.
   - Note which capabilities (tools, permissions, sessions, subagents, hooks, MCP) map to code you wrote by hand in "Agent Loop From Scratch".
1. Read Anthropic's article [Building agents with the Claude Agent SDK](https://claude.com/resources/articles/building-agents-with-the-claude-agent-sdk) for the design reasoning behind the SDK.
   - Focus on the "gather context, take action, verify work" loop. You will see it again in coding agents and evals.
1. Work through the [Agent SDK quickstart](https://code.claude.com/docs/en/agent-sdk/quickstart) and build a small agent with it.
   - Install the SDK with `uv add claude-agent-sdk` in a new project and read your key from `ANTHROPIC_API_KEY`.
   - Print every message in the stream so you can see each tool call and the final cost.
1. Skim the [Agent SDK permissions guide](https://code.claude.com/docs/en/agent-sdk/permissions) and the [Python SDK reference](https://code.claude.com/docs/en/agent-sdk/python).
   - Restrict your quickstart agent to read-only tools, then ask it to edit a file. Write down what happens.
1. Port one tool from "Agent Loop From Scratch" into the SDK as a custom tool and compare how many lines each version takes.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Building effective agents](https://www.anthropic.com/research/building-effective-agents) is a reminder that many problems need a workflow, not a full harness.
