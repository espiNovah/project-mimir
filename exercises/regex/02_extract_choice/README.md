# 02 · Extract a multiple-choice answer

**Lesson:** [Regular Expressions](https://espinovah.github.io/project-mimir/#/lessons/foundations/regular-expressions)

## Task

You asked a model to finish with "Answer: X", where X is A, B, C or D. Models don't always obey the format exactly. Write `extract_choice(reply)` that returns the chosen letter, uppercased, or `None` if there isn't one.

```python
extract_choice("Answer: B")                                    # 'B'
extract_choice("**Answer:** c) Because the loop never ends.")  # 'C'
extract_choice("I considered answer A, but my final answer: D.")  # 'D'
extract_choice("Answer: Because it is faster.")                # None
extract_choice("I'm not sure.")                                # None
```

Rules:

- The word "answer" can be in any case.
- Between "answer" and the letter there may be any non-word characters: colons, spaces, `**`, brackets.
- The letter must stand on its own, so "Answer: Because" does not count as B.
- If the reply says "answer" more than once, trust the **last** one.

## Hints

- One capturing group, `([A-D])`, makes `findall` return just the letters.
- `\W*` soaks up the punctuation, and `\b` after the group stops "Because" from matching.
- `re.IGNORECASE` makes `[A-D]` match lowercase letters too, so uppercase the result.

## Run the tests

```bash
cd exercises
uv run pytest regex/02_extract_choice
```

Stuck? Make the tests pass first, then compare with `solution/extract_choice.py`.
