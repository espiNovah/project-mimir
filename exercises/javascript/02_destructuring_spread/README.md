# 02 · Destructuring and spread

**Lesson:** [JavaScript Fundamentals](https://espinovah.github.io/project-mimir/#/lessons/core/javascript-fundamentals)

## Task

In `destructuring_spread.js`, write:

- `withDefaults(options)`: merge `options` over the defaults `{ model: "small", temperature: 0, maxTokens: 256 }` and return a **new** object. Calling it with no argument returns the defaults.
- `describe(message)`: destructure `role` and `content` in the parameter list and return `"role: content"`. A message without a `role` counts as `"user"`.
- `headAndTail(items)`: return `{ head, tail }`, where `head` is the first item and `tail` is an array of the rest.
- `updateMessage(history, index, changes)`: return a new history in which the message at `index` has `changes` merged into it. Don't change `history` or any message in it.

```js
withDefaults({ temperature: 0.7 });          // { model: "small", temperature: 0.7, maxTokens: 256 }
describe({ content: "Hi" });                 // "user: Hi"
headAndTail([1, 2, 3]);                      // { head: 1, tail: [2, 3] }
updateMessage(history, 1, { content: "Edited" });
```

## Coming from Python

| Python | JavaScript |
| --- | --- |
| `{**defaults, **options}` | `{ ...defaults, ...options }` |
| `head, *tail = items` | `const [head, ...tail] = items;` |
| `def f(options=None)` | `function f(options = {})` |
| `[*history, message]` | `[...history, message]` |

## Hints

- Later spreads win, just like later `**` unpacks in Python.
- Defaults work inside a destructuring pattern too: `function describe({ role = "user", content })`.
- `history.map((m, i) => (i === index ? { ...m, ...changes } : m))` copies only the message you change. The others are the same objects as before, which is fine because you didn't change them.
- `const` stops you reassigning a variable. It does **not** stop you changing the object it points to. That's why you copy with spread.

## Run the tests

```bash
cd exercises
npm test -- javascript/02_destructuring_spread
```

Stuck? Make the tests pass first, then compare with `solution/`.
