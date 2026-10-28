// Each message looks like { role: "user", content: "Hi", tokens: 3 }.

/** The content of every message with this role, in order. */
export function contents(messages, role) {
  return messages.filter((m) => m.role === role).map((m) => m.content);
}

/** The sum of every message's tokens (0 for an empty history). */
export function totalTokens(messages) {
  return messages.reduce((total, m) => total + m.tokens, 0);
}

/** An object from each role to the sum of its tokens. */
export function tokensByRole(messages) {
  return messages.reduce((totals, m) => {
    totals[m.role] = (totals[m.role] ?? 0) + m.tokens;
    return totals;
  }, {});
}

/** The numbers in ascending order, as a new array. Don't change the input. */
export function sortNumbers(numbers) {
  return [...numbers].sort((a, b) => a - b);
}
