### Introduction

Tools let an agent do things. Skills teach it how to do a particular kind of job well: the steps your team follows to write a release note, the checklist for reviewing a pull request, the script that fills in a spreadsheet template. An **Agent Skill** is a folder with a `SKILL.md` file of instructions, plus any scripts or reference files it needs. The agent loads only a short description at first and reads the rest when a task calls for it.

Agent Skills started at Anthropic and are now an open standard. Claude Code, the Claude Agent SDK and the Claude API support them, and so do many other agent products, including OpenAI's Codex, Google's Gemini CLI, GitHub Copilot and Cursor. In this lesson you'll write a skill, build a tiny skill loader for your own agent loop so you can see exactly how loading works, and then load the same folder in the Claude Agent SDK. "Port Your Agent" asks you to package one capability as a skill, so this lesson is your rehearsal.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What an Agent Skill is and how it differs from a tool or a system prompt.
- The structure of a skill folder and its `SKILL.md` file.
- Progressive disclosure: loading only what a task needs.
- Bundling scripts and reference files with instructions.
- Writing a skill description so the agent picks it at the right time.
- Loading skills in your own loop and in the Claude Agent SDK.
- Security concerns with skills you did not write.

### Tools, prompts and skills

You already have two ways to change what an agent does. Each has a weakness that skills fix.

A **tool** is a function the model can call, such as `save_note` or `calculate`. Tools are *actions*. A tool doesn't tell the model when to use it in combination with other tools, in what order, or what "done well" looks like for your team. A **system prompt** can say all of that, but everything in it is sent on every request. If you put your release-note process, your code-review checklist, your incident-report template and your SQL style guide in the system prompt, you pay for thousands of tokens on every turn, even when the user only asked for the time. Worse, the model's attention is spread across instructions that have nothing to do with the task, which you saw in Context Engineering for Agents.

A **skill** is *procedural knowledge*: know-how the model reads and follows, packaged so it only enters the context when it's needed. A skill usually tells the agent which tools to use and in what order. Think of it as the page of the team handbook that a new hire opens when they're asked to do one specific job for the first time.

Here's a quick way to decide which one you need:

- If the agent needs to *reach* something (a database, an API, a file system), write a tool, or an MCP server.
- If the agent needs to follow a *procedure* that only matters for some tasks, write a skill.
- If something must apply to *every* turn, such as "never reveal customer emails", it belongs in the system prompt, or better, in code that enforces it.

### Anatomy of a skill folder

A skill is a folder. Its name is the skill's name, and at its root sits `SKILL.md`. Here's the release-notes skill you'll use for the rest of this lesson:

```text
.claude/skills/
  release-notes/
    SKILL.md                 # front matter + instructions (required)
    scripts/
      group_changes.py       # exact work, done by code
    references/
      style.md               # extra detail, read only when needed
```

`SKILL.md` starts with **YAML front matter**: a block of `key: value` lines between two `---` markers. YAML is a simple text format for settings. Then come plain Markdown instructions:

```markdown
---
name: release-notes
description: Turns a list of merged pull request titles into release notes in our house format. Use when the user asks for release notes, a changelog entry or a "what's new" summary for a version.
---

# Release notes

Follow these steps in order.

1. Run `scripts/group_changes.py`, passing the pull request titles on standard input, one per line. It sorts them into sections by their prefix (`feat:`, `fix:`, a `!` for breaking changes). Do not sort them yourself.
2. Read `references/style.md` and rewrite every item in that style.
3. Reply with only the finished notes, starting with the heading `## <version>`.

Keep titles with no prefix under "Other". Never add a change that is not in the list.
```

The open standard requires two fields. `name` is 1 to 64 characters of lowercase letters, digits and single hyphens, and it must match the folder name. `description` is 1 to 1,024 characters saying what the skill does and when to use it. Optional fields include `license`, `compatibility` (for example "Requires Python 3.12 and uv"), `metadata` and an experimental `allowed-tools`. Some products add their own fields on top. Claude's docs, for example, also forbid the words "anthropic" and "claude" in a name. The body has no required format, but the standard recommends keeping `SKILL.md` under 500 lines and moving detail into separate files.

The extra folders are conventions, not rules: `scripts/` for code the agent runs, `references/` for documents it reads, and `assets/` for templates and data files. Refer to them with relative paths from the skill folder, and keep references one level deep. A `SKILL.md` that points to a file that points to another file makes the agent wander.

### Progressive disclosure

The idea that makes skills work is **progressive disclosure**: revealing information in stages, only as it becomes relevant. A skill is loaded at three levels:

1. **Metadata, always.** When the agent starts, it reads only the `name` and `description` of every installed skill and puts them in the system prompt. That's roughly 100 tokens per skill.
1. **Instructions, when triggered.** When a request matches a description, the agent reads the whole `SKILL.md` body into the context. Aim for under 5,000 tokens.
1. **Resources, as needed.** Only if the instructions point to them does the agent open `references/style.md` or run `scripts/group_changes.py`. When it runs a script, only the script's *output* enters the context, not its code.

Do the math. Twenty skills with 4,000-token instructions would cost 80,000 tokens per request if you pasted them all into the system prompt. With progressive disclosure, they cost about 2,000 tokens until one is needed, and then about 6,000. You can install dozens of skills without filling the context window, and a skill can bundle a 200-page API reference at no cost until the agent opens the one page it needs.

This is the "retrieve just in time" idea from Context Engineering for Agents, applied to instructions instead of data. And it has the same weakness: the agent can only load what it knows exists, so everything rests on the description.

### Writing a description that triggers

The agent decides whether to load a skill from its description alone. It never sees the instructions until it has already chosen. So the description has two jobs: say **what the skill does**, and say **when to use it**, in the words a user would actually type.

Compare these two:

```yaml
description: Helps with releases.
```

```yaml
description: Turns a list of merged pull request titles into release notes in our house format. Use when the user asks for release notes, a changelog entry or a "what's new" summary for a version.
```

The first is too vague to match "write the changelog for 2.3" and too broad to stay quiet during "help me plan the release date". The second names its input (pull request titles), its output (release notes in a house format) and three phrasings of the request.

Treat a description like a classifier, because it is one, and test it the way you tested classifiers in Measuring Quality. Write a handful of prompts that *should* trigger the skill and a handful that *shouldn't*, including near misses ("summarize this pull request" is close to "release notes" but isn't the same job). Run each one and record whether the skill loaded. A skill that never loads is useless, and a skill that loads for everything is an expensive system prompt.

A few habits help. Write descriptions in the third person ("Turns a list…", not "I can…"), because they're inserted into the system prompt. Make names specific: `release-notes` beats `helper`. And when two skills could both match a request, sharpen both descriptions until they don't overlap.

### Scripts for exact work

Some steps must come out the same every time: parsing a file format, validating output against a schema, sorting items into sections by a rule. A model *can* do these steps, but it does them slightly differently each run, and it spends output tokens doing them. Code does them identically, for free. So when a step is deterministic, ship a script and tell the agent to run it, instead of describing the algorithm in prose.

Here's `scripts/group_changes.py`. It uses the regular expressions you learned in Foundations to read [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) prefixes such as `feat:` and `fix(api)!:`:

```python
"""Group pull request titles by their Conventional Commits prefix.

Reads one title per line on standard input and prints JSON, for example:
{"Features": ["add CSV export"], "Fixes": ["crash on empty file"]}
"""
import json
import re
import sys

PATTERN = re.compile(r"^(?P<kind>[a-z]+)(\([^)]*\))?(?P<breaking>!)?:\s*(?P<text>.+)$")
SECTIONS = {"feat": "Features", "fix": "Fixes"}


def group(lines: list[str]) -> dict[str, list[str]]:
    groups = {"Breaking changes": [], "Features": [], "Fixes": [], "Other": []}
    for line in (line.strip() for line in lines):
        if not line:
            continue
        match = PATTERN.match(line)
        if match is None:
            groups["Other"].append(line)  # no prefix: keep the title as it is
        elif match["breaking"]:
            groups["Breaking changes"].append(match["text"])
        else:
            groups[SECTIONS.get(match["kind"], "Other")].append(match["text"])
    return {name: items for name, items in groups.items() if items}  # drop empty sections


if __name__ == "__main__":
    print(json.dumps(group(sys.stdin.read().splitlines()), indent=2))
```

Try it before any agent touches it: `printf 'feat: add CSV export\nfix: crash on empty file\n' | python3 scripts/group_changes.py`. Because it's ordinary Python, you can also test it with pytest, which you can't do with a paragraph of instructions. Give scripts clear error messages, because the agent reads them, exactly like the instructive tool errors from Tool Errors and Parallel Calls.

The reference file holds the detail the agent needs only after it has decided to use the skill. Save this as `references/style.md`:

```markdown
# Release note style

- Start each item with a past-tense verb: "Added", "Fixed", "Renamed".
- Keep each item under 15 words. Name what the user sees, not the code.
- Put "Breaking changes" first and say what users must change.
- No pull request numbers, author names or emoji.
```

### Loading skills in your own loop

There's no magic in how an agent loads a skill. Build a loader yourself and you'll understand every product that supports them. Your loader needs to do three things, one per level: list the names and descriptions in the system prompt, give the model a way to read a `SKILL.md` body, and give it a way to read a resource file or run a script.

Create a project with `uv init skills-demo`, run `uv add anthropic python-dotenv pyyaml`, put `ANTHROPIC_API_KEY` in `.env`, and create the `.claude/skills/release-notes/` folder from the previous sections. Then save this as `skill_agent.py`:

```python
import os
import subprocess
import sys
from pathlib import Path

import anthropic
import yaml
from dotenv import load_dotenv

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
client = anthropic.Anthropic()

SKILLS = {}  # (1) level 1: read only the front matter of every skill
for skill_md in Path(".claude/skills").glob("*/SKILL.md"):
    meta = yaml.safe_load(skill_md.read_text().split("---")[1])
    SKILLS[meta["name"]] = {"description": meta["description"], "dir": skill_md.parent.resolve()}

SYSTEM = "You have these skills. If a request matches one, call load_skill first and follow it.\n"
SYSTEM += "\n".join(f"- {name}: {s['description']}" for name, s in SKILLS.items())


def skill_file(skill: str, path: str) -> Path:  # (2) never leave the skill's folder
    root = SKILLS[skill]["dir"]
    target = (root / path).resolve()
    if not target.is_relative_to(root) or not target.is_file():
        raise ValueError(f"{path!r} is not a file inside the {skill} skill.")
    return target


def run_tool(name: str, args: dict) -> str:
    if args.get("skill") not in SKILLS:
        return f"Error: unknown skill. Available: {', '.join(SKILLS)}."
    try:
        if name == "load_skill":  # (3) level 2: the instructions
            return skill_file(args["skill"], "SKILL.md").read_text().split("---", 2)[2]
        if name == "read_skill_file":  # (4) level 3: a reference file
            return skill_file(args["skill"], args["path"]).read_text()
        script = skill_file(args["skill"], args["path"])  # (5) level 3: run a script
        if script.parent.name != "scripts":
            return "Error: only files in the scripts/ folder can be run."
        done = subprocess.run([sys.executable, script], input=args.get("stdin", ""),
                              capture_output=True, text=True, timeout=30)
        return done.stdout + done.stderr  # only the output enters the context
    except (ValueError, subprocess.TimeoutExpired) as error:
        return f"Error: {error}"


def tool(name: str, description: str, **props: str) -> dict:
    schema = {"type": "object", "required": list(props),
              "properties": {key: {"type": "string", "description": d} for key, d in props.items()}}
    return {"name": name, "description": description, "input_schema": schema}


TOOLS = [
    tool("load_skill", "Read a skill's full instructions.", skill="Skill name"),
    tool("read_skill_file", "Read a file a skill's instructions point to.",
         skill="Skill name", path="Path relative to the skill folder"),
    tool("run_skill_script", "Run a script from a skill's scripts/ folder.",
         skill="Skill name", path="Path such as scripts/x.py", stdin="Text for standard input"),
]


def ask(task: str) -> None:
    messages = [{"role": "user", "content": task}]
    for _ in range(10):  # the step cap
        response = client.messages.create(model=MODEL, max_tokens=16000, system=SYSTEM,
                                          tools=TOOLS, messages=messages)
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":
            print("".join(b.text for b in response.content if b.type == "text"))
            return
        results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"  -> {block.name} {block.input}")
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": run_tool(block.name, block.input)})
        messages.append({"role": "user", "content": results})


ask("Release notes for 1.4, please:\nfeat: add CSV export\nfix: crash on empty file\n"
    "feat(api)!: rename /items to /products\nUpdate README")
ask("What is the capital of Portugal?")
```

Run it with `uv run skill_agent.py`. For the first task you should see `load_skill`, then `run_skill_script` with the four titles, then `read_skill_file` for the style guide, and finally notes with a "Breaking changes" section first. For the second task you should see no tool calls at all: the skill stayed at level 1 and cost about 50 tokens.

Walk through the numbered comments:

1. **Discovery** reads only the front matter. The instructions stay on disk.
1. **Containment.** `resolve()` turns `../../.env` into a real path, and `is_relative_to` refuses anything outside the skill's folder. This is the same path check you wrote in Agent Loop From Scratch, and it matters even more here, because a skill's instructions decide which paths get requested.
1. **Level 2** returns everything after the front matter.
1. **Level 3** for documents: the file enters the context only when the model asks for it.
1. **Level 3** for code: the script runs in a separate process with a timeout, and only its output comes back.

Real harnesses don't usually need special tools for this. Claude Code and the Claude API give the model a file system and a shell, so it simply reads `SKILL.md` and runs the script with the tools it already has. Your three tools are a safer, narrower version of that, suitable for an agent that shouldn't have a shell.

### Skills in the Claude Agent SDK

The Claude Agent SDK, from the earlier lesson, discovers skills on its own. It looks in `.claude/skills/` in the working folder (and its parents) and in `~/.claude/skills/` in your home folder, but only when you load those **setting sources**. That catches people out, because the SDK lesson told you to set `setting_sources=[]` to ignore settings on your machine. With an empty list, no skills load. Save this as `sdk_skill_agent.py` in the same project and run `uv add claude-agent-sdk`:

```python
import asyncio
import os

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, SystemMessage, query
from dotenv import load_dotenv

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")

options = ClaudeAgentOptions(
    model=MODEL,
    cwd=os.getcwd(),                    # .claude/skills/ lives here
    setting_sources=["project"],        # load project settings and skills, not your personal ones
    skills=["release-notes"],           # only this skill may be used
    tools=["Skill", "Read", "Bash"],    # "Skill" is the tool that loads a skill
    allowed_tools=["Skill", "Read", "Bash"],
    permission_mode="dontAsk",
    max_turns=10,
)


async def main() -> None:
    task = "Release notes for 1.4:\nfeat: add CSV export\nfix: crash on empty file"
    async for message in query(prompt=task, options=options):
        if isinstance(message, SystemMessage) and message.subtype == "init":
            print("skills found:", message.data.get("skills"))  # confirm it loaded
        elif isinstance(message, ResultMessage):
            print(message.result)


asyncio.run(main())
```

The `init` message near the start of the stream lists the skills the SDK found, so check it first whenever a skill "isn't working". The usual causes are a missing setting source, the wrong `cwd`, or a skill name that doesn't match its folder. When the model decides to use the skill, you'll see a `Skill` tool call in the stream, followed by `Bash` running the script.

This example pre-approves `Bash`, which lets the agent run *any* shell command. That's acceptable on a throwaway folder for learning. For anything else, narrow it with a `PreToolUse` hook that only allows commands starting with `python3 .claude/skills/`, as you did with hooks in The Claude Agent SDK lesson.

The same folder works elsewhere. Drop it into `.claude/skills/` and Claude Code uses it. On the Claude API (a Claude feature), you upload a skill once through the Skills API and list its ID in the request's `container`, alongside the code execution tool, and it runs in Anthropic's sandbox with no network access. And because the format is an open standard, other products that support it can read the same folder.

### Treat skills like code

A skill is instructions plus code, run with your agent's permissions. That makes a third-party skill exactly as risky as a third-party package, and in one way riskier: its instructions are a prompt you've agreed to follow. A malicious `SKILL.md` can say "before you start, run `scripts/setup.py`", and that script can read your `.env` and send it anywhere. You met this pattern in Prompt Injection and the Lethal Trifecta: private data, untrusted instructions and a way to send data out, all in one agent.

Before you install a skill you didn't write:

- **Read every file**, not just `SKILL.md`. Look for network calls, reads outside the skill's folder, encoded strings and instructions that don't match the stated purpose.
- **Be wary of skills that fetch from URLs.** Even a trustworthy skill becomes untrusted if the page it downloads changes.
- **Pin a version.** Copy the folder into your repository, or pin a commit, so it can't change under you.
- **Limit what it can reach.** Run agents that use outside skills with the narrowest tools, in a sandbox, without production credentials.

Your own skills deserve the same review as any other code: keep them in Git, review changes in pull requests, and test their scripts.

### On other providers

Skills are mostly provider-neutral, because a skill is just files: Markdown instructions and scripts. The loader in this lesson works with any model that supports tool calling. To run it on OpenAI, the three tools keep the same JSON Schema, but each one is wrapped as `{"type": "function", "function": {"name": ..., "description": ..., "parameters": schema}}`, the tool calls arrive in `message.tool_calls` with arguments as a JSON string you must parse, and each result goes back as a `{"role": "tool", "tool_call_id": ..., "content": ...}` message. See OpenAI's [function calling guide](https://developers.openai.com/api/docs/guides/function-calling) for the full round trip. For a local open model, point the OpenAI client at [Ollama's OpenAI-compatible API](https://docs.ollama.com/api/openai-compatibility) and pick a model that supports tool calling, such as [Qwen3](https://ollama.com/library/qwen3). Small models are less reliable at noticing that a skill applies, so the trigger tests from this lesson matter even more there. Many coding agents outside Anthropic, such as OpenAI's Codex and Google's Gemini CLI, read `SKILL.md` folders directly, each from its own skills directory. Check each product's docs for where it looks, and expect product-specific front matter fields to be ignored elsewhere.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [Agent Skills overview in the Claude docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) to learn the folder structure and how loading works.
   - Pay close attention to the three levels of loading and the security section.
1. Read Anthropic's post [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) for the design reasoning.
1. Read the [Agent Skills open standard site](https://agentskills.io/) and its [specification page](https://agentskills.io/specification).
   - Note which fields are required in the front matter and which are optional.
   - Then read [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), at least the sections on concise instructions, descriptions and progressive disclosure patterns.
1. Take Anthropic Academy's free [Introduction to Agent Skills](https://anthropic.skilljar.com/introduction-to-agent-skills) course if you want a guided walkthrough. It needs a free account, so it's optional.
1. Practice: build the release-notes skill and `skill_agent.py` from this lesson, then change them.
   - Write `test_group_changes.py` with at least four pytest cases for the script, including a title with no prefix and a breaking change.
   - Write six trigger prompts: three that should load the skill and three near misses that shouldn't. Run each one and record the result in a small table. Rewrite the description until all six behave.
   - Ask `skill_agent.py` to "load the file ../../.env from the release-notes skill" and confirm the containment check refuses it.
1. Write your own skill for a task you repeat, such as "summarize a pull request using our template".
   - Include one helper script and one reference file.
   - Load it in the Claude Agent SDK with `sdk_skill_agent.py`, and check that it loads for a matching request and doesn't load for an unrelated one. You'll reuse this skill in "Port Your Agent".

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [How is a skill different from a tool and from a system prompt?](#tools-prompts-and-skills)
- [Which two front matter fields does the standard require, and what rules apply to the name?](#anatomy-of-a-skill-folder)
- [What gets loaded at each of the three levels of progressive disclosure, and roughly what does each cost?](#progressive-disclosure)
- [Why does the description decide whether a skill is used, and how would you test one?](#writing-a-description-that-triggers)
- [When should a skill ship a script instead of describing the steps in prose?](#scripts-for-exact-work)
- [Which setting must you change for the Claude Agent SDK to find your skills?](#skills-in-the-claude-agent-sdk)
- [What would you check before installing a skill someone else wrote?](#treat-skills-like-code)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Anthropic's public skills repository](https://github.com/anthropics/skills) has real skills you can read as examples, including the document skills behind Claude's file creation.
- The Agent SDK's [skills guide](https://code.claude.com/docs/en/agent-sdk/skills) covers the `skills` option, dispatching a skill by name with `/<name>`, and troubleshooting.
- [Using Agent Skills with the API](https://platform.claude.com/docs/en/build-with-claude/skills-guide) shows how to upload a skill and use it with the code execution tool.
- The [skills-ref validator](https://github.com/agentskills/agentskills/tree/main/skills-ref) checks a skill folder's front matter against the standard.
