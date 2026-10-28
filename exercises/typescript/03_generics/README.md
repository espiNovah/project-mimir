# 03 · Generic helpers

**Lesson:** [TypeScript Basics](https://espinovah.github.io/project-mimir/#/lessons/core/typescript-basics)

## Task

A *generic* function works for any type and keeps track of which one. `first<T>(items: T[]): T | undefined` returns a `string | undefined` when you pass a `string[]`, and a `Message | undefined` when you pass a `Message[]`. In `generics.ts`, add the type parameters and write:

- `first(items)`: the first item, or `undefined` for an empty array.
- `chunk(items, size)`: split the array into arrays of `size` items (the last one may be shorter). Throw a `RangeError` if `size` is not a whole number of at least 1. This is how you'd batch documents for an embeddings API.
- `groupBy(items, keyOf)`: an object from each key that `keyOf(item)` returns to the items with that key, in their original order.
- `tryResult(fn)`: call `fn()` and return `{ ok: true, value }`, or `{ ok: false, error }` if it throws. If it throws something that isn't an `Error` (JavaScript lets you throw a string), wrap it: `new Error(String(thrown))`.

```ts
chunk([1, 2, 3, 4, 5], 2);                       // [[1, 2], [3, 4], [5]]
groupBy(docs, (d) => d.source);                  // { "faq.md": [...], "guide.md": [...] }
const r = tryResult(() => JSON.parse(text));
if (r.ok) use(r.value); else log(r.error.message);
```

## Coming from Python

| Python | TypeScript |
| --- | --- |
| `T = TypeVar("T")`, or `def first[T](items: list[T]) -> T \| None` (3.12+) | `function first<T>(items: T[]): T \| undefined` |
| `K = TypeVar("K", bound=Hashable)` | `<K extends PropertyKey>` (string, number or symbol, the types allowed as object keys) |
| `dict[K, list[T]]` | `Record<K, T[]>` (or `Partial<Record<K, T[]>>` when not every key is present) |

`Result<T>` is a discriminated union (see exercise 02): check `r.ok` and TypeScript knows whether `r.value` or `r.error` exists.

## Hints

- In `groupBy`, `(groups[key] ??= []).push(item)` creates the array the first time you see a key.
- `Number.isInteger(size)` checks for a whole number.
- `err instanceof Error ? err : new Error(String(err))`.

## Run the tests

```bash
cd exercises
npm test -- typescript/03_generics
```

Stuck? Make the tests pass first, then compare with `solution/`.
