# 03 · Deduplicate documents before embedding

**Lesson:** [Complexity and Core Data Structures](https://espinovah.github.io/project-mimir/#/lessons/foundations/complexity-and-core-data-structures)

## Task

You pay per document to embed text, so you remove duplicates first. Two documents count as the same if they match after **normalizing**: lowercase, with every run of whitespace turned into a single space and no leading or trailing spaces. `dedupe(docs)` returns the documents with later duplicates removed, keeping the **first** occurrence of each, unchanged, in the original order.

```python
dedupe(["Reset your password", "reset  your password ", "Billing FAQ"])
# ['Reset your password', 'Billing FAQ']
```

The starter is correct but keeps the normalized texts it has seen in a **list**, and checks `key not in seen` for every document. Find the hidden O(n²) and fix it.

## How the speed is tested

One test times `dedupe` on 30,000 distinct documents. The starter takes several seconds; an O(n) version takes a few hundredths of a second. The limit is a generous half second, so a correct fix passes even on a slow machine.

## Hints

- `key not in seen` looks harmless, but on a list it scans every element.
- Changing one data structure is enough. Keep the output list as a list: it needs to remember order.
- `" ".join(text.lower().split())` does the normalization.

## Run the tests

```bash
cd exercises
uv run pytest complexity/03_dedupe_documents
```

Before you change any code, write a comment at the top of the file with the Big-O of the starter and of the version you plan to write. Stuck? Make the tests pass first, then compare with `solution/dedupe_documents.py`.
