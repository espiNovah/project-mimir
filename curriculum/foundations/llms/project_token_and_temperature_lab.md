### Introduction

In this project you'll act like a scientist: instead of taking this section's claims on trust, you'll test them, measure the results and write up what you found. You'll investigate three things:

- **Tokenization:** how much the same content "costs" in tokens depending on language and format.
- **Sampling:** how temperature changes what a real (small) model generates.
- **Hallucination:** real examples of models confidently getting things wrong, and why.

Along the way you'll write a small token-counting tool. The result is a public repository that shows you understand how LLMs behave, which is exactly the understanding you'll draw on every time a model surprises you later. You don't need an API key or any money for this project.

### Before you start

- Create a new public GitHub repository named `mimir-token-lab` and clone it.
- Run `uv init`, then `uv add tiktoken` and `uv add --dev pytest ruff`.
- Add the `[tool.ruff]` and `[tool.ruff.lint]` settings and the `.github/workflows/ci.yml` file from Linting, Formatting and CI, as you did for the Expense Tracker and Weather CLI. GitHub's runners have internet access, so `tiktoken` can download its vocabulary files there the same way it did on your machine.
- Your write-up will live in `README.md`, with your raw notes and data in a `data/` or `notes/` folder.
- Have these tools open: [Tiktokenizer](https://tiktokenizer.vercel.app/) and the [Transformer Explainer](https://poloclub.github.io/transformer-explainer/).
- Find your hallucination log from the Why Models Hallucinate assignment.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Tokenizers differ between providers

`tiktoken` uses OpenAI's tokenizers. Anthropic, Google, Meta and others each use different ones, so the same text gives different counts on different models. Your numbers are real measurements for the tokenizer you chose, not universal truths. Say which tokenizer you used everywhere you report a number. You'll learn to count tokens for Claude models specifically in the Tokens, Cost and Rate Limits lesson.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. **Write a token-counting script.** Create `count_tokens.py` that takes a file path on the command line and prints the number of characters, words and tokens in the file, plus the characters-per-token ratio.
   - Add an `--encoding` option that defaults to `o200k_base` and also accepts `cl100k_base` (an older OpenAI tokenizer), so you can compare tokenizers.
   - Add a `--show` flag that prints the file with a visible separator (such as `|`) between tokens.
   - Print a clear error, not a traceback, if the file doesn't exist.
   - Put the counting logic in a function that takes a string, and write at least three pytest tests for it (for example: an empty string has zero tokens; a known short sentence has the count you measured; the counts for `o200k_base` and `cl100k_base` can differ).
   - Give the script the `main(argv=None)` shape from Command-Line Apps and add one test that calls it with a path that doesn't exist (inside `tmp_path`) and checks the exit code and error message with `capsys`, as in Testing with pytest.
1. **Lint, format and CI.** `uv run ruff check .` and `uv run ruff format --check .` must both pass, and a GitHub Actions workflow runs `uv sync --locked`, both ruff commands and `uv run pytest` on every push and pull request.
1. **Run the language and format experiment.** Choose one paragraph of English prose (about 100 words). Create at least four versions of the same content in `data/` and count each with your script using both encodings:
   - The original English.
   - A translation into a second language (one you know, or use a translation tool and say so). Bonus points for a language that doesn't use the Latin alphabet.
   - The same information as Python code (for example, a dictionary or a dataclass holding the paragraph's facts).
   - The same information as JSON.
   - Present the results as a table in your README and write a short paragraph explaining the differences. Which version was cheapest, which was most expensive, and why do you think so?
1. **Run the temperature experiment.** In the Transformer Explainer, pick a short prompt that has several plausible continuations (such as "My favorite thing to do on the weekend is").
   - Generate at least five next tokens each at three temperatures: low (0.2 or lower), the default (around 1) and high (1.5 or higher). Record every generated token.
   - Take a screenshot of the probability chart at each temperature and add them to your repository.
   - Explain in your README what temperature does to the probabilities, using your own data as evidence. Which temperature would you choose for a customer support bot, and which for brainstorming band names?
1. **Document three hallucinations.** From your log (or new attempts), pick the three most interesting hallucinations you caught. For each, record:
   - The exact prompt, the model and app you used, and the date.
   - What the model said, and what's actually true, with a link to the source you used to check.
   - Your explanation of *why* it happened, using ideas from this section (rare facts, knowledge cutoff, plausible-sounding patterns, rewards for guessing, tokenization).
   - One design change from the Why Models Hallucinate lesson that would have prevented or caught it.
1. Push your project to GitHub with a README that summarizes your three experiments, includes the tables, screenshots and hallucination write-ups, explains how to run your script and its tests, and ends with a short "What I learned" section.

#### Evidence

- `uv run pytest` passes with at least four tests, including the missing-file test, and the README includes its output.
- The GitHub Actions workflow runs ruff and pytest on every push, and the latest run on `main` passes. Show its status badge at the top of the README. (Linting, Formatting and CI)
- The README includes the command and real output of `count_tokens.py` on at least one of your `data/` files, with and without `--show`.
- The token-count table names the tokenizer for every number, and the raw files it was measured on are in `data/`.
- The three temperature screenshots are committed and shown in the README next to the tokens you recorded.
- Each hallucination write-up includes the date, the model and app, and a link to the source that shows the true answer.

#### Extra credit

- Count the tokens in a large real file, such as a long Wikipedia article saved as text or one of your own earlier projects' source files, and estimate what it would cost to send to a model at a price per million input tokens taken from a provider's pricing page. State the price and the date you looked it up.
- Write a small `sample.py` that reproduces the temperature experiment in pure Python with made-up scores for five tokens (like the example in Context Windows and Sampling), then add top-k and top-p, and plot or tabulate how the probabilities change.
- Find a short word or phrase that tokenizes very differently in `o200k_base` and `cl100k_base`, and explain what that suggests about how tokenizers change between model generations.

</div>

### Submitting your work

A strong submission reads like a small lab report. Someone skimming your README should be able to see your three findings in under two minutes, with the evidence right there: the token count table, the temperature screenshots and the hallucination examples with their sources. Be precise about your setup (tokenizer names, temperatures, model and app names, dates), because results that can't be reproduced aren't very useful. And be honest: if an experiment surprised you or didn't show what you expected, say so and offer an explanation. That's good science, and it's exactly how you'll write eval reports later.
