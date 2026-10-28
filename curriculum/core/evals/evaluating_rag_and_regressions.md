### Introduction

A RAG system can fail in two places: it can retrieve the wrong passages, or it can answer badly from the right ones. If you only score the final answer, you can't tell which part to fix. You might spend a day rewriting the answer prompt when the real problem is that the right chunk never made it into the top 5.

This lesson shows how to evaluate retrieval and generation separately, with retrieval metrics you compute in plain Python and answer metrics that use the judges from the previous lesson. Then it turns those metrics into a *regression suite*: an eval that runs automatically in GitHub Actions on every push and fails the build when a change makes things worse. That last idea, testing prompts and retrieval settings like code, is what lets a team change an AI system without fear.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- How to evaluate retrieval and generation separately.
- Retrieval metrics: hit rate at k, recall at k, MRR and context precision.
- Answer metrics: faithfulness, correctness and refusal accuracy.
- What evaluation frameworks such as Ragas and promptfoo offer.
- What a regression is and how to catch one per question.
- How to run a regression suite in CI and fail the build.

### Evaluate the pipeline in stages

Picture your Chat With Your Docs pipeline as a chain: the question goes to the retriever, the retriever returns chunks, and the model writes an answer from those chunks. A failure at the end can start anywhere along the chain.

So for each test question, record not only a reference answer but also the IDs of the chunk or chunks that contain the answer. These are your *relevance labels*, and they let you score retrieval on its own. The order of debugging follows the chain: if the right chunk isn't retrieved, no prompt change can fix the answer. Fix retrieval first, then generation.

A test case in `eval_set.jsonl` might look like this:

```json
{"id": "q14", "type": "answerable", "question": "How do I raise the request timeout?", "relevant_ids": ["config.md#3"], "reference": "Pass --timeout with a number of seconds; the default is 30."}
```

Write these from the documents, not from your system's outputs, or you'll end up testing only what already works.

### Retrieval metrics in plain Python

Retrieval metrics compare a ranked list of retrieved IDs with the set of relevant IDs. They need no model, so they're free and perfectly repeatable. Here are the four you'll use most, where *k* is how many retrieved results you look at:

- **Hit rate at k:** did *any* relevant chunk appear in the top k? Per question it's 1 or 0; averaged over questions it's a rate.
- **Recall at k:** what share of *all* relevant chunks appeared in the top k? It matters for questions that need two passages. Ragas calls a similar idea *context recall*.
- **Precision at k:** what share of the top k chunks are relevant? Low precision means the prompt is padded with noise, which costs tokens and can distract the model. Ragas' *context precision* is a rank-weighted version that rewards putting relevant chunks near the top.
- **MRR (mean reciprocal rank):** for each question, take 1 divided by the rank of the first relevant chunk (1 if it's first, 1/2 if second, 0 if it never appears), then average. MRR rewards getting the right chunk to the very top, which matters because models pay most attention to what comes first.

```python
# retrieval_metrics.py: all four metrics, no model calls.
def hit_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    return float(any(doc_id in relevant for doc_id in retrieved[:k]))


def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    return len(relevant & set(retrieved[:k])) / len(relevant)


def precision_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    top = retrieved[:k]
    return sum(doc_id in relevant for doc_id in top) / len(top) if top else 0.0


def reciprocal_rank(retrieved: list[str], relevant: set[str]) -> float:
    for rank, doc_id in enumerate(retrieved, start=1):
        if doc_id in relevant:
            return 1 / rank
    return 0.0


if __name__ == "__main__":
    cases = [  # (what the retriever returned, what should have been returned)
        (["a#2", "b#1", "c#4", "a#7", "d#1"], {"b#1"}),
        (["e#3", "e#4", "f#1", "g#2", "h#9"], {"x#1"}),          # a miss
        (["k#1", "m#2", "k#2", "n#5", "p#1"], {"k#1", "k#2"}),   # needs two passages
    ]
    for name, fn in [("hit@5", hit_at_k), ("recall@5", recall_at_k), ("precision@5", precision_at_k)]:
        print(name, round(sum(fn(r, rel, 5) for r, rel in cases) / len(cases), 2))
    print("MRR", round(sum(reciprocal_rank(r, rel) for r, rel in cases) / len(cases), 2))
```

Running this prints `hit@5 0.67`, `recall@5 0.67`, `precision@5 0.2` and `MRR 0.5`. Only score answerable questions this way; out-of-scope questions have no relevant chunks.

Each of these is an average over questions, so it gets a bootstrap confidence interval exactly like any other score from Eval Statistics. With 40 questions, a hit rate of 0.80 can easily have an interval from 0.68 to 0.92.

### Answer metrics

Once retrieval is measured, score what the model did with the chunks it got. Three metrics cover most RAG systems:

- **Faithfulness:** is every claim in the answer supported by the *retrieved* chunks? This is the judge you built in the previous lesson, and you already know its TPR and TNR.
- **Correctness:** does the answer agree with your *reference* answer? Use code when the answer is short and exact (a number, a flag name), and a binary judge ("Does the answer state the same facts as the reference? Extra correct detail is fine; any contradiction is a FAIL") otherwise.
- **Refusal accuracy:** on out-of-scope and trick questions, did the system say "I don't know"? And on answerable questions, how often did it refuse wrongly? Track these two rates separately; a system that refuses everything scores perfectly on the first and terribly on the second.

Faithfulness and correctness are different, and the difference is diagnostic. An answer can be faithful to the wrong passage: every claim is supported by the retrieved chunk, but the chunk was about version 1 and the question was about version 2. Faithful but incorrect usually points at retrieval. Unfaithful points at generation: the model ignored or embellished its sources.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Break every score down by question type

Report each metric separately for easy, hard, multi-passage, trick and out-of-scope questions. An overall average can stay flat while one type collapses.

</div>

### What frameworks add

You can write everything above yourself in under 200 lines, and doing it once is the best way to understand it. Two free, open-source tools package the same ideas:

- **Ragas** offers ready-made RAG metrics, including context precision, context recall, faithfulness and response relevancy. Many of them use an LLM under the hood, for example to split an answer into claims and check each one.
- **promptfoo** runs prompts and models against test cases defined in a YAML config, with code-based and model-graded assertions, a results viewer, and a ready-made GitHub Action.

Treat any LLM-graded metric from a framework exactly like your own judge: label a sample yourself and measure its TPR and TNR before you trust it. A framework's faithfulness score is somebody else's judge prompt, tuned on somebody else's data.

### What a regression is

A *regression* is something that used to work and now doesn't. AI systems regress constantly, and quietly. You shrink chunk size to fix a retrieval miss and three multi-passage questions start failing. You upgrade the model and its refusals get more aggressive. The average might even go up while specific questions break.

That's why you compare results *per question*, not only per average. Save each run's per-question results to a file, then diff two runs:

```python
# compare.py: per-question diff plus a pass/fail gate for CI.
# usage: uv run python compare.py results/baseline.json results/current.json
import json
import sys

MAX_DROP = 0.05  # fail if any metric falls more than 5 points below baseline
FLOORS = {"hit_at_5": 0.80, "faithfulness": 0.85, "refusal_accuracy": 0.75}


def load(path):
    # {"metrics": {"hit_at_5": 0.86, ...}, "per_question": {"q01": {"faithfulness": 1, ...}}}
    with open(path) as f:
        return json.load(f)


base, cur = load(sys.argv[1]), load(sys.argv[2])
failed = False

for metric, old in base["metrics"].items():
    new = cur["metrics"][metric]
    flag = ""
    if new < old - MAX_DROP or new < FLOORS.get(metric, 0):
        flag, failed = "  <-- REGRESSION", True
    print(f"{metric:<18} {old:.2f} -> {new:.2f}{flag}")

for qid, old_scores in base["per_question"].items():
    for metric, old in old_scores.items():
        new = cur["per_question"][qid][metric]
        if new < old:
            print(f"  broke: {qid} {metric}")
        elif new > old:
            print(f"  fixed: {qid} {metric}")

sys.exit(1 if failed else 0)  # a non-zero exit code fails the CI job
```

The per-question lines tell you *which* questions to read. The exit code is what makes CI care.

### Comparing fairly

Before you trust a "before and after," make the comparison fair:

- **Change one thing at a time.** If you change the chunk size and the prompt together, you can't say which helped.
- **Hold everything else fixed:** the same eval set, the same judge prompt and judge model, the same k.
- **Account for noise.** Model outputs vary between runs. Run each version at least twice and look at how much the score moves between identical runs. If the confidence intervals of the two versions overlap heavily, you haven't shown a difference, so say so. A one-point change on 50 questions is usually noise.

This is also why the CI gate above uses a tolerance (`MAX_DROP`) rather than failing on any drop at all. Set the tolerance from the run-to-run variation you actually measured.

### Regression suites in CI

You already run ruff and pytest in GitHub Actions on every push. An eval regression suite is one more job in that workflow. Two practical differences: it calls a real model, so it needs your API key, and it costs money, so you keep it small.

Store the key as a repository secret (on GitHub: **Settings → Secrets and variables → Actions → New repository secret**) named `ANTHROPIC_API_KEY`. Secrets are encrypted and never printed in logs.

```yaml
# .github/workflows/evals.yml
name: evals
on:
  pull_request:
  push:
    branches: [main]

jobs:
  regression:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: astral-sh/setup-uv@v10.3.3
      - run: uv sync
      - name: Run eval set
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: uv run python run_evals.py --out results/current.json
      - name: Compare with committed baseline
        run: uv run python compare.py results/baseline.json results/current.json
```

`run_evals.py` is your own script that runs every question, applies the code checks and judges, and writes the JSON that `compare.py` reads. When you deliberately accept a new baseline, for example after an improvement, you commit the new `results/baseline.json` in the same pull request, so the history of your scores lives in Git next to the code that produced them.

Keep the CI set to a size that finishes in a few minutes and costs cents: 30 to 60 questions, the [cheap model](#/models) where your judge's TPR and TNR allow it. Run a larger set nightly or before a release.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [Ragas documentation](https://docs.ragas.io/), starting from the home page and the [list of available metrics](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/).
   - Read the descriptions of context precision, context recall, faithfulness and response relevancy. Note which ones use an LLM, and how their definitions differ from the ID-based versions in this lesson.
1. Read [promptfoo's introduction](https://www.promptfoo.dev/docs/intro/) and follow its [getting started guide](https://www.promptfoo.dev/docs/getting-started/).
   - Set up a config with two prompt variants and a few test cases, and run `promptfoo eval` and `promptfoo view`.
   - OpenAI announced it would acquire promptfoo in March 2026. It remains open source and works with many model providers, including Claude.
1. Read [promptfoo's assertions and metrics reference](https://www.promptfoo.dev/docs/configuration/expected-outputs/) to see which checks are code-based and which are model-graded, and [promptfoo's GitHub Action guide](https://www.promptfoo.dev/docs/integrations/github-action/) to compare its CI setup with the hand-written one above.
1. Revisit the sections of the [Hamel and Shreya evals FAQ](https://hamel.dev/blog/posts/evals-faq/) that cover RAG and retrieval.
1. Practice: write 20 test questions for your Chat With Your Docs system, each with the relevant chunk IDs and a short reference answer, plus 5 the documents can't answer.
   - Compute hit rate at 5, recall at 5 and MRR with the code from this lesson, each with a bootstrap confidence interval.
   - Change one retrieval setting (such as chunk size or the number of reranked results), rerun, and use `compare.py` to list which questions got better and which got worse.
   - Add the eval as a GitHub Actions job and confirm that a deliberately bad change (for example, k=1) fails the build.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Why should you score retrieval separately from the final answer?](#evaluate-the-pipeline-in-stages)
- [What is the difference between hit rate at k, recall at k and MRR?](#retrieval-metrics-in-plain-python)
- [How can an answer be faithful but incorrect, and what does that tell you?](#answer-metrics)
- [Why should you check a framework's LLM-graded metric before trusting it?](#what-frameworks-add)
- [Why compare results per question instead of only comparing averages?](#what-a-regression-is)
- [What three things make a before-and-after comparison fair?](#comparing-fairly)
- [How does an eval job in GitHub Actions fail the build?](#regression-suites-in-ci)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Evaluating Chunking Strategies for Retrieval](https://www.trychroma.com/research/evaluating-chunking) by Chroma is a worked example of measuring retrieval settings with token-level recall and precision.
- [What We've Learned From A Year of Building with LLMs](https://applied-llms.org/) collects practitioner advice on evals and RAG, including why retrieval quality usually matters more than the generator.
