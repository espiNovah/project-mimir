<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Once you know how function calling works, the hard part is no longer the plumbing. It is designing tools the model actually uses well. A tool with a vague name, a confusing schema or a huge, noisy output will make even a strong model stumble. In this lesson you will learn to treat tools as an interface for a new kind of user: one that is smart, literal and has a limited attention span.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why tools for agents are different from APIs for programmers.
- Choosing which tools to build, and which to merge or leave out.
- Writing names, descriptions and parameters the model understands.
- Designing tool outputs that are small, relevant and readable.
- Testing and improving tools with evaluations.

### Key ideas

- **Tools are a contract with a non-deterministic user.** A programmer reads documentation once and writes code that calls an API the same way every time. A model decides afresh on every turn, from the description alone. Design for that reader.
- **Fewer, higher-level tools usually beat many thin wrappers.** Instead of `list_users`, `list_events` and `create_event`, an agent often does better with a single `schedule_event` tool that finds availability and books it. Each tool should match a task a person would actually ask for.
- **Names and descriptions do most of the work.** Use clear, unambiguous names, and namespace related tools (for example, `github_search_issues`, `github_create_issue`). Write descriptions the way you would explain the tool to a new teammate: what it does, when to use it, when not to, and what each parameter means, with an example.
- **Parameters should be hard to misuse.** Use specific names like `user_id` rather than `user`, enums for fixed choices, and sensible defaults. Some providers can also enforce your schema strictly, so the model's arguments always validate.
- **Return what the agent needs, not everything you have.** Prefer human-readable fields (names, not opaque IDs), paginate or truncate large results, and offer a `concise` versus `detailed` response option. Every token a tool returns stays in the context window for the rest of the task.
- **Errors are part of the interface.** A good error message says what went wrong and what to try next. You will practice this in the next lesson.
- **Improve tools with evals, not guesses.** Write realistic tasks, run the agent on them, read the transcripts, and change the tool where the agent got confused. You can even ask a model to review your tool descriptions against those transcripts.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Writing effective tools for agents](https://www.anthropic.com/research/writing-tools-for-agents) from Anthropic. This is the core reading for the lesson, and the Project: Agent Loop From Scratch and Project: Your Own MCP Server both expect you to follow its advice.
   - Read the whole article. Take notes on the "Principles for writing effective tools" section in particular.
1. Read "Appendix 2: Prompt engineering your tools" at the end of [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents). It is short and gives concrete advice, including the idea of "poka-yoke" (mistake-proofing) your tool arguments.
1. Read "Best practices for tool definitions" in [Define tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools), and skim [Strict tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use) to see how a schema can be enforced.
1. Practice: take the `get_word_length` tool from the previous lesson, or any tool you have written, and rewrite its definition using what you learned. Then write a deliberately bad version (vague name, one-line description, unclear parameter). Run both on the same five questions and record how often the model calls each one correctly.

</div>
