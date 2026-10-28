export type Result<T> = { ok: true; value: T } | { ok: false; error: Error };

// TODO: add type parameters (<T>, <T, K extends PropertyKey>) and types, then write the bodies.

/** The first item, or undefined for an empty array. */
export function first(items) {
  throw new Error("TODO");
}

/** Arrays of `size` items; the last may be shorter. RangeError if size isn't a whole number >= 1. */
export function chunk(items, size) {
  throw new Error("TODO");
}

/** An object from each key to the items with that key, in order. */
export function groupBy(items, keyOf) {
  throw new Error("TODO");
}

/** { ok: true, value } if fn() returns, { ok: false, error } if it throws. */
export function tryResult(fn) {
  throw new Error("TODO");
}
