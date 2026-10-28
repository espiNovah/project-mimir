export const DEFAULTS = { model: "small", temperature: 0, maxTokens: 256 };

/** DEFAULTS with `options` merged over them, as a new object. */
export function withDefaults(options) {
  throw new Error("TODO: use object spread and a default parameter");
}

/** "role: content", where a missing role counts as "user". */
export function describe(message) {
  throw new Error("TODO: destructure role and content in the parameter list");
}

/** { head: first item, tail: array of the rest }. */
export function headAndTail(items) {
  throw new Error("TODO: use array destructuring with a rest element");
}

/** A new history where history[index] has `changes` merged in. Mutates nothing. */
export function updateMessage(history, index, changes) {
  throw new Error("TODO: use map and object spread");
}
