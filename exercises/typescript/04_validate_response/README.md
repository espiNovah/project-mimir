# 04 · Validating an API response

**Lesson:** [TypeScript Basics](https://espinovah.github.io/project-mimir/#/lessons/core/typescript-basics)

## Task

`await res.json()` gives you a value TypeScript can't know anything about. Writing `const data = await res.json() as ChatResponse` only *tells* TypeScript to trust you. If the API changes, or a proxy returns an error page, your code breaks far from the cause. The safe pattern is to treat the body as `unknown` and check it once, at the edge, turning it into a typed object.

In `validate_response.ts`, write `parseChatResponse(data: unknown): ChatResponse`. The raw JSON looks like this (snake_case, as the API sends it):

```json
{
  "id": "msg_01",
  "model": "small-model",
  "content": [
    { "type": "text", "text": "Hello" },
    { "type": "tool_use", "id": "tu_1", "name": "search", "input": { "q": "docs" } }
  ],
  "stop_reason": "tool_use",
  "usage": { "input_tokens": 12, "output_tokens": 30 }
}
```

Return a `ChatResponse` (camelCase, see the types in the file) and check:

- `data` is an object; `id` and `model` are strings; `content` is an array.
- each content block is an object whose `type` is `"text"` (with a string `text`) or `"tool_use"` (with string `id` and `name`, and an object `input`).
- `stop_reason` is one of `"end_turn"`, `"max_tokens"`, `"stop_sequence"` or `"tool_use"`.
- `usage.input_tokens` and `usage.output_tokens` are numbers.
- Ignore any extra fields, and don't copy them into the result.

On the first problem, throw the provided `ValidationError` with the **path** to the bad value and what was wrong. The tests check these messages:

| Problem | Message |
| --- | --- |
| not an object | `(root): expected object, got array` |
| wrong type | `usage.input_tokens: expected number, got string` |
| missing field | `model: expected string, got undefined` |
| bad block | `content[1].type: unknown block type "image"` |
| bad stop reason | `stop_reason: unknown value "paused"` |

Then write `textOf(response)`: the text of every `text` block, joined with `""`.

In a project with dependencies you would usually write this with a validation library such as Zod. Doing it by hand once shows you what those libraries do.

## Coming from Python

This is what Pydantic's `ChatResponse.model_validate(data)` does for you. TypeScript's `unknown` is like a value you must `isinstance`-check before using it. A function with the return type `value is Record<string, unknown>` is a *type guard*: when it returns true, TypeScript narrows the value for you.

## Hints

- `typeOf(value)` is provided: it returns `"array"` and `"null"` where `typeof` would say `"object"`.
- Write small helpers like `str(obj, key, path)` and `num(obj, key, path)` that check one field and return it with the right type. Most of the work is building the path strings, such as `` `content[${i}].text` ``.
- `(STOP_REASONS as readonly string[]).includes(value)` checks membership in a `readonly` tuple.

## Run the tests

```bash
cd exercises
npm test -- typescript/04_validate_response
```

Stuck? Make the tests pass first, then compare with `solution/`.
