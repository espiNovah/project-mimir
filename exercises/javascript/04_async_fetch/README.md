# 04 · async/await with fetch

**Lesson:** [JavaScript Fundamentals](https://espinovah.github.io/project-mimir/#/lessons/core/javascript-fundamentals)

## Task

Each function takes the fetch function as its last argument (`fetchFn`) instead of using the global `fetch`. Your real code passes `fetch`. The tests pass a fake that returns ready-made `Response` objects, so they never touch the network. This trick is called *dependency injection*.

In `async_fetch.js`, write:

- `getJson(url, fetchFn)`: fetch the URL and return the parsed JSON body. If the response isn't OK (status outside 200–299), throw an `Error` whose message is `` `GET ${url} failed with ${status}` ``.
- `getAll(urls, fetchFn)`: fetch every URL **at the same time** and return their JSON bodies in the same order as `urls`. If any request fails, the returned promise rejects.
- `firstAvailable(urls, fetchFn)`: try the URLs **one after another** and return the JSON of the first that succeeds (think fallback servers). If all fail, throw an `Error` with the message `"all URLs failed"`.

```js
await getJson("/models", fetch);                  // { data: [...] }
await getAll(["/a", "/b"], fetch);                // [bodyA, bodyB]
await firstAvailable(["/primary", "/backup"], fetch);
```

## Coming from Python

| Python (`asyncio`, `httpx`) | JavaScript |
| --- | --- |
| `async def f():` | `async function f() {}` |
| `await client.get(url)` | `await fetch(url)` |
| `response.raise_for_status()` | `if (!res.ok) throw new Error(...)` (fetch does **not** throw on 404 or 500) |
| `response.json()` | `await res.json()` (it's async too) |
| `await asyncio.gather(*coros)` | `await Promise.all(promises)` |

## Hints

- Calling an async function starts it right away and gives you a promise. `urls.map((u) => getJson(u, fetchFn))` starts every request, and `Promise.all` waits for all of them.
- An `await` inside a `for...of` loop waits for each step before starting the next. That's what you want in `firstAvailable` and what you don't want in `getAll`.
- `try { return await getJson(...) } catch { /* try the next one */ }` inside the loop.

## Run the tests

```bash
cd exercises
npm test -- javascript/04_async_fetch
```

Stuck? Make the tests pass first, then compare with `solution/`.
