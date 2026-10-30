### Introduction

An agent that can run shell commands can do anything you can do from a terminal: delete files, read your SSH keys, install packages or send data to any server. Asking permission before every command is safe but exhausting, and people soon start approving without reading. Sandboxing solves this differently. You put the agent in an environment where the worst it can do is limited, then let it work freely inside.

The tiny coding agent from How Coding Agents Work ran its `run` tool with your full user account. In this lesson you'll move that tool into a locked-down Docker container with no access to your files, a network allowlist and resource limits, while the API key and your Git credentials stay on the host. That setup is the backbone of the Sandboxed Coding Agent project.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why permission prompts alone don't scale, and what a sandbox is defending against.
- Filesystem isolation: what the agent can read and write.
- Network isolation: which hosts the agent can reach, enforced with an allowlist proxy.
- Resource limits on memory, CPU, processes and time.
- Keeping secrets out of the sandbox.
- OS-level sandboxes, containers, microVMs and hosted sandboxes, and when to use each.
- Proving your sandbox works.

### Why prompts alone fall short

In Prompt Injection you learned that anything an agent reads can contain instructions: a README, a code comment, a web page, an error message from a package. A coding agent reads a lot of untrusted text. So the honest way to think about a coding agent's shell is: **someone you don't know may be typing into it.** The model might be tricked, or simply make a mistake, such as running `rm -rf build /` with a stray space.

Permission prompts ("Allow `npm install`? y/n") put a human between the model and each command. That works for ten commands. By command two hundred, the human is pressing "y" on reflex, which security people call **approval fatigue**, and the prompt protects nothing. Worse, a prompt shows you the command, not its effect. `uv run pytest` looks harmless, but it runs whatever code is in the test files, and a malicious test can do anything.

A **sandbox** flips the approach. Instead of judging each command, you decide once what the agent's environment can touch. Inside that boundary it runs freely, with no prompts. Anything outside is blocked by the operating system, not by the model's good behavior. Anthropic reported that sandboxing cut permission prompts in Claude Code by 84% while making it safer, because the few remaining prompts are for things that actually deserve attention.

### The walls every sandbox needs

Think about what a hijacked agent would want to do, and build a wall against each:

- **Filesystem.** Read secrets (`~/.ssh`, `~/.aws`, `.env` files, browser cookies), or write somewhere that runs later, such as your shell startup file `~/.zshrc` or a Git hook. The wall: the agent can write only to its project folder and can't read anything sensitive.
- **Network.** Send what it read to an attacker's server, download malware, or call internal services. The wall: deny all traffic by default and allow only a short list of hosts.
- **Resources.** Burn your CPU mining cryptocurrency, fill your disk, or start processes until the machine freezes (a **fork bomb**). The wall: limits on memory, CPU, process count, disk and time.
- **Secrets.** Use credentials it was handed, such as an API key in an environment variable or a Git token, to act as you. The wall: don't put credentials inside at all.

You need the first two together. Filesystem isolation without network isolation still lets the agent send your project's source code anywhere. Network isolation without filesystem isolation lets it plant a command in `~/.zshrc` that runs, unsandboxed, the next time you open a terminal. Simon Willison calls the dangerous combination the **lethal trifecta**: access to private data, exposure to untrusted content, and a way to send data out. A coding agent has all three unless you remove one.

### A locked-down container

You already know Docker from Docker and Docker Compose. A container gets its own filesystem, its own process list and its own network interfaces, which covers most of the walls with flags you can read. Here is a sandbox for a coding agent, as a Dockerfile, a Compose file and a proxy config. The agent's harness runs on your laptop; only the agent's commands run in the container.

```dockerfile
# sandbox/Dockerfile: the agent's computer
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /uvx /bin/
RUN useradd --create-home --uid 1000 agent
USER agent
WORKDIR /work
CMD ["sleep", "infinity"]
```

```yaml
# compose.yaml
services:
  sandbox:
    build: ./sandbox
    container_name: sandbox
    volumes:
      - ./workspace:/work            # (1) the ONLY host folder the agent sees
    read_only: true                  # (2) everything else is read-only...
    tmpfs:
      - /tmp:size=256m               #     ...except a small scratch space
    environment:
      HOME: /tmp
      UV_CACHE_DIR: /tmp/uv-cache
      HTTP_PROXY: http://proxy:3128  # (3) the only way out
      HTTPS_PROXY: http://proxy:3128
      NO_PROXY: localhost,127.0.0.1
    cap_drop: [ALL]                  # (4) no special kernel privileges
    security_opt: ["no-new-privileges:true"]
    mem_limit: 2g                    # (5) resource limits
    cpus: 2
    pids_limit: 256
    networks: [sandbox_net]

  proxy:
    image: ubuntu/squid:latest
    volumes:
      - ./squid.conf:/etc/squid/squid.conf:ro
    networks: [sandbox_net, egress]  # (6) the proxy alone touches both networks

networks:
  sandbox_net:
    internal: true                   # (7) no route to the internet from this network
  egress: {}
```

```text
# squid.conf: the allowlist
http_port 3128
acl allowed dstdomain pypi.org files.pythonhosted.org
http_access allow allowed
http_access deny all
```

Walk through the numbered lines:

1. **One bind mount.** `workspace/` is a fresh clone of the target repository, not your working copy. It contains no `.env` file and no Git credentials. Your home folder doesn't exist inside the container, so `cat ~/.ssh/id_ed25519` fails with "No such file or directory."
1. **A read-only root filesystem** means the agent can't modify the image, install system packages or plant files outside `/work` and `/tmp`. The `tmpfs` gives it scratch space in memory, capped at 256 MB, which vanishes when the container stops.
1. **Proxy settings** tell well-behaved tools such as `uv` and `pip` where to send traffic. Tools that ignore them get nowhere, which is the point of the next two lines.
1. **Dropping capabilities.** Linux splits root's powers into pieces called *capabilities* (changing file owners, binding low ports, tracing other processes). `cap_drop: [ALL]` removes them, and `no-new-privileges` stops a program from regaining them through a `setuid` binary. Together with the non-root `agent` user, this closes most routes to escalating privileges inside the container.
1. **Resource limits.** `mem_limit` kills processes that use more than 2 GB instead of letting them freeze your laptop. `cpus` caps CPU use. `pids_limit` caps the number of processes, which stops a fork bomb at 256.
1. **The proxy** is a small, well-known HTTP proxy called Squid. It sits on both networks and forwards only requests to hosts in its allowlist.
1. **An internal network** has no gateway to the outside world. A container that's only on `sandbox_net` can reach the proxy and nothing else, so a program that ignores the proxy settings and connects directly simply fails. This is what makes the allowlist enforced, not polite.

For HTTPS, the proxy sees only the host name (from the `CONNECT` request), not the URL or the contents. That's enough for a domain allowlist, and it means you never have to break encryption. It also means an allowed domain is fully allowed: if you allow `github.com`, the agent can upload to any GitHub repository. Keep the list to what the task needs, such as your package registry. The model API isn't on it, because the harness, not the sandbox, calls the model.

Start it with `docker compose up -d --build`. When a run is over, `docker compose down` and delete `workspace/`, so every run starts clean.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Two gaps in an internal network

An internal network is cut off from the outside by design, so don't plan on publishing ports from the sandbox to check a web app in your host browser. Run the browser inside the sandbox (it reaches the app on `localhost`), or in another container on `sandbox_net`. Also, Docker's docs note that containers on an internal network can still reach the network's gateway address, and with it any service on the Docker host that listens on all interfaces (`0.0.0.0`). Don't leave a database or dev server listening that way on the host while an agent runs, and test for it.

</div>

### Running tools inside the sandbox

The container does nothing on its own. Your harness on the host sends each shell command into it with `docker exec`. Here's the `run` tool from How Coding Agents Work, rewritten so commands execute in the sandbox:

```python
# sandbox_tools.py: the agent's shell lives in the container, the agent's brain on the host
import subprocess

CONTAINER = "sandbox"
MAX_OUTPUT = 4000


def run(command: str, timeout: int = 120) -> str:
    """Run a shell command inside the sandbox container, in /work."""
    try:
        result = subprocess.run(
            ["docker", "exec", "--workdir", "/work", CONTAINER,
             "timeout", "--signal=KILL", str(timeout),   # kill it INSIDE the container
             "bash", "-c", command],
            capture_output=True, text=True, timeout=timeout + 15,
        )
    except subprocess.TimeoutExpired:
        return "Error: the sandbox did not respond. It may need a restart."
    output = f"exit code {result.returncode}\n{result.stdout}{result.stderr}"
    if result.returncode == 137:                          # 128 + 9: killed by SIGKILL
        output += f"\n(killed: over the {timeout}s time limit or the memory limit)"
    if len(output) > MAX_OUTPUT:
        output = output[:MAX_OUTPUT // 2] + "\n...[cut]...\n" + output[-MAX_OUTPUT // 2:]
    return output


if __name__ == "__main__":
    print(run("whoami && pwd && ls -la"))
    print(run("cat ~/.ssh/id_ed25519"))                    # should fail: no host home inside
    print(run("python -c \"import urllib.request as u; "
              "u.urlopen('https://example.com', timeout=5)\""))  # should fail: not allowlisted
```

Two details matter. The `timeout` command runs *inside* the container, because killing the `docker exec` process on the host doesn't stop the command it started. And exit code 137 means the process was killed by `SIGKILL`, which happens both at the time limit and when the memory limit is hit, so the agent gets a useful message instead of a mystery.

File tools can stay on the host, working on `workspace/` directly, as long as they check paths with `Path.resolve()` as `coder_tools.py` did. That check matters more now: the agent can create a **symbolic link** (a file that points to another path) inside `workspace/`, such as `notes.txt -> /Users/you/.ssh/id_ed25519`. Inside the container that link points nowhere, but a careless host-side read tool would follow it straight to your key. `resolve()` follows the link and the `is_relative_to` check refuses it. If in doubt, route file reads through `docker exec` too.

### Secrets stay outside

The simplest rule is the strongest: **no credential the agent shouldn't use ever enters the sandbox.**

- **The model API key** lives in the harness process on the host. The model is called from outside, so the sandbox never needs it. Never pass it with `environment:` or `--env-file`; anything in the container's environment is one `env` command away from the agent.
- **Git push credentials** stay on the host. The agent can commit inside `workspace/`, since commits are local. Pushing is a host-side function that shows you the diff and waits for you to type "yes", which you'll build in the project and study in Approvals and Permissions.
- **Credentials the task genuinely needs**, such as a token for a test API, should be short-lived and narrowly scoped: read-only, one repository, expiring in an hour. Better still is a **credential proxy**: the proxy adds the token to requests for one allowed host as they leave, so the agent can use the service without ever seeing the secret. Some hosted platforms offer this built in, such as vault credentials in Anthropic's Managed Agents (a Claude feature); elsewhere you'd configure your own proxy to do it.
- **The workspace itself** must be clean. Create it with `git clone` from the remote, not by copying your working folder, which may contain `.env` files and a `.git/config` with tokens in it.

### Choosing a level of isolation

Sandboxes come in several strengths, and stronger usually means heavier.

**OS-level sandboxes** use features built into the operating system to restrict one process and its children, with no container at all. On Linux the common tool is **bubblewrap**, and on macOS it's the built-in **Seatbelt** (`sandbox-exec`). Anthropic's open-source **sandbox-runtime** (`srt`) wraps both and adds a network allowlist proxy, configured in a small JSON file:

```json
{
  "filesystem": {
    "denyRead": ["~/.ssh", "~/.aws"],
    "allowWrite": ["."],
    "denyWrite": [".git/hooks"]
  },
  "network": {
    "allowedDomains": ["pypi.org", "files.pythonhosted.org"]
  }
}
```

Save it as `~/.srt-settings.json`, install with `npm install -g @anthropic-ai/sandbox-runtime`, and run a command with `srt "uv run pytest"`. Writes go only to the current folder, and network access is denied except to the listed domains. OS-level sandboxes start instantly and work on your real files, which is why Claude Code and Codex CLI use them for local work. Their weakness is that the agent still runs on your machine, under your operating system, and the rules are only as good as the paths you remembered to deny.

**Containers** give the agent a separate filesystem and network by default, so you list what to let in rather than what to keep out. That's the setup above. But all containers on a machine share the host's **kernel** (the core of the operating system), so a kernel bug can let code escape. That's rare, but it's why containers alone aren't considered strong enough for running code from strangers.

**Stronger isolation** puts a different kernel between the agent and the host. **gVisor** is a user-space kernel that Docker can use as a drop-in runtime (`runtime: runsc` in Compose). **MicroVMs** such as **Firecracker**, the technology behind AWS Lambda, give each sandbox its own tiny virtual machine that boots in a fraction of a second. On a Mac, Docker Desktop already runs containers inside a Linux VM, which adds a layer between them and macOS.

**Hosted sandboxes** take the agent off your machine entirely. Services such as [E2B](https://e2b.dev/docs), [Modal Sandboxes](https://modal.com/docs/guide/sandboxes) and [Daytona](https://www.daytona.io/docs) create an isolated cloud machine through an API call, usually a microVM, and bill by the second; most have a free tier with sign-up. Model providers also offer their own: Anthropic's code execution tool and Managed Agents run code in Anthropic-hosted containers (Claude features), and OpenAI's code interpreter and Codex cloud do the same on OpenAI's side. Hosted sandboxes are the right choice when you run agents for other people, run many at once, or don't want untrusted code on your laptop at all. The costs are money, a little latency, and your code leaving your machine.

A good default for learning and for this curriculum's project: a Docker container like the one above on your own machine. Move to gVisor, microVMs or a hosted sandbox when the code you run comes from strangers.

### Prove the walls hold

A sandbox you haven't tested is a hope, not a control. Write a script that tries to break out and expects every attempt to fail, and keep it in your repository so you rerun it whenever the config changes:

```bash
#!/usr/bin/env bash
# sandbox_check.sh: every "must fail" attempt must be blocked
status=0
must_fail() {   # usage: must_fail "description" command...
  if docker exec sandbox "${@:2}" >/dev/null 2>&1; then
    echo "HOLE    $1"; status=1
  else
    echo "blocked $1"
  fi
}
must_work() {
  if docker exec sandbox "${@:2}" >/dev/null 2>&1; then
    echo "works   $1"
  else
    echo "BROKEN  $1"; status=1
  fi
}
must_fail "write outside the project" touch /etc/agent-was-here
must_fail "reach a site not on the allowlist" python -c \
  "import urllib.request as u; u.urlopen('https://example.com', timeout=5)"
must_work "write inside the project" touch /work/.sandbox-check
must_work "reach the package registry" python -c \
  "import urllib.request as u; u.urlopen('https://pypi.org/simple/', timeout=10)"
exit $status
```

The `must_work` checks matter as much as the `must_fail` ones. A sandbox that blocks everything also "passes" every escape test, and an agent that can't install packages can't do its job. Add your own attempts: read a canary file you created in your home folder, connect directly to an IP address without the proxy, reach a service running on your host, start 1,000 processes.

Finally, remember that the sandbox is one layer of **defense in depth**. Keep the step and cost budgets, the tool allowlist, the human approval before irreversible actions such as pushing, and the trace of every command. Each layer catches some of what the others miss.

### On other providers

Sandboxing is independent of the model: the container, the proxy and `sandbox_check.sh` work the same whether your harness calls Claude, an OpenAI model or a local model through Ollama, because only the harness talks to the model and only tool calls reach the sandbox. With a local model, you can even put the model server on the host and keep the sandbox's allowlist down to the package registry. What differs between providers is the hosted options. Anthropic's [code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool) and OpenAI's [code interpreter](https://platform.openai.com/docs/guides/tools-code-interpreter) each run model-written code in a provider-hosted container, but with different file handling, limits and network rules, and each works only with its own provider's models. Third-party sandboxes such as E2B and Modal work with any model, which makes them the portable choice. On the coding-agent side, [Codex CLI's sandbox](https://developers.openai.com/codex/security) uses the same OS-level tools as sandbox-runtime (Seatbelt on macOS, and Linux kernel features), with modes from read-only to full access.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read Anthropic's [Beyond permission prompts: making Claude Code more secure and autonomous](https://www.anthropic.com/research/claude-code-sandboxing) for the reasoning behind filesystem and network isolation.
1. Read the [Claude Code sandboxing docs](https://code.claude.com/docs/en/sandboxing) to see how the boundaries are configured in a real coding agent.
   - Note how allowed domains and writable paths are set, and what happens when a command tries to cross them.
1. Read the README of [sandbox-runtime](https://github.com/anthropics/sandbox-runtime), the open-source tool behind it, which you can use to sandbox your own agents.
   - Focus on the "Dual Isolation Model" section and how the network proxy works on your operating system.
1. Read Docker's guide to [resource constraints](https://docs.docker.com/engine/containers/resource_constraints/) and Simon Willison's [The lethal trifecta for AI agents](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/).
   - For each part of the trifecta, name the wall in this lesson's Compose file that removes or limits it.
1. Practice: build the sandbox from this lesson.
   - Create `workspace/` with `git clone` of one of your earlier projects, then start the sandbox and run `sandbox_check.sh` until every line passes.
   - Add a `must_fail` check that reads a canary file you put in your home folder, and one that connects straight to an IP address, bypassing the proxy.
   - Replace the `run` tool in your `coder.py` from How Coding Agents Work with the version in `sandbox_tools.py`, and fix a planted bug with the agent working inside the sandbox.
   - Optional: install sandbox-runtime and show the same results (write inside the project only, one allowed domain) without a container.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Why do permission prompts stop protecting you as the number of commands grows?](#why-prompts-alone-fall-short)
- [Why do you need both filesystem and network isolation, not just one?](#the-walls-every-sandbox-needs)
- [What makes the network allowlist in the Compose file enforced rather than optional?](#a-locked-down-container)
- [Why does the run tool use the timeout command inside the container, and what does exit code 137 mean?](#running-tools-inside-the-sandbox)
- [How can the agent push code or call an API without its credentials ever entering the sandbox?](#secrets-stay-outside)
- [What are the trade-offs between OS-level sandboxes, containers, microVMs and hosted sandboxes?](#choosing-a-level-of-isolation)
- [Why does a sandbox check script need checks that must succeed as well as checks that must fail?](#prove-the-walls-hold)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Claude Code development containers](https://code.claude.com/docs/en/devcontainer) shows a ready-made container setup with a firewall script that allows only listed domains.
- [Inspect's sandboxing docs](https://inspect.aisi.org.uk/sandboxing.html) show how an evaluation framework runs untrusted agent code in containers.
- The [gVisor documentation](https://gvisor.dev/docs/) explains how a user-space kernel adds a layer between containers and the host.
- Docker's [network create reference](https://docs.docker.com/reference/cli/docker/network/create/) documents internal networks and the other options used in this lesson.
