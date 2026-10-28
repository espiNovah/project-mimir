### Introduction

In this project you will build an MCP server that other people can actually install and use. You will pick a real API or dataset, design a small set of tools and a resource around the tasks people want to do with it, test it thoroughly with the MCP Inspector, and connect it to a real AI app. Then you will publish it with instructions clear enough that a stranger could set it up in five minutes.

This is one of the most portfolio-friendly projects in the curriculum. A well-designed, documented MCP server for a useful data source is something other developers can try immediately, and it shows you understand tool design, protocols and security, not just prompting.

### Before you start

- Create a new GitHub repository named `mimir-mcp-<your-topic>`, for example `mimir-mcp-library-catalog` or `mimir-mcp-citibike`. Set it up as a `uv` project and add the SDK with `uv add "mcp[cli]"`.
- Choose a data source that is free and does not require you to share private credentials. Good options: a public API with a free tier or no key (weather, public transit, open government data, Wikipedia, a book catalog), or a public dataset (CSV or SQLite) you download and ship with the server. Avoid sources whose terms forbid this kind of use.
- Target the **2026-07-28** MCP specification. Do not rely on sampling, roots or the old HTTP+SSE transport; they are deprecated. Check that your SDK version supports the current spec.
- Install a real MCP client to test with: Claude Desktop or Claude Code.
- Reread Writing effective tools for agents. Your tool descriptions will be judged against it.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Keep secrets out of your repo

If your API needs a key, read it from an environment variable and document which variable to set. Never commit a key, and never log it. A reviewer will search your commit history.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

#### Design

1. Before writing code, write `DESIGN.md` listing five realistic questions or tasks a user would bring to an AI app about your data (for example, "Which branches have this book available today?"). Design your tools around those tasks, not around the API's endpoints.
1. Provide at least three tools and at least one resource. The resource should be useful read-only context, such as a schema, a list of valid categories or a data dictionary.
1. Write every tool name, description and parameter following Writing effective tools for agents: say when to use the tool, give an example, use specific parameter names and enums where they fit, and keep outputs compact and human-readable. Offer a way to limit result size (such as a `limit` parameter) on any tool that can return many items.

#### Build

1. Return instructive error messages for bad input, empty results, rate limits and upstream API failures. No tool may crash the server.
1. Use the `logging` module for all diagnostics. The server must never write anything but protocol messages to standard output.
1. Add timeouts to every outbound network call.
1. Write `pytest` tests for your tool functions, including at least one error case per tool. Mock or record API responses so the tests run without network access.

#### Test and connect

1. Test every tool and the resource in the MCP Inspector. Include screenshots or a short recording in your README showing a successful call and an error call.
1. Connect the server to a real client (Claude Desktop or Claude Code) and complete at least three of the tasks from `DESIGN.md` through natural conversation. Save the transcripts or screenshots in a `demo/` folder.
1. Note any task where the model picked the wrong tool or passed bad arguments, change your descriptions to fix it, and record the before and after in your README.

#### Publish

1. Write install instructions that work from a fresh clone: prerequisites, any environment variables, the exact JSON block for Claude Desktop's config file and the exact `claude mcp add` command for Claude Code.
1. Ask one other person (a friend, or someone in the community) to follow your instructions from scratch, and fix whatever confuses them.
1. Push your project to GitHub with a README that explains what it does, how to run it, and what you learned.

#### Extra credit

- Also serve it over Streamable HTTP, bound to `127.0.0.1` with `Origin` validation, and show the Inspector connecting by URL.
- Add a prompt (an MCP prompt template) for a common workflow with your data.
- Write a tiny evaluation: 10 tasks with expected answers, run through a model connected to your server, with a pass rate you report and improve.
- Publish the package so users can run it with `uvx`, and list it in a public MCP server directory.

</div>

### Submitting your work

A strong submission is something a stranger can install and trust. Lead the README with what the server does and one example conversation, then the install steps. Include a table of tools and resources with one-line descriptions, the Inspector screenshots, the demo transcripts and a passing test run. Mention which spec version you target and which features you deliberately did not use. A short "security notes" section (what the server can access, what it never does, where keys come from) shows reviewers you took the MCP Transports and Security lesson seriously.
