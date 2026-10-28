<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Now that you know what MCP servers are, it is time to build one. The good news: with the official Python SDK, a working server is a few decorated functions. The SDK reads your type hints and docstrings and turns them into tool definitions, handles the protocol for you, and gives you a command to open your server in the **MCP Inspector**, a testing tool that lets you call tools by hand before any model touches them. In this lesson you will build a small server, test it, and connect it to a real AI app.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Setting up an MCP server project with `uv` and the Python SDK.
- Defining tools and resources with decorators, type hints and docstrings.
- Testing a server with the MCP Inspector.
- Why a stdio server must never print to standard output.
- Connecting a server to Claude Desktop or Claude Code.
- Applying good tool design to MCP tools.

### Key ideas

- **The SDK does the protocol work.** You install the SDK with `uv add "mcp[cli]"`, create a server object, and decorate ordinary Python functions with `@mcp.tool()` or `@mcp.resource("some://uri")`. Type hints become the input schema and the docstring becomes the description.
- **Descriptions are still prompts.** Everything from the Designing Tools for Agents lesson applies: clear names, descriptions that say when to use a tool, specific parameters and compact outputs. An MCP server is just a reusable way of shipping tools.
- **Resources are for data, tools are for actions.** Expose a database schema, a config file or a document as a resource the app can attach. Expose "search," "create" or "update" as tools.
- **Test with the Inspector before a model.** The Inspector connects to your server, lists its tools and resources, and lets you call them with any arguments you like. This separates "my server is broken" from "the model is using it wrong."
- **Never write to standard output in a stdio server.** In the stdio transport, standard output carries the protocol messages. A stray `print()` corrupts them and breaks the connection. Use the `logging` module, which writes to standard error.
- **Connecting to a host is a config entry.** Claude Desktop reads a JSON config file listing servers and the command to start each one; Claude Code adds servers with the `claude mcp add` command. Once connected, the host's model can discover and call your tools.
- **Handle errors in the tool, not in the protocol.** Return clear, instructive error messages from tools (for example, "City not found; try a nearby larger city"), exactly as you did in the Tool Errors and Parallel Calls lesson.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Work through the Python version of [Build an MCP server](https://modelcontextprotocol.io/docs/develop/build-server) on the official site. You will build a weather server on the free US National Weather Service API and connect it to Claude Desktop.
   - Read the logging warning near the top carefully before you write any code.
   - If you do not use Claude Desktop, connect the server to Claude Code instead, using the guide in the next item.
1. Read the README of the [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk), especially "A server in 15 lines" and how to open a server with `mcp dev`.
1. Read the [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) docs and use it to call every tool in your weather server by hand, including one call with bad arguments.
1. Read [Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp) to learn how to add, list and remove servers in Claude Code.
1. Practice: browse the [reference servers repository](https://github.com/modelcontextprotocol/servers), pick one server (the filesystem or git server are good choices), and read its tool definitions. Write down two things it does well and one thing you would change, based on Writing effective tools for agents.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Connect to local MCP servers](https://modelcontextprotocol.io/docs/develop/connect-local-servers) walks through installing the reference filesystem server in Claude Desktop, with a helpful troubleshooting section.
- The [Hugging Face MCP Course](https://huggingface.co/learn/mcp-course) has more hands-on server-building units.
