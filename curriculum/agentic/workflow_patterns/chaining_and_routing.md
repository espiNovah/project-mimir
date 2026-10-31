### Introduction

Most useful LLM systems in production are not autonomous agents. They are workflows: a handful of model calls arranged in a fixed order by ordinary code. In this lesson you will learn the two simplest and most common patterns. **Prompt chaining** breaks a task into steps where each call builds on the last, with checks in between. **Routing** looks at an input first and sends it to the handler best suited to it. Together they solve a surprising share of real problems, at a fraction of an agent's cost.

You met chaining and gates briefly in Thinking and Prompt Chaining, back in the Prompting section. This lesson goes further. You'll treat each step as a contract, write gates that retry and escalate instead of just stopping, build a router that uses cheap rules before it spends money on a model, plan for the router being wrong, and evaluate each step on its own. These are exactly the pieces the Support Ticket Pipeline project at the end of this section asks you to build.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What the "augmented LLM" building block is.
- How to design a prompt chain where each step has a clear input and output.
- Programmatic gates that check, retry, repair or escalate.
- How routing works, and when rules beat a model as the classifier.
- What to do when the router is wrong, and routing to different models to save money.
- How to evaluate each step, and how to tell a chain or router beats a single prompt.

### The augmented LLM

Every pattern in this section is built from the same block. Anthropic's [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) calls it the **augmented LLM**: one model call that can be given extra powers, such as retrieved documents (from the RAG section), tools (from Tool Use) and memory. A single call to `messages.create` with a system prompt, some context and maybe a few tools is one augmented LLM.

A **workflow pattern** is a way of wiring several of these blocks together with your own Python. The model never decides the shape of the workflow. Your code does: it calls block A, looks at the result, maybe calls block B or block C, and returns. That is the difference from the agents you built in Tool Use, where the model chose the next action in a loop. In a workflow, every path is one you wrote, so every path is one you can test.

Keep that in mind through this section. The question is never "can a workflow do this?" but "is this workflow better than one well-written prompt?" Every extra block costs tokens and adds latency, the time the user waits. You'll learn to measure that at the end of this lesson.

### Chains are contracts between steps

**Prompt chaining** splits one big task into a sequence of smaller ones, where each step's output becomes the next step's input. In the Prompting section, you passed plain text from one step to the next. That works, but it leaves the next step (and your gate) to guess at the shape of what it received.

A sturdier habit is to treat every step as a function with a **contract**: a defined input and a defined output. The best way to define the output is structured output, which you learned in Getting Structured Output. Instead of "list the facts," step one returns a Pydantic object such as `Request(need: str, article_ids: list[str])`. Now step two receives exactly the fields it needs, and the gate between them can check those fields with ordinary code.

Three rules make chains easier to build and debug:

1. **One job per step.** "Understand the ticket" and "write a friendly reply" are different skills. A prompt that does both is harder to improve, because fixing the tone can break the understanding.
1. **Pass only what the next step needs.** If the drafting step only needs the customer's request and two help articles, don't send it the whole knowledge base. Less context means fewer tokens and fewer chances to grab the wrong fact.
1. **Log every intermediate output.** When the final reply is wrong, the logged outputs tell you which step to blame. This is the same habit as the traces you kept in Agent Tracing and Debugging.

The price of a chain is **latency**. Each step waits for the one before it, so a three-step chain takes roughly three times as long as one call. That is fine for an email reply that goes out in a minute, and painful for a chat answer the user is staring at.

### Gates that retry, repair or stop

A **gate** is plain code that checks an intermediate result before the chain moves on. Gates are cheap, fast and deterministic, which means they give the same answer every time. Typical gates check:

- **Format:** Did the step return valid JSON, or does `parsed_output` exist?
- **Limits:** Is the draft under 120 words? Is the list non-empty?
- **References:** Does every ID the model mentioned exist in your data? Models happily invent plausible IDs like `KB-104`, so this check catches real bugs.
- **Required content:** Does the reply cite at least one of the articles step one chose?

When a gate fails, your code has four choices. It can **stop** and return an error. It can **retry** the step, ideally with feedback that says what went wrong ("Your draft did not cite any article ID"), which fixes far more failures than a blind retry. It can **repair** the output with code, for example trimming whitespace or dropping an unknown ID. Or it can **escalate**, sending the case to a human review queue. Always cap retries. One retry with feedback is a good default; if the second try fails too, the problem is usually the prompt or the input, and more retries just burn money.

Here is a two-step chain for a school's IT help desk, with a gate after each step. Set up a project with `uv init workflows`, run `uv add anthropic pydantic python-dotenv`, and save this as `chain.py`:

```python
# chain.py  (run with: uv run chain.py)
import os
import re

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
client = anthropic.Anthropic()

KB = {  # the help articles a reply may cite
    "KB-101": "Password resets: use reset.school.example. Links expire after 15 minutes.",
    "KB-102": "Accounts lock after 5 failed logins and unlock on their own after 30 minutes.",
    "KB-201": "Broken laptops: bring them to room B12. Loaner laptops last 5 days.",
}


class Request(BaseModel):  # (1) the contract between step 1 and step 2
    need: str = Field(description="What the person actually wants, in one sentence")
    article_ids: list[str] = Field(description="IDs of the articles that answer it")


def extract(ticket: str, kb: dict[str, str]) -> Request | None:
    articles = "\n".join(f"{k}: {v}" for k, v in kb.items())
    response = client.messages.parse(
        model=MODEL, max_tokens=2000, output_format=Request,
        system=f"You triage help-desk tickets. Pick only from these articles:\n{articles}",
        messages=[{"role": "user", "content": f"<ticket>\n{ticket}\n</ticket>"}],
    )
    return response.parsed_output  # None if the model refused or was cut off


def draft(ticket: str, req: Request, kb: dict[str, str], feedback: str) -> str:
    cited = "\n".join(f"{i}: {kb[i]}" for i in req.article_ids)
    prompt = (f"Write a reply under 120 words. The person needs: {req.need}\n"
              f"Use only these articles, citing each ID in square brackets:\n{cited}\n\n"
              f"<ticket>\n{ticket}\n</ticket>")
    if feedback:  # (2) a retry carries the gate's complaint
        prompt += f"\n\nYour previous draft was rejected: {feedback} Fix that."
    response = client.messages.create(
        model=MODEL, max_tokens=2000, messages=[{"role": "user", "content": prompt}])
    return "".join(b.text for b in response.content if b.type == "text")


def check_draft(reply: str, req: Request) -> str:
    """Gate 2: plain code, no model. Returns '' when the draft passes."""
    if not set(re.findall(r"\[(KB-\d+)\]", reply)) & set(req.article_ids):
        return "It did not cite any of the chosen article IDs."
    if (words := len(reply.split())) > 120:
        return f"It was {words} words long; the limit is 120."
    return ""


def answer(ticket: str, kb: dict[str, str] = KB) -> dict:
    req = extract(ticket, kb)
    if req is None or not req.article_ids or any(i not in kb for i in req.article_ids):
        return {"status": "human_review", "why": "no valid articles"}  # (3) gate 1: escalate
    feedback = ""
    for attempt in (1, 2):  # (4) one try plus one retry, never more
        reply = draft(ticket, req, kb, feedback)
        feedback = check_draft(reply, req)
        print(f"  draft {attempt}: gate says {feedback or 'OK'}")  # log the verdict
        if not feedback:
            return {"status": "sent", "reply": reply, "attempts": attempt}
    return {"status": "human_review", "why": feedback, "draft": reply}


if __name__ == "__main__":
    print(answer("I typed my password wrong a bunch and now I'm locked out. Help!"))
```

Walk through the numbered comments:

1. **The contract.** `Request` is what step one promises step two. `messages.parse` sends its schema and hands back a validated object, so the gate deals with fields, not text. That helper and its `parsed_output` field belong to the Anthropic SDK; other SDKs have their own versions, shown in [On other providers](#on-other-providers).
1. **Retry with feedback.** The drafting prompt grows one sentence on a retry, the exact complaint from the gate. The model gets a specific thing to fix.
1. **Gate one escalates.** If step one found no articles, or invented an ID that isn't in `KB`, there's nothing safe to draft from. A human sees the ticket instead of the customer seeing a made-up answer.
1. **A hard cap.** Two drafts at most. A ticket that fails twice goes to review with the last draft and the reason attached, so the reviewer starts with context.

### Routing: classify, then specialize

**Routing** puts a decision at the front of the workflow. A first step classifies the input (is this an account problem, a hardware problem, or something else?), and code sends it to a **handler** built for that category: its own prompt, its own documents, maybe its own tools or model.

Why not one prompt that handles everything? Because prompts interfere with each other. Add three paragraphs about laptop repairs to a prompt that handles password resets, and the password answers often get worse: longer, vaguer, sometimes quoting the wrong policy. Tuning one prompt for one kind of input tends to hurt the others. With routing, each handler stays small and focused, and you can improve the hardware handler without touching the accounts one.

The classifier step is usually small, and this is where you save money. A good classifier has:

- **A fixed list of categories**, enforced with structured output (a `Literal` type in Pydantic), so the model can't invent a new one.
- **Short definitions** of each category in the prompt. Most routing errors come from fuzzy boundaries, and one line per category ("hardware: broken or missing devices") fixes many of them.
- **An "other" category** for anything that doesn't fit, including tickets that mix two issues.
- **A way to say "unsure"**, such as a `confident` field. A guess that admits it's a guess is much more useful than a confident wrong answer.
- **The [cheap model](#/models) at low effort.** Picking a label is an easy job, and the classifier runs on every single input. The `effort` setting is a Claude feature; other providers' reasoning models have similar knobs, and on a model without one, the cheap model alone is enough.

### Rules first, then a model

The cheapest classifier is not a model at all. Many inputs are obvious: a ticket that says "password" and nothing about devices is an accounts ticket. A **rule**, such as a regular expression (you learned these in Regular Expressions), can catch those in microseconds for free, and send only the unclear cases to the model.

Rules have a weakness: they're precise only on the inputs you thought of. "I forgot my laptop charger's password" matches both rules below. So use rules only when exactly one rule fires, and let the model handle everything else. Then measure how often each source (rules or model) is right, because a rule that looks obvious can still be wrong 20% of the time.

Save this next to `chain.py` as `router.py`:

```python
# router.py  (run with: uv run router.py)
import os
import re
from typing import Literal

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from chain import KB, answer

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
client = anthropic.Anthropic()


class Route(BaseModel):
    category: Literal["accounts", "hardware", "other"]
    confident: bool = Field(description="False if more than one category could fit")


RULES = [  # (1) cheap, precise rules for the obvious cases
    (re.compile(r"\b(password|locked out|log ?in)\b", re.I), "accounts"),
    (re.compile(r"\b(laptop|screen|keyboard|charger)\b", re.I), "hardware"),
]
SYSTEM = """Route the help-desk ticket to one team.
accounts: passwords, logins, locked accounts.
hardware: broken or missing devices.
other: anything else, including tickets that mix several issues."""
TEAM_KB = {  # (2) each handler sees only its own articles
    "accounts": {k: v for k, v in KB.items() if k.startswith("KB-1")},
    "hardware": {k: v for k, v in KB.items() if k.startswith("KB-2")},
}


def classify(ticket: str) -> tuple[Route, str]:
    hits = {category for pattern, category in RULES if pattern.search(ticket)}
    if len(hits) == 1:  # exactly one rule fired: trust it and skip the model
        return Route(category=hits.pop(), confident=True), "rules"
    response = client.messages.parse(  # (3) everything else goes to a cheap model
        model=MODEL, max_tokens=1000, output_config={"effort": "low"},
        system=SYSTEM, output_format=Route,
        messages=[{"role": "user", "content": f"<ticket>\n{ticket}\n</ticket>"}],
    )
    if response.parsed_output is None:  # refused or cut off: treat as unsure
        return Route(category="other", confident=False), "model-failed"
    return response.parsed_output, "model"


def handle(ticket: str) -> dict:
    route, source = classify(ticket)
    print(f"route={route.category} confident={route.confident} via={source}")
    if route.category == "other" or not route.confident:  # (4) unsure: the safe default
        return {"status": "human_review", "why": "router unsure", "route": route.category}
    result = answer(ticket, TEAM_KB[route.category])
    if result["status"] == "human_review":  # (5) maybe misrouted: one try with every article
        result = answer(ticket, KB)
    return result | {"route": route.category, "via": source}


if __name__ == "__main__":
    for t in ["I'm locked out after too many tries.",
              "My laptop screen cracked and I can't log in to anything.",
              "Can you book room B12 for the chess club?"]:
        print(handle(t))
```

The second ticket matches both rules, so it goes to the model, which should mark it as mixed or unsure. The third fits no team and goes to a person. Run it and read which path each ticket took.

### When the router is wrong

Your router will be wrong sometimes. Plan for it the way you planned for tool errors: decide in advance what a misroute costs and how you'll recover.

- **Make the default safe.** In `router.py`, "other" and "not confident" both go to human review. Pick the default by asking what a wrong answer costs. For a help desk, a person reading the ticket is cheap. For a chatbot that must answer instantly, the default might be a general handler that sees every article.
- **Let handlers bounce.** A specialist can notice that a ticket isn't its kind, for example when gate one finds no matching article. Step (5) above treats that as a hint of a misroute and tries once with all the articles. Like every retry, cap it.
- **Watch for asymmetric costs.** Sending a billing dispute to the "general questions" handler might be annoying. Sending a security report there might be a real incident. When one category is dangerous to miss, bias the router toward it, and accept more false alarms in exchange.
- **Log every decision.** Record the category, the confidence and whether rules or the model decided. When a reply goes wrong, the log tells you whether the router or the handler was to blame, and over time it becomes labeled data for improving the router.

### Routing to different models

Routing can choose the model as well as the prompt. Most traffic in a real product is easy and repetitive: "How do I reset my password?" A [cheap model](#/models) answers that well for a small fraction of the price. A few inputs are genuinely hard, such as a long, angry email describing three problems at once. Route those to the [capable model](#/models).

The classifier for this can be the same one you already have, with a `difficulty` field added, or a simple rule such as "more than 300 words or more than one category." Measure the result in both directions: what you saved on the easy route, and whether quality dropped on tickets the router wrongly called easy. Agent Cost and Latency, later in this section, comes back to choosing a model per step.

### Evaluate each step

A chain or router has more places to fail than a single prompt, so evaluate the steps separately, then the whole thing. This is error analysis from the Measuring Quality section, applied to a pipeline.

- **The router** is a classifier, so score it like one. With 20 to 50 labeled inputs, compute accuracy and a confusion matrix (Eval Statistics), which shows which categories get mixed up. Break the score down by source: are the rules right as often as you assumed?
- **Each gate** should report how often it fires. A gate that fires on 40% of drafts means the drafting prompt needs work. A gate that never fires is either unneeded or checking the wrong thing.
- **End to end**, score the final replies with the methods from Evals in Practice, and compare against a **baseline**: one well-written prompt that does the whole job. The pipeline is only worth it if it beats the baseline on accuracy, cost or latency, by more than the confidence interval.

Here is a router eval. Write a `tickets.jsonl` file with one labeled ticket per line, like `{"text": "My charger is missing", "label": "hardware"}`, then save this as `eval_router.py`:

```python
# eval_router.py  (run with: uv run eval_router.py)
import json
from collections import Counter

from router import classify

rows = [json.loads(line) for line in open("tickets.jsonl", encoding="utf-8")]
mistakes, total, correct = Counter(), Counter(), Counter()
for row in rows:
    route, source = classify(row["text"])
    predicted = route.category if route.confident else "other"  # unsure counts as "other"
    total[source] += 1
    if predicted == row["label"]:
        correct[source] += 1
    else:
        mistakes[(row["label"], predicted)] += 1

print(f"router accuracy: {sum(correct.values())}/{len(rows)}")
for source in total:  # are the free rules as good as you assumed?
    print(f"  via {source}: {correct[source]}/{total[source]}")
for (gold, predicted), n in mistakes.most_common():
    print(f"  {gold} routed to {predicted}: {n}")
```

The last loop is the part to read closely. "hardware routed to accounts: 3" tells you exactly which category definition to sharpen, or which rule to tighten.

### On other providers

Chains, gates, rules-first routing, misroute recovery and per-step evals are plain Python, so they carry over to any provider unchanged. The provider shows up in two places: the structured-output call that enforces each contract, and the effort setting on the classifier. With the OpenAI SDK, `client.chat.completions.parse(response_format=Request)` takes the same Pydantic class and returns it as `choices[0].message.parsed`, as OpenAI's [Structured Outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs) explains. Two details differ: a refusal arrives as text in `message.refusal`, and a reply cut off by the token limit raises `LengthFinishReasonError` (a small model's JSON that doesn't fit the schema raises a Pydantic `ValidationError`) instead of returning `None`, so gate one should catch those exceptions too. Claude's `output_config={"effort": "low"}` becomes `reasoning_effort="low"` on OpenAI's [reasoning models](https://developers.openai.com/api/docs/guides/reasoning), and you leave it out for models that don't reason. For a local open model, Ollama accepts the same `response_format` through its [OpenAI-compatible API](https://docs.ollama.com/api/openai-compatibility), though small models fill schemas less reliably, which makes your gates matter even more. Here is step one of `chain.py` on a local model:

```python
from openai import OpenAI  # uv add openai
from chain import KB, Request

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")  # or OpenAI() with OPENAI_API_KEY

def extract(ticket: str, kb: dict[str, str] = KB, model: str = "qwen3:4b") -> Request | None:
    articles = "\n".join(f"{k}: {v}" for k, v in kb.items())
    completion = client.chat.completions.parse(
        model=model, response_format=Request,  # the same Pydantic contract as before
        messages=[{"role": "system", "content": f"You triage help-desk tickets. Pick only from these articles:\n{articles}"},
                  {"role": "user", "content": f"<ticket>\n{ticket}\n</ticket>"}])
    return completion.choices[0].message.parsed  # None on a refusal; a cutoff or bad JSON raises
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the sections "Building block: The augmented LLM," "Workflow: Prompt chaining" and "Workflow: Routing" in [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents). Note the examples it gives for when each pattern fits, and compare them with the help-desk example in this lesson.
1. Open the [basic workflows notebook](https://github.com/anthropics/claude-cookbooks/blob/main/patterns/agents/basic_workflows.ipynb) from the Claude Cookbooks and run Example 1 (the chain) and Example 3 (the router) yourself.
   - Read the helper functions in `util.py` in the [same folder](https://github.com/anthropics/claude-cookbooks/tree/main/patterns/agents) first so the notebook code makes sense.
   - The notebook passes text between steps and parses XML tags. Notice where a structured-output contract and a gate, as in `chain.py`, would make it sturdier.
1. Read the "Orchestration" section of OpenAI's [A Practical Guide to Building Agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf) for another view of when a fixed flow beats a single agent.
1. Practice: build a two-step chain that turns a messy meeting transcript into (1) a list of decisions and then (2) a short email summarizing them.
   - Make step one return structured output (a list of decisions, each with an owner). Add a gate in code that checks the list has at least one item and that every owner's name appears in the transcript. On failure, retry once with feedback, then stop with a clear message.
   - Log both steps' outputs and the gate's verdict for each run.
1. Practice: run `chain.py`, `router.py` and `eval_router.py` from this lesson.
   - Write 15 labeled tickets in `tickets.jsonl`, including at least three that mix two issues and two that fit no team. Run the eval, then change one rule or one category definition to fix the most common mistake, and run it again. Write down both scores and how many tickets went through rules versus the model.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What is an augmented LLM, and who decides the shape of a workflow built from them?](#the-augmented-llm)
- [Why should each step in a chain return structured output, and what does a chain cost in latency?](#chains-are-contracts-between-steps)
- [What four things can your code do when a gate fails, and why cap retries?](#gates-that-retry-repair-or-stop)
- [Why does routing to specialized handlers often beat one prompt that handles everything?](#routing-classify-then-specialize)
- [When is it safe to let a rule route an input instead of a model?](#rules-first-then-a-model)
- [How should a workflow recover when the router sends an input to the wrong place?](#when-the-router-is-wrong)
- [How would you evaluate a router separately from the rest of the pipeline?](#evaluate-each-step)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Chain complex prompts](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/chain-prompts) in the Claude docs gives more chain examples, including self-correction chains.
