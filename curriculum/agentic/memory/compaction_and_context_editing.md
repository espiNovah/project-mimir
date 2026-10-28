<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Every turn of an agent loop adds to the conversation: the model's reasoning, tool calls and, above all, tool results. A long task can fill even a very large context window, and well before it does, quality and cost start to suffer. This lesson covers the two main ways to keep a long-running conversation inside the window: **compaction**, which replaces older history with a summary, and **context editing**, which removes specific content, like stale tool results, that the agent no longer needs.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why agent conversations grow so quickly, and what that costs.
- Measuring context size with token counts.
- Compaction: summarizing older turns to free up space.
- Choosing when to compact, and what a good summary keeps.
- Context editing: clearing old tool results and thinking.
- How these techniques interact with memory and prompt caching.

### Key ideas

- **Tool results are usually the biggest cost.** A single file read or search result can be thousands of tokens, and every one of them is resent on every later turn. Measure this: the API reports input tokens on each response, and a token counting endpoint lets you check a request before sending it.
- **Compaction summarizes and restarts.** When the conversation nears a limit, the older turns are replaced with a summary of what matters (the goal, decisions made, progress so far and open problems), and the agent continues from there. Done well, the agent barely notices; done badly, it forgets a key detail and repeats work.
- **You can compact yourself or let the API do it.** A do-it-yourself version is one extra model call: send the history with a "summarize this for your future self" prompt, then rebuild the conversation as the summary plus the last few turns. Some providers, including Claude, now offer compaction as an API feature, either on demand or automatically at a token threshold you set.
- **Pick a threshold and keep recent turns.** Compact well before the hard limit (for example, at 50 to 70 percent of the window), and keep the most recent turns word for word, because the model usually needs exact details from them.
- **Context editing removes rather than summarizes.** The simplest strategy is clearing old tool results once they have been used, replacing each with a short placeholder. The agent keeps its own reasoning about the result without carrying the full text. Claude's API offers this as a server-side option with settings for when to trigger and how much to keep.
- **Pair clearing with memory.** Before old results are cleared, the agent can save anything important to a memory file or progress notes, so nothing essential is lost.
- **Editing context affects caching.** Prompt caching saves money by reusing an unchanged prefix of the conversation. Changing earlier content breaks the cache, so clear in larger chunks rather than a little on every turn.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Reread the "Compaction" part of [Effective context engineering for AI agents](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents), paying attention to what it says a good summary should keep and what can safely be dropped.
1. Read the Claude [Compaction overview](https://platform.claude.com/docs/en/build-with-claude/compaction), including the table comparing compaction on demand, compaction at a token threshold and your own summarizer.
1. Read the "Overview," "Server-side strategies" and "Context editing and prompt caching" sections of the Claude [context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing) docs.
1. Read the [context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows) page to understand how the window fills up across turns, especially with tool use.
1. Practice: give the agent from Project: Agent Loop From Scratch a task that reads many large files. Log input tokens per turn and plot or print them. Then add a simple client-side compaction step that triggers at a token threshold you choose, run the task again and compare the token totals and whether it still finished correctly.

</div>
