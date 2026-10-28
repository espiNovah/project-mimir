# 01 · Array methods

**Lesson:** [JavaScript Fundamentals](https://espinovah.github.io/project-mimir/#/lessons/core/javascript-fundamentals)

## Task

A chat history is an array of objects like `{ role: "user", content: "Hi", tokens: 3 }`. In `array_methods.js`, write:

- `contents(messages, role)`: the `content` of every message with that role, in order. Use `filter` and `map`.
- `totalTokens(messages)`: the sum of all `tokens`. Use `reduce`. An empty history has 0 tokens.
- `tokensByRole(messages)`: an object from each role to its token total, like `{ user: 7, assistant: 12 }`. Use `reduce` with `{}` as the start value.
- `sortNumbers(numbers)`: the numbers in ascending order, as a **new** array. Don't change the input.

```js
contents(history, "user");   // ["Hi", "Thanks"]
totalTokens(history);        // 22
tokensByRole(history);       // { system: 4, user: 7, assistant: 11 }
sortNumbers([10, 9, 1]);     // [1, 9, 10]
```

## Coming from Python

| Python | JavaScript |
| --- | --- |
| `[m["content"] for m in ms if m["role"] == r]` | `ms.filter((m) => m.role === r).map((m) => m.content)` |
| `sum(m["tokens"] for m in ms)` | `ms.reduce((total, m) => total + m.tokens, 0)` |
| `sorted(nums)` | `nums.toSorted((a, b) => a - b)` or `[...nums].sort((a, b) => a - b)` |

## Hints

- Always pass `reduce` a start value. Without one, an empty array throws a `TypeError`.
- `===` compares without type conversion. Use it instead of `==`.
- `sort()` with no comparator sorts as **strings**, so `[10, 9, 1].sort()` gives `[1, 10, 9]`. It also sorts the array in place. Pass `(a, b) => a - b`, and copy first (or use `toSorted`).
- For `tokensByRole`, `(totals[m.role] ?? 0) + m.tokens` handles the first time you see a role. `??` is like Python's `x if x is not None else 0`.

## Run the tests

```bash
cd exercises
npm test -- javascript/01_array_methods
```

Stuck? Make the tests pass first, then compare with `solution/`.
