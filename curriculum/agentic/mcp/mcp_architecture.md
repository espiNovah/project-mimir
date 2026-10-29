### Introduction

In the Tool Use section you wrote tools directly into your agent's code. That works for one agent, but it doesn't scale: every app that wants to talk to GitHub, a database or your calendar would need its own copy of that integration. The **Model Context Protocol (MCP)** is an open standard that fixes this. You write an integration once, as an MCP server, and any MCP-compatible app (Claude Code, Claude Desktop, ChatGPT, VS Code, Cursor and many agent frameworks) can use it.

In this lesson you'll learn the pieces of MCP and how they fit together, and you'll follow one tool all the way from a server to a model. Everything here uses the current version of the specification, **2026-07-28** (checked on 2026-10-29 at [modelcontextprotocol.io](https://modelcontextprotocol.io/specification/2026-07-28)). MCP changes quickly, so the lesson also shows you how to spot outdated advice.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The problem MCP solves, and why it's often compared to a USB-C port for AI apps.
- The three participants: hosts, clients and servers.
- The data layer and the transport layer.
- The server primitives (tools, resources and prompts) and the client primitive, elicitation.
- What "stateless" means in the 2026-07-28 spec, and how discovery and capabilities work.
- How an MCP tool reaches the model, step by step.
- When MCP is worth it, and when plain function calling is enough.

### The integration problem

Picture five AI apps (a coding assistant, a chat app, an IDE plugin, your own agent, a teammate's agent) and five services they'd like to use (GitHub, Postgres, Slack, Google Drive, your company's ticket system). Without a standard, every app writes its own code for every service: 5 × 5 = 25 integrations, each with its own bugs and its own idea of what a "search issues" tool should look like. Add a sixth service and five more integrations need writing.

MCP turns that multiplication into addition. Each service ships **one** MCP server. Each app implements **one** MCP client. Now 5 apps and 5 services need 10 pieces of code, and any app can use any server. That's why MCP is often compared to a USB-C port: the laptop doesn't need to know who made the monitor, only that both speak the same plug.

MCP was created by Anthropic in late 2024 and is now an open project with its own governance, SDKs in many languages, and support from most AI app makers. It's not a Claude feature. A server you write in this section works in any host that speaks MCP, whichever model sits behind it.

### Hosts, clients and servers

MCP has three participants, and the words are easy to mix up, so be precise:

- The **host** is the AI application the user works in, such as Claude Code, Claude Desktop or VS Code. It owns the conversation and the model.
- A **client** is a small component *inside* the host that speaks MCP. The host creates **one client per server connection**. Connect Claude Code to three servers and it runs three clients.
- A **server** is a program that offers tools and data. It never talks to the model directly. It only answers its client.

Servers come in two kinds. A **local** server runs on your machine as a child process of the host, for example the reference filesystem server that reads files in a folder you choose. A **remote** server runs somewhere on the internet, for example a company's hosted server for its own product, and many users connect to the same one. A local server usually serves one client; a remote server serves many.

Notice what this split means for trust. The host decides which servers to connect to, what to show the model, and when to ask the user for permission. The server only sees the requests its client sends. Keep that picture in mind, because the security lesson later in this section builds on it.

### Two layers

MCP is split into two layers, the same way the web separates "what's in an HTTP request" from "how bytes cross the network."

The **data layer** defines the messages. MCP uses **JSON-RPC 2.0**, a simple format for requests and responses written as JSON. A request has a `method` (such as `tools/list` or `tools/call`), `params` and an `id`; the response carries the same `id` and either a `result` or an `error`. A **notification** is a message with no `id`, which expects no reply.

The **transport layer** defines how those messages travel. There are two standard transports:

- **stdio**: the host starts the server as a subprocess and they exchange messages over the server's standard input and output. Used for local servers.
- **Streamable HTTP**: the client sends each message as an HTTP POST to one URL, such as `https://example.com/mcp`. Used for remote servers.

Because the layers are separate, the same server code can run over either transport without changing a single tool. You'll study transports, and the security each one needs, in MCP Transports and Security.

### Server primitives

A **primitive** is a kind of thing one side can offer the other. Servers offer three:

- **Tools** are functions the model can call, exactly like the tools you built in Function Calling. A tool has a name, a description and an input schema, and calling it can have side effects: searching, creating, sending.
- **Resources** are read-only data identified by a **URI** (a uniform resource identifier, an address like `file:///notes/todo.md` or `postgres://shop/schema`). A database schema, a config file or a list of valid categories are good resources. A URI with a placeholder, such as `books://{title}`, is a **resource template**: one definition that covers many resources.
- **Prompts** are reusable message templates the user picks by name, such as "summarize this pull request." In Claude Code, server prompts show up as slash commands.

What really separates them is **who decides to use each one**:

| Primitive | Controlled by | Example |
| --- | --- | --- |
| Tools | The model | The model calls `github_search_issues` in the middle of a task |
| Resources | The application or user | The user attaches the database schema to the conversation |
| Prompts | The user | The user runs `/review-pr` |

That table explains a common beginner mistake: putting everything in tools. If some data should *always* be in context, or should only be added when the user asks, it's a resource. If it's an action the model should decide to take, it's a tool. A rough analogy from web APIs: a resource is like a `GET` (load data, change nothing), and a tool is like a `POST` (do work).

### Elicitation and other client features

Communication also goes the other way. MCP defines **elicitation**, a primitive the *client* offers: a server can ask the user a question in the middle of a tool call. A `delete_folder` tool might ask "This folder has 12 files. Delete anyway?", and the host shows that question to the user as a form. The answer comes from a person, not from the model, which makes elicitation a useful safety tool you'll use in the security lesson. There's also a URL mode, where the server sends the user to a web page (to pay, or to log in) so that sensitive data never passes through the model at all.

In the 2026-07-28 spec, elicitation uses a pattern called **multi round-trip requests**: instead of the server sending a request of its own, it answers the tool call with "input required" plus the question, and the client retries the original call with the user's answer attached. You won't need the details, because the SDK handles them, but it explains why old tutorials that show a server "calling back" into the client look different.

A few smaller features round out the protocol: **notifications** (for example, "my tool list changed"), progress updates for slow calls, argument autocompletion, and optional **extensions** such as Tasks, which lets a server hand back a handle for a long-running job that the client polls later.

### Statelessness and discovery

Earlier versions of MCP began every connection with an `initialize` handshake: the client and server agreed on a protocol version and swapped capabilities once, and the server remembered that session. The 2026-07-28 spec removed it. MCP is now **stateless**: every request carries what the server needs to answer it, in a `_meta` field holding the protocol version and the client's **capabilities** (the features it supports, such as elicitation). Any server instance can answer any request, which makes remote servers far easier to run behind ordinary web infrastructure.

To learn what a server supports, a client sends a `server/discover` request, which every server must implement. Here's a real exchange with the reading-list server you'll build in the next lesson, captured over HTTP (lightly shortened):

```json
{"jsonrpc": "2.0", "id": 1, "method": "server/discover",
 "params": {"_meta": {"io.modelcontextprotocol/protocolVersion": "2026-07-28",
                      "io.modelcontextprotocol/clientCapabilities": {}}}}

{"jsonrpc": "2.0", "id": 1, "result": {
   "resultType": "complete",
   "supportedVersions": ["2026-07-28"],
   "capabilities": {"tools": {"listChanged": true},
                    "resources": {"listChanged": true, "subscribe": true},
                    "prompts": {"listChanged": true}},
   "instructions": "Search the list before adding a book.",
   "_meta": {"io.modelcontextprotocol/serverInfo": {"name": "reading-list", "version": ""}}}}
```

This is **capability negotiation** in its modern form. The server lists what it offers (`tools`, `resources`, `prompts`, and `listChanged` meaning it can announce changes), and the client only calls methods for capabilities the server declared. The client declares its own capabilities on every request, so a server knows, for example, whether it may ask for elicitation. If the versions don't match, the server answers with an `UnsupportedProtocolVersionError` listing the versions it does support, and the client retries with one of them. Discovery is optional: a client may simply send `tools/list` straight away and handle a version error if one comes back.

### How an MCP tool reaches the model

Here is the path one tool takes, from server to model and back:

1. **Connect and discover.** The host starts or connects to the server, and its client learns the server's capabilities.
1. **List.** The client sends `tools/list`. The server returns each tool's `name`, `description` and `inputSchema`.
1. **Translate.** The host converts each MCP tool into its model provider's tool format and adds it to the request, alongside any tools of its own. This is the key step: **the model never speaks MCP.** It sees ordinary tool definitions, exactly like the ones you wrote by hand.
1. **Call.** When the model replies with a tool call, the host looks up which server owns that tool and sends `tools/call` with the arguments.
1. **Return.** The server's result (a list of content blocks, plus an `isError` flag) goes back to the model as an ordinary tool result.

You can watch steps 1 to 5 yourself without an API key. Install the SDK in a scratch project (`uv init mcp-peek && cd mcp-peek && uv add "mcp[cli]"`), save this as `peek.py`, and run `uv run peek.py`:

```python
"""See what a host sees: discover a server, list its tools, turn one into a Claude tool."""
import json

import anyio
from mcp import Client
from mcp.server import MCPServer

server = MCPServer("weather")                     # the server side, in the same file for now


@server.tool()
def weather_current(city: str) -> str:
    """Get the current weather for one city. Returns a one-line summary."""
    return f"{city}: 22°C, clear"                 # a fake; a real server would call an API


async def main() -> None:
    async with Client(server) as client:          # the client side: connect in memory
        print("protocol version:", client.protocol_version)
        print("server capabilities:", client.server_capabilities.model_dump(exclude_none=True))

        tool = (await client.list_tools()).tools[0]           # MCP's tools/list
        claude_tool = {"name": tool.name,                     # the host's translation step
                       "description": tool.description,
                       "input_schema": tool.input_schema}
        print(json.dumps(claude_tool, indent=2))

        result = await client.call_tool("weather_current", {"city": "Lagos"})  # tools/call
        print("result:", result.content[0].text, "| is_error:", result.is_error)


anyio.run(main)
```

The output shows `protocol version: 2026-07-28`, the capabilities, a tool definition with `name`, `description` and `input_schema` (built by the SDK from the type hint `city: str` and the docstring), and finally `result: Lagos: 22°C, clear | is_error: False`. That dictionary in the middle is exactly what you'd pass in `tools=[...]` to the Claude API. `anyio.run` starts the async code, just like `asyncio.run` from Async Basics; the MCP SDK uses `anyio`, a library that works on top of `asyncio`.

Two consequences follow. First, **everything from Designing Tools for Agents still applies.** An MCP tool's description is a prompt, written by whoever wrote the server. Second, the host can only show the model what servers send. A server's description lands in your model's context exactly as written, which is why you'll learn to treat third-party servers with care.

### Outdated features to avoid

Many tutorials, videos and even some SDK examples were written for earlier versions. Here's what the 2026-07-28 spec removed or deprecated (**deprecated** means it still works for now but is scheduled for removal, so new code shouldn't use it):

- **Removed:** the `initialize` handshake, protocol sessions and the `Mcp-Session-Id` header, the `ping` method and `logging/setLevel`.
- **Deprecated:** **sampling** (a server asking the host's model for a completion; call a model API directly instead), **roots** (a client telling a server which folders it may use; pass paths as tool arguments or configuration instead), the **logging** feature (log to standard error instead), and the old **HTTP+SSE transport** from 2024 (use Streamable HTTP).

One more naming change affects Python specifically: in version 2 of the official SDK, the `FastMCP` class was renamed `MCPServer`. If a tutorial imports `from mcp.server.fastmcp import FastMCP`, it was written for the old SDK.

### When MCP is worth it

MCP is a way of *packaging and sharing* tools. It doesn't make a tool smarter, and it adds a process, a protocol and a dependency. So ask who will use the tool.

**Use plain function calling** when the tools exist for one agent you're building, live in the same codebase, and won't be reused. A `lookup_order` tool inside your support bot's backend is simplest as a Python function plus a tool definition, as in the Agent Loop From Scratch project. There's nothing to install and nothing to version separately.

**Use MCP** when:

- **More than one app should use the tool.** You want your team's ticket system available in Claude Code, in an IDE and in your own agent. One server serves all of them.
- **You want to use tools someone else already built.** Thousands of servers exist for popular services. Connecting one is a config entry instead of a week of work, as long as you trust it.
- **The tool belongs to a different team or runs elsewhere.** A remote MCP server lets the team that owns a database expose safe operations on it, with its own auth, without handing out credentials.
- **Users, not developers, choose the tools.** Hosts like Claude Desktop let people add servers themselves.

A useful middle path: write your tools as normal Python functions first. If they prove useful beyond one agent, wrapping them in an MCP server is a few decorators, as you'll see in the next lesson.

### On other providers

MCP is an open protocol, so almost nothing in this lesson is Claude-specific. Hosts built on OpenAI, Gemini and open models use MCP servers the same way: list the tools, translate them into the provider's tool format, route calls back. The translation step is where providers differ. In `peek.py`, the `input_schema` key is Claude's name for the schema; for OpenAI you'd put the same schema under `parameters`, as you saw in Function Calling, and local models served by Ollama accept OpenAI-style tool definitions too (see [Ollama's tool calling docs](https://docs.ollama.com/capabilities/tool-calling)). Some providers can also connect to *remote* MCP servers for you, so your code never runs a client: OpenAI's Responses API has an `mcp` tool type described in its [MCP and connectors guide](https://developers.openai.com/api/docs/guides/tools-connectors-mcp), and the Claude API has a similar MCP connector (a Claude feature, in beta). Both only reach remote servers over HTTP, not local stdio servers.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [MCP introduction](https://modelcontextprotocol.io/) on the official site to see what MCP is for and which apps support it.
1. Read the [MCP architecture overview](https://modelcontextprotocol.io/docs/learn/architecture). This is the core reading for the lesson.
   - Read "Participants," "Layers" and "Data Layer Protocol" carefully, including "Statelessness and discovery" and "Primitives." Then read the worked example, comparing its messages with the `server/discover` exchange in this lesson.
1. Read [Understanding MCP servers](https://modelcontextprotocol.io/docs/learn/server-concepts) for more detail on tools, resources and prompts, and who controls each. Skim [Understanding MCP clients](https://modelcontextprotocol.io/docs/learn/client-concepts) for elicitation.
1. Skim the [specification changelog for 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/changelog). Make a list of what was removed or deprecated, so you can spot outdated advice in older tutorials and videos.
1. Practice: run `peek.py` from this lesson, then extend it.
   - Add a second tool and a resource (`@server.resource("weather://cities")` returning a list of supported cities). Print the result of `client.list_resources()` and read the resource with `client.read_resource("weather://cities")`.
   - Write a `to_openai_tool(tool)` function next to the Claude translation, and print both for the same tool.
1. Practice: draw a diagram (on paper or in any drawing tool) of Claude Code connected to two MCP servers, one local and one remote. Label the host, each client, each server, the transport each one uses, and one tool, resource and prompt each server might offer.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What problem does MCP solve, and why does it turn many-to-many integrations into one standard?](#the-integration-problem)
- [What are the host, the client and the server, and how many clients does a host create?](#hosts-clients-and-servers)
- [What does the data layer define, and what does the transport layer define?](#two-layers)
- [Who controls tools, resources and prompts, and how would you decide whether something should be a tool or a resource?](#server-primitives)
- [What does "stateless" mean in the 2026-07-28 spec, and what does server/discover tell a client?](#statelessness-and-discovery)
- [Does the model ever see MCP? What does the host do between tools/list and the model?](#how-an-mcp-tool-reaches-the-model)
- [When is plain function calling a better choice than an MCP server?](#when-mcp-is-worth-it)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- The [2026-07-28 specification](https://modelcontextprotocol.io/specification/2026-07-28) is the source of truth when a tutorial and the spec disagree.
- Anthropic Academy's [Introduction to Model Context Protocol](https://anthropic.skilljar.com/introduction-to-model-context-protocol) is a free video course that walks through MCP concepts and a first server. It requires a free account. Check that what it teaches matches the 2026-07-28 spec.
- The [Hugging Face MCP Course](https://huggingface.co/learn/mcp-course) is a free, longer course with hands-on units. Parts of it predate the stateless spec and the `MCPServer` rename, so treat details like the initialization handshake and `FastMCP` as history.
