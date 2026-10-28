// TODO: replace each placeholder type with the real one (see README.md).
export type Role = unknown;
export type Message = unknown;
export type Usage = unknown;
export type Price = unknown;

// TODO: add parameter and return types, then write the bodies.

/** One "role: content" line per message, joined with "\n". */
export function formatTranscript(messages) {
  throw new Error("TODO");
}

/** The cost in dollars, given prices per million tokens. */
export function costUsd(usage, price) {
  throw new Error("TODO");
}

/** The last message, or the last one with `role` if given. */
export function lastMessage(messages, role) {
  throw new Error("TODO");
}
