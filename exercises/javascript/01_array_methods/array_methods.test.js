import { test } from "node:test";
import assert from "node:assert/strict";
import { contents, sortNumbers, tokensByRole, totalTokens } from "./array_methods.js";

const history = [
  { role: "system", content: "Be brief.", tokens: 4 },
  { role: "user", content: "Hi", tokens: 3 },
  { role: "assistant", content: "Hello! How can I help?", tokens: 8 },
  { role: "user", content: "Thanks", tokens: 4 },
  { role: "assistant", content: "Any time.", tokens: 3 },
];

test("contents keeps only one role, in order", () => {
  assert.deepEqual(contents(history, "user"), ["Hi", "Thanks"]);
  assert.deepEqual(contents(history, "tool"), []);
});

test("totalTokens sums every message", () => {
  assert.equal(totalTokens(history), 22);
});

test("totalTokens of an empty history is 0", () => {
  assert.equal(totalTokens([]), 0);
});

test("tokensByRole totals each role", () => {
  assert.deepEqual(tokensByRole(history), { system: 4, user: 7, assistant: 11 });
  assert.deepEqual(tokensByRole([]), {});
});

test("sortNumbers sorts numerically, not as strings", () => {
  assert.deepEqual(sortNumbers([10, 9, 1, 100, 25]), [1, 9, 10, 25, 100]);
  assert.deepEqual(sortNumbers([3, -1, 2]), [-1, 2, 3]);
});

test("sortNumbers does not change its input", () => {
  const numbers = [3, 1, 2];
  sortNumbers(numbers);
  assert.deepEqual(numbers, [3, 1, 2]);
});
