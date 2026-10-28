# 02 · Code checks

**Lesson:** [Code Checks and LLM-as-Judge](https://espinovah.github.io/project-mimir/#/lessons/core/code-checks-and-llm-as-judge)

## Task

Code graders are the cheapest evals: plain functions that return `True` for PASS. Write four of them for a docs chatbot that answers with numbered citations like `[2]`:

- `has_citation(answer)`: every answer must cite at least one source, **unless** it's a refusal containing "i don't know" (in any case).
- `citations_were_retrieved(answer, num_sources)`: a citation `[n]` is only valid if `1 <= n <= num_sources`. Return `True` if every citation is valid (an answer with no citations passes this check; `has_citation` catches that).
- `under_word_limit(answer, limit=150)`: at most `limit` words, splitting on whitespace.
- `is_allowed_label(output, allowed)`: for a classifier, the output must be **exactly** one of the allowed labels, after stripping surrounding whitespace. "Label: billing" fails.

```python
answer = "Set the timeout with --timeout [2]. The default is 30 seconds [5]."
has_citation(answer)                   # True
citations_were_retrieved(answer, 4)    # False: [5] was never retrieved
is_allowed_label(" billing\n", {"billing", "bug", "other"})   # True
```

Then write `run_checks(answer, num_sources)`, which returns a dict of the three answer checks' results, keyed `"has_citation"`, `"citations_were_retrieved"` and `"under_word_limit"`.

## Hints

- `re.compile(r"\[(\d+)\]")` matches `[1]`, `[12]`. With one group, `findall` returns the numbers as strings.
- `all([])` is `True`.
- Test each check on outputs that should fail, not just ones that should pass.

## Run the tests

```bash
cd exercises
uv run pytest evals/02_code_checks
```

No API key is needed: everything runs offline on fixed data. Stuck? Make the tests pass first, then compare with `solution/code_checks.py`.
