<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

A demo agent has three tools. A real one connected to email, a calendar, a CRM and a few internal systems can easily have a hundred. Every tool definition takes up space in the context window on every request, and every tool result passes through the model even when only one line of it matters. This lesson covers the techniques that let agents work with large toolsets without drowning in tokens: loading tools only when they are needed, and letting the model call tools from code.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why large toolsets hurt both cost and accuracy.
- Tool search: discovering tool definitions on demand instead of loading them all.
- Programmatic tool calling: letting the model write code that calls your tools.
- Tool use examples: showing the model how a tool should be called.
- How to decide when these techniques are worth the extra complexity.

### Key ideas

- **Tool definitions cost tokens on every call.** Fifty detailed tools can consume tens of thousands of tokens before the user has said anything. Large menus also make the model more likely to pick the wrong tool or invent parameters.
- **Tool search defers loading.** You mark most tools as deferred and give the model a search tool. It starts with only a few definitions and searches for the rest when it needs them, much like a person looking up a function in documentation. Use it when you have many tools, not five.
- **Every tool result passes through the context window.** In a normal loop, if the agent fetches 1,000 rows to find three, all 1,000 rows land in its context. That costs tokens and can push out more important information.
- **Programmatic tool calling moves the work into code.** Instead of one model round trip per tool call, the model writes a short script that calls your tools as functions, loops over results, filters them and returns only the summary. The intermediate data never enters the context window. This is faster and cheaper for multi-step data work.
- **The same idea applies to MCP.** You will see the "code execution with MCP" pattern in the Model Context Protocol section: presenting tools as code the agent can import, rather than as a long list of definitions.
- **Examples teach usage that schemas cannot.** A JSON Schema says which fields exist but not which combinations make sense. A few example calls attached to a tool show the model conventions like date formats or when to include optional fields.
- **These are optimizations, not defaults.** Add them when you can measure a problem: too many tokens per request, wrong tool choices, or slow multi-step workflows.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Introducing advanced tool use](https://www.anthropic.com/research/advanced-tool-use) from Anthropic (November 2025). It explains tool search, programmatic tool calling and tool use examples, and when to use each.
1. Read "How tool search works" and "When to use tool search" in the [Tool search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool) docs.
1. Read the introduction and "How programmatic tool calling works" in the [Programmatic tool calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling) docs.
   - Look at the budget-checking example and count how many model round trips it saves.
1. Practice: count the tokens your tool definitions use. Take the tools from your previous practice exercises, send a request with and without them using the [token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting) endpoint, and write down the difference. Multiply it by 50 tools to see why these techniques exist.

</div>
