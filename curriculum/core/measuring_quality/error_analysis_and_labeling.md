### Introduction

In Why Evals Matter you read 30 traces, wrote a note on each failure, grouped the notes and counted them. That first pass is usually eye-opening. It is also easy to do badly. You can skim instead of read, invent categories before looking at the data, label one day with one standard and the next day with another, and end up with counts nobody trusts, yourself included.

This lesson turns that first pass into a process you can repeat every week and defend in a code review or a job interview. You will choose which traces to read, generate test inputs when you have no users yet, write notes that describe behavior, turn the notes into a small set of failure categories, write labeling guidelines so the labels mean the same thing every time, label with a tiny tool of your own, check whether a second person would agree with you, and turn each category into eval cases. The labels you make here feed straight into the next lesson, Eval Statistics, which shows how far you can trust the counts.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- How to choose a sample of traces worth reading, and how to generate synthetic inputs from dimensions.
- Open coding: writing notes that describe what went wrong.
- Axial coding: merging notes into a failure taxonomy and knowing when to stop.
- Writing labeling guidelines with binary criteria and examples.
- Building a small labeling tool and tallying the results.
- Measuring agreement between two labelers with Cohen's kappa.
- Turning failure categories into eval cases.

### Choosing what to read

You can't read everything, so the first decision is which traces to read. A **random sample** is the honest baseline: it shows you what a typical user sees, and it's the only kind of sample whose failure counts you can turn into rates. Draw it with a fixed seed (`traces.sample(100, random_state=0)` in pandas) so you can draw the same sample again later.

Then add a smaller **targeted sample** to find failures faster: traces where a user gave a thumbs-down, traces that hit an error or a timeout, unusually long or short outputs, and inputs from rare kinds of user. Keep the two samples apart in your notes. The targeted traces are great for discovering failure modes, but they're full of problems on purpose, so they would make your failure rate look far worse than it is.

How many? Aim for about 100 traces in total, and keep reading until new traces stop teaching you anything. Researchers call that point **theoretical saturation**: ten traces in a row add no new kind of failure and don't change any category you already have.

### Synthetic inputs when you have no users

Before launch you have no real traces. You can make test inputs yourself, but asking a model to "write 50 support emails" gives you 50 polite, medium-length emails that all sound alike. A better method is to name the **dimensions** along which real inputs differ, pick values for each one, and generate one input per combination of values. A combination such as `(billing, two topics, sarcastic, one line)` is called a **tuple**.

Write the first ten or twenty tuples by hand, which forces you to think about what users actually do. Then let code produce the combinations and a model turn each one into text:

```python
# synth.py: generate varied test inputs from dimensions.   setup: uv add anthropic
import itertools
import json
import os
import random

import anthropic

MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY

# Each dimension is one way real emails differ. Pick values from your error analysis.
DIMENSIONS = {
    "topic": ["billing", "bug", "feature_request", "account_access"],
    "mix": ["one topic", "two topics, main one second", "two topics, main one first"],
    "tone": ["polite", "angry", "sarcastic"],
    "length": ["one line", "a long rambling paragraph"],
}

combos = list(itertools.product(*DIMENSIONS.values()))  # 4 * 3 * 3 * 2 = 72 tuples
random.Random(0).shuffle(combos)

with open("synthetic_inputs.jsonl", "a", encoding="utf-8") as out:
    for combo in combos[:20]:  # start small; read these before making more
        spec = dict(zip(DIMENSIONS, combo))
        response = client.messages.create(
            model=MODEL,
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": (
                    "Write one realistic customer support email for a project-management app.\n"
                    f"Main topic: {spec['topic']}. Topics: {spec['mix']}. "
                    f"Tone: {spec['tone']}. Length: {spec['length']}.\n"
                    "Write only the email body, with no subject line and no commentary."
                ),
            }],
        )
        email = "".join(b.text for b in response.content if b.type == "text").strip()
        out.write(json.dumps({"input": email, "spec": spec}) + "\n")
        print(spec, "->", email[:60].replace("\n", " "))
```

`itertools.product` builds every combination of the dimension values, and saving the `spec` next to each email means you can later ask "do we fail more on sarcastic emails?" Read the generated emails before you use them; throw out the ones no real customer would write. Synthetic data is for *finding* failures before launch. It can't tell you how often a failure happens with real users, so replace it with real traces as soon as you have them.

### Open coding

**Open coding** means reading each trace and writing a short free-text note on what went wrong, with no categories decided in advance. Two habits make the notes useful.

First, **describe behavior, not causes.** "Email asked about a refund and a login problem; output was billing, login ignored" is a good note. "Model is bad at multi-intent" is a guess about the cause, and it hides what you actually saw. Notes should be specific enough that someone else could find the same problem in the trace.

Second, **note the first thing that went wrong.** In a multi-step system, one early mistake causes several later ones. If the system misread the question, a wrong answer and a missing citation are both consequences. Writing down the first, *upstream* failure keeps your counts from piling up on symptoms.

One person, ideally whoever knows the domain best, should own the labels. Practitioners call this person the **benevolent dictator**: others can give input, but one person decides what counts as a failure, so the standard doesn't wobble.

### Axial coding

**Axial coding** means grouping the notes into a **failure taxonomy**: a short list of named categories, each with a one-sentence definition. Read all your notes, put similar ones together, and give each group a name that describes the behavior: "two topics, picked one," not "reasoning issue."

Then refine. Split a category when it holds failures with different fixes; for example, "wrong label" is too broad, while "refund labeled other" points to a specific missing rule. Merge categories that always get the same fix. Aim for four to ten categories. Fewer usually means they're too vague, and more means you'll struggle to apply them consistently. A model can suggest groupings from your notes, but check its suggestions against the traces: it doesn't know which differences matter to your users.

Once the categories are stable, go back and tag every failing trace with one. Now you can count, which is where the next sections pick up.

### Writing labeling guidelines

A label is only useful if it means the same thing every time. **Labeling guidelines** (also called a **rubric**) are a short written document that says exactly how to label. Write them as soon as your categories settle, and keep them in your repo next to the data. A good guideline has, for each criterion:

- **A binary question.** PASS or FAIL, not a score from 1 to 5. Nobody can say consistently what separates a 3 from a 4, but you can decide whether the label is the right one.
- **A definition** in plain words.
- **One or two examples on each side of the line**, taken from real traces.
- **Rules for the cases you argued about.**

```text
Criterion: CORRECT LABEL
PASS if the output is exactly one allowed label and it matches the customer's main request.
The main request is the one the customer asks us to act on. If two topics are equally
important, the first one mentioned wins.
FAIL example: "Refund my March invoice, and also the login page is slow." -> bug
PASS example: "Love paying twice! Fix this." -> billing (sarcasm, but the request is billing)
Unsure? Label it FAIL, write "unsure" in the note, and bring it to the next review.
```

Expect the guidelines to change. As you label more traces, your sense of what counts as a failure sharpens; researchers call this **criteria drift**. That's healthy, as long as you update the document, note the date, and relabel the traces the new rule affects.

### A tiny labeling tool

Labeling in a spreadsheet works, but a small tool of your own is faster and less error-prone: it shows one trace at a time, takes a single keypress, and saves after every label so you can stop and resume. This one runs in the terminal and uses only what you learned in Foundations:

```python
# label.py: a tiny terminal labeling tool.   run: uv run label.py traces.jsonl
import json
import sys
from pathlib import Path

LABELS = Path("labels.jsonl")
LABELER = "ada"  # your name, so you can compare labelers later
CATEGORIES = []  # empty on your first pass; fill in after axial coding


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def ask(prompt: str, allowed: set[str]) -> str:
    while True:
        answer = input(prompt).strip().lower()
        if answer in allowed:
            return answer
        print("  please type one of:", ", ".join(sorted(allowed)))


def main() -> None:
    traces = load_jsonl(Path(sys.argv[1]))
    done = {row["trace_id"] for row in load_jsonl(LABELS)}  # resume where you left off
    todo = [t for t in traces if t["trace_id"] not in done]
    print(f"{len(done)} already labeled, {len(todo)} to go. Type q to stop.\n")

    for i, trace in enumerate(todo, start=1):
        print(f"=== [{i}/{len(todo)}] {trace['trace_id']} ({trace['prompt_version']})")
        print("INPUT: ", trace["input"])
        print("OUTPUT:", trace["output"] if trace["error"] is None else f"ERROR {trace['error']}")
        verdict = ask("p = pass, f = fail, q = quit > ", {"p", "f", "q"})
        if verdict == "q":
            break
        row = {"trace_id": trace["trace_id"], "prompt_version": trace["prompt_version"],
               "label": "PASS" if verdict == "p" else "FAIL", "note": "", "category": None,
               "labeler": LABELER}
        if verdict == "f":
            row["note"] = input("note (what went wrong, in your words) > ").strip()
            if CATEGORIES:
                for n, name in enumerate(CATEGORIES, start=1):
                    print(f"  {n}. {name}")
                pick = ask("category number > ", {str(n) for n in range(1, len(CATEGORIES) + 1)})
                row["category"] = CATEGORIES[int(pick) - 1]
        with LABELS.open("a", encoding="utf-8") as f:  # save after every trace
            f.write(json.dumps(row) + "\n")
        print()


if __name__ == "__main__":
    main()
```

It reads the trace files your `traced_call` from Why Evals Matter writes. On your first pass, leave `CATEGORIES` empty and write notes (open coding). After axial coding, fill it in, start a fresh labels file, and label again, this time tagging each failure with a category. The tool also shows the prompt version and never shows a previous label, which keeps you from simply agreeing with your past self. Later, in Prototyping with Streamlit and Gradio, you'll learn to build the same thing as a web page that a non-programming domain expert can use.

### Tallying your labels

With a labels file in hand, pandas does the counting. Here is a tally of 40 labeled traces, 20 from each of two prompt versions:

```python
# tally.py: summarize your labels.   setup: uv add pandas
import pandas as pd

labels = pd.read_json("labels.jsonl", lines=True)
labels["failed"] = labels["label"] == "FAIL"
fails = labels[labels["failed"]]

# 1. How often does each prompt version fail?
print(labels.groupby("prompt_version")["failed"].agg(["sum", "count", "mean"]), "\n")

# 2. Which failure categories are most common? Share is out of ALL traces.
counts = fails["category"].value_counts()
print(pd.DataFrame({"count": counts, "share": (counts / len(labels)).round(3)}), "\n")

# 3. Categories by prompt version: what did the v2 change fix, and what did it break?
print(pd.crosstab(fails["category"], fails["prompt_version"]))
```

```text
                sum  count  mean
prompt_version
few-shot-v1      10     20   0.5
few-shot-v2       6     20   0.3

                         count  share
category
two topics, picked one       7  0.175
extra text around label      4  0.100
refund labeled other         3  0.075
sarcasm misread              2  0.050

prompt_version           few-shot-v1  few-shot-v2
category
extra text around label            3            1
refund labeled other               2            1
sarcasm misread                    0            2
two topics, picked one             5            2
```

The cross-tabulation is the most useful table. Version 2 fixed most of the "two topics" and "extra text" failures but introduced two sarcasm failures that version 1 never had. A single overall rate would have hidden that trade. And is 30% really better than 50% on 20 traces each? That's exactly the question Eval Statistics answers.

### Do two labelers agree

When more than one person labels, or when you want to check that your guidelines are clear, have a second person label the same 30 traces **independently**, without seeing your labels. The simplest measure is **percent agreement**: the share of traces where you both chose the same label. It flatters you, though. If 90% of outputs pass and both labelers say PASS almost every time, they agree a lot without paying attention.

**Cohen's kappa** corrects for that. It compares the agreement you got with the agreement you'd expect by chance, given how often each person says PASS:

```python
# agreement.py: how often do two labelers agree, beyond chance?
from collections import Counter


def percent_agreement(a: list[str], b: list[str]) -> float:
    return sum(x == y for x, y in zip(a, b)) / len(a)


def cohens_kappa(a: list[str], b: list[str]) -> float:
    n = len(a)
    observed = percent_agreement(a, b)
    count_a, count_b = Counter(a), Counter(b)
    # Chance agreement: how often you'd match if each labeler kept their own
    # PASS/FAIL rates but labeled at random.
    expected = sum(count_a[k] * count_b[k] for k in count_a | count_b) / n**2
    return (observed - expected) / (1 - expected)


# The same 30 traces, labeled independently by you and a teammate.
you  = ["PASS"] * 20 + ["FAIL"] * 10
mate = ["PASS"] * 17 + ["FAIL"] * 3 + ["FAIL"] * 7 + ["PASS"] * 3

print(f"agreement: {percent_agreement(you, mate):.0%}")
print(f"kappa:     {cohens_kappa(you, mate):.2f}")
disagree = [i for i, (x, y) in enumerate(zip(you, mate)) if x != y]
print("discuss traces:", disagree)
```

```text
agreement: 80%
kappa:     0.55
discuss traces: [17, 18, 19, 27, 28, 29]
```

Kappa is 1 for perfect agreement and 0 for agreement no better than chance. Eighty percent agreement sounds good, but a kappa of 0.55 says the guidelines leave a lot of room for interpretation. As a rough rule, aim for 0.7 or higher before you trust labels from several people. The number matters less than the list of disagreements: sit down together, find which rule caused each one, and fix the guidelines so the next decision is obvious.

### From categories to eval cases

Each failure category becomes part of your eval, in two ways.

**It becomes a check.** Decide how to detect the failure automatically. "Extra text around label" is a one-line code check: is the output exactly one allowed label? "Two topics, picked one" needs to know the right answer, so it becomes labeled test cases with an exact-match check. Fuzzy categories, like "tone is rude," may need a model as a judge, which you'll build and validate in Code Checks and LLM-as-Judge.

**It becomes test cases.** Copy the failing traces into your golden dataset, with the correct answer and the category as a tag, and add a few hand-written variations of each:

```text
{"id": "two-topics-03", "input": "Refund my March invoice, and the login page is slow.", "expected": "billing", "category": "two topics, picked one", "source": "trace 3f2a9c1e"}
{"id": "sarcasm-01", "input": "Love paying twice! Fix this.", "expected": "billing", "category": "sarcasm misread", "source": "handwritten"}
```

Tagging each case with its category lets you report a pass rate per category, so you can see that a prompt change fixed one kind of failure and broke another, as the cross-tabulation showed. Keep the cases even after the failure is fixed. They become **regression tests**: they catch the bug if it ever comes back.

Then repeat the whole loop regularly. Every prompt or model change creates new failure modes, and the only way to find them is to read new traces.

### On other providers

Error analysis is about as provider-neutral as anything in this curriculum: open coding, axial coding, labeling guidelines, the labeling tool and the agreement math never touch a model API. Only `synth.py` calls a model. To run it on OpenAI's Chat Completions API, create `OpenAI()` instead of `anthropic.Anthropic()`, call `client.chat.completions.create(model=..., messages=[...])` with the same user message, and read the text from `response.choices[0].message.content`; the output cap is optional there (it's called `max_completion_tokens`), so you can drop `max_tokens`. One choice is worth making on purpose: don't let the model you're testing be the only one that writes your synthetic inputs. Inputs written by the same model family can share its habits of phrasing and miss failures that other phrasings would trigger. Generating some of the tuples with a second provider, or for free with a local open model such as [Qwen3](https://ollama.com/library/qwen3) through [Ollama's OpenAI-compatible API](https://docs.ollama.com/api/openai-compatibility), gives you more varied inputs. OpenAI's [evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices) guide covers building datasets and calibrating against human feedback from OpenAI's side.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Why is error analysis so important, and how is it performed?](https://hamel.dev/blog/posts/evals-faq/why-is-error-analysis-so-important-in-llm-evals-and-how-is-it-performed.html) from the AI evals FAQ by Hamel Husain and Shreya Shankar. It's a compact summary of the open coding, axial coding and saturation process this lesson teaches.
   - Then read two related answers from the same FAQ: [the best approach for generating synthetic data](https://hamel.dev/blog/posts/evals-faq/what-is-the-best-approach-for-generating-synthetic-data.html), on dimensions and tuples, and [how many people should annotate](https://hamel.dev/blog/posts/evals-faq/how-many-people-should-annotate-my-llm-outputs.html), on the benevolent dictator and resolving disagreements.
1. Read [A Field Guide to Rapidly Improving AI Products](https://hamel.dev/blog/posts/field-guide/) by Hamel Husain.
   - Focus on the first two sections, on skipping error analysis and on building a simple data viewer, and on the section about synthetic data. They show why teams that build their own viewing and labeling tools move faster.
1. Read [Product Evals in Three Simple Steps](https://eugeneyan.com/writing/product-evals/) by Eugene Yan. It covers labeling a sample, keeping labels binary, and aligning evaluators with those labels, from the point of view of a team shipping a product.
1. Skim the introduction and findings of [Who Validates the Validators?](https://arxiv.org/abs/2404.12272) by Shreya Shankar and colleagues. It's the research behind the idea of criteria drift: people only learn what their criteria are by labeling outputs.
1. Practice on your Prompt Lab task:
   - Generate 30 synthetic inputs from at least three dimensions with `synth.py`, read them, and discard any unrealistic ones. Run your best prompt on the rest through `traced_call`.
   - Label every trace with `label.py`, writing a note for each failure. Group the notes into four to eight categories, write a labeling guideline with a PASS and FAIL example for each, then relabel with `CATEGORIES` filled in.
   - Ask a friend or classmate to label 20 of the same traces using only your guideline. Compute kappa with `agreement.py`, discuss every disagreement, and update the guideline.
   - Run `tally.py`, then add at least two test cases per category to your `test_set.jsonl`, each tagged with its category. Commit the guideline, the labels and the new cases.
1. Practice: if you haven't already, do the trace-reading exercise in the [evals exercise set](https://github.com/espiNovah/project-mimir/tree/main/exercises/evals) with `uv run pytest evals/01_read_traces` from the `exercises/` folder. It drills loading JSONL traces and counting failure categories in a stable order.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Why should you keep a random sample of traces separate from a targeted sample of likely failures?](#choosing-what-to-read)
- [What are dimensions and tuples, and why do they produce better synthetic inputs than "write 50 emails"?](#synthetic-inputs-when-you-have-no-users)
- [Why should an open-coding note describe behavior and the first failure, rather than a guessed cause?](#open-coding)
- [When should you split a failure category, and when should you merge two?](#axial-coding)
- [What belongs in a labeling guideline, and why use binary criteria?](#writing-labeling-guidelines)
- [Why can percent agreement be misleading, and what does Cohen's kappa correct for?](#do-two-labelers-agree)
- [What two things does each failure category turn into in your eval?](#from-categories-to-eval-cases)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Should I build a custom annotation tool?](https://hamel.dev/blog/posts/evals-faq/should-i-build-a-custom-annotation-tool-or-use-something-off-the-shelf.html) from the AI evals FAQ argues for small, custom labeling tools like `label.py`, and lists what makes one good.
- [How can I efficiently sample production traces for review?](https://hamel.dev/blog/posts/evals-faq/how-can-i-efficiently-sample-production-traces-for-review.html) from the same FAQ covers smarter sampling once you have lots of traffic.
- [Cohen's kappa on Wikipedia](https://en.wikipedia.org/wiki/Cohen%27s_kappa) gives worked examples and the commonly quoted (and debated) scale for interpreting kappa values.
