# 01 · Read traces

**Lesson:** [Why Evals Matter](https://espinovah.github.io/project-mimir/#/lessons/core/why-evals-matter)

## Task

`traces.jsonl` in this folder holds ten traces in the format the lesson's `traced_call` writes: one JSON object per line, with `trace_id`, `prompt_version`, `input`, `output`, `error` (`null` when the call worked) and `latency_s`, among others. There's a blank line in the middle, as there often is in a file people edit by hand. Write three functions:

- `load_traces(path)` returns a list of dicts, one per non-blank line, in file order.
- `error_rate_by_version(traces)` returns `{prompt_version: share of traces whose error is not None}`.
- `count_categories(notes)` takes your error-analysis notes, a list of dicts with `trace_id`, `note` and `category`, and returns `(category, count)` tuples, most common first. Break ties alphabetically, so the result is always in the same order.

```python
traces = load_traces("traces.jsonl")
len(traces)                     # 10
error_rate_by_version(traces)   # {'few-shot-v1': 0.25, 'few-shot-v2': 0.333...}
count_categories([
    {"trace_id": "a4d2", "note": "refund AND login; picked billing", "category": "two topics"},
    {"trace_id": "b4c8", "note": "sarcasm read as a request", "category": "sarcasm"},
    {"trace_id": "b5d6", "note": "sentence instead of a label", "category": "extra text"},
    {"trace_id": "c0a1", "note": "two topics again", "category": "two topics"},
])
# [('two topics', 2), ('extra text', 1), ('sarcasm', 1)]
```

The counts tell you which failure to fix first, which is the point of error analysis.

## Hints

- Open the file with `encoding="utf-8"`, loop over its lines, skip the ones where `line.strip()` is empty, and `json.loads` the rest.
- JSON `null` becomes Python `None`.
- For the rates, count calls and errors per version in two dicts, then divide.
- `collections.Counter` counts things. To sort by count descending and then name ascending, use `sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))`.

## Run the tests

```bash
cd exercises
uv run pytest evals/01_read_traces
```

No API key is needed: everything runs offline on fixed data. Stuck? Make the tests pass first, then compare with `solution/read_traces.py`.
