// Each message looks like { role: "user", content: "Hi", tokens: 3 }.

/** The content of every message with this role, in order. */
export function contents(messages, role) {
  throw new Error("TODO: use filter and map");
}

/** The sum of every message's tokens (0 for an empty history). */
export function totalTokens(messages) {
  throw new Error("TODO: use reduce");
}

/** An object from each role to the sum of its tokens. */
export function tokensByRole(messages) {
  throw new Error("TODO: use reduce with {} as the start value");
}

/** The numbers in ascending order, as a new array. Don't change the input. */
export function sortNumbers(numbers) {
  throw new Error("TODO: sort numerically, without mutating the input");
}
