export const DEFAULTS = { model: "small", temperature: 0, maxTokens: 256 };

/** DEFAULTS with `options` merged over them, as a new object. */
export function withDefaults(options = {}) {
  return { ...DEFAULTS, ...options };
}

/** "role: content", where a missing role counts as "user". */
export function describe({ role = "user", content }) {
  return `${role}: ${content}`;
}

/** { head: first item, tail: array of the rest }. */
export function headAndTail(items) {
  const [head, ...tail] = items;
  return { head, tail };
}

/** A new history where history[index] has `changes` merged in. Mutates nothing. */
export function updateMessage(history, index, changes) {
  return history.map((m, i) => (i === index ? { ...m, ...changes } : m));
}
