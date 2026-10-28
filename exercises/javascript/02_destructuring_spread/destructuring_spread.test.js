import { test } from "node:test";
import assert from "node:assert/strict";
import { DEFAULTS, describe, headAndTail, updateMessage, withDefaults } from "./destructuring_spread.js";

test("withDefaults merges options over the defaults", () => {
  assert.deepEqual(withDefaults({ temperature: 0.7, stream: true }), {
    model: "small",
    temperature: 0.7,
    maxTokens: 256,
    stream: true,
  });
});

test("withDefaults with no argument returns a copy of the defaults", () => {
  const result = withDefaults();
  assert.deepEqual(result, { model: "small", temperature: 0, maxTokens: 256 });
  assert.notEqual(result, DEFAULTS, "return a new object, not DEFAULTS itself");
});

test("withDefaults does not change DEFAULTS or the options", () => {
  const options = { model: "large" };
  withDefaults(options);
  assert.deepEqual(DEFAULTS, { model: "small", temperature: 0, maxTokens: 256 });
  assert.deepEqual(options, { model: "large" });
});

test("describe formats role and content", () => {
  assert.equal(describe({ role: "assistant", content: "Hello" }), "assistant: Hello");
});

test("describe treats a missing role as user", () => {
  assert.equal(describe({ content: "Hi" }), "user: Hi");
});

test("headAndTail splits the first item from the rest", () => {
  assert.deepEqual(headAndTail([1, 2, 3]), { head: 1, tail: [2, 3] });
  assert.deepEqual(headAndTail(["only"]), { head: "only", tail: [] });
  assert.deepEqual(headAndTail([]), { head: undefined, tail: [] });
});

test("updateMessage merges changes into one message", () => {
  const history = [
    { role: "user", content: "Hi" },
    { role: "assistant", content: "Hello", tokens: 2 },
  ];
  const updated = updateMessage(history, 1, { content: "Edited" });
  assert.deepEqual(updated, [
    { role: "user", content: "Hi" },
    { role: "assistant", content: "Edited", tokens: 2 },
  ]);
});

test("updateMessage mutates nothing", () => {
  const history = [{ role: "user", content: "Hi" }];
  const updated = updateMessage(history, 0, { content: "Bye" });
  assert.notEqual(updated, history);
  assert.deepEqual(history, [{ role: "user", content: "Hi" }]);
});
