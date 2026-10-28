# 02 · Unions and narrowing

**Lesson:** [TypeScript Basics](https://espinovah.github.io/project-mimir/#/lessons/core/typescript-basics)

## Task

A streaming chat sends four kinds of event. `StreamEvent` in `unions_narrowing.ts` is a **discriminated union**: every member has a `type` field with a different literal value, so checking `event.type` tells TypeScript which member you have.

1. `applyEvent(state, event)` returns the **new** `ChatState` after one event. Don't change `state`.
   - `token`: append `event.text` to `text`.
   - `citations`: add `event.sources` to the end of `sources`.
   - `done`: set `status` to `"done"`.
   - `error`: set `status` to `"error"` and `error` to `event.message`.
   - Any other `type` (it can happen when the data comes from outside your program): throw an `Error` whose message contains the unknown type.

   Use a `switch` on `event.type`. In the `default` branch, assign `event` to a variable of type `never`. If you later add a fifth event type and forget to handle it, TypeScript reports an error there.
2. `toDisplay(value)` takes a `string | number | string[] | null` and returns a string:
   - `null` gives `""`, a string is returned as it is, a number is formatted with `toLocaleString("en-US")` (so `1234.5` gives `"1,234.5"`), and an array is joined with `", "`.

```ts
let state = initialState();
state = applyEvent(state, { type: "token", text: "Hi" });
state = applyEvent(state, { type: "done", stopReason: "end_turn" });
// { text: "Hi", sources: [], status: "done" }
```

## Coming from Python

A discriminated union is like a set of dataclasses that share a `type: Literal[...]` field, and narrowing is what `match event: case Token(): ...` or `isinstance` does for mypy. TypeScript narrows on `typeof x === "string"`, `Array.isArray(x)`, `x === null` and `switch (event.type)`.

## Hints

- Inside `case "token":`, TypeScript knows `event` has a `text` field. Outside, it doesn't.
- `const unreachable: never = event;` in the `default` branch compiles only if every case is handled. At run time it still runs, so throw after it.
- Check `null` and arrays before `typeof`: `typeof null` is `"object"`.

## Run the tests

```bash
cd exercises
npm test -- typescript/02_unions_narrowing
```

Stuck? Make the tests pass first, then compare with `solution/`.
