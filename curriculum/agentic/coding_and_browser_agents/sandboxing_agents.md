<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

An agent that can run shell commands can do anything you can do from a terminal: delete files, read your SSH keys, install packages or send data to any server. Asking permission before every command is safe but exhausting, and people soon start clicking "yes" without reading. Sandboxing solves this differently. You put the agent in an environment where the worst it can do is limited, then let it work freely inside. This lesson covers the two walls every sandbox needs, filesystem isolation and network isolation, and the tools that provide them.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why permission prompts alone don't scale.
- Filesystem isolation: what the agent can read and write.
- Network isolation: which hosts the agent can reach.
- Operating-system sandboxes versus containers versus remote VMs.
- Keeping secrets out of the sandbox.
- How sandboxing fits with permissions and human approval.

### Key ideas

- **Sandboxes replace many prompts with a few boundaries.** Instead of asking "may I run this?" each time, you decide once what the agent can touch. Inside the boundary it runs freely, and anything outside is blocked by the operating system, not by the model's good behavior.
- **You need both walls.** Without filesystem isolation, an attacker who controls the agent's input can change files outside the project, such as your shell startup files. Without network isolation, the agent can send your data anywhere. Either one alone leaves a big hole.
- **Filesystem isolation means a writable project folder and little else.** Allow writes only to the working directory. Block reads of secrets such as `~/.ssh`, cloud credentials and `.env` files.
- **Network isolation means an allowlist.** Route traffic through a proxy that only permits approved domains, such as your package registry and the site you are testing. Deny everything else by default.
- **There are several levels of sandbox.** OS-level sandboxes (Linux bubblewrap, macOS Seatbelt, used by Anthropic's open-source `sandbox-runtime`) are light and fast. Containers such as Docker add more separation. Remote VMs or hosted sandboxes keep the agent off your machine entirely.
- **Secrets belong outside.** Don't mount credentials into the sandbox. If the agent needs to push code or call an API, have a trusted process outside the sandbox do it, ideally after a human approves.
- **Sandboxing is one layer of defense in depth.** Combine it with allowed-tool lists, approval for irreversible actions and logging, so one failure doesn't become a disaster.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read Anthropic's [Beyond permission prompts: making Claude Code more secure and autonomous](https://www.anthropic.com/research/claude-code-sandboxing) for the reasoning behind filesystem and network isolation.
1. Read the [Claude Code sandboxing docs](https://code.claude.com/docs/en/sandboxing) to see how the boundaries are configured in practice.
   - Note how allowed domains and writable paths are set, and what happens when a command tries to cross them.
1. Read the README of [sandbox-runtime](https://github.com/anthropics/sandbox-runtime), the open-source tool behind it, which you can use to sandbox your own agents.
1. Work through Docker's [Get started guide](https://docs.docker.com/get-started/) up to running your own container, if you haven't used Docker yet. You will need it in the next project.
1. Try it yourself: run a small script inside `sandbox-runtime` or a Docker container with networking restricted.
   - Show that the script can write in its project folder but not in your home directory.
   - Show that it can reach one allowed domain but not another.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Claude Code development containers](https://code.claude.com/docs/en/devcontainer) shows a ready-made container setup with a network firewall.
- [Inspect's sandboxing docs](https://inspect.aisi.org.uk/sandboxing.html) show how an evaluation framework runs untrusted agent code in containers.
