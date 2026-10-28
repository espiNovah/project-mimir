# 03 · Modules: import and export

**Lesson:** [JavaScript Fundamentals](https://espinovah.github.io/project-mimir/#/lessons/core/javascript-fundamentals)

## Task

This exercise has two files.

1. In `text.js`, write the two text helpers and **export** them:
   - `slugify(title)` (named export): lower-case the title, replace every run of characters that aren't `a-z` or `0-9` with one `-`, and trim `-` from both ends.
   - `truncate(text, max)` (named export): return `text` unchanged if it has at most `max` characters. Otherwise cut it and end it with `"…"` so the result is exactly `max` characters long.
   - `wordCount(text)` is already written. Make it the file's **default** export.
2. In `index.js`, re-export `slugify` and `truncate` from `./text.js`, and re-export the default `wordCount` as a **named** export called `wordCount`. Other code can then import everything from one place.

```js
import wordCount, { slugify } from "./text.js";
import { slugify, truncate, wordCount } from "./index.js";

slugify("  Hello, World! 2025 ");   // "hello-world-2025"
truncate("streaming", 6);           // "strea…"
```

## Coming from Python

| Python | JavaScript |
| --- | --- |
| everything at module level is importable | only what you mark with `export` is importable |
| `from text import slugify` | `import { slugify } from "./text.js";` |
| `import text` | `import * as text from "./text.js";` |
| re-exporting in `__init__.py` | `export { slugify } from "./text.js";` |

## Hints

- Relative imports need the `./` and the `.js` extension in Node and in browsers.
- A file has at most one `export default`. Importers pick its name: `import anything from "./text.js"`.
- `export { default as wordCount } from "./text.js";` turns a default export into a named one.
- For `slugify`, the regex `/[^a-z0-9]+/g` matches a run of other characters, and `/^-+|-+$/g` matches dashes at the ends.

## Run the tests

```bash
cd exercises
npm test -- javascript/03_modules
```

Stuck? Make the tests pass first, then compare with `solution/` (it has both files).
