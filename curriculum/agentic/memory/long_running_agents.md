<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Some tasks are too big for one sitting, for a person or an agent. Building a full web app, migrating a codebase or researching a large topic can take many hours and far more context than any window holds. Compaction helps, but it is not enough on its own: summaries lose detail, and an agent that forgets where it was will redo work or declare victory too early. In this lesson you will learn how **harnesses** (the code and files around an agent) let it work across many sessions, picking up exactly where the last one left off, the way a well-run engineering team hands off between shifts.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why long tasks fail even with compaction.
- The harness: the scaffolding around the agent loop.
- Progress files, feature lists and other notes the agent reads and writes.
- Using Git as a record of progress and a way to recover.
- Starting each session well and ending each session cleanly.
- Verifying work before marking it done.

### Key ideas

- **Long tasks fail in predictable ways.** Agents try to do everything at once and run out of context midway, leaving work half-finished. Or they look at partial progress, decide the job is done and stop early. Both come from a lack of shared, written state.
- **The harness carries state, not the model.** A harness is the code and files around the agent loop: setup scripts, notes files, tests and rules about how each session begins and ends. It is what makes a stateless model act like a persistent worker.
- **Start with an initializer session.** The first session does not try to solve the task. It sets up the environment, breaks the goal into a detailed list of features or subtasks (each with a "done" flag), writes a progress file and makes a first commit.
- **Every later session follows a routine.** Read the progress file and recent Git history, check that the project still works, pick *one* unfinished item, do it, test it, then update the progress file and commit. Small, verified steps keep each session inside its context window.
- **Git is memory and an undo button.** Descriptive commits tell the next session what happened, and if a session breaks something, it can roll back to the last good state.
- **Only verified work counts.** Mark an item complete only after testing it end to end, the way a user would, not when the code is written. This is the single biggest defense against an agent that falsely reports success.
- **Structured files beat free-form notes.** A JSON feature list with pass/fail fields is harder for the agent to quietly rewrite than prose, and easy for your code to check.
- **These ideas apply beyond coding.** A research agent can keep a source list and findings file; a data-cleaning agent can track which files it has processed.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Effective harnesses for long-running agents](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents) from Anthropic. This is the core reading for the lesson, and the Project: The Agent That Remembers is based on its approach.
   - Note what goes into the initializer session, the progress file and the feature list, and the routine each later session follows.
1. Read "Multisession software development pattern" in the Claude [memory tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool) docs, a short summary of the same pattern using memory files.
1. Reread the "Structured note-taking" part of [Effective context engineering for AI agents](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents), including the example of an agent keeping notes while playing a long game.
1. Practice: write the files an initializer session would produce for a task of your choice, such as "build a command-line to-do app with five features." Write a `features.json` with each feature and a `passes: false` field, a `PROGRESS.md` template with sections for done, next and known problems, and a list of the steps every later session must follow.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Harness design for long-running application development](https://www.anthropic.com/research/harness-design-long-running-apps) from Anthropic goes further: a planner, generator and evaluator working together over multi-hour coding runs, and why a clean context reset with a handoff file can beat compaction.
