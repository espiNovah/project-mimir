<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Subagents report back to the agent that called them. A handoff is different: one agent passes the whole conversation to another, and the new agent takes over. Customer support is the classic example. A triage agent figures out what you need, then hands you to a billing agent or a technical agent. This lesson covers handoffs inside one app, and then briefly looks at the Agent2Agent (A2A) protocol for agents built by different teams to talk to each other, and how it relates to MCP.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The difference between delegating to a subagent and handing off control.
- Handoffs in the OpenAI Agents SDK.
- What context to pass along, and what to filter out.
- Handoffs versus a router workflow.
- The A2A protocol in brief.
- How A2A and MCP fit together.

### Key ideas

- **Delegation returns, a handoff transfers.** With a subagent, the caller stays in charge and gets a result. With a handoff, the receiving agent now owns the conversation with the user until it finishes or hands off again.
- **A handoff is usually a tool call.** In the OpenAI Agents SDK, each possible handoff appears to the model as a tool such as `transfer_to_billing_agent`. Calling it switches which agent's instructions and tools are active.
- **Decide what history travels.** Passing everything keeps context but can confuse the new agent with instructions meant for the old one. Input filters let you trim or summarize the history during the handoff.
- **Often a router is enough.** If the choice of specialist is made once at the start, the routing workflow from the workflow patterns section is simpler and easier to test. Use handoffs when agents need to pass control back and forth during a conversation.
- **A2A connects agents across team and vendor lines.** It is an open protocol for one agent to discover another (through an "agent card" describing its skills), send it a task and receive results, without seeing its internals.
- **MCP connects an agent to tools, A2A connects agents to agents.** An agent might use MCP to call a database tool and A2A to ask a partner company's agent to do a job. Most projects only need MCP. Reach for A2A only when the other side is itself an independent agent you don't control.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [OpenAI Agents SDK handoffs docs](https://openai.github.io/openai-agents-python/handoffs/).
   - Note how handoffs are declared, how input filters work and the recommended prompt prefix.
1. Read [A2A and MCP](https://a2a-protocol.org/latest/topics/a2a-and-mcp/) from the A2A protocol docs.
   - Write two example systems in one sentence each: one that needs only MCP and one where A2A makes sense.
1. Reread the routing section of [Building effective agents](https://www.anthropic.com/research/building-effective-agents) and compare it with handoffs.
1. Build a small support bot with a triage agent and two specialist agents that hand off to each other. Test five conversations, including one where the user changes topic midway, and record whether each one reached the right agent.

</div>
