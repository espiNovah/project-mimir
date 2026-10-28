<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Some actions should never happen without a person saying yes: sending money, emailing a customer, deleting records, pushing code to production. Human-in-the-loop design is about putting those checkpoints in the right places. If there are too few, mistakes slip through. If there are too many, people approve everything without reading, which is no protection at all. This lesson covers how to decide what needs approval, how to build approval into an agent so it can pause and resume, and how permission systems in real agent tools work.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Classifying actions by how reversible and how risky they are.
- Approval fatigue and why more prompts can mean less safety.
- Allow, ask and deny rules in permission systems.
- Pausing an agent for approval and resuming it later.
- Showing the approver the right information.
- Logging approvals for audit.

### Key ideas

- **Classify actions by reversibility and blast radius.** Reading is usually safe. Writing a draft is easy to undo. Sending, paying, deleting and deploying are hard or impossible to undo and affect other people. Require approval for the last group, and let the rest run.
- **Approval fatigue is real.** People shown dozens of prompts start approving without reading. Cut the number of prompts with sandboxes and allowlists, so the prompts that remain matter.
- **Permission systems use allow, ask and deny rules.** Tools like Claude Code let you allow some tools or commands outright, require a prompt for others and block some completely. Deny rules should win over allow rules.
- **Approval must live in code, not the prompt.** "Ask the user before sending email" in a system prompt is a suggestion the model can skip or be tricked out of. Put the check in the tool or the harness, so the action can't run without a recorded yes.
- **Agents need to pause and resume.** A real approval can take hours. Frameworks support this with interrupts or checkpoints: the run saves its state, waits for a human decision and continues from the same point.
- **Show what will actually happen.** The approver should see the exact action and its arguments (the recipient, amount or diff), not the model's summary of them, which may be wrong or manipulated.
- **Keep an audit trail.** Record who approved what, when and what was executed. It helps with debugging, with compliance and with deciding later which approvals you can safely automate.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [Claude Code permissions docs](https://code.claude.com/docs/en/permissions) to see allow, ask and deny rules and permission modes in a real tool.
1. Read the [Agent SDK permissions guide](https://code.claude.com/docs/en/agent-sdk/permissions) and skim [Agent SDK hooks](https://code.claude.com/docs/en/agent-sdk/hooks).
   - Note how your own code can approve, deny or change a tool call before it runs.
1. Read either the [OpenAI Agents SDK human-in-the-loop guide](https://openai.github.io/openai-agents-python/human_in_the_loop/) or the [LangGraph interrupts docs](https://docs.langchain.com/oss/python/langgraph/interrupts).
   - Focus on how a run pauses, where its state is stored and how it resumes.
1. Revisit [How we built Claude Code auto mode](https://www.anthropic.com/research/claude-code-auto-mode) with one question in mind: which decisions did Anthropic move from a human to an automated reviewer, and which did they keep with the human?
1. Add an approval gate to one of your agents for one irreversible tool. Show the exact arguments to the approver, log every decision to a file and confirm that the tool can't run without approval even if the prompt tells the model to skip it.

</div>
