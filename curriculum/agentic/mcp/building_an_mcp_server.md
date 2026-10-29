### Introduction

Now that you know what MCP servers are, it's time to build one. The good news: with the official Python SDK, a working server is a few decorated functions. The SDK reads your type hints and docstrings and turns them into tool definitions, handles the protocol for you, and gives you a command to open your server in the **MCP Inspector**, a testing tool that lets you call tools by hand before any model touches them.

In this lesson you'll build a small server for a team reading list, test it with the Inspector and with pytest, connect it to Claude Code or Claude Desktop, and then write your own tiny host in Python that lets a model use it. That last step closes the loop from the previous lesson: you'll write the translation code a host runs.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Setting up an MCP server project with `uv` and the official Python SDK.
- Defining tools, resources and prompts with decorators, type hints and docstrings.
- Returning errors the model can act on.
- Why a stdio server must never print to standard output.
- Testing a server with the MCP Inspector and with pytest.
- Connecting a server to Claude Code, Claude Desktop and your own Python client.

### Setting up the project

The official SDK is the `mcp` package on PyPI. At the time of writing (October 2026) the current release is **2.3**, which supports the 2026-07-28 spec and still talks to clients on older versions. Version 2 renamed the main class: older tutorials use `FastMCP`, and current code uses `MCPServer`. Check the version you get with `uv run mcp version`.

```bash
uv init reading-list-mcp
cd reading-list-mcp
uv add "mcp[cli]" anthropic python-dotenv
uv add --dev pytest
```

The `[cli]` part is an **extra**: an optional set of dependencies, here the `mcp` command-line tool with `mcp dev`, `mcp run` and `mcp install`. The `anthropic` and `python-dotenv` packages are only for the small client at the end of the lesson; the server itself doesn't need them.

### A server in one file

Save this as `server.py`. It has two tools, one resource and one prompt:

```python
"""A small MCP server for a team reading list, built with the official Python SDK."""
import logging
from typing import Annotated, Literal

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import Field

logger = logging.getLogger(__name__)          # logs go to stderr, never stdout

mcp = MCPServer("reading-list", instructions="Search the list before adding a book.")

BOOKS: list[dict] = [                          # a stand-in for a real database
    {"id": 1, "title": "Dune", "author": "Frank Herbert", "status": "read"},
    {"id": 2, "title": "Kindred", "author": "Octavia E. Butler", "status": "to_read"},
    {"id": 3, "title": "Piranesi", "author": "Susanna Clarke", "status": "reading"},
]
Status = Literal["to_read", "reading", "read"]


@mcp.tool()
def reading_search_books(
    query: str,
    status: Status | None = None,
    limit: Annotated[int, Field(ge=1, le=20, description="Max books to return")] = 5,
) -> str:
    """Search the team reading list by title or author.

    Use this before adding a book, to avoid duplicates, or to answer questions
    like "what are we reading?". Example: query="butler", status="to_read".
    Returns one line per book: id, title, author, status.
    """
    logger.info("search query=%r status=%r", query, status)
    q = query.lower()
    hits = [b for b in BOOKS
            if (q in b["title"].lower() or q in b["author"].lower())
            and (status is None or b["status"] == status)]
    if not hits:
        raise ToolError(f"No books match {query!r}. Try part of a title or an author's last name.")
    return "\n".join(f"{b['id']}: {b['title']} by {b['author']} ({b['status']})"
                     for b in hits[:limit])


@mcp.tool()
def reading_add_book(title: str, author: str) -> str:
    """Add a book to the reading list with status "to_read".

    Search first: this tool refuses exact duplicates. Returns the new book's id.
    """
    if any(b["title"].lower() == title.lower() for b in BOOKS):
        raise ToolError(f"{title!r} is already on the list. Use reading_search_books to see it.")
    book = {"id": max(b["id"] for b in BOOKS) + 1, "title": title,
            "author": author, "status": "to_read"}
    BOOKS.append(book)
    return f"Added {title} by {author} as book {book['id']}."


@mcp.resource("reading://statuses")
def statuses() -> str:
    """The valid reading statuses and what each one means."""
    return "to_read: on the list, not started\nreading: in progress\nread: finished"


@mcp.prompt()
def weekly_pick(mood: str) -> str:
    """Ask for one book from the list to read next, matching a mood."""
    return (f"Use reading_search_books to look at our to_read books, "
            f"then pick one for this mood: {mood}.")


if __name__ == "__main__":
    mcp.run()                                  # stdio by default
```

Each decorator is the entire registration:

- **`@mcp.tool()`** turns a function into a tool. The function name becomes the tool name, the docstring becomes the description, and the type hints become the input schema. `query: str` becomes a required string; `status: Status | None = None` becomes an optional field whose value must be one of three strings (an **enum** in JSON Schema); and the `Annotated[int, Field(ge=1, le=20, ...)]` hint adds a minimum, a maximum and a parameter description. You never write JSON Schema by hand.
- **`@mcp.resource("reading://statuses")`** registers read-only data at a URI. The host or user decides when to load it.
- **`@mcp.prompt()`** registers a template. Its return value becomes a user message the user can insert by name.
- **`mcp.run()`** with no arguments serves over stdio. It sits under `if __name__ == "__main__":` because the `mcp` command, the Inspector and your tests all *import* this file, and an import shouldn't start a server.

The `instructions` string is optional text the server sends to hosts to describe how its tools fit together. Hosts may add it to the model's context.

### Descriptions are still prompts

An MCP server is just a reusable way of shipping tools, so everything from Designing Tools for Agents applies. The model reads only the name, description and schema; it never sees the function body. Look at the choices above:

- **Namespaced names.** `reading_search_books` and `reading_add_book` share a prefix. A host might load tools from five servers at once, and two of them could easily both have a `search` tool. The prefix keeps them apart.
- **Descriptions that say when to use the tool**, with an example and the shape of the output. "Search first" in `reading_add_book` nudges the model into the right order.
- **Constrained parameters.** The `Literal` turns a free-text `status` into three allowed values, and `limit` has bounds, so the model can't ask for 10,000 rows.
- **Compact output.** One line per book, not a dump of every field.

**Resources are for data, tools are for actions.** The list of valid statuses rarely changes and is useful context, so it's a resource the user can attach. Searching and adding are things the model decides to do, so they're tools.

### Errors the model can act on

When a search finds nothing, the tool raises `ToolError`. The SDK catches it and returns a normal result with `isError: true` and your message as the text, exactly the pattern from Tool Errors and Parallel Calls: the model reads "No books match 'zzz'. Try part of a title..." and tries again with a better query.

The SDK draws three lines, and it's worth knowing which side of each you're on:

- **`ToolError`**: a failure the model could fix with better arguments. The model sees your message.
- **Any other exception** (a `KeyError`, a database driver crashing): the model gets only "Error executing tool reading_search_books", and the full traceback goes to your log. That's deliberate. Tracebacks can reveal internals such as file paths or SQL, and they're no help to a model anyway.
- **Bad arguments** never reach your function. If the model sends `status="done"` or `limit=0`, the SDK rejects the call against the schema and returns an error result the model can read.

Don't `return "Error: ..."` from a tool. A returned string has `isError: false`, so the host and the model both think the call worked.

### Never print in a stdio server

In the stdio transport, the server's **standard output is the wire**: every byte the host reads from it must be a protocol message. A stray `print("got here")` puts text in the middle of that stream, and the host may drop the connection with a confusing parse error. The current SDK tries to redirect stray output while it's serving, but an unflushed `print` can still leak onto the wire when the process exits, so don't rely on that.

Use the `logging` module, which you learned in Debugging and Logging. Its default handler writes to **standard error**, which is yours to use. `MCPServer` configures logging for you at the `INFO` level (pass `log_level="DEBUG"` to see more). Log output never reaches the model. If the model should see something, return it.

### Testing with the Inspector

Before any model touches your server, call it by hand. The **MCP Inspector** is a small web app that connects to a server and shows one tab per primitive. It runs on Node.js, which you installed in the Frontend section:

```bash
uv run mcp dev server.py
```

Open the URL it prints. In the **Tools** tab, call `reading_search_books` with `query` set to `butler`, then try a query that matches nothing, then a `limit` of `0`. In **Resources**, read `reading://statuses`. In **Prompts**, fill in a mood and see the message it builds. Notice the forms: the Inspector built them from your type hints, exactly as every other client does.

The Inspector separates two very different problems. If a tool fails in the Inspector, your *server* is broken. If it works in the Inspector but the model uses it badly, your *descriptions* need work. Without this step you'd be guessing which one you're looking at.

### Automated tests with pytest

The Inspector is for exploring. For tests that run in CI, the SDK's `Client` can connect to your server object **in memory**: no subprocess, no port. It's the same idea as FastAPI's `TestClient`. Save this as `test_server.py`:

```python
import pytest
from mcp import Client

import server
from server import mcp


@pytest.fixture
def anyio_backend():
    return "asyncio"                    # run the async tests on asyncio


@pytest.fixture
async def client():
    async with Client(mcp, raise_exceptions=True) as c:   # in memory: no subprocess, no port
        yield c


@pytest.fixture(autouse=True)
def fresh_books(monkeypatch):           # every test starts from the same data
    monkeypatch.setattr(server, "BOOKS", [
        {"id": 1, "title": "Dune", "author": "Frank Herbert", "status": "read"},
    ])


@pytest.mark.anyio
async def test_search_finds_by_author(client):
    result = await client.call_tool("reading_search_books", {"query": "herbert"})
    assert not result.is_error
    assert "Dune" in result.content[0].text


@pytest.mark.anyio
async def test_search_miss_is_a_tool_error_the_model_can_read(client):
    result = await client.call_tool("reading_search_books", {"query": "zzz"})
    assert result.is_error
    assert "No books match" in result.content[0].text


@pytest.mark.anyio
async def test_limit_out_of_range_is_rejected(client):
    result = await client.call_tool("reading_search_books", {"query": "dune", "limit": 0})
    assert result.is_error


@pytest.mark.anyio
async def test_add_refuses_duplicates(client):
    result = await client.call_tool("reading_add_book", {"title": "dune", "author": "F. Herbert"})
    assert result.is_error and "already on the list" in result.content[0].text


@pytest.mark.anyio
async def test_resource_lists_statuses(client):
    result = await client.read_resource("reading://statuses")
    assert "to_read" in result.contents[0].text
```

Run `uv run pytest`. The `@pytest.mark.anyio` marker comes from a pytest plugin that ships with `anyio` (installed with the SDK); it lets pytest run `async def` tests, and the `anyio_backend` fixture picks asyncio. The `client` fixture is an async generator: everything before `yield` is setup, everything after is cleanup, like the context managers from Pythonic Python. `raise_exceptions=True` makes unexpected server crashes show up in your test with their real message instead of the generic text a remote caller would get. And `monkeypatch` replaces the module's `BOOKS` list so tests don't leak into each other, as in Testing With pytest.

Notice what these tests check: the result the *model* would see. An error test asserts `is_error` and the text, because that text is part of your interface.

### Connecting to a real host

Connecting a stdio server to a host means telling the host **the command that starts your server**. The host runs that command as a child process from its own working directory, with a minimal environment, so use absolute paths.

**Claude Code.** Register the server with the `claude` CLI. Everything after `--` is the launch command:

```bash
claude mcp add reading-list -- uv run --directory /absolute/path/to/reading-list-mcp mcp run server.py
```

Start Claude Code and type `/mcp` to check that `reading-list` is connected and its two tools are listed. Then ask "What's on our to-read list?" and approve the tool call. Use `claude mcp list` and `claude mcp remove reading-list` to manage servers.

**Claude Desktop.** Run `uv run mcp install server.py` from your project folder. It writes an entry into Claude Desktop's config file (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS, `%APPDATA%\Claude\claude_desktop_config.json` on Windows) with absolute paths filled in. The entry is plain JSON, a `command` and its `args` under an `mcpServers` key, so you can also write it by hand. Fully quit and reopen Claude Desktop afterwards; it reads the config only at launch.

If the server doesn't show up, run the launch command yourself in a terminal first. Silence is correct, because a stdio server waits for a host to speak first. A traceback is your bug, and now you can read it. The three usual causes are a relative path, a host still running its old config, and something writing to standard output. Claude Desktop keeps your server's standard error in `mcp-server-reading-list.log`, under `~/Library/Logs/Claude` on macOS.

If the server needs an API key, pass it as an environment variable in the config (`claude mcp add --env NAME=value ...`, or `-v NAME=value` with `mcp install`). Never hard-code it in `server.py`.

### Your own host in Python

Claude Code is a host, but so is any program with an MCP client inside it. Writing a small one shows you exactly what hosts do. This script launches `server.py` over stdio, lists its tools, translates them into Claude tool definitions, and runs the agent loop from Function Calling, routing each tool call to the server. Save it as `agent.py` next to `server.py`, with `ANTHROPIC_API_KEY` in `.env`:

```python
"""A tiny host: connect to an MCP server over stdio and let Claude use its tools."""
import os
import sys

import anthropic
import anyio
from dotenv import load_dotenv
from mcp import Client, StdioServerParameters

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
MAX_STEPS = 8


def to_claude_tool(tool) -> dict:
    """An MCP tool definition becomes a Claude tool definition: same three parts."""
    return {"name": tool.name, "description": tool.description or "",
            "input_schema": tool.input_schema}


def result_text(result) -> str:
    """Flatten an MCP CallToolResult into the text a tool_result carries."""
    return "\n".join(c.text for c in result.content if c.type == "text") or "(no output)"


async def ask(question: str, llm=None) -> str:
    llm = llm or anthropic.Anthropic()
    params = StdioServerParameters(command=sys.executable, args=["server.py"])
    async with Client(params) as mcp_client:              # 1. launch the server and connect
        tools = [to_claude_tool(t) for t in (await mcp_client.list_tools()).tools]
        messages = [{"role": "user", "content": question}]
        for _ in range(MAX_STEPS):
            reply = llm.messages.create(model=MODEL, max_tokens=4000,
                                        tools=tools, messages=messages)
            messages.append({"role": "assistant", "content": reply.content})
            if reply.stop_reason != "tool_use":
                return "".join(b.text for b in reply.content if b.type == "text")
            results = []
            for block in reply.content:                    # 2. route each call to the server
                if block.type == "tool_use":
                    out = await mcp_client.call_tool(block.name, block.input)
                    results.append({"type": "tool_result", "tool_use_id": block.id,
                                    "content": result_text(out), "is_error": bool(out.is_error)})
            messages.append({"role": "user", "content": results})
    return "Stopped: step limit reached."


if __name__ == "__main__":
    print(anyio.run(ask, " ".join(sys.argv[1:]) or "What is on our to-read list?"))
```

Run `uv run agent.py "Add The Fifth Season by N. K. Jemisin, unless it's already there"` and watch the model search, then add. `StdioServerParameters` holds the launch command, just like a host's config; `sys.executable` is the path of the Python running this script, so the server starts in the same environment. The server's `isError` flag maps straight onto the Claude `tool_result`'s `is_error` field. And because `ask` takes the model client as an argument (dependency injection, from Testing With pytest), you can test the whole round trip with a fake model and no API key: a fake whose `messages.create` first returns a `tool_use` block for `reading_search_books`, then returns the tool's text as its answer. That's how this lesson's example was checked.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Let a framework do this later

Real hosts add more: approval prompts before tool calls, several servers at once, tool name collisions, reconnection. The Anthropic Python SDK has beta helpers that convert MCP tools for its tool runner, and the Claude Agent SDK and other frameworks accept MCP servers directly. You'll meet them in the Frameworks section. Writing the loop yourself once is how you'll know what they're doing.

</div>

### On other providers

Your server doesn't change at all for other providers: MCP is an open protocol, and OpenAI-based apps, VS Code, Cursor and agent frameworks connect to it the same way Claude Code does. Only the host code in `agent.py` is Claude-specific. On OpenAI's Chat Completions API, `to_claude_tool` would produce `{"type": "function", "function": {"name": ..., "description": ..., "parameters": tool.input_schema}}`, tool calls arrive in `message.tool_calls` with arguments as a JSON *string* you must `json.loads`, and results go back as messages with `"role": "tool"` and a `tool_call_id`. The same code runs against a local open model through Ollama's [OpenAI-compatible API](https://docs.ollama.com/api/openai-compatibility) by pointing the OpenAI client at `http://localhost:11434/v1`. OpenAI's [function calling guide](https://developers.openai.com/api/docs/guides/function-calling) shows the full loop, and the [OpenAI Agents SDK MCP docs](https://openai.github.io/openai-agents-python/mcp/) show a framework launching stdio servers for you. The `MCPServer` and `Client` classes, the Inspector and your pytest tests are all provider-neutral.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Work through the Python version of [Build an MCP server](https://modelcontextprotocol.io/docs/develop/build-server) on the official site. You'll build a weather server on the free US National Weather Service API and connect it to Claude Desktop.
   - Read the logging warning near the top carefully before you write any code.
   - If you don't use Claude Desktop, connect the server to Claude Code instead, using the next item.
1. Read [Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp) to learn how to add, list and remove servers in Claude Code, and what the local, project and user scopes mean.
1. Read the MCP Python SDK docs, starting from the [SDK README](https://github.com/modelcontextprotocol/python-sdk) and its [documentation site](https://py.sdk.modelcontextprotocol.io/).
   - Read "First steps," [Testing](https://py.sdk.modelcontextprotocol.io/get-started/testing/) and [Handling errors](https://py.sdk.modelcontextprotocol.io/servers/handling-errors/). Skim [Connect to a real host](https://py.sdk.modelcontextprotocol.io/get-started/real-host/).
1. Read the [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) docs. Then build this lesson's reading-list server and use the Inspector to call every tool, read the resource and fill in the prompt, including at least two calls with bad arguments.
1. Practice: extend the reading-list server.
   - Add a `reading_set_status(book_id, status)` tool with a clear description and constrained arguments, and a `reading://books/{book_id}` resource template that returns one book.
   - Write pytest tests for the new tool, including one error case each for an unknown id and an invalid status. Make them pass.
   - Connect the server to Claude Code or Claude Desktop and complete three tasks in plain English. Write down any time the model picked the wrong tool or bad arguments, change a description, and try again.
1. Practice: browse the [reference servers repository](https://github.com/modelcontextprotocol/servers), pick one server (the filesystem or git server are good choices), and read its tool definitions. Write down two things it does well and one thing you'd change, based on Designing Tools for Agents.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Which package and class do you use to build a Python MCP server today, and what did older tutorials call the class?](#setting-up-the-project)
- [Where does the SDK get a tool's name, description and input schema?](#a-server-in-one-file)
- [When should data be a resource rather than a tool?](#descriptions-are-still-prompts)
- [What's the difference between raising ToolError and letting any other exception escape a tool?](#errors-the-model-can-act-on)
- [Why must a stdio server never print to standard output, and what should it use instead?](#never-print-in-a-stdio-server)
- [What does the Inspector let you separate before a model is involved?](#testing-with-the-inspector)
- [How does a host connect to a stdio server, and why do paths in its config need to be absolute?](#connecting-to-a-real-host)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Connect to local MCP servers](https://modelcontextprotocol.io/docs/develop/connect-local-servers) walks through installing the reference filesystem server in Claude Desktop, with a helpful troubleshooting section.
- The SDK's [migration guide](https://py.sdk.modelcontextprotocol.io/migration/) lists everything that changed between version 1 and version 2, useful when you adapt older example code.
- The [Hugging Face MCP Course](https://huggingface.co/learn/mcp-course) has more hands-on server-building units. Its Python examples use the older `FastMCP` name.
