<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Coding agents such as Claude Code, Codex and Cursor's agent mode are the most widely used agents today. They read a codebase, edit files, run commands and tests, and keep going until the job is done. They are worth studying for two reasons. You will use them every day as a developer, and their design (a model with a shell, a file system and a way to check its own work) is a template for many other agents you will build.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The core loop of a coding agent: explore, plan, edit, verify.
- Why tests and other checks are what make coding agents reliable.
- Project memory files and other ways to give an agent context.
- How context limits shape how you work with a coding agent.
- Working patterns: plan first, small steps, fresh sessions.
- Reviewing agent-written code before it ships.

### Key ideas

- **The loop is gather context, act, verify.** A coding agent searches and reads files to understand the code, edits files, then runs tests, linters or the app to see if the change worked. Results feed the next step. The tools are ordinary ones: read, write, search and a shell.
- **Verification is the most important input you give.** An agent that can run a test suite can check itself and fix its own mistakes. Without a way to verify, it can only guess. Give it tests, a type checker, expected output or a screenshot to compare against.
- **Context is the scarce resource.** Every file read and command output fills the context window, and performance drops as it fills. Clear or restart sessions between unrelated tasks, and let subagents do wide searches so only summaries come back.
- **Memory files carry standing instructions.** A file like `CLAUDE.md` or `AGENTS.md` in the repo tells the agent how to build, test and style code. Keep it short and only include things the agent would otherwise get wrong.
- **Plan before you code for anything non-trivial.** Ask the agent to explore and propose a plan, review the plan, then let it implement. Catching a wrong approach in a plan is much cheaper than in a diff.
- **Permissions decide how much the agent can do alone.** Coding agents ask before risky actions such as running unfamiliar commands, and you can allow or deny specific tools. More autonomy needs a sandbox, which is the next lesson.
- **You own the result.** Read every diff before merging. Agents produce plausible code that can be subtly wrong, delete tests to make them pass or add needless complexity.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Claude Code best practices](https://code.claude.com/docs/en/best-practices) from start to finish. It is the clearest guide to working with any coding agent.
   - Note the advice on giving the agent a way to verify its work, and on managing context.
1. Reread the agent-computer interface part of [Building effective agents](https://www.anthropic.com/research/building-effective-agents), including the appendix on prompt engineering your tools.
   - Connect it to the SWE-bench example: why did tool design matter more than the prompt?
1. Skim the [SWE-bench site](https://www.swebench.com/) to see how coding agents are measured on real GitHub issues.
1. Use a coding agent of your choice on one of your earlier projects.
   - Ask it to explore and plan a small feature first, review the plan, then let it implement and run the tests.
   - Write down every point where you had to correct it, and what instruction would have prevented it. Put the useful ones in a project memory file.

</div>
