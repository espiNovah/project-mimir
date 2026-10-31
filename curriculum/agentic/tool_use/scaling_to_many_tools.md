### Introduction

A demo agent has three tools. A real one connected to email, a calendar, a CRM and a few internal systems can easily have a hundred. Every tool definition takes up space in the context window on every request, and every tool result passes through the model even when only one line of it matters. Worse, a model choosing from a hundred similar-looking tools picks the wrong one more often than a model choosing from five. This lesson covers the techniques that let agents work with large toolsets without drowning in tokens or confusion: organizing tools, sending only the ones a request needs, loading tools on demand, letting the model call tools from code, and measuring whether any of it actually helped.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why large toolsets hurt both cost and accuracy.
- Grouping and namespacing tools so they are easier to choose between.
- Routing each request to a smaller set of tools.
- Tool search: discovering tool definitions on demand instead of loading them all.
- Programmatic tool calling and tool use examples.
- Measuring tool-selection accuracy with a small eval.
- How to decide when these techniques are worth the extra complexity.

### What every tool costs

Remember from Function Calling that the model never sees your Python code, only the tool definitions. The API turns those definitions into text and puts them at the front of the prompt, before the system prompt and the conversation. That happens on **every request**, and an agent makes a request on every step of its loop.

A short tool with one parameter costs a few dozen tokens. A well-written one, with the three-or-four-sentence description that Designing Tools for Agents recommends and a described parameter or two, costs a few hundred. The API also adds a fixed block of tool-use instructions whenever you pass any tools at all. Now multiply: fifty good tools can take tens of thousands of tokens before the user has said a word. Anthropic's tool search docs give a concrete example: connecting five common services (GitHub, Slack, Sentry, Grafana and Splunk) through MCP, which you'll meet later in this path, adds about 55,000 tokens of definitions. A 15-step run pays that 15 times.

Tool *results* have the same problem from the other direction. In a normal loop, if the agent fetches 1,000 spreadsheet rows to find three, all 1,000 rows land in its context and stay there for the rest of the run, pushing up the cost of every later step and crowding out the information that matters. You saw this as rising input tokens in your traces in Agent Tracing and Debugging.

### More tools, more wrong picks

Cost isn't the only problem. Every tool you add is another option the model must rule out, and options start to look alike. With `search_docs`, `search_files`, `search_drive` and `find_document` all available, which one holds the travel policy? A person would ask. A model guesses, and guesses differently from run to run.

Large menus cause three kinds of mistakes, the same ones you learned to spot in traces:

- **Wrong tool:** two descriptions overlap, so the model picks the one you didn't mean.
- **Invented arguments:** the model picks a tool that needs an ID it doesn't have yet, and makes one up instead of calling the lookup tool first.
- **No tool at all:** the right tool is buried, so the model answers from memory.

Anthropic's docs report that tool selection starts to degrade once a model has more than roughly 30 to 50 tools. Treat that as a warning sign, not a law. The number depends on the model and on how distinct your tools are, which is why this lesson ends with a way to measure it for *your* tools.

### Group and namespace your tools

The cheapest fix is organization, and it costs no extra code at runtime. Designing Tools for Agents introduced two ideas that matter even more at scale:

- **Namespacing:** prefix every tool name with its service or resource, such as `calendar_create_event` and `email_send`. The prefix tells the model which family a tool belongs to, it lets your code group tools by family, and it makes tool search work better, as you'll see below.
- **Consolidation:** fewer, more capable tools beat many thin ones. Three tools that each move a deal to one stage can become one `crm_update_deal` with a `stage` parameter.

Here is a small catalog of twelve namespaced tools for an office assistant. The `tool` helper keeps each definition to a few lines. Save it as `catalog.py`; the rest of this lesson builds on it:

```python
# catalog.py: a namespaced tool catalog
def tool(name: str, description: str, **params: str) -> dict:
    """Build a tool whose parameters are all required strings."""
    return {"name": name, "description": description,
            "input_schema": {"type": "object",
                             "properties": {p: {"type": "string", "description": d}
                                            for p, d in params.items()},
                             "required": list(params)}}


CATALOG = [
    tool("calendar_list_events", "List events on the user's calendar between two dates.",
         start="First day, YYYY-MM-DD", end="Last day, YYYY-MM-DD"),
    tool("calendar_create_event", "Create a calendar event. Only use after the user confirms a time.",
         title="Event title", start="Start, ISO 8601", end="End, ISO 8601"),
    tool("calendar_find_free_time", "Find open slots of a given length in the user's calendar.",
         day="Day to search, YYYY-MM-DD", minutes="Length of the slot in minutes"),
    tool("email_search", "Search the user's inbox by sender, subject or words in the message.",
         query="Search words, for example 'from:dana invoice'"),
    tool("email_send", "Send a new email. Only use when the user asks to send something.",
         to="Recipient address", subject="Subject line", body="Plain-text body"),
    tool("email_draft_reply", "Save a draft reply to an email without sending it.",
         message_id="ID from email_search", body="Plain-text body"),
    tool("crm_find_contact", "Look up a customer contact in the CRM by name or company.",
         query="Name or company"),
    tool("crm_update_deal", "Move a sales deal to a new stage in the CRM.",
         deal_id="Deal ID from crm_find_contact", stage="One of: lead, demo, proposal, won, lost"),
    tool("crm_log_call", "Add notes about a phone call to a CRM contact.",
         contact_id="Contact ID from crm_find_contact", notes="What was discussed"),
    tool("files_search", "Search the shared drive for documents by title or content.",
         query="Search words"),
    tool("files_read", "Read the text of one document from the shared drive.",
         path="Path from files_search"),
    tool("files_share", "Share a document with someone by email.",
         path="Path from files_search", email="Address to share with"),
]
```

Notice that the descriptions are short so the example stays readable. Real ones should be longer, which only makes the token problem bigger. Also notice parameter descriptions like "Deal ID from crm_find_contact". They tell the model which tool must come first, which prevents the invented-arguments mistake.

### Route each request to a smaller set

If a request is about the calendar, the model doesn't need to see the CRM tools. **Routing** means your code picks a subset of tools for each request before calling the model. You'll meet routing as a general workflow pattern in Chaining and Routing; here it's applied to tools. Add this to `catalog.py`:

```python
KEYWORDS = {                                       # namespace -> words that suggest it
    "calendar": ("calendar", "meeting", "schedule", "free", "busy"),
    "email": ("email", "inbox", "reply", "send", "message"),
    "crm": ("customer", "contact", "deal", "crm", "call"),
    "files": ("file", "doc", "document", "drive", "share"),
}


def route(request: str) -> list[dict]:
    """Send only the namespaces the request mentions; fall back to everything."""
    words = request.lower()
    picked = {ns for ns, hints in KEYWORDS.items() if any(h in words for h in hints)}
    return [t for t in CATALOG if t["name"].split("_")[0] in picked] or CATALOG
```

Namespacing is what makes this easy: `t["name"].split("_")[0]` turns `crm_log_call` into `crm`. The `or CATALOG` at the end is the important line. When the router isn't sure, it sends everything rather than nothing, because a model with too many tools can still succeed, while a model with none can't.

Keyword matching is the simplest router and a fine start. Two common upgrades are a call to the [cheap model](#/models) that classifies the request into namespaces, and an embedding search that compares the request with each tool description, using the embeddings you learned in the RAG section. A third kind of routing uses the application's state: an agent in "billing mode" only gets billing tools.

Routing has costs of its own. A router that guesses wrong hides the right tool, which is worse than a long menu, so routing needs its own eval. It also decides once, up front, which doesn't suit a multi-step run that drifts from email into the calendar. And it changes the tool list from request to request, which defeats **prompt caching**, a feature most providers offer that makes repeated prompt prefixes cheaper. Because tool definitions sit at the very front of the prompt, a different tool list means a different prefix. Caching was introduced in Core, and Agent Cost and Latency shows how it applies to agent runs.

### Tool search and deferred loading

**Tool search** flips routing around: instead of your code guessing which tools a request needs, the model looks them up itself, the way you'd search the docs for a function. It starts with only a few tools loaded plus a search tool. When it needs something else, it searches, and the matching definitions are added to its context.

Claude offers this as a built-in server tool, so the following is **specific to the Claude API**. You still send every definition in `tools`, but you mark most of them with `"defer_loading": True`. Deferred tools aren't shown to the model until a search finds them. Add this to `catalog.py`:

```python
def with_tool_search(always_loaded: tuple[str, ...] = ("email_search", "calendar_list_events")) -> list[dict]:
    """Claude-specific: defer every tool except a few, and add the search tool."""
    search = {"type": "tool_search_tool_bm25_20251119", "name": "tool_search_tool_bm25"}
    return [search] + [t if t["name"] in always_loaded else {**t, "defer_loading": True}
                       for t in CATALOG]
```

You pass the result as `tools=with_tool_search()`, and the rest of your loop stays the same. When the model searches, the response contains two extra blocks before its normal `tool_use` request: a `server_tool_use` block (the search itself, which the API runs) and a `tool_search_tool_result` block listing the tools it found. You keep them in the history like any other content, but you never send a `tool_result` for them, because the search isn't your tool. A few rules from the docs:

- **The search tool itself is never deferred**, and at least one tool must stay loaded. Keep your three to five most-used tools loaded, so common requests don't pay for a search.
- **There are two variants.** The BM25 one searches with natural-language queries (BM25 is the keyword-ranking method you met in Hybrid Search); the regex one has the model write search patterns. Both search tool names, descriptions and parameter names, so namespaced names and good keywords in descriptions make tools easier to find.
- **It keeps the prompt cache working**, because found definitions are added later in the conversation instead of changing the tool list at the front.
- **You can bring your own search.** If you'd rather use embeddings, write a client tool that runs your search and returns `tool_reference` blocks naming the tools it found.

Anthropic's docs suggest considering tool search once you have about ten or more tools, or more than 10,000 tokens of definitions. Below that, the extra search step usually costs more than it saves. Other providers and agent frameworks are adding similar features under different names; when one isn't available, the "bring your own search" pattern works anywhere: a `find_tools` tool whose results your code adds to the tool list on the next request.

### Programmatic tool calling

Tool search shrinks the definitions. **Programmatic tool calling** shrinks the results. Instead of one model round trip per tool call, the model writes a short Python script that calls your tools as functions, loops over the results, filters them and returns only a summary. The script runs in a sandbox, and the intermediate data never enters the model's context.

Anthropic's docs give a good example: checking which of 20 employees went over their travel budget. The normal way takes 20 round trips and pulls thousands of expense lines into the context. With programmatic calling, one script does all 20 lookups and hands back just the names of the people over budget.

This is also **specific to the Claude API**. You add the code execution server tool to `tools`, and on each tool you want callable from code you add `"allowed_callers": ["code_execution_20260120"]`. When the script calls one of your tools, the API pauses and sends you an ordinary `tool_use` block with a `caller` field saying it came from code. You run the tool and return a `tool_result` as usual, and the script carries on. It shines for multi-step data work: aggregating, filtering, or calling the same tool in a loop. It adds little for a single lookup, and a sandbox that runs model-written code is something you must budget for and secure, a topic you'll come back to in the Safety section. You'll see the same idea again in MCP, in the "code execution with MCP" pattern, where tools are presented as code the agent can import rather than as a long list of definitions.

### Show examples, not only schemas

A JSON Schema says which fields exist, but not which combinations make sense. Should a date be `2026-11-03` or `next Tuesday`? When is an optional field worth including? Examples teach conventions like these better than descriptions do.

The Claude API has an `input_examples` field on tool definitions for this: a list of example argument objects, each of which must match the tool's schema. Each one costs tokens, from a couple of dozen for a simple example to a couple of hundred for a nested one, so save them for tools with tricky inputs. On any provider, you can get most of the benefit by putting one or two example calls in the tool's description. Both work alongside tool search: a found tool brings its examples with it.

### Measure tool-selection accuracy

Every technique above trades something away: routing can hide tools, tool search adds a step, and examples cost tokens. The only way to know whether a change helped is to measure it. The question to measure is narrow and cheap to answer: **for a given request, is the first tool the model calls the right one?** You don't need to run the tools or finish the task, just one model call per case.

First, look at what each setup costs. Claude's token counting endpoint, `count_tokens`, counts a request's input tokens without running the model, and it's free to use within its own rate limits. That endpoint is a Claude API feature: OpenAI has a [similar one](https://developers.openai.com/api/docs/guides/token-counting) for its Responses API, and with a local model you can read the input token count from the `usage` of a real request. Save this as `count_tool_tokens.py`:

```python
# count_tool_tokens.py  (uv add anthropic python-dotenv)
import os

import anthropic
from dotenv import load_dotenv

from catalog import CATALOG, route, with_tool_search

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
client = anthropic.Anthropic()
QUESTION = [{"role": "user", "content": "Is anything on my calendar tomorrow?"}]


def count(tools: list[dict]) -> int:
    kwargs = {"tools": tools} if tools else {}
    return client.messages.count_tokens(model=MODEL, messages=QUESTION, **kwargs).input_tokens


baseline = count([])
for label, tools in [("one namespace (routed)", route(QUESTION[0]["content"])),
                     ("all 12 tools", CATALOG),
                     ("tool search, 2 loaded", with_tool_search())]:
    total = count(tools)
    print(f"{label:<24} {total:>6} tokens  ({total - baseline} for tools)")
print(f"{'no tools':<24} {baseline:>6} tokens")
```

Then check accuracy. Each case pairs a request with the set of tools that would be an acceptable first move. Some requests have more than one good start, and an empty set means the right move is no tool at all. Save this as `selection_eval.py`:

```python
# selection_eval.py: does the model pick the right first tool?
import math
import os

import anthropic
from dotenv import load_dotenv

from catalog import CATALOG, route, with_tool_search

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
client = anthropic.Anthropic()

CASES = [  # (request, acceptable first tools); an empty set means "no tool at all"
    ("What's on my calendar on 2026-11-03?", {"calendar_list_events"}),
    ("Find me a free 30 minutes on Friday 2026-10-30.", {"calendar_find_free_time"}),
    ("Did Dana email me about the invoice?", {"email_search"}),
    ("Reply to Dana's last email saying I'll pay tomorrow, but don't send it yet.", {"email_search"}),
    ("Move the Acme deal to proposal.", {"crm_find_contact"}),
    ("Log that I called Priya at Globex and she wants a demo.", {"crm_find_contact"}),
    ("Share the Q3 report with sam@example.com.", {"files_search"}),
    ("What does our travel policy doc say about trains?", {"files_search"}),
    ("Book a meeting with the Acme team next week.", {"calendar_find_free_time", "crm_find_contact"}),
    ("Thanks, that's everything for today!", set()),
]
CONFIGS = {"all tools": lambda request: CATALOG,
           "routed": route,
           "tool search": lambda request: with_tool_search()}


def first_tool(request: str, tools: list[dict]) -> tuple[str | None, int]:
    response = client.messages.create(model=MODEL, max_tokens=4000, tools=tools,
                                      messages=[{"role": "user", "content": request}])
    names = [b.name for b in response.content if b.type == "tool_use"]  # client tools only
    return (names[0] if names else None), response.usage.input_tokens


for config, pick_tools in CONFIGS.items():
    hits, tokens, misses = 0, 0, []
    for request, accept in CASES:
        picked, used = first_tool(request, pick_tools(request))
        tokens += used
        if (picked in accept) or (picked is None and not accept):
            hits += 1
        else:
            misses.append(f"    {request!r}: picked {picked}, wanted {sorted(accept) or 'no tool'}")
    n = len(CASES)
    p = hits / n
    margin = 1.96 * math.sqrt(p * (1 - p) / n)                       # from Eval Statistics
    print(f"{config:<12} accuracy {hits}/{n} = {p:.0%} (±{margin:.0%})  "
          f"avg input tokens {tokens // n}")
    print("\n".join(misses))
```

Run both with `uv run`. The output gives you, for each setup, an accuracy, a rough 95% interval, the average input tokens per request and a list of misses. A few things to notice when you read it:

- **Read the misses, not just the score.** A miss like `'Move the Acme deal to proposal.': picked crm_update_deal` means the model called the update tool without the deal ID it needs, which is the invented-arguments mistake. The fix is in a description, not in the routing.
- **The search tool's own call isn't counted.** `first_tool` only looks at blocks of type `tool_use`. With tool search, the search appears as a `server_tool_use` block, so the score reflects the tool the model chose after searching.
- **Ten cases is a smoke test, not a verdict.** With 10 cases the interval is about ±30 points, and at 10 out of 10 the simple formula claims ±0%, which Eval Statistics warned you is wrong. Grow the set from real requests and real misses in your traces, run each case a few times, and since every setup runs on the same cases, compare them with the paired method from Eval Statistics.
- **Look at accuracy and tokens together.** A setup that's as accurate and uses half the tokens is a win. One that saves tokens but drops accuracy usually isn't, because a wrong tool call costs whole extra steps.

### Optimizations, not defaults

None of these techniques belong in a three-tool agent. Each adds code, moving parts and new ways to fail. A sensible order is:

1. **Organize first:** namespace, consolidate and write clear descriptions. It's free and helps every other technique.
1. **Measure:** count tokens and run a selection eval on your real requests.
1. **Then reach for a technique that matches the problem you measured.** Too many definition tokens or falling accuracy as the catalog grows suggests routing or tool search. Big intermediate results suggest programmatic tool calling or better-shaped tool outputs. Badly formatted arguments suggest examples.

The Agent Loop From Scratch project doesn't need any of them, which is the point. Knowing when *not* to add a technique is as much a skill as knowing how.

### On other providers

The first half of this lesson holds on every provider: tool definitions cost tokens on every request, namespacing and consolidation help any model choose, and the router in `catalog.py` is plain Python that picks a subset before the call. Tool search, programmatic tool calling and `input_examples`, as written here, are Claude features. OpenAI has its own [tool search](https://developers.openai.com/api/docs/guides/tools-tool-search) in the Responses API on recent models, built on the same `defer_loading` idea, but you set it up differently (a `tool_search` tool, ideally with deferred functions grouped into `namespace` objects), so Claude's search-tool types and `tool_search_tool_result` blocks don't carry over. With an open model there's no server-side search at all, so retrieve tools yourself: embed each tool description, send only the closest few for each request, or give the model a `find_tools` tool as described above. The selection eval carries over almost unchanged, and it's the right way to check a new model, because how many tools a model handles well varies a lot from model to model. Here is `first_tool` for a local model through [Ollama's OpenAI-compatible API](https://docs.ollama.com/api/openai-compatibility); use it in `selection_eval.py` with the "all tools" and "routed" configs and drop "tool search":

```python
from openai import OpenAI  # uv add openai

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")  # a local model via Ollama

def as_openai(tools: list[dict]) -> list[dict]:
    return [{"type": "function", "function": {"name": t["name"], "description": t["description"],
             "parameters": t["input_schema"]}} for t in tools]

def first_tool(request: str, tools: list[dict]) -> tuple[str | None, int]:
    response = client.chat.completions.create(model="qwen3:4b", tools=as_openai(tools),
                                              messages=[{"role": "user", "content": request}])
    calls = response.choices[0].message.tool_calls or []
    return (calls[0].function.name if calls else None), response.usage.prompt_tokens
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Introducing advanced tool use](https://www.anthropic.com/research/advanced-tool-use) from Anthropic (November 2025). It explains tool search, programmatic tool calling and tool use examples, and when to use each.
1. Read "How tool search works" and "When to use tool search" in the [Tool search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool) docs.
   - Also read "Custom tool search implementation" to see how your own search can return `tool_reference` blocks.
1. Read the introduction and "How programmatic tool calling works" in the [Programmatic tool calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling) docs.
   - Look at the budget-checking example and count how many model round trips it saves.
1. Read "Providing tool use examples" in [Define tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools), and reread its best practices on consolidating and namespacing tools.
1. Practice: count the tokens your tool definitions use. Take the tools from your previous practice exercises, send a request with and without them using the [token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting) endpoint, and write down the difference. Multiply it by 50 tools to see why these techniques exist. Then run `count_tool_tokens.py` from this lesson and compare the three setups.
1. Practice: run `selection_eval.py` from this lesson and improve the results.
   - Add five cases of your own, including two that the keyword router sends to the wrong namespace (try a request that never uses any of its keywords).
   - Read every miss, change one tool description or the router, and rerun. Report the before and after accuracy for each setup, with the number of cases.
   - If the intervals confuse you, redo the [evals exercise](https://github.com/espiNovah/project-mimir/tree/main/exercises/evals) on pass rates and standard errors (`04_pass_rate_se`).

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Why do tool definitions cost tokens on every step of an agent loop, not just once?](#what-every-tool-costs)
- [What three kinds of mistakes become more common as the tool list grows?](#more-tools-more-wrong-picks)
- [How do namespacing and consolidation help a model choose between tools?](#group-and-namespace-your-tools)
- [What does a tool router do, and why should it fall back to the full tool list when unsure?](#route-each-request-to-a-smaller-set)
- [How does tool search with deferred loading work, and which tools should stay loaded?](#tool-search-and-deferred-loading)
- [What problem does programmatic tool calling solve that tool search doesn't?](#programmatic-tool-calling)
- [How would you measure whether routing or tool search improved tool selection for your agent?](#measure-tool-selection-accuracy)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Code execution with MCP](https://www.anthropic.com/research/code-execution-with-mcp) from Anthropic shows the same "tools as code" idea applied to MCP servers, a preview of the MCP section.
- The [tool search with embeddings](https://platform.claude.com/cookbook/tool-use-tool-search-with-embeddings) cookbook builds a custom client-side tool search with embeddings, end to end.
- [RAG-MCP: Mitigating Prompt Bloat in LLM Tool Selection](https://arxiv.org/abs/2505.03275) is a short research paper that measures how tool selection degrades as the tool list grows and tests retrieving tools before each request, much like the router in this lesson.
