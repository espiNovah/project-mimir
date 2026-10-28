import { test } from "node:test";
import assert from "node:assert/strict";
import { applyEvent, initialState, toDisplay } from "./unions_narrowing.ts";
import type { StreamEvent } from "./unions_narrowing.ts";

test("token events append text", () => {
  let state = initialState();
  state = applyEvent(state, { type: "token", text: "Hel" });
  state = applyEvent(state, { type: "token", text: "lo" });
  assert.deepEqual(state, { text: "Hello", sources: [], status: "streaming" });
});

test("citations events add sources in order", () => {
  let state = initialState();
  state = applyEvent(state, { type: "citations", sources: ["a.md"] });
  state = applyEvent(state, { type: "citations", sources: ["b.md", "c.md"] });
  assert.deepEqual(state.sources, ["a.md", "b.md", "c.md"]);
});

test("a whole stream ends with status done", () => {
  const events: StreamEvent[] = [
    { type: "token", text: "Hi" },
    { type: "citations", sources: ["faq.md"] },
    { type: "done", stopReason: "end_turn" },
  ];
  assert.deepEqual(events.reduce(applyEvent, initialState()), {
    text: "Hi",
    sources: ["faq.md"],
    status: "done",
  });
});

test("an error event keeps the partial text and records the message", () => {
  let state = applyEvent(initialState(), { type: "token", text: "Partial" });
  state = applyEvent(state, { type: "error", message: "Model overloaded" });
  assert.deepEqual(state, { text: "Partial", sources: [], status: "error", error: "Model overloaded" });
});

test("applyEvent does not change the old state", () => {
  const before = initialState();
  applyEvent(before, { type: "token", text: "x" });
  applyEvent(before, { type: "citations", sources: ["y"] });
  assert.deepEqual(before, { text: "", sources: [], status: "streaming" });
});

test("applyEvent throws on an unknown event type", () => {
  const strange = { type: "thinking", text: "hmm" } as unknown as StreamEvent;
  assert.throws(() => applyEvent(initialState(), strange), /thinking/);
});

test("toDisplay narrows each kind of value", () => {
  assert.equal(toDisplay(null), "");
  assert.equal(toDisplay("plain"), "plain");
  assert.equal(toDisplay(1234.5), "1,234.5");
  assert.equal(toDisplay(0), "0");
  assert.equal(toDisplay(["a", "b", "c"]), "a, b, c");
  assert.equal(toDisplay([]), "");
});
