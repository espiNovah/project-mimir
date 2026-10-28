<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

A language model remembers nothing between API calls. Everything it "knows" about the current task is whatever you send in the context window on each request. That is fine for a short chat, but an agent that works for hours, or that should remember a user's preferences next week, needs more. In this lesson you will learn the two kinds of memory agents use: **short-term memory** within a single task, and **long-term memory** that persists across tasks and sessions. You will also learn why "just keep everything" is the wrong answer.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why the context window is the agent's working memory.
- What short-term memory is, and how it grows during a task.
- Kinds of long-term memory: facts, past experiences and instructions.
- Ways to store and retrieve long-term memories.
- When to write memories: during the task or in the background.
- Why more context is not always better.

### Key ideas

- **The context window is working memory.** Short-term memory is the conversation history your loop sends on every turn: the goal, messages, tool calls and results. It is limited in size, it costs tokens every time it is sent, and it disappears when the task ends unless you save it.
- **Context is a finite resource with diminishing returns.** As the context grows, models get slower, more expensive and worse at finding the important details, a problem sometimes called "context rot." Good agents keep the *smallest* set of high-signal information they need, which is the core idea of context engineering, introduced in the Long Context and Context Engineering lesson.
- **Long-term memory lives outside the model.** You store it in files, a database or a vector store, and load the relevant parts into the context when needed. The model never "learns" these facts; your code retrieves them, using the same techniques as RAG.
- **There are three useful kinds of long-term memory.** *Semantic* memory holds facts ("the user prefers metric units," "the project uses PostgreSQL"). *Episodic* memory holds past experiences, such as how a similar task went last time. *Procedural* memory holds instructions and rules, such as an evolving system prompt.
- **Memory can be a tool.** Instead of your code deciding what to remember, you can give the agent tools to view, create and edit memory files, and let it manage its own notes. The MemGPT research project framed this like an operating system: a small "main memory" (the context) and a large "external memory" the agent pages information in and out of.
- **Writing memories has trade-offs.** Writing *in the hot path* (during the task) makes memories available immediately but adds latency and work for the agent. Writing *in the background* (after the task, or on a schedule) keeps the agent fast but means memories appear later.
- **Memory needs hygiene.** Stored facts go stale, conflict or include sensitive data. Decide what may be stored, how it gets updated or deleted, and keep each user's memory separate.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Effective context engineering for AI agents](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents) from Anthropic. It explains why context is a scarce resource and introduces the techniques the rest of this section builds on.
   - Read the whole article. Note the three techniques under "Context engineering for long-horizon tasks": compaction, structured note-taking and sub-agent architectures.
1. Read the LangChain [Memory overview](https://docs.langchain.com/oss/python/concepts/memory). It is a clear, framework-neutral explanation of short-term and long-term memory, and of semantic, episodic and procedural memory.
   - Skip the code samples; focus on the concepts and on "Writing memories."
1. Read the abstract and introduction of the [MemGPT paper](https://arxiv.org/abs/2310.08560), and look at its main diagram. Its idea of the agent managing its own memory tiers influenced many later systems.
1. Read "How it works" and "Security considerations" in the Claude [memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool) docs, an example of memory exposed as a tool the model calls.
1. Practice: add a `remember` tool and a `recall` tool to the agent from Project: Agent Loop From Scratch, backed by a single JSON file. Tell the agent a preference in one run ("I always want answers in bullet points"), then start a fresh run and check whether it recalls and applies it.

</div>
