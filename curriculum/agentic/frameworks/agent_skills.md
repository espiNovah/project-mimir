<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Tools let an agent do things. Skills teach it how to do a particular kind of job well: the steps your team follows to write a release note, the checklist for reviewing a pull request, the script that fills in a spreadsheet template. An Agent Skill is a folder with a `SKILL.md` file of instructions, plus any scripts or reference files it needs. The agent loads only a short description at first and reads the rest when a task calls for it. Agent Skills started at Anthropic and are now an open standard that several agent products support.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What an Agent Skill is and how it differs from a tool or a system prompt.
- The structure of a skill folder and its `SKILL.md` file.
- Progressive disclosure: loading only what a task needs.
- Bundling scripts and reference files with instructions.
- Writing a skill description so the agent picks it at the right time.
- Security concerns with skills you did not write.

### Key ideas

- **Skills are procedural knowledge, not actions.** A tool is a function the model calls. A skill is know-how: instructions, examples and helper files the model reads and follows. Skills often tell the agent which tools to use and in what order.
- **A skill is a folder.** At its root sits `SKILL.md`, which starts with YAML front matter (a `name` and a `description`) followed by Markdown instructions. Extra files such as `reference.md`, templates or Python scripts sit next to it.
- **Progressive disclosure keeps context small.** At startup the agent sees only each skill's name and description. When a task matches, it reads the full `SKILL.md`. Only if the instructions point to them does it open the extra files or run the scripts. You can install many skills without filling the context window.
- **The description is the trigger.** The agent decides whether to load a skill from its description alone. State what the skill does and when to use it, with words a user would actually say.
- **Scripts beat prose for exact work.** If a step must be deterministic, such as parsing a file format or validating output, ship a script and tell the agent to run it rather than describing the algorithm.
- **Skills are portable.** Because the format is an open standard, the same folder can work in Claude Code, the Claude Agent SDK, the Claude API and other compatible agents.
- **Treat third-party skills like third-party code.** A skill can contain instructions and scripts that run with your agent's permissions. Read it before you install it.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [Agent Skills overview in the Claude docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) to learn the folder structure and how loading works.
   - Pay close attention to the three levels of loading and the security section.
1. Read Anthropic's post [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/research/equipping-agents-for-the-real-world-with-agent-skills) for the design reasoning.
1. Read the [Agent Skills open standard site](https://agentskills.io/) and its specification page.
   - Note which fields are required in the front matter and which are optional.
1. Take Anthropic Academy's free [Introduction to Agent Skills](https://anthropic.skilljar.com/introduction-to-agent-skills) course if you want a guided walkthrough. It needs a free account.
1. Write your own skill for a task you repeat, such as "summarize a pull request using our template".
   - Include one helper script and one reference file.
   - Test it in an agent that supports skills, and check that it loads for a matching request and does not load for an unrelated one.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Anthropic's public skills repository](https://github.com/anthropics/skills) has real skills you can read as examples.
