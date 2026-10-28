# JavaScript

Exercises for Python programmers learning JavaScript. They go with these lessons:

- [JavaScript Fundamentals](https://espinovah.github.io/project-mimir/#/lessons/core/javascript-fundamentals): array methods, destructuring and spread, modules, async/await and error handling (exercises 01–06).
- [Streaming in the Browser](https://espinovah.github.io/project-mimir/#/lessons/core/streaming-in-the-browser): reading a `text/event-stream` body chunk by chunk (exercise 05).

Everything runs offline. The fetch and streaming exercises use fake `fetch` functions and fake `ReadableStream`s, so no server or API key is needed.

## How to run

You need Node 22.18 or newer (`node --version`). There's nothing to install: the tests use Node's built-in test runner.

```bash
cd exercises
npm test -- javascript/01_array_methods   # one exercise
npm test -- javascript                    # the whole set
```

Each exercise folder has a `README.md` with the task, a starter file to edit, a test file, and a reference solution in `solution/`. The tests fail until you write the code.

## Exercises

| # | Exercise | Practices |
| --- | --- | --- |
| 01 | [Array methods](01_array_methods/) | `map`, `filter`, `reduce`, numeric `sort` without mutation |
| 02 | [Destructuring and spread](02_destructuring_spread/) | object and array destructuring, defaults, `...` spread and rest |
| 03 | [Modules](03_modules/) | named and default `export`, `import`, re-exporting |
| 04 | [async/await with fetch](04_async_fetch/) | injected `fetch`, `res.ok`, `Promise.all`, sequential fallback |
| 05 | [Reading a server-sent event stream](05_sse_stream/) | `ReadableStream`, `TextDecoderStream`, buffering, async generators |
| 06 | [Error handling](06_error_handling/) | `Error` subclasses, `try`/`catch`, `instanceof`, retries with backoff |
