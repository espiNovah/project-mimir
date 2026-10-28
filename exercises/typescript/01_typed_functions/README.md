# 01 · Typing functions and objects

**Lesson:** [TypeScript Basics](https://espinovah.github.io/project-mimir/#/lessons/core/typescript-basics)

## Task

In `typed_functions.ts`:

1. Replace the placeholder types:
   - `Role` is one of the strings `"system"`, `"user"` or `"assistant"`.
   - `Message` has a `role: Role` and a `content: string`.
   - `Usage` has `inputTokens` and `outputTokens`, both numbers.
   - `Price` has `input` and `output`: dollars per million tokens.
2. Add parameter and return types to every function, then write it:
   - `formatTranscript(messages)`: one `"role: content"` line per message, joined with `"\n"`.
   - `costUsd(usage, price)`: what the call cost, in dollars.
   - `lastMessage(messages, role?)`: the last message, or the last one with that role if you pass `role` (an **optional** parameter). Return `undefined` if there isn't one.

```ts
costUsd({ inputTokens: 2_000, outputTokens: 500 }, { input: 3, output: 15 });  // 0.0135
lastMessage(history, "user");  // { role: "user", content: "Thanks" }
```

## The tests don't check types

Node runs TypeScript by *stripping* the types and running what's left as JavaScript. So the tests check what your code does, not whether the types are right. Your editor (VS Code) checks types as you type: hover over things, and look for red squiggles. To check the whole file from the command line (this downloads the TypeScript compiler once):

```bash
npx -p typescript tsc --noEmit --strict --target es2022 --module nodenext --allowImportingTsExtensions typescript/01_typed_functions/typed_functions.ts
```

Because Node only strips types, avoid the few TypeScript features that generate code: `enum`, `namespace`, and constructor parameter properties (`constructor(private x: number)`). A union of string literals does the job of an enum.

## Coming from Python

| Python type hints | TypeScript |
| --- | --- |
| `def f(x: int) -> str:` | `function f(x: number): string {` |
| `Literal["user", "assistant"]` | `"user" \| "assistant"` |
| `class Message(TypedDict): role: str` | `interface Message { role: string }` or `type Message = { role: string }` |
| `list[Message]` | `Message[]` |
| `Optional[Role] = None` | `role?: Role` |
| hints are ignored at run time; mypy checks them | types are stripped at run time; `tsc` checks them |

## Hints

- `messages.findLast((m) => ...)` returns the last match or `undefined`.
- For an optional parameter, check `role === undefined` before you use it.

## Run the tests

```bash
cd exercises
npm test -- typescript/01_typed_functions
```

Stuck? Make the tests pass first, then compare with `solution/`.
