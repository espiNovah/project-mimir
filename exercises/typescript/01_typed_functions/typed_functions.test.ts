import { test } from "node:test";
import assert from "node:assert/strict";
import { costUsd, formatTranscript, lastMessage } from "./typed_functions.ts";
import type { Message } from "./typed_functions.ts";

const history: Message[] = [
  { role: "system", content: "Be brief." },
  { role: "user", content: "Hi" },
  { role: "assistant", content: "Hello!" },
  { role: "user", content: "Thanks" },
  { role: "assistant", content: "Any time." },
];

test("formatTranscript writes one line per message", () => {
  assert.equal(
    formatTranscript(history.slice(0, 3)),
    "system: Be brief.\nuser: Hi\nassistant: Hello!",
  );
  assert.equal(formatTranscript([]), "");
});

test("costUsd prices input and output tokens per million", () => {
  const cost = costUsd({ inputTokens: 2_000, outputTokens: 500 }, { input: 3, output: 15 });
  assert.ok(Math.abs(cost - 0.0135) < 1e-12, `expected 0.0135, got ${cost}`);
  assert.equal(costUsd({ inputTokens: 0, outputTokens: 0 }, { input: 3, output: 15 }), 0);
});

test("lastMessage without a role returns the last message", () => {
  assert.deepEqual(lastMessage(history), { role: "assistant", content: "Any time." });
});

test("lastMessage with a role returns the last message with that role", () => {
  assert.deepEqual(lastMessage(history, "user"), { role: "user", content: "Thanks" });
  assert.deepEqual(lastMessage(history, "system"), { role: "system", content: "Be brief." });
});

test("lastMessage returns undefined when nothing matches", () => {
  assert.equal(lastMessage([]), undefined);
  assert.equal(lastMessage(history.slice(0, 1), "assistant"), undefined);
});
