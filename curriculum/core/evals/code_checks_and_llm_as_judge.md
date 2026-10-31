### Introduction

In Measuring Quality you learned why evals matter, how to read traces and name failure modes, and how to put a confidence interval around a score. Every one of those steps assumed you could decide whether a single output passed or failed. So far, you made that call by hand. That works for 30 traces. It does not work for 500 traces on every commit.

This lesson is about automating that call with a *grader*: something that looks at one output and says PASS or FAIL. The best grader is plain code, because it's fast, free and never changes its mind. Some qualities, such as whether an answer is faithful to its sources, are too fuzzy for code, so people use another language model as the grader. That setup is called *LLM-as-judge*. A judge is powerful, but it's a model, and models make mistakes. So the second half of this lesson shows you how to measure your judge against your own labels before you trust a single number it gives you.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The three kinds of graders: code, model and human.
- How to write code-based checks for format, content and rules.
- When an LLM judge is the right choice.
- How to write a binary judge prompt that gives reliable verdicts.
- How to measure a judge's true positive and true negative rates against human labels.
- Common judge biases and how to reduce them.

### Three kinds of graders

Every eval needs something that turns an output into a verdict. There are only three options:

- **Code.** A Python function that returns `True` or `False`. Exact match, regular expressions, schema validation and arithmetic all count.
- **A model.** Another LLM call that reads the output and some criteria, and returns a verdict.
- **A human.** You, or a domain expert, reading the output and deciding.

They trade off in a predictable way. Code is cheap, instant and perfectly consistent, but it can only check what you can spell out precisely. Humans can judge anything, but they're slow, expensive and get tired. Model judges sit in the middle: they can handle fuzzy criteria at machine speed, but they cost money per call and can be wrong.

The rule of thumb is to use the cheapest grader that can actually do the job. Use code wherever you can, a judge where you must, and humans to check both.

### Code checks come first

A surprising number of failures from your error analysis can be caught with a few lines of Python. Look back at the failure categories you counted in Error Analysis and Labeling. "Didn't cite a source," "cited a passage that wasn't retrieved," "answer too long," "label not in the allowed list" and "invalid JSON" are all code checks.

Here are some for the Chat With Your Docs system you just built, which answers with numbered citations like `[2]`:

```python
# checks.py: code-based graders. Each returns True for PASS.
import re

CITATION = re.compile(r"\[(\d+)\]")  # matches [1], [12], ...
REFUSAL = "i don't know"


def has_citation(answer: str) -> bool:
    """Every non-refusal answer should cite at least one source."""
    if REFUSAL in answer.lower():
        return True
    return bool(CITATION.search(answer))


def citations_were_retrieved(answer: str, num_sources: int) -> bool:
    """A citation like [7] is only valid if we actually sent 7+ sources."""
    cited = {int(n) for n in CITATION.findall(answer)}
    return all(1 <= n <= num_sources for n in cited)


def under_word_limit(answer: str, limit: int = 150) -> bool:
    return len(answer.split()) <= limit


if __name__ == "__main__":
    answer = "Set the timeout with --timeout [2]. The default is 30 seconds [5]."
    print(has_citation(answer))                 # True
    print(citations_were_retrieved(answer, 4))  # False: [5] was never retrieved
    print(under_word_limit(answer))             # True
```

Notice how specific these are. Each one maps to a failure mode you actually saw, not a generic idea of "quality." Because they cost nothing, you can run them on every output, in every test run, forever. Write them as plain functions so you can also cover them with pytest, exactly as you did in Testing with pytest.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Check structure with your schema

If an output is supposed to be JSON, your Pydantic model from Structured Outputs is already a code grader. `Model.model_validate_json(text)` either succeeds or raises `ValidationError`, and that's a PASS or a FAIL.

</div>

### When to reach for a judge

Some failure modes resist code. "Every claim in the answer is supported by the sources" is the classic example. You can't regex your way to knowing whether "the default timeout is 60 seconds" is supported by a passage that says "requests time out after one minute." Others include "the answer actually addresses the question," "the tone is appropriate for a customer" and "these two answers mean the same thing."

For these, a judge model gets the question, the output, any context it needs (such as the retrieved sources) and a precise criterion, and returns a verdict. A judge doesn't need to be smarter than the system it grades; checking an answer is usually easier than writing one. Still, when the criterion is subtle, try the [capable model](#/models) as the judge and keep it only if the [cheap model](#/models) can't match its agreement with your labels.

### Writing a binary judge

Three habits separate judges that work from judges that produce noise.

**One criterion per judge.** A judge asked to rate "overall quality" mixes faithfulness, style, length and helpfulness into one number, and you can never tell which one moved. Write one judge per failure mode. If you care about faithfulness and relevance, that's two judges.

**A binary verdict.** PASS or FAIL, not 1 to 5. On a 5-point scale, nobody, human or model, can say consistently what separates a 3 from a 4, so scores drift between runs. A binary verdict forces you to define the line, it's easy to compare with your own labels, and it plugs directly into the precision, recall and confidence interval math from Eval Statistics.

**Reason first, then verdict.** Asking for a short reason before the verdict gives the model room to find the unsupported claim before committing. It also gives *you* something to read when the judge disagrees with you, which is how you improve the prompt.

Here is a faithfulness judge. It uses `client.messages.parse` (the Anthropic SDK's helper; other SDKs have their own, shown in On other providers) with a Pydantic model, as in Getting Structured Output, so the verdict can only ever be `"PASS"` or `"FAIL"`:

```python
# judge.py   setup: uv add anthropic pydantic
import os
from typing import Literal

import anthropic
from pydantic import BaseModel

MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY

JUDGE_PROMPT = """You are checking one answer from a documentation assistant.

Criterion: FAITHFULNESS. The answer PASSES only if every factual claim in it is
directly supported by the sources. It FAILS if any claim is missing from the
sources, contradicts them, or adds details (numbers, names, flags, steps) the
sources do not contain. An answer that says "I don't know" PASSES.
Ignore style, length and helpfulness. They are not part of this criterion.

Examples of FAIL:
- Sources say the timeout defaults to 30 seconds; the answer says 60 seconds.
- The answer recommends a command-line flag that no source mentions.

<sources>
{sources}
</sources>

<question>{question}</question>

<answer>{answer}</answer>

First give a one- or two-sentence reason that quotes any unsupported claim.
Then give the verdict."""


class Verdict(BaseModel):
    reason: str                       # listed first so the model reasons first
    verdict: Literal["PASS", "FAIL"]


def judge_faithfulness(question: str, answer: str, sources: list[str]) -> Verdict:
    numbered = "\n\n".join(f"[{i}] {text}" for i, text in enumerate(sources, start=1))
    prompt = JUDGE_PROMPT.format(sources=numbered, question=question, answer=answer)
    response = client.messages.parse(
        model=MODEL,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
        output_format=Verdict,
    )
    return response.parsed_output


if __name__ == "__main__":
    v = judge_faithfulness(
        question="What is the default timeout?",
        answer="The default timeout is 60 seconds [1].",
        sources=["Requests time out after 30 seconds unless you pass --timeout."],
    )
    print(v.verdict, "-", v.reason)
```

The examples of FAIL in the prompt come straight from your error analysis. The best judge prompts are built from real failures, not imagined ones.

### Your judge needs its own eval

A judge is a model making predictions, so it needs to be measured like any other model. If your judge says faithfulness is 92%, that number is only as good as the judge. A judge that passes everything reports a beautiful score and catches nothing.

The method:

1. Take 50 to 100 real outputs and label each one PASS or FAIL yourself, *before* you look at any judge verdicts. Try to include at least 15 real failures; if your system rarely fails, deliberately include traces from the failure categories you found.
1. Split the labels in two. A *dev set* (about half) is what you look at while writing and tuning the judge prompt. A *test set* is the rest, which you only use to measure the finished judge. If you tune the prompt on the same examples you score it on, you are grading the judge on its own homework.
1. Run the judge on the test set and compare its verdicts with yours.

### Measuring TPR and TNR

Plain agreement ("the judge matched me 90% of the time") hides the important part. If 90% of your outputs pass, a judge that always says PASS agrees with you 90% of the time and is useless. So measure the two kinds of error separately. Treat FAIL as the thing you're trying to detect:

- **True positive rate (TPR):** of the outputs *you* labeled FAIL, the share the judge also called FAIL. This is the judge's recall for failures. Low TPR means real problems slip through.
- **True negative rate (TNR):** of the outputs you labeled PASS, the share the judge also called PASS. Low TNR means the judge cries wolf, and your scores look worse than reality.

These are the same confusion-matrix ideas from Eval Statistics, and they need confidence intervals for the same reason: with 20 failures in your test set, one disagreement moves TPR by five points.

```python
# measure_judge.py: compare judge verdicts with your own labels.
# labels_test.jsonl has one object per line:
# {"id": "q07", "question": "...", "answer": "...", "sources": ["..."], "human": "FAIL"}
import json
import random

from judge import judge_faithfulness


def rates(pairs: list[tuple[str, str]]) -> tuple[float, float]:
    """pairs are (human, judge). Returns (TPR, TNR) with FAIL as the positive class."""
    on_fails = [judge for human, judge in pairs if human == "FAIL"]
    on_passes = [judge for human, judge in pairs if human == "PASS"]
    tpr = sum(j == "FAIL" for j in on_fails) / len(on_fails)
    tnr = sum(j == "PASS" for j in on_passes) / len(on_passes)
    return tpr, tnr


def bootstrap_ci(pairs, n_resamples=2000, seed=0):
    """95% percentile bootstrap intervals for TPR and TNR."""
    rng = random.Random(seed)
    tprs, tnrs = [], []
    for _ in range(n_resamples):
        sample = [rng.choice(pairs) for _ in pairs]
        try:
            tpr, tnr = rates(sample)
        except ZeroDivisionError:  # a resample with no FAILs (or no PASSes)
            continue
        tprs.append(tpr)
        tnrs.append(tnr)

    def interval(xs):
        xs = sorted(xs)
        return xs[int(0.025 * len(xs))], xs[int(0.975 * len(xs))]

    return interval(tprs), interval(tnrs)


rows = [json.loads(line) for line in open("labels_test.jsonl")]
pairs = []
for row in rows:
    v = judge_faithfulness(row["question"], row["answer"], row["sources"])
    pairs.append((row["human"], v.verdict))
    if v.verdict != row["human"]:
        print(f"DISAGREE {row['id']}: you={row['human']} judge={v.verdict} | {v.reason}")

tpr, tnr = rates(pairs)
(tpr_lo, tpr_hi), (tnr_lo, tnr_hi) = bootstrap_ci(pairs)
print(f"TPR {tpr:.0%} (95% CI {tpr_lo:.0%}-{tpr_hi:.0%})")
print(f"TNR {tnr:.0%} (95% CI {tnr_lo:.0%}-{tnr_hi:.0%})")
```

Read every disagreement. Sometimes the judge is wrong and the prompt needs a clearer rule or a new example (drawn from the dev set, never the test set). Sometimes *you* were wrong, and you fix the label. Both are progress. Iterate on the dev set, then measure once on the test set and report that number. A common target is TPR and TNR both above 85 to 90%, but the right bar depends on what a missed failure costs you.

Once you know TPR and TNR, you can even correct the judge's raw score. If the judge flags a share `obs` of outputs as FAIL, the estimated true failure rate is `(obs + TNR - 1) / (TPR + TNR - 1)`. You'll rarely need this, but it shows why the two rates matter: they tell you exactly how the judge distorts the truth.

### Judge biases and how to reduce them

Research on LLM judges keeps finding the same habits:

- **Verbosity bias.** Judges tend to favor longer answers. Specific criteria help ("every claim is supported" doesn't reward length), and so does an explicit line like "ignore length."
- **Position bias.** When asked to pick the better of two answers, judges favor one position, often the first. If you compare pairs, run each comparison in both orders and only count consistent wins.
- **Self-preference.** Judges can favor outputs written by their own model family. When it matters, try a judge from a different provider and see whether TPR and TNR change.
- **Leniency.** Judges often pass borderline outputs. Concrete FAIL examples in the prompt pull the line back to where you drew it.

None of these biases is a reason to avoid judges. They're the reason you measure TPR and TNR, and the reason a human keeps reading a sample of outputs every week. A domain expert's judgment is the ground truth that both code checks and judges approximate; schedule time to check the approximation, especially after you change the model or the prompt.

### On other providers

Everything about measuring a judge carries over unchanged: binary verdicts, reason before verdict, dev and test splits, and TPR and TNR with bootstrap intervals. The structured-output call is what changes. On OpenAI, the SDK's helper is `client.chat.completions.parse` with `response_format=Verdict`, and the parsed object is in `choices[0].message.parsed` (see OpenAI's [Structured Outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs)). Ollama's OpenAI-compatible API accepts `response_format` too, but small local models follow schemas less reliably, so count a reply that fails to parse as a judge error, never as a silent PASS.

```python
# In judge.py, replacing the Anthropic client and judge_faithfulness.   setup: uv add openai
from openai import OpenAI

judge_client = OpenAI()  # or OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
JUDGE_MODEL = os.environ["MIMIR_JUDGE_MODEL"]  # a different family from the system you grade


def judge_faithfulness(question: str, answer: str, sources: list[str]) -> Verdict:
    numbered = "\n\n".join(f"[{i}] {text}" for i, text in enumerate(sources, start=1))
    prompt = JUDGE_PROMPT.format(sources=numbered, question=question, answer=answer)
    completion = judge_client.chat.completions.parse(
        model=JUDGE_MODEL, messages=[{"role": "user", "content": prompt}], response_format=Verdict,
    )
    return completion.choices[0].message.parsed  # None if the model refused
```

Which provider judges is a real design decision, because of self-preference. If your system runs on Claude, a judge from OpenAI or from an open family such as [Qwen3](https://ollama.com/library/qwen3) has no family style to favor, and the reverse holds if your system runs on OpenAI. Don't assume the outside judge is better, though; measure it. Run `measure_judge.py` once per judge on the same labeled test set and compare TPR and TNR with their intervals, as you would compare two classifiers. If the in-family judge passes noticeably more of the outputs you labeled FAIL (a lower TPR) than the outside judge does, that's self-preference showing up in your own data. Calibrate each judge separately, too: a prompt you tuned until one model agreed with you won't automatically transfer, so repeat the dev-set iteration whenever you change the judge model. OpenAI's [evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices) guide gives the same advice: validate a judge against human labels before you trust it.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Using LLM-as-a-Judge For Evaluation](https://hamel.dev/blog/posts/llm-judge/) by Hamel Husain.
   - Read the whole guide. It covers working with a domain expert, writing critiques, and iterating until the judge agrees with the expert, which is the loop this lesson's code automates.
1. Read [Evaluating the Effectiveness of LLM-Evaluators](https://eugeneyan.com/writing/llm-evaluators/) by Eugene Yan.
   - Read the introduction, the sections on use cases and on scoring approaches, and the key takeaways. Skim the summaries of individual papers; they are the evidence behind the biases listed above.
1. Read the grading section of [Develop tests](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests) in the Claude docs.
   - Compare code-based, human and model-based grading, and read the tips for model-based grading.
1. Practice with the [evals exercise set](https://github.com/espiNovah/project-mimir/tree/main/exercises/evals).
   - Do the exercises on code graders and on confusion-matrix rates. They're tested offline with `uv run pytest evals/<exercise>` from the `exercises/` folder, so no API key is needed.
1. Practice on your own system: collect 40 traces from your Chat With Your Docs project (question, retrieved sources and answer).
   - Label each one PASS or FAIL for faithfulness yourself first, and save them as JSONL. Split them into 20 dev and 20 test.
   - Write two code checks (for example, "has at least one citation" and "every cited number was retrieved") and run them on all 40.
   - Run the faithfulness judge from this lesson on the test set and report TPR and TNR with bootstrap confidence intervals.
   - Change the judge prompt once, using only disagreements from the dev set, and report the new TPR and TNR on the test set.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What are the three kinds of graders, and how do they trade off?](#three-kinds-of-graders)
- [Give three failure modes you can check with code instead of a model.](#code-checks-come-first)
- [Why should a judge check one criterion with a binary verdict instead of a 1-to-5 score?](#writing-a-binary-judge)
- [Why do you split your labels into a dev set and a test set before tuning a judge?](#your-judge-needs-its-own-eval)
- [What do TPR and TNR measure, and why is plain agreement not enough?](#measuring-tpr-and-tnr)
- [Name two judge biases and one way to reduce each.](#judge-biases-and-how-to-reduce-them)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [A Field Guide to Rapidly Improving AI Products](https://hamel.dev/blog/posts/field-guide/) by Hamel Husain shows where judges fit in a team's whole improvement loop.
- [Task-Specific LLM Evals that Do & Don't Work](https://eugeneyan.com/writing/evals/) by Eugene Yan surveys which automated metrics hold up for classification, summarization and other common tasks.
