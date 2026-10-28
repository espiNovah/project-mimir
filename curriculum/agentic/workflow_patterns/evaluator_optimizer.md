### Introduction

Good writers rarely get it right on the first draft. They write, reread, spot problems and revise. The **evaluator-optimizer** pattern gives an LLM system the same habit: one call generates a response, another evaluates it against clear criteria, and the feedback drives a revision. Used well, it can lift quality noticeably. Used carelessly, it burns tokens on endless loops of tiny changes. This lesson covers how to get the first without the second.

You've already built half of this pattern twice. In Chaining and Routing, a gate rejected a draft and the chain retried once with feedback. In Code Checks and LLM-as-Judge, you wrote judges that return a PASS or FAIL verdict with a reason. Evaluator-optimizer joins those two ideas into a loop and adds the questions that decide whether the loop is worth running: when to stop, which draft to keep, and how to prove each extra round bought something.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- How the generate, evaluate, revise loop works.
- When the pattern helps, and when it does not.
- Writing evaluation criteria a model can apply consistently.
- Combining model feedback with code checks.
- Stopping the loop: iteration caps, "good enough" thresholds and no-progress checks.
- Keeping the best draft instead of the last one.
- Measuring how much each extra iteration improves quality, and what it costs.

### Two roles, one loop

The pattern has two roles. The **generator** (Anthropic's guide calls it the optimizer) produces a draft. The **evaluator** reviews the draft and returns a verdict, such as pass or fail, plus specific feedback. If the draft fails, the generator revises it using that feedback, and the evaluator looks again.

```text
task ──> generator ──> draft ──> evaluator ──> PASS ──> return the draft
             ^                       │
             └──── feedback <── FAIL ┘   (until the cap is reached)
```

The two roles don't need two different models. Usually they are the same model with two different prompts: one that says "write this," and one that says "check this against these criteria." Splitting the jobs works for the same reason sectioning worked in Parallelization and Orchestrator-Workers. Each prompt has one clear goal, and a model asked to check a finished piece of writing notices problems it glossed over while it was producing it.

Notice that this is still a **workflow**, not an agent. Your code decides how many rounds can run, what counts as passing, and what happens at the end. The model only fills in the drafts and the verdicts. That's what makes the loop testable: you can count its rounds, log every verdict, and cap its spending.

It also helps to see how it differs from the gate in `chain.py`. A gate is plain code with a yes or no answer, and its feedback is a fixed sentence such as "It did not cite any article ID." An evaluator can judge things code can't, like whether a sentence would confuse a parent, and it writes feedback tailored to the draft in front of it. The price is that every evaluation is another model call, with its own tokens, latency and mistakes.

### When the loop pays off

Anthropic's [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) gives a two-part test. The pattern fits when:

1. **A human could improve the output by giving written feedback.** If an editor's note like "this paragraph uses three terms a beginner won't know" would make the next draft better, the task has room for revision.
1. **A model can give similar feedback.** The evaluator has to be able to spot the problem. If even you can't say what's wrong with a draft, a model can't either.

Good fits include literary translation (an evaluator catches nuances the first pass missed), code that must pass tests (the test output *is* the feedback), writing for a specific audience or reading level, and search tasks where each round shows what's still missing.

Poor fits are just as common:

- **Vague goals.** "Make it better" has no stopping point. The evaluator will always find something, and the generator will keep making changes that are different, not better.
- **Tasks the model already does well.** If 95% of first drafts pass, the loop adds an evaluation call to every request to fix 5% of them. A cheap code check or a sampled human review might catch those for less.
- **Errors the model can't see.** A model asked to recheck its own arithmetic or reasoning often confirms the wrong answer, or "fixes" a right one. Research such as [Large Language Models Cannot Self-Correct Reasoning Yet](https://arxiv.org/abs/2310.01798) found that, without outside feedback like a test result or a tool, self-correction on reasoning tasks often made answers worse. Loops work best when the evaluator has something concrete to check against: criteria, a source text, test output or a tool result.
- **Latency-sensitive answers.** Each round is a generation plus an evaluation, one after another. Three rounds can mean six sequential calls while a user stares at a spinner.

### Criteria an evaluator can apply

The evaluator is a judge, so everything from Code Checks and LLM-as-Judge applies. Two habits matter most here.

**One binary verdict per criterion.** Asking for "overall quality from 1 to 10" gives you a number that drifts between runs and feedback that is impossible to act on. Instead, list a few named criteria, each with a one-line definition, and ask for PASS or FAIL on each one with a short reason first. "Clear action: the reader knows exactly what to do, and by when" is a criterion. "Engaging" is not, until you define what you mean by it.

**Structured output.** Ask the evaluator for JSON with a field per criterion and a `feedback` field, using `messages.parse` and a Pydantic model as in Getting Structured Output. Then your code can decide what to do next by reading fields, not by parsing prose. It can count how many criteria passed, notice that "no jargon" failed three rounds in a row, and log every verdict in a form you can analyze later.

The feedback itself should be an instruction the generator can follow, not a grade. "The phrase 'MFA' is unexplained; say 'a second sign-in step, such as a code sent to your phone'" fixes a draft. "Too technical" usually produces a different draft that is still too technical.

### Code checks first, then the model

If something can be checked by code, check it with code: word count, required facts, valid JSON, tests passing, a link that resolves. Code checks are free, instant and give the same answer every time. Use the model evaluator only for what code cannot judge, such as tone, clarity or whether a summary is faithful to its source.

Order matters too. Run the code checks first, and skip the model evaluation when they fail. There's no point paying a model to judge the tone of a draft that is 40 words over the limit; the draft has to change anyway, and the code check already wrote the feedback.

### Stopping the loop

A loop needs a reason to stop, and in practice you want three:

1. **It passed.** Every criterion is met. Stop immediately; an extra round can only add cost and risk.
1. **It hit the cap.** Always set a maximum number of rounds, such as three. Without a cap, a picky evaluator can loop forever. Later rounds also tend to make smaller, sometimes harmful, changes, so most of the gain usually comes in the first revision or two. You'll measure that below.
1. **It stopped improving.** If a revision scores no better than the best draft so far, the feedback isn't working. Another round with the same prompts is unlikely to do better, so stop early and save the money.

What "passed" means is a design decision. Requiring every criterion is strict and clear. A **good-enough threshold**, such as "all code checks plus at least one of the two model criteria," trades a little quality for fewer rounds. Decide it in advance and write it in code, so the loop never depends on the evaluator's mood.

Finally, decide what happens when the cap is reached without a pass. You have the same choices as a failed gate: return the best draft with a warning, or send it to a human with the last feedback attached.

### Walkthrough: a plain-language rewriter

This loop rewrites a jargon-heavy IT notice for parents and students at the school from Chaining and Routing. Code checks enforce length, sentence length and three facts that must survive word for word. A model evaluator judges two criteria code can't: no jargon, and a clear action. Set up a project with `uv init refine`, run `uv add anthropic pydantic python-dotenv`, and save this as `refine.py`:

```python
# refine.py  (run with: uv run refine.py)
import json
import os
import re

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
client = anthropic.Anthropic()
MAX_WORDS, MAX_SENTENCE = 120, 25

SOURCE = """IT NOTICE: Effective Mon 3 Nov, legacy SSO credentials will be deprecated.
All users must enroll in MFA via the self-service portal (mfa.school.example) prior
to cutover. Non-compliant accounts will be suspended pending remediation. Hardware
tokens are available on request from Room B12."""
FACTS = ["3 Nov", "mfa.school.example", "B12"]  # must appear word for word


class Criterion(BaseModel):
    reason: str = Field(description="One sentence; quote the problem if there is one")
    passed: bool


class Evaluation(BaseModel):  # (1) one binary verdict per named criterion
    no_jargon: Criterion = Field(description="A parent with no IT background understands every word")
    clear_action: Criterion = Field(description="The reader knows exactly what to do, and by when")
    feedback: str = Field(description="If anything failed, specific instructions to fix it; else empty")


def tokens(response) -> dict:
    return {"in": response.usage.input_tokens, "out": response.usage.output_tokens}


def generate(source: str, facts: list[str], previous: str, feedback: str):
    prompt = (f"Rewrite this notice for parents and students in plain words. Stay under "
              f"{MAX_WORDS} words and keep these details exactly: {', '.join(facts)}.\n\n"
              f"<notice>\n{source}\n</notice>")
    if previous:  # (2) a revision sees its last draft and the feedback, not every round
        prompt += f"\n\n<draft>\n{previous}\n</draft>\nRevise the draft. Fix exactly this: {feedback}"
    response = client.messages.create(
        model=MODEL, max_tokens=2000, messages=[{"role": "user", "content": prompt}])
    return "".join(b.text for b in response.content if b.type == "text").strip(), tokens(response)


def code_checks(draft: str, facts: list[str]) -> list[str]:
    problems = [f"Include '{f}' exactly as written." for f in facts if f not in draft]
    if (words := len(draft.split())) > MAX_WORDS:
        problems.append(f"It is {words} words; the limit is {MAX_WORDS}.")
    sentences = [s for s in re.split(r"[.!?]+\s+", draft) if s.strip()]
    if sentences and (longest := max(len(s.split()) for s in sentences)) > MAX_SENTENCE:
        problems.append(f"One sentence is {longest} words; keep each under {MAX_SENTENCE}.")
    return problems


def evaluate(draft: str):
    response = client.messages.parse(
        model=MODEL, max_tokens=2000, output_format=Evaluation,
        system="You review school notices strictly. Judge only the listed criteria.",
        messages=[{"role": "user", "content": f"<notice>\n{draft}\n</notice>"}])
    return response.parsed_output, tokens(response)


def refine(source: str, facts: list[str], max_rounds: int = 3,
           log_path: str | None = "rounds.jsonl") -> dict:
    total = len(facts) + 2 + 2  # facts, two length checks, two model criteria
    rounds, draft, feedback = [], "", ""
    for n in range(1, max_rounds + 1):  # (3) the hard cap
        draft, used = generate(source, facts, draft, feedback)
        problems, model_passed = code_checks(draft, facts), 0
        if not problems:  # (4) only pay for the model when the code checks pass
            verdict, judge_used = evaluate(draft)
            used = {k: used[k] + judge_used[k] for k in used}
            if verdict is None:
                problems = ["The evaluator gave no verdict."]
            else:
                model_passed = verdict.no_jargon.passed + verdict.clear_action.passed
                if model_passed < 2:
                    problems = [verdict.feedback or "Fix the failed criteria."]
        code_passed = total - 2 - len(problems) if model_passed or not problems else 0
        score = (len(facts) + 2 - len(code_checks(draft, facts))) + model_passed
        record = {"round": n, "score": score, "of": total, "passed": score == total,
                  "feedback": " ".join(problems), "tokens": used, "draft": draft}
        rounds.append(record)
        if log_path:  # (5) every round is logged, like a trace span
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        if record["passed"]:
            break
        if n > 1 and score <= max(r["score"] for r in rounds[:-1]):
            break  # (6) no progress: more rounds of the same feedback won't help
        feedback = record["feedback"]
    best = max(rounds, key=lambda r: (r["score"], -r["round"]))  # (7) best, not last
    return {"best": best, "rounds": rounds}


if __name__ == "__main__":
    result = refine(SOURCE, FACTS)
    for r in result["rounds"]:
        print(f"round {r['round']}: {r['score']}/{r['of']}  {r['feedback'] or 'PASS'}")
    print(f"\nkept round {result['best']['round']}:\n{result['best']['draft']}")
```

Walk through the numbered comments:

1. **A structured verdict.** `Evaluation` has one `Criterion` per thing you care about, each with its reason listed before its verdict so the model reasons first. Your code reads `passed` fields; it never parses prose.
1. **Lean revisions.** The revision prompt carries the source, the previous draft and the feedback, not a growing transcript of every round. That keeps each round's input about the same size, which matters for cost, as you'll see in Agent Cost and Latency.
1. **The cap.** `max_rounds` is a parameter with a small default. Three is a sensible start; your measurements will tell you whether it should be two.
1. **Code before model.** When a fact is missing or the draft is too long, the round costs one generation and zero evaluations. The code check's message becomes the feedback.
1. **Logging.** Each round is one JSON line with its score, feedback, tokens and draft. When the loop misbehaves, this file shows you which round went wrong, the same way traces did in Agent Tracing and Debugging.
1. **The no-progress stop.** A round that doesn't beat the best score so far ends the loop.
1. **Keep the best draft.** Covered next.

The score counts how many checks passed, out of seven. Because the model criteria are only checked once the code checks pass, a draft that fails a code check gets zero for the model criteria, which ranks it below any draft that meets the hard requirements. That ordering is deliberate: a beautifully clear notice that drops the deadline is worse than a slightly stiff one that keeps it.

Run it a few times and read `rounds.jsonl`. You'll see runs that pass on round one, runs where round two fixes a missing fact, and the occasional run where the evaluator keeps objecting to the word "portal."

### Keep the best draft

The obvious way to write the loop returns whatever the last round produced. That's a bug waiting to happen. A revision can fix the jargon and drop the deadline in the process, or follow the feedback so literally that it breaks something that was fine. If the loop then hits its cap, the last draft is worse than an earlier one, and you return it anyway.

So track every round's score and return the highest-scoring draft, breaking ties in favor of the earliest round (it took less editing to get there, and it's what the evaluator saw first). This one line, `max(rounds, key=...)`, also gives the loop a useful guarantee: by the evaluator's own measure, the result can never be worse than the first draft. Extra rounds can waste money, but they can't make the output worse in the eyes of the evaluator.

That last phrase is the catch, and it leads to measurement.

### Measuring improvement per iteration

The loop feels like it helps, because you watch it fix things. Feelings aren't evidence. You want three numbers, from the Measuring Quality section:

- **Pass rate by round.** On a set of test inputs, what fraction pass by round 1, by round 2 and by round 3? This shows where the gains come from. If round 3 lifts the pass rate from 84% to 85%, the cap should probably be 2.
- **Cost by round.** The average tokens and dollars spent if you stopped after each round. Cases that pass early stop early, so the cost of a cap of 3 is less than three times the cost of a cap of 1.
- **The gain, with an interval.** The difference between first drafts and final drafts, as a paired comparison with a bootstrap confidence interval, exactly as in Eval Statistics.

Write a `cases.jsonl` file with one notice per line, like `{"source": "...", "facts": ["5 Dec", "Room A4"]}`, and save this next to `refine.py` as `measure.py` (run `uv add numpy` first):

```python
# measure.py  (run with: uv run measure.py)
import json

import numpy as np

from refine import refine

PRICE_IN, PRICE_OUT = 0.10, 0.50  # $ per million tokens for the cheap model; check the pricing page


def cost(rounds: list[dict]) -> float:
    return sum(r["tokens"]["in"] * PRICE_IN + r["tokens"]["out"] * PRICE_OUT
               for r in rounds) / 1_000_000


cases = [json.loads(line) for line in open("cases.jsonl", encoding="utf-8")]
results = [refine(c["source"], c["facts"], max_rounds=3, log_path=None) for c in cases]
n = len(results)

for k in (1, 2, 3):  # what if the cap had been k?
    passed = sum(any(r["passed"] for r in res["rounds"][:k]) for res in results)
    spent = sum(cost(res["rounds"][:k]) for res in results) / n
    print(f"cap {k}: pass {passed}/{n} ({passed / n:.0%}), avg cost ${spent:.6f} per case")

first = np.array([res["rounds"][0]["passed"] for res in results], dtype=float)
final = np.array([res["best"]["passed"] for res in results], dtype=float)
diff = final - first  # paired: same cases, before and after the loop
idx = np.random.default_rng(0).integers(0, n, size=(10_000, n))  # fixed seed
low, high = np.percentile(diff[idx].mean(axis=1), [2.5, 97.5])
print(f"gain from the loop: {diff.mean():+.0%} (95% CI {low:+.0%} to {high:+.0%}, n={n})")
print(f"rounds used on average: {np.mean([len(r['rounds']) for r in results]):.2f}")
```

The loop for `k` replays one set of results as if the cap had been 1, 2 or 3. That works because a capped loop is the same loop with its later rounds removed, so you don't need to pay for three separate experiments.

Now the catch. Every number above was scored by the loop's *own* evaluator, the one the generator was revising against. A generator can learn to satisfy a particular evaluator without really improving, for example by adding "Do this by 3 Nov" to every sentence because the evaluator once complained about a missing deadline. So for a real decision, score a sample of first and final drafts with something independent: your own labels (Error Analysis and Labeling), or a separate judge with different criteria that you've validated against those labels. If the independent score barely moves, the loop is teaching the generator to please the evaluator, not to write better notices.

Then make the call with all three numbers in front of you. "The loop lifts the pass rate from 62% to 88% (paired 95% CI +14% to +38%, n = 50), at 2.4 times the cost per notice, with almost all of the gain in round 2" is a decision you can defend. It probably means "keep the loop, cap it at 2." "+3%, CI −4% to +10%" means the extra calls aren't worth their cost.

### Evaluator pitfalls

A few failure patterns show up again and again in evaluator-optimizer loops. Each one leaves a mark in your round log.

- **The evaluator is too easy.** Almost everything passes on round one, including drafts you'd reject. Check it the way you checked judges: measure its TPR and TNR against a few dozen labeled drafts. An evaluator that never fails anything is an expensive way to do nothing.
- **The evaluator is too picky.** Nothing ever passes, so every case runs to the cap. Look at the feedback field across rounds. If it keeps raising new, minor complaints, tighten the criteria definitions or loosen the pass threshold.
- **Oscillation.** Round 2 fixes the jargon and breaks the length; round 3 fixes the length and brings the jargon back. The scores go up and down instead of up. The no-progress stop catches this, and keep-the-best returns the good draft. A permanent fix is to send *all* the failed criteria in the feedback at once, not just the newest one.
- **Grading its own homework.** Using the same model and similar prompts for both roles can make the evaluator share the generator's blind spots. If error analysis shows the evaluator missing a whole kind of problem, try a stronger model for the evaluator only (the Support Ticket Pipeline project allows exactly this), or a different prompt framing.
- **Feedback the generator can't act on.** "Improve clarity" leads to random edits. Make the feedback field's description demand specific, quoted problems and concrete fixes.

The same ideas reach well beyond writing. A coding agent that runs the tests, reads the failures and edits the code is an evaluator-optimizer loop where the evaluator is a test suite, and the guardrails you'll build in the Safety section are evaluators that check output before a user sees it.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read "Workflow: Evaluator-optimizer" and "Combining and customizing these patterns" in [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents).
   - Note the two signs it gives that the pattern fits, and compare them with the poor fits listed in this lesson.
1. Work through the [evaluator-optimizer notebook](https://github.com/anthropics/claude-cookbooks/blob/main/patterns/agents/evaluator_optimizer.ipynb) in the Claude Cookbooks.
   - Notice how the evaluator's response is parsed and how the loop decides when to stop. Change it so the loop stops after at most three iterations.
   - The notebook passes the whole history of attempts back to the generator. Compare that with the lean revision prompt in `refine.py`, and note what each costs as the rounds pile up.
1. Read the "Guardrails" section of OpenAI's [A Practical Guide to Building Agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf). Guardrails are closely related: an evaluator that checks output before it reaches the user.
1. Practice: build a loop that writes a product description under 80 words that mentions three given features.
   - Use a code check for length and features and a model evaluator for tone, with a binary verdict per criterion and structured output.
   - Cap it at three rounds, stop early on a pass or when the score doesn't improve, and return the best draft.
   - Log each round's score and draft, and note on which round it passed.
1. Practice: measure your loop with `measure.py` (adapted to your task) on at least 15 inputs.
   - Report the pass rate and average cost for caps of 1, 2 and 3, and the paired gain with its 95% interval.
   - Hand-label the first and final drafts for 10 of the inputs yourself. Does your labeling agree with the evaluator about how much the loop helped? Write two sentences on which cap you'd ship and why.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What do the generator and the evaluator each do, and why can they be the same model?](#two-roles-one-loop)
- [What two signs suggest the evaluator-optimizer pattern fits a task, and when does it waste money?](#when-the-loop-pays-off)
- [Why should the evaluator return one binary verdict per criterion as structured output?](#criteria-an-evaluator-can-apply)
- [Why run code checks before the model evaluator?](#code-checks-first-then-the-model)
- [What three reasons should a loop have to stop?](#stopping-the-loop)
- [Why return the best-scoring draft instead of the last one?](#keep-the-best-draft)
- [How would you show that each extra iteration is worth its cost, and why isn't the loop's own evaluator enough?](#measuring-improvement-per-iteration)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Self-Refine: Iterative Refinement with Self-Feedback](https://arxiv.org/abs/2303.17651) is the research paper that popularized generate, critique and revise loops, with results across tasks and a look at how gains shrink with each round.
- [Large Language Models Cannot Self-Correct Reasoning Yet](https://arxiv.org/abs/2310.01798) is the counterpoint: why loops without outside feedback can make reasoning answers worse.
