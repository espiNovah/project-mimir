### Introduction

Some tasks are too hard to answer in one go. A person solving a tricky problem thinks it through, or breaks it into smaller jobs. Language models are the same. In this lesson you will learn two ways to handle hard tasks: give the model room to reason before it answers, and split one big prompt into a chain of smaller prompts where each step's output feeds the next. Prompt chaining is also your first taste of the workflow patterns you will build in the Agentic Systems path.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why letting a model reason before answering improves accuracy on hard tasks.
- The difference between prompting for step-by-step reasoning and using a model's built-in thinking feature.
- How to keep reasoning separate from the final answer so your code can parse it.
- What prompt chaining is and when to use it.
- How to pass outputs between steps and check them along the way.
- The cost and latency trade-offs of both techniques.

### Reasoning takes tokens

Recall from Tokens and Tokenization that a model writes its answer one token at a time, and each new token is chosen by looking at everything before it. That has a surprising consequence: a model can only "think" by writing. If you ask a question and demand the answer immediately, the first tokens of the answer must carry the whole decision. If instead the model first writes out the relevant facts, the intermediate steps and the options, then by the time it writes the answer, all that work is sitting in the context for it to use.

This is why "think step by step" became famous. Asking the model to reason first helps a lot on math, logic, multi-step analysis, and judgment calls such as "which of these three categories fits best, given that the email mentions two topics?" It barely helps on simple lookups like "what is the capital of France?", where there is nothing to work out.

When you prompt for reasoning yourself, keep the reasoning and the answer apart so your code can read just the answer:

```text
Classify the support email below into one of: billing, bug, feature_request,
account_access, other.

First, think through which categories could apply and why, inside <thinking>
tags. Then give only the final label inside <answer> tags.

<email>
{email}
</email>
```

Your code then extracts the text between `<answer>` and `</answer>`, as you did with `<summary>` tags in Prompting Fundamentals, and ignores the thinking. Keep the thinking for debugging, though. When an answer is wrong, the reasoning often shows exactly where your prompt misled the model: it misread a category definition, or it gave too much weight to one sentence.

### Built-in thinking

You learned in Reasoning Models that many current models have reasoning built in. They were trained to think before answering, and the API returns that thinking as separate `thinking` content blocks before the final `text` block. On current Claude models this is called **adaptive thinking**: the model decides for itself how much to think, based on how hard the request looks. You steer the overall amount with an **effort** setting (`low`, `medium`, `high` and higher), which trades quality against tokens and time. The parameter names below are Claude features; other providers have their own reasoning switches with different names and levels, covered in [On other providers](#on-other-providers) below.

When built-in thinking is available, prefer it over hand-written `<thinking>` tags. The model was trained to use it, it does not clutter your answer text, and you control it with one setting instead of prompt wording. Manual tags are still useful with models or settings that lack a thinking mode, and when you want the reasoning in a specific format you can show to users or log.

Here is a call that asks for a summary of the thinking and sets the effort level:

```python
# think.py  (run with: uv run think.py)
import os

import anthropic

MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
client = anthropic.Anthropic()

question = (
    "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. "
    "How much does the ball cost? Give just the amount in your final answer."
)

response = client.messages.create(
    model=MODEL,
    max_tokens=4000,  # covers thinking plus the answer
    thinking={"type": "adaptive", "display": "summarized"},  # show a summary of the reasoning
    output_config={"effort": "high"},  # try "low" and compare
    messages=[{"role": "user", "content": question}],
)

for block in response.content:
    if block.type == "thinking":
        print("THINKING SUMMARY:\n", block.thinking, "\n")
    elif block.type == "text":
        print("ANSWER:\n", block.text)

print(response.usage)  # output_tokens includes the thinking tokens you paid for
```

Two things to notice. The `max_tokens` cap covers thinking *and* answer, so set it high enough that thinking does not crowd out the answer (check for `stop_reason == "max_tokens"`). And the `usage` line shows that thinking costs output tokens. Run it at `"low"` and `"high"` effort and compare the token counts.

<div class="lesson-note" markdown="1">

#### Hints beat scripts

Whether the thinking is built in or prompted, guide it with high-level hints rather than a rigid recipe. "Consider whether the email could fit more than one category before deciding" usually works better than a ten-step procedure, because the model can often find a better path than the one you would dictate.

</div>

### Prompt chaining

The second technique splits work across several calls. Suppose you want to turn a long news article into a short summary for a newsletter. One giant prompt could say: "Read the article, find the key facts, check that they are supported, then write a three-sentence summary in a friendly tone." That asks one call to do four jobs at once, and when the result is wrong you can't tell which job failed.

**Prompt chaining** splits the task into a sequence of smaller prompts, where each step's output becomes part of the next step's input. For the newsletter:

1. **Extract:** "List the key facts in this article as bullets."
1. **Write:** "Using only these facts, write a three-sentence summary."

Each step is simpler, so each is more accurate. Each step can use its own prompt, model and settings: a cheap model may be fine for extraction while the writing step uses a stronger one. And because you can see the output of every step, debugging becomes easy. If the summary contains a wrong number, look at the fact list. If the number is wrong there, the extraction step is the problem; if not, the writing step invented it.

### Gates between steps

Chains have another advantage: between steps, your ordinary Python code is in charge. It can check the intermediate output and decide what to do next. A check like this is called a **gate**. Gates catch problems early, before they turn into confident-sounding nonsense at the end.

```python
# chain.py  (run with: uv run chain.py article.txt)
import os
import sys

import anthropic

MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
client = anthropic.Anthropic()


def ask(prompt: str) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in response.content if b.type == "text")


article = open(sys.argv[1], encoding="utf-8").read()

# Step 1: extract facts.
facts_text = ask(
    "List the key facts from the article below as bullet points, one per line, "
    "each starting with '- '. Include only facts stated in the article.\n\n"
    f"<article>\n{article}\n</article>"
)
facts = [line for line in facts_text.splitlines() if line.startswith("- ")]
print("STEP 1 OUTPUT:\n" + "\n".join(facts) + "\n")

# Gate: stop early instead of summarizing from too little.
if len(facts) < 3:
    sys.exit(f"Stopping: only {len(facts)} facts extracted. Check the article or the prompt.")

# Step 2: write from the facts only.
summary = ask(
    "Write a three-sentence summary for a general audience using ONLY these facts. "
    "Do not add anything that is not in the list.\n\n"
    "<facts>\n" + "\n".join(facts) + "\n</facts>"
)
print("STEP 2 OUTPUT:\n" + summary)
```

Gates can do more than stop. They can retry a step, send the input down a different path ("if step one finds no facts about prices, skip the pricing section"), or pass the result to a human. A common three-step chain is **draft, critique, revise**: one call writes a draft, a second reviews it against a checklist, and a third fixes the issues the review found. You will meet this again in Workflow Patterns as the evaluator-optimizer pattern.

### When to use each technique

Both techniques buy accuracy with tokens and time. Thinking adds output tokens to every call. A three-step chain makes three calls, each of which waits for the previous one, so latency adds up. For a chatbot that must answer in a second, that matters; for a nightly batch job, it doesn't.

A rough guide:

- **Simple, single-skill tasks** (short classification, reformatting): try a plain prompt first, with low effort.
- **Hard reasoning in one step** (math, tricky judgment calls): use built-in thinking, or prompted reasoning in tags.
- **Several distinct jobs** (extract, then analyze, then write), or **steps you want to check**: use a chain with gates.

These are starting points, not rules. Whether thinking or chaining helps *your* task is an empirical question. You answer it by running both versions on the same test inputs and comparing scores, tokens and seconds, which is exactly what the Prompt Lab project asks you to do.

### On other providers

Prompted reasoning in `<thinking>` and `<answer>` tags works on any model, which makes it the portable choice when you compare providers. So does prompt chaining: `chain.py` only needs its `ask()` function rewritten for another SDK, and the gates are plain Python. Built-in thinking is where providers differ. OpenAI calls its thinking models **reasoning models** and controls them with `reasoning_effort` in Chat Completions (`reasoning.effort` in the Responses API); the allowed levels vary by model and include `none`, `minimal`, `low`, `medium`, `high` and more, so check the model's page. OpenAI never returns the raw reasoning, only an optional summary through the Responses API, and the hidden reasoning tokens are counted in `usage.completion_tokens_details.reasoning_tokens` and billed as output. Its output cap is `max_completion_tokens`, and as with Claude it must leave room for the thinking. Open models vary most: some, like [Qwen3](https://ollama.com/library/qwen3), think by default, and Ollama returns their reasoning in a separate field from the answer, as its [thinking docs](https://docs.ollama.com/capabilities/thinking) show. OpenAI's [reasoning guide](https://developers.openai.com/api/docs/guides/reasoning) has the details. Here's `think.py`'s request through the OpenAI SDK:

```python
# think_other.py  (uv add openai; ollama pull qwen3:4b)
import os

from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")  # OpenAI(): reads OPENAI_API_KEY
question = ("A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. "
            "How much does the ball cost? Give just the amount in your final answer.")
response = client.chat.completions.create(
    model=os.environ.get("MIMIR_MODEL", "qwen3:4b"),  # or an OpenAI reasoning model ID
    reasoning_effort="high",       # try "low"; levels depend on the model
    max_completion_tokens=4000,    # reasoning + answer (Ollama documents max_tokens)
    messages=[{"role": "user", "content": question}],
)
print(response.choices[0].message.content)
print(response.usage)  # on OpenAI, completion_tokens_details.reasoning_tokens is the thinking
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the reasoning and chaining parts of [Anthropic's prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices).
   - Focus on the sections about thinking and about chaining or multi-step work.
1. Read the [adaptive thinking docs](https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking) and the [effort docs](https://platform.claude.com/docs/en/build-with-claude/effort) to see how built-in reasoning is controlled through the API on current models. Then skim the [extended thinking docs](https://platform.claude.com/docs/en/build-with-claude/extended-thinking) for background; it describes the older fixed-budget style you may still see in tutorials.
   - Read the overview and the first code example on each page. Note how thinking content comes back as separate blocks from the final text.
1. Read the "prompt chaining" part of [Building effective agents](https://www.anthropic.com/research/building-effective-agents) by Anthropic.
   - Read up to the end of the "Workflow: Prompt chaining" section. The rest belongs to the Agentic Systems path.
1. Revisit chapter 6 ("Precognition: Thinking Step by Step") of [Anthropic's interactive prompt engineering tutorial](https://github.com/anthropics/prompt-eng-interactive-tutorial), which you did in the last lesson, then complete the appendix notebook on chaining prompts (10.1).
1. Practice: run `chain.py` from this lesson on a news article saved as a text file. Then extend it:
   - Add a third step that checks the summary against the fact list and replies `OK` or lists unsupported claims. Make that a gate: print a warning if the reply is not `OK`.
   - Run `think.py` at `low` and `high` effort on three hard questions of your choice, and record the answer and `usage.output_tokens` for each in a small table.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Why does writing out reasoning before the answer improve accuracy on hard tasks?](#reasoning-takes-tokens)
- [How do you keep prompted reasoning separate from the final answer?](#reasoning-takes-tokens)
- [When should you prefer built-in thinking over thinking in tags, and how do you control how much the model thinks?](#built-in-thinking)
- [What is prompt chaining, and why is a chain easier to debug than one big prompt?](#prompt-chaining)
- [What is a gate, and what can your code do at one?](#gates-between-steps)
- [What do thinking and chaining cost, and how should you decide whether to use them?](#when-to-use-each-technique)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Chain complex prompts](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/chain-prompts) in the Claude docs gives more chain examples, including self-correction chains.
