### Introduction

Most people tweak a prompt, look at one or two outputs, and decide it "feels better." In this project you will do what professionals do instead: build a small labelled test set, run several prompt variants against it, and let a score decide. You will pick one task, write at least three prompt variants using the techniques from this section, measure each one with code, and then try a two-step chain on an input that every variant gets wrong.

The habit you build here, measure before you believe, is the foundation of the Evals section later in this path.

### Before you start

- Create a new GitHub repository called `mimir-prompt-lab` and set it up as a `uv` project, as you did in the Hello, uv project. Add the `anthropic` package with `uv add anthropic`.
- Make sure `ANTHROPIC_API_KEY` is set in your environment and that `.env` is in your `.gitignore` (see the API Keys and Secrets lesson).
- Choose a task with a clear right answer that code can check. Good options:
  - Classify support emails into categories such as `billing`, `bug`, `feature_request`, `account_access` and `other`.
  - Label product reviews as `positive`, `negative` or `mixed`.
  - Decide whether a job posting is remote, hybrid or on-site.
- Use the [cheap model](#/models) for your runs. It is cheap, and small models make prompt differences easier to see.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Make the test set hard on purpose

If every variant scores 100%, your test set is too easy to tell them apart. Include ambiguous inputs, sarcasm, emails that mention two topics, and very short or very long inputs. Hard cases are where good prompts earn their keep.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Write 15 realistic inputs for your task and label each one by hand with the correct answer. Store them in `data/test_set.jsonl`, one JSON object per line with `id`, `input` and `expected` fields. Write the labels yourself before running any model, so the model cannot influence them.
1. Write at least three prompt variants, each in its own file under `prompts/`:
   - **Zero-shot:** clear instructions and a list of allowed labels, no examples.
   - **Few-shot:** the same instructions plus 3 to 5 examples. Do not reuse inputs from your test set as examples.
   - **Structured with thinking:** instructions and data separated with XML tags, the model asked to reason inside `<thinking>` tags first and give its final label inside `<answer>` tags.
1. Write `run.py`, which runs every variant on every test input, extracts the label from the response with code (no eyeballing), and compares it to `expected`. A response that does not contain a valid label counts as wrong.
1. Print and save a results table, with one row per variant, showing at least: accuracy (correct out of 15), number of invalid outputs, total input and output tokens, and average latency in seconds. Save the raw model outputs to `results/` so you can inspect failures.
1. Run each variant at least twice and report whether scores changed between runs. Explain in one or two sentences why they might.
1. Pick one input that most variants got wrong. Build a two-step prompt chain for it (for example, step one lists the topics the email mentions, step two picks the label from that list). Run it on that input and on the rest of the test set, and write a short note on whether the chain helped, hurt, or made no difference, and what it cost in extra tokens.
1. Push your project to GitHub with a README that explains what it does, how to run it, and what you learned.

#### Extra credit

- Add a fourth variant of your own design, and explain the hypothesis behind it before you run it.
- Run your best variant with the [capable model](#/models) or a model from another provider, and compare accuracy against cost.
- Grow the test set to 50 inputs and see whether the ranking of variants holds.

</div>

### Submitting your work

A strong submission makes the results easy to trust. Your README should show the results table, explain your task and labels, show one or two example failures with the raw model output, and state which variant you would ship and why. Anyone should be able to clone the repo, set their API key, run one command and reproduce your numbers within a few points.
