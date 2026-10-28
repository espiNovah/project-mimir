<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Modern models can read hundreds of thousands of tokens at once. That does not mean you should stuff everything in. What you put in the context window, and where you put it, has a large effect on quality, cost and speed. This shift in thinking, from crafting the perfect sentence to curating the right information, is called *context engineering*. It is the skill that separates toy demos from systems that work, and it underpins RAG, memory and agents later in the curriculum.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What context engineering is and how it extends prompt engineering.
- How to structure long documents inside a prompt.
- Where to place instructions and questions relative to long material.
- Why more context can make answers worse.
- How prompt caching makes reused context cheaper and faster.
- How to think of context as a limited budget.

### Key ideas

- **Context is everything the model sees.** The system prompt, conversation history, retrieved documents, tool definitions and tool results all compete for the same window. Context engineering is deciding which of those tokens earn their place on each call.
- **Attention is a budget, not a bucket.** Research shows models use information unevenly: facts buried in the middle of long inputs are found less reliably ("lost in the middle"), and quality tends to drop as inputs grow ("context rot"). The goal is the smallest set of high-signal tokens that gets the job done.
- **Put long documents first and the question last.** For long inputs, place the documents near the top of the prompt and your instructions and question at the end. Wrap each document in tags with metadata, such as `<document><source>…</source><content>…</content></document>`, so the model can tell them apart and refer to them.
- **Ask the model to quote before it answers.** For long-document tasks, have the model first pull out the relevant quotes into tags, then answer from those quotes. This cuts through noise and makes the answer easier to check.
- **Fewer, better tokens beat more tokens.** Trim boilerplate, deduplicate, summarize old conversation turns, and retrieve only the relevant passages. Retrieval (the RAG section) and compaction (the Memory section) are both context engineering tools.
- **Prompt caching rewards stable prefixes.** Providers can cache the start of a prompt that repeats across calls, which cuts cost and latency for reused content like a long system prompt or reference document. Put stable content first and changing content last to benefit.
- **Know your limits.** Every model has a maximum context size and an output limit. Check the numbers for the model you use, and measure what long inputs cost you in tokens and seconds.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Effective context engineering for AI agents](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents) by Anthropic.
   - Read the whole post. Do not worry if the agent-specific parts feel abstract; you will return to them in the Memory section.
1. Read the long-context section of [Anthropic's prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices).
   - Note the advice on document placement, XML structure and quoting.
1. Read [Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows) in the Claude docs to understand how input, output and thinking tokens share the window.
1. Skim [Context Rot](https://research.trychroma.com/context-rot) by Chroma research.
   - Read the introduction and look at the charts. The takeaway: performance drops as input length grows, even on simple tasks.
1. Practice: take a long document (a 30+ page PDF converted to text, or a long Wikipedia article). Ask the same five questions twice: once with the question before the document, once after, with the document wrapped in tags. Record which answers were correct and how many input tokens each call used (the API response's `usage` field tells you).

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172) is the research paper behind the "middle of the context is weakest" finding.
- [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) in the Claude docs explains how to mark cacheable prefixes. You will use it seriously in the Cost and Latency section.
