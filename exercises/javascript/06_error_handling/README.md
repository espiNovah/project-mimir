# 06 · Error handling

**Lesson:** [JavaScript Fundamentals](https://espinovah.github.io/project-mimir/#/lessons/core/javascript-fundamentals)

## Task

In `error_handling.js`, write:

- `class HttpError extends Error`: its constructor takes `(status, message)`. Set `this.status` and set `this.name` to `"HttpError"`.
- `parseJsonOr(text, fallback)`: return `JSON.parse(text)`, or `fallback` if the text isn't valid JSON.
- `isRetryable(error)`: `true` only for an `HttpError` with status 429 (rate limited) or 500 and above (server errors). Anything else, including a plain `Error` or a 400, is not worth retrying.
- `withRetries(fn, { retries = 2, sleep })`: call the async function `fn(attempt)`, with `attempt` starting at 1, and return its result. If it throws a retryable error and you have retries left, wait with `await sleep(ms)` and try again. The wait doubles each time: 100 ms, then 200, then 400. If it throws a non-retryable error, rethrow it at once. If you run out of retries, rethrow the last error.

`sleep` is passed in so the tests don't have to wait. Real code would pass `(ms) => new Promise((r) => setTimeout(r, ms))`.

```js
await withRetries((attempt) => callModel(prompt), { retries: 3, sleep });
```

## Coming from Python

| Python | JavaScript |
| --- | --- |
| `class HttpError(Exception):` | `class HttpError extends Error {}` |
| `raise HttpError(...)` | `throw new HttpError(...)` |
| `except HttpError as e:` | `catch (e) { if (e instanceof HttpError) ... }` (one `catch`, then check the type yourself) |
| `except: pass` | `catch { }` |
| `finally:` | `finally { }` |

## Hints

- In a subclass constructor, call `super(message)` before you use `this`.
- JavaScript lets you `throw` any value, even a string, so check with `instanceof` before you read `.status`.
- A `for` loop over the attempts with `try { return await fn(attempt); } catch (err) { ... }` inside reads clearly.
- The wait before retry number `n` (1, 2, 3, ...) is `100 * 2 ** (n - 1)`.

## Run the tests

```bash
cd exercises
npm test -- javascript/06_error_handling
```

Stuck? Make the tests pass first, then compare with `solution/`.
