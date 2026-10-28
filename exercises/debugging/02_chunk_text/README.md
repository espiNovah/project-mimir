# 02 · Chunk text for embedding

**Lesson:** [Debugging and Logging](https://espinovah.github.io/project-mimir/#/lessons/foundations/debugging-and-logging)

## The bug report

Before you embed a long document, you split it into overlapping chunks. `chunk_text(text, size, overlap)` should return chunks of `size` characters, each one starting `size - overlap` characters after the previous one, so neighbouring chunks share `overlap` characters. The last chunk may be shorter, and no text may be lost.

```python
chunk_text("abcdefghij", size=4, overlap=1)
# expected: ['abcd', 'defg', 'ghij']
chunk_text("abcdefghijk", size=4, overlap=1)
# expected: ['abcd', 'defg', 'ghij', 'jk']
```

Users report that the end of their documents never shows up in search results.

## How to work on it

1. Run the tests and read the failures. Which input breaks, and what came out instead?
1. Set a breakpoint (or add `breakpoint()`) and watch the variables until you see where the program stops doing what you expect.
1. Write one sentence at the top of the file saying what the bug was, then fix it.

## Run the tests

```bash
cd exercises
uv run pytest debugging/02_chunk_text
```

Stuck? Make the tests pass first, then compare with `solution/chunk_text.py`.
