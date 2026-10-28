### Introduction

Once you know how function calling works, the hard part is no longer the plumbing. It is designing tools the model actually uses well. A tool with a vague name, a confusing schema or a huge, noisy output will make even a strong model stumble. In this lesson you will learn to treat tools as an interface for a new kind of user: one that is smart, literal and has a limited attention span.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why tools for agents are different from APIs for programmers.
- Choosing which tools to build, and which to merge, split or leave out.
- Writing names, descriptions and parameters the model understands.
- Designing tool outputs that are small, relevant and readable.
- Writing error messages the model can act on.
- Testing and improving tools by watching transcripts.

### Tools are prompts for a new kind of user

When you design an API for programmers, you can count on a few things. A programmer reads the documentation once, writes code that calls the API, tests it, and from then on the call happens the same way every time. If the docs are confusing, they ask a colleague or read the source.

A model is a different kind of user. In Function Calling you learned that **the model never sees your code**. All it has is the tool's name, its description and its input schema. And it doesn't learn your tool once and remember it. On every single turn of the loop it rereads those definitions and decides afresh whether to use the tool, which one, and with what arguments. It's also **non-deterministic**: given the same situation twice, it may choose differently.

So a tool definition is really a prompt. It gets sent with every request, it shapes every decision the model makes, and everything you learned in the Prompting section applies to it. Picture a smart new teammate on their first day: capable, but with no context beyond what you write down, and who takes your words literally.

Designing for that reader comes down to four questions, which the rest of this lesson takes one at a time. Which tools should exist? What should they be called and how should they be described? What arguments should they take? And what should they send back, both when they work and when they don't?

### Choosing which tools to build

The instinct of most programmers is to wrap every endpoint of an existing API as a tool. If the calendar service has `list_users`, `list_events` and `create_event`, you make three tools. This usually works badly.

Think about what the model has to do with those three tools to handle "book an hour with Femi next week." It lists users to find Femi's ID, lists her events, works out the free slots itself by reading every event, then creates one. That's three round trips, a pile of raw data and several chances to make a mistake. A person doing this task would never think of it as three operations. They'd think "schedule a meeting."

So the first rule is: **build tools around tasks, not endpoints.** A single `schedule_meeting(attendee_names, duration_minutes, earliest_date)` tool can find the people, check calendars and book the first free slot inside your code, where loops and date arithmetic are cheap and reliable. The model makes one decision instead of five. This is **consolidating** tools: merging several thin wrappers into one higher-level tool that matches what someone would actually ask for.

Consolidating has limits, though. Sometimes you should **split** a tool instead:

- **When one tool does unrelated things.** A `manage_files(action, ...)` tool with fourteen possible actions and a different set of arguments for each is just fourteen tools wearing a disguise, with a harder schema to fill in.
- **When the risks differ.** Reading a record and deleting it should be separate tools, so your code can require approval for one and not the other.
- **When the model needs the intermediate result.** If the agent has to look at search results and judge which one is relevant, a search tool and a separate fetch tool let it do that.

The third option is to **leave a tool out.** Every tool you add makes every request longer and gives the model one more option to weigh. If a capability isn't needed for the tasks your agent actually does, don't offer it. A small set of well-chosen tools beats a large set of overlapping ones, especially when two tools look similar and the model has to guess which one you meant.

When you do have many tools, **namespace** them: give related tools a shared prefix that says what system they belong to, such as `github_search_issues` and `github_create_issue`, or `directory_search_contacts`. Prefixes help the model tell apart tools from different services that would otherwise have the same name, like two different `search` tools. Scaling to Many Tools, later in this section, covers what to do when you have dozens.

### Names and descriptions

Names and descriptions do most of the work in getting a tool used correctly. Compare these two definitions for the same function:

```python
BAD_TOOL = {
    "name": "contacts",
    "description": "Gets contacts.",
    "input_schema": {"type": "object", "properties": {"q": {"type": "string"}}},
}
```

The model can't tell from this whether `contacts` reads, creates or deletes, what `q` should contain, whether it matches part of a name, or what comes back. It will guess, and guesses vary from turn to turn.

A good **name** is a short verb phrase that says exactly what happens: `search_contacts`, not `contacts` or `contact_helper`. A good **description** is written the way you'd explain the tool to that new teammate, in a few full sentences:

- **What it does**, in plain words.
- **When to use it**, and when not to. "Use this whenever you need someone's email, instead of guessing" is a direct instruction to the model, and trigger conditions like this measurably improve how often the right tool gets called.
- **How the inputs behave**: is matching exact or partial? Case-sensitive? What format do dates take?
- **What it returns**, including limits, such as "at most 20 results."
- **An example call**, if the arguments are at all tricky.

Long descriptions are fine. A tool definition of a few hundred tokens that gets used correctly is far cheaper than a short one that causes two wrong calls per task. You'll see a full, well-described tool in the code example below.

### Input schemas that are hard to misuse

The input schema is the part of the definition that lists the arguments. Your goal is to make wrong arguments hard to send. Anthropic's Building Effective Agents calls this **poka-yoke**, a Japanese manufacturing term for designs that make mistakes difficult, like a plug that only fits one way round.

A few habits get you most of the way:

- **Specific parameter names.** `user_id` instead of `user`, `start_date` instead of `date`, `duration_minutes` instead of `duration`. The name alone should rule out the most likely misunderstanding.
- **A description on every parameter**, with an example value: "Full or partial name, such as 'Grace' or 'okafor'."
- **Enums for fixed choices.** If a field can only be `"sales"`, `"support"`, `"engineering"` or `"finance"`, list those values with `enum`. The model can't invent `"Sales Team"`.
- **Sensible defaults, stated in the description.** "Use 5 unless you need more" tells the model what a normal call looks like.
- **Fewer arguments.** Every optional argument is a decision the model has to make. If your code can work something out itself, don't ask for it.

Some providers can also enforce the schema. In Tool Errors and Parallel Calls you'll see `"strict": True`, which makes the API guarantee the arguments match your schema's types, fields and enums. Strict mode supports only part of JSON Schema, though. It doesn't enforce number ranges or string lengths, so rules like "between 1 and 20" still need a check in your code, and the description should state them so the model gets them right the first time.

### Returning what the agent needs

Here's the cost most people miss: **every token a tool returns stays in the conversation for the rest of the task.** You learned in The Agent Loop that the message list is the agent's whole state and gets resent on every turn. A tool that dumps a 5,000-token record into the conversation makes every later step slower and more expensive, and it buries the useful part where the model is more likely to miss it.

So design outputs as carefully as inputs:

- **Return only the relevant fields.** If the agent asked for an email, it doesn't need `avatar_url`, `created_at` and an internal database ID.
- **Prefer human-readable values to opaque IDs.** "Grace Kim, sales" is something the model can reason about and repeat to a user. `usr_00074` isn't, and models are more likely to garble a long random ID when copying it. Include an ID only when a later tool call needs it.
- **Cap the size.** Paginate or truncate big results, and when you cut something off, say so and say how to get the rest: "62 more matches not shown; add a team or more letters to narrow." That note steers the model toward a better search instead of a bigger one.
- **Offer a detail level.** A `response_format` argument with `"concise"` and `"detailed"` options lets the model ask for the small version by default and the full version only when the task needs it.

### Errors the model can act on

Errors are part of the interface too. When a call fails, the error message is the only thing the model has to decide its next step. "Error" teaches it nothing, so it guesses again. "No one named like 'Hiro Tanaka' in the sales team. Check the spelling, search with fewer letters, or set team to 'any'" tells it exactly how to succeed on the next try.

A good error message says **what went wrong**, **what's true instead** and **what to do next**. The next lesson, Tool Errors and Parallel Calls, covers how to send errors back as tool results and how to stop an agent from repeating the same failing call. For now, the design point is this: when you write a tool, write its error messages at the same time, for the same reader as the description.

### A well-designed tool in code

Here is a directory search tool that puts all of this together. It's one consolidated tool (search by name, filtered by team) with a namespaced name, a description that says when to use it, an enum for the team, an explicit limit, a detail level, compact results and errors that point at the fix. Save it as `contacts.py`:

```python
import itertools
import json
import random

random.seed(7)                               # the same fake directory every run
FIRST = ["Ada", "Ben", "Chioma", "Dev", "Elena", "Femi", "Grace", "Hiro", "Ines", "Jamal"]
LAST = ["Okafor", "Smith", "Tanaka", "Silva", "Novak", "Mensah", "Garcia", "Kim"]
TEAMS = ["sales", "support", "engineering", "finance"]
CONTACTS = [                                 # 80 people, one per first/last pair
    {"id": f"usr_{i:05d}", "name": f"{first} {last}",
     "team": random.choice(TEAMS), "email": f"person{i}@example.com",
     "phone": f"+1-555-{i:04d}", "created_at": "2024-03-01T09:00:00Z",
     "avatar_url": f"https://example.com/avatars/{i}.png", "timezone": "UTC"}
    for i, (first, last) in enumerate(itertools.product(FIRST, LAST))
]

SEARCH_CONTACTS = {
    "name": "directory_search_contacts",
    "description": (
        "Search the company directory for people by name, in one team or all teams. "
        "Use this whenever you need someone's email or team, instead of guessing. "
        "Matching is case-insensitive and matches part of a name, so 'okaf' finds "
        "'Ada Okafor'. Returns at most `limit` matches, plus a count of any "
        "extra matches. Example: {\"name\": \"grace\", \"team\": \"sales\", "
        "\"limit\": 5, \"response_format\": \"concise\"}."
    ),
    "strict": True,                          # arguments always match this schema
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string",
                     "description": "Full or partial name, such as 'Grace' or 'okafor'."},
            "team": {"type": "string", "enum": ["any", "sales", "support", "engineering", "finance"],
                     "description": "Limit to one team, or 'any' for all teams."},
            "limit": {"type": "integer",
                      "description": "Maximum results to return, 1 to 20. Use 5 unless you need more."},
            "response_format": {"type": "string", "enum": ["concise", "detailed"],
                                "description": "'concise' returns name, team and email. "
                                               "'detailed' adds id, phone and timezone."},
        },
        "required": ["name", "team", "limit", "response_format"],
        "additionalProperties": False,
    },
}


def directory_search_contacts(name: str, team: str, limit: int, response_format: str) -> str:
    if not 1 <= limit <= 20:                 # strict mode can't enforce ranges, so check here
        raise ValueError(f"limit must be between 1 and 20, got {limit}. Try 5.")
    query = name.strip().lower()
    if len(query) < 2:
        raise ValueError("name must have at least 2 letters, such as 'gr' or 'grace'.")
    matches = [c for c in CONTACTS
               if query in c["name"].lower() and team in ("any", c["team"])]
    if not matches:
        teams = "any team" if team == "any" else f"the {team} team"
        raise ValueError(f"No one named like '{name}' in {teams}. Check the spelling, "
                         "search with fewer letters, or set team to 'any'.")
    fields = (["name", "team", "email"] if response_format == "concise"
              else ["id", "name", "team", "email", "phone", "timezone"])
    shown = [{f: c[f] for f in fields} for c in matches[:limit]]
    extra = len(matches) - len(shown)
    note = f" {extra} more matches not shown; add a team or more letters to narrow." if extra else ""
    return json.dumps(shown) + note
```

A few things to notice:

- **Every property is in `required`, and the optional-feeling ones have a neutral value instead.** `team` can be `"any"`, and the description says to use a `limit` of 5. Strict mode works best with this shape, and it means the model always makes an explicit choice.
- **The range check lives in code**, because strict mode doesn't enforce `minimum` or `maximum`. The error message names the rule and suggests a value.
- **The whole directory is about 4,500 tokens** of JSON. A typical concise search returns under 20. Multiply that difference by every remaining step of a task and you'll see why output design matters.
- **The function raises `ValueError` for problems the model can fix.** The loop below catches those and sends them back as error results, so a bad call becomes an observation instead of a crash.

### Testing tools by watching transcripts

You can't tell whether a tool is well designed by reading it. You find out by watching an agent use it. The loop is simple: write a few **realistic tasks**, run the agent on them, read the **transcript** (the full record of every call and result), and change the tool wherever the agent got confused.

This script does exactly that. It runs three tasks through a small agent loop and prints every call, the size of every result and the final answer. Save it as `watch.py` next to `contacts.py`, run `uv add anthropic python-dotenv` if you haven't, and run it with `uv run watch.py`:

```python
import json
import os

import anthropic
from dotenv import load_dotenv

from contacts import SEARCH_CONTACTS, directory_search_contacts

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
client = anthropic.Anthropic()
TOOLS = [SEARCH_CONTACTS]
FUNCTIONS = {"directory_search_contacts": directory_search_contacts}

TASKS = [                                    # realistic requests, not toy ones
    "What's Grace Kim's email address?",
    "Who on the finance team is called Femi? I need their phone numbers.",
    "Find the email for Hiro Tanaka. I think he's in sales.",
]


def run(task: str, max_steps: int = 6) -> None:
    print(f"\n=== TASK: {task}")
    messages = [{"role": "user", "content": task}]
    for step in range(1, max_steps + 1):
        response = client.messages.create(model=MODEL, max_tokens=2000,
                                          tools=TOOLS, messages=messages)
        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":
            text = "".join(b.text for b in response.content if b.type == "text")
            print(f"ANSWER ({step - 1} tool steps): {text}")
            return
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            print(f"CALL   {block.name}({json.dumps(block.input)})")
            try:
                output, failed = FUNCTIONS[block.name](**block.input), False
            except ValueError as err:        # expected failures become messages for the model
                output, failed = str(err), True
            print(f"RESULT {'ERROR ' if failed else ''}~{len(output) // 4} tokens: {output[:120]}")
            results.append({"type": "tool_result", "tool_use_id": block.id,
                            "content": output, "is_error": failed})
        messages.append({"role": "user", "content": results})
    print(f"STOPPED after {max_steps} steps")


for task in TASKS:
    run(task)
```

The third task is the interesting one. The user is wrong about Hiro's team, so the first search fails. A healthy transcript looks like this:

```text
=== TASK: Find the email for Hiro Tanaka. I think he's in sales.
CALL   directory_search_contacts({"name": "Hiro Tanaka", "team": "sales", "limit": 5, "response_format": "concise"})
RESULT ERROR ~29 tokens: No one named like 'Hiro Tanaka' in the sales team. Check the spelling, search with fewer letters, or set team to 'any'.
CALL   directory_search_contacts({"name": "Hiro Tanaka", "team": "any", "limit": 5, "response_format": "concise"})
RESULT ~19 tokens: [{"name": "Hiro Tanaka", "team": "support", "email": "person58@example.com"}]
ANSWER (2 tool steps): Hiro Tanaka is on the support team, not sales. His email is person58@example.com.
```

The error told the model what to do, and it did it. Your runs may differ, because the model isn't deterministic, so run each task a few times.

When you read transcripts, look for these signs of a tool problem:

- **The model didn't call the tool when it should have**, and answered from memory instead. The description probably doesn't say clearly enough when to use it.
- **It sent arguments in the wrong shape**, like a full sentence in a name field. A parameter description or an example is missing.
- **It called the same tool several times to do one job.** Maybe the tool should be consolidated, or its results are too thin to be useful.
- **It asked for `"detailed"` when `"concise"` would do**, or results are big and full of fields nobody used. Trim the output.
- **It retried the same failing call.** The error message isn't telling it what to change.

Then change one thing, run the same tasks again and compare. This is error analysis, the habit you built in Measuring Quality, applied to tools. You can even paste a few transcripts and your tool definitions into a chat with a capable model and ask it to point out where the descriptions are ambiguous. It's often good at spotting the sentence that misled it. In Agent Eval Fundamentals you'll turn these checks into a proper eval with graders and repeated trials.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Writing effective tools for agents](https://www.anthropic.com/research/writing-tools-for-agents) from Anthropic. This is the core reading for the lesson, and the Project: Agent Loop From Scratch and Project: Your Own MCP Server both expect you to follow its advice.
   - Read the whole article. Take notes on the "Principles for writing effective tools" section in particular.
1. Read "Appendix 2: Prompt engineering your tools" at the end of [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents). It is short and gives concrete advice, including the idea of "poka-yoke" (mistake-proofing) your tool arguments.
1. Read "Best practices for tool definitions" in [Define tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools), and skim [Strict tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use) to see how a schema can be enforced and which schema features it supports.
1. Practice with this lesson's code: run `watch.py` with the [cheap model](#/models), then break the tool on purpose and watch what changes.
   - Run it three times and save the transcripts. Did the model always pick sensible arguments?
   - Replace the "No one named like..." error with just `"Not found."` and rerun the Hiro Tanaka task five times. Count how often the model recovers. Then make every search return all fields for all matches, and compare the token sizes. Write a short note on what you saw.
1. Practice on your own tool: take the `get_word_length` tool from Function Calling, or any tool you have written, and rewrite its definition using what you learned. Then write a deliberately bad version (vague name, one-line description, unclear parameter). Run both on the same five questions and record how often the model calls each one correctly.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Why is a tool definition effectively a prompt, and how is a model different from a programmer as a user of your API?](#tools-are-prompts-for-a-new-kind-of-user)
- [When should you consolidate several tools into one, and when should you split one apart?](#choosing-which-tools-to-build)
- [What five things should a good tool description cover?](#names-and-descriptions)
- [Name three ways to make a tool's input schema hard to misuse.](#input-schemas-that-are-hard-to-misuse)
- [Why does the size of a tool's output matter for the rest of the task, and how can you keep it small?](#returning-what-the-agent-needs)
- [What three things should a tool's error message tell the model?](#errors-the-model-can-act-on)
- [What signs in a transcript point to a badly designed tool?](#testing-tools-by-watching-transcripts)
