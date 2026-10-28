<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

In the Tool Use section you wrote tools directly into your agent's code. That works for one agent, but it does not scale: every app that wants to talk to GitHub, a database or your calendar would need its own integration. The **Model Context Protocol (MCP)** is an open standard that fixes this. You write an integration once, as an MCP server, and any MCP-compatible app (Claude Code, Claude Desktop, IDEs and many agent frameworks) can use it. In this lesson you will learn the pieces of MCP and how they fit together, using the current version of the specification, dated 2026-07-28.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The problem MCP solves, and why it is often compared to a USB-C port for AI apps.
- The three participants: hosts, clients and servers.
- The data layer and the transport layer.
- The three server primitives: tools, resources and prompts.
- What "stateless" means in the 2026-07-28 spec, and how discovery works.
- Which older features are deprecated, and why you should not build on them.

### Key ideas

- **MCP turns many-to-many integrations into one standard.** Without it, every AI app needs custom code for every service. With it, a service ships one MCP server and every compatible app can use it.
- **There are three participants.** The **host** is the AI application the user works in, such as Claude Code. The host creates one **client** per connection, and each client talks to one **server**, a program that provides tools and data. A server can run locally on your machine or remotely on the internet.
- **MCP has two layers.** The *data layer* defines the messages, using JSON-RPC 2.0 (a simple format for sending requests and responses as JSON). The *transport layer* defines how those messages travel: over standard input and output for local servers (stdio), or over HTTP for remote ones (Streamable HTTP). You will study transports in the MCP Transports and Security lesson.
- **Servers offer three primitives.** **Tools** are functions the model can call, like the tools you already built. **Resources** are read-only data the app can load into context, such as a file or a database schema, each identified by a URI. **Prompts** are reusable templates a user can pick, such as "summarize this pull request."
- **Who controls each primitive differs.** The model decides when to call tools. The application or user decides which resources to attach. The user chooses prompts explicitly.
- **The 2026-07-28 spec is stateless.** There is no longer an initialization handshake or session ID. Every request carries its own protocol version and capabilities, and clients can ask a server what it supports with a `server/discover` request. This makes servers simpler to write and much easier to run behind ordinary web infrastructure.
- **Some older features are deprecated.** Sampling (a server asking the client's model for a completion), Roots (a client telling a server which folders it may use) and the Logging feature are deprecated, as is the old HTTP+SSE transport. Many older tutorials still teach them. For new servers, call model APIs directly, use configuration instead of roots, and log to standard error.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [MCP introduction](https://modelcontextprotocol.io/) on the official site to see what MCP is for and which apps support it.
1. Read the [MCP architecture overview](https://modelcontextprotocol.io/docs/learn/architecture). This is the core reading for the lesson.
   - Read "Participants," "Layers" and "Data Layer Protocol" carefully, including "Statelessness and discovery" and "Primitives." Skim the worked example.
1. Read [Understanding MCP servers](https://modelcontextprotocol.io/docs/learn/server-concepts) for more detail on tools, resources and prompts, and who controls each.
1. Skim the [specification changelog for 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/changelog). Make a list of what was removed or deprecated, so you can spot outdated advice in older tutorials and videos.
1. Practice: draw a diagram (on paper or in any drawing tool) of Claude Code connected to two MCP servers, one local and one remote. Label the host, each client, each server, the transport each one uses, and one tool, resource and prompt each server might offer.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- Anthropic Academy's [Introduction to Model Context Protocol](https://anthropic.skilljar.com/introduction-to-model-context-protocol) is a free video course that walks through MCP concepts and a first server. It requires a free account. Check that what it teaches matches the 2026-07-28 spec.
- The [Hugging Face MCP Course](https://huggingface.co/learn/mcp-course) is a free, longer course with hands-on units. Parts of it predate the stateless spec, so treat details like the initialization handshake as history.
