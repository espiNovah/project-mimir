### Introduction

Most people tweak a prompt, look at one or two outputs, and decide it "feels better." In this project you will do what professionals do instead: build a small labelled test set, run several prompt variants against it, and let a score decide. You will pick one task, write at least three prompt variants using the techniques from this section, measure each one with code on two models from different providers, and then try a two-step chain on an input that every variant gets wrong.

The habit you build here, measure before you believe, is the foundation of the Measuring Quality section that comes next, where you'll return to this project to read its traces and put confidence intervals on its scores.

### Before you start

- Create a new GitHub repository called `mimir-prompt-lab` and set it up as a `uv` project, as you did in the Hello, uv project. Add the `anthropic` and `openai` packages with `uv add anthropic openai`, and `pytest` and `ruff` as dev dependencies with `uv add --dev pytest ruff`.
- Make sure `ANTHROPIC_API_KEY` is set in your environment and that `.env` is in your `.gitignore` (see the API Keys and Secrets lesson).
- Choose a task with a clear right answer that code can check. Good options:
  - Classify support emails into categories such as `billing`, `bug`, `feature_request`, `account_access` and `other`.
  - Label product reviews as `positive`, `negative` or `mixed`.
  - Decide whether a job posting is remote, hybrid or on-site.
- Use the [cheap model](#/models) for your Claude runs. It is cheap, and small models make prompt differences easier to see.
- Choose your second model, from a different provider. The free option is a small local model through Ollama, such as `qwen3:4b`, called with the OpenAI SDK as in the "On other providers" section of Prompting Fundamentals. Install [Ollama](https://ollama.com/) and pull the model before you start. If you have credit with OpenAI or another provider with an OpenAI-compatible API, a hosted model works too.

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
1. Run every variant on two models: one Claude model and one model from another provider or a local open model through Ollama. Put each provider behind one small function, such as `complete(prompt, model) -> (text, input_tokens, output_tokens, seconds)`, so the prompts, label extraction and scoring are shared and only the API call differs. Map each provider's usage fields onto the same names, as shown in "On other providers" in Prompting Fundamentals (`input_tokens` and `output_tokens` on Claude, `prompt_tokens` and `completion_tokens` on OpenAI-style APIs). Send the same prompt text to both; if a model has a built-in thinking switch, note whether it was on, as in Thinking and Prompt Chaining.
1. Print and save a results table, with one row per variant and model, showing at least: accuracy (correct out of 15), number of invalid outputs, total input and output tokens, and average latency in seconds. Save the raw model outputs to `results/` so you can inspect failures.
1. Run each variant at least twice on each model and report whether scores changed between runs. Explain in one or two sentences why they might. Then write a short comparison of the two models: which variant won on each, whether the ranking of variants was the same, and how invalid outputs, tokens and latency differed. Report cost for each model as well ("$0.00 (local)" for Ollama).
1. Pick one input that most variants got wrong. Build a two-step prompt chain for it (for example, step one lists the topics the email mentions, step two picks the label from that list). Run it on that input and on the rest of the test set, and write a short note on whether the chain helped, hurt, or made no difference, and what it cost in extra tokens.
1. Write pytest tests that never call a model, as in Testing with pytest. At minimum, test the function that pulls a label out of a response: a clean label, a label inside `<answer>` tags, extra whitespace or capitalization, and an invalid label. Then test `run.py`'s scoring with a fake client swapped in with `monkeypatch` or passed in as an argument, so a fixed set of fake responses produces a known accuracy and invalid count. Give each provider's usage mapping a test too, using a fake response object.
1. Push your project to GitHub with a README that explains what it does, how to run it, and what you learned.

#### Evidence

- A GitHub Actions workflow runs `ruff check`, `ruff format --check` and `pytest` on every push, and the latest run on `main` passes. Show its status badge at the top of the README. The tests use fakes, so CI needs no API key. (Linting, Formatting and CI)
- The README shows the results table from requirement 5 for both runs of every variant on both models, produced by `run.py`, with the same metrics for each model, and the raw outputs behind it are committed in `results/`. Each row names the provider and model ID.
- The README's model comparison from requirement 6, in a few sentences, says which model and variant you would ship and why.
- One command per model, given in the README, reproduces the table from a fresh clone with only an API key set (or Ollama running, for a local model).
- No confidence interval is required yet. Scores out of 15 are rough, and you'll add intervals and a paired comparison to this table in the Eval Statistics assignment, so keep `run.py` easy to extend.

#### Extra credit

- Add a fourth variant of your own design, and explain the hypothesis behind it before you run it.
- Run your best variant with the [capable model](#/models) or a third provider, and compare accuracy against cost.
- Grow the test set to 50 inputs and see whether the ranking of variants holds.

</div>

### Submitting your work

A strong submission makes the results easy to trust. Your README should show the results table for both models, explain your task and labels, show one or two example failures with the raw model output, and state which variant you would ship and why. Anyone should be able to clone the repo, set their API key, run one command and reproduce your numbers within a few points.
