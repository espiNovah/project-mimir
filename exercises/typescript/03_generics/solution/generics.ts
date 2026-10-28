export type Result<T> = { ok: true; value: T } | { ok: false; error: Error };

/** The first item, or undefined for an empty array. */
export function first<T>(items: T[]): T | undefined {
  return items[0];
}

/** Arrays of `size` items; the last may be shorter. RangeError if size isn't a whole number >= 1. */
export function chunk<T>(items: T[], size: number): T[][] {
  if (!Number.isInteger(size) || size < 1) {
    throw new RangeError(`size must be a whole number >= 1, got ${size}`);
  }
  const chunks: T[][] = [];
  for (let i = 0; i < items.length; i += size) chunks.push(items.slice(i, i + size));
  return chunks;
}

/** An object from each key to the items with that key, in order. */
export function groupBy<T, K extends PropertyKey>(
  items: T[],
  keyOf: (item: T) => K,
): Partial<Record<K, T[]>> {
  const groups: Partial<Record<K, T[]>> = {};
  for (const item of items) (groups[keyOf(item)] ??= []).push(item);
  return groups;
}

/** { ok: true, value } if fn() returns, { ok: false, error } if it throws. */
export function tryResult<T>(fn: () => T): Result<T> {
  try {
    return { ok: true, value: fn() };
  } catch (err) {
    return { ok: false, error: err instanceof Error ? err : new Error(String(err)) };
  }
}
