import { test } from "node:test";
import assert from "node:assert/strict";
import { parseChatResponse, textOf, ValidationError } from "./validate_response.ts";

// A fresh copy of a valid raw response each time, so tests can break it safely.
function raw(): any {
  return {
    id: "msg_01",
    model: "small-model",
    content: [
      { type: "text", text: "Let me look that up. " },
      { type: "tool_use", id: "tu_1", name: "search", input: { q: "docs" } },
      { type: "text", text: "Done." },
    ],
    stop_reason: "tool_use",
    usage: { input_tokens: 12, output_tokens: 30 },
    extra_field: "ignored",
  };
}

function rejects(data: unknown, message: string, path: string) {
  assert.throws(
    () => parseChatResponse(data),
    (err: unknown) => {
      assert.ok(err instanceof ValidationError, `expected a ValidationError, got ${err}`);
      assert.equal(err.message, message);
      assert.equal(err.path, path);
      return true;
    },
  );
}

test("parses a valid response into the typed, camelCase shape", () => {
  assert.deepEqual(parseChatResponse(raw()), {
    id: "msg_01",
    model: "small-model",
    content: [
      { type: "text", text: "Let me look that up. " },
      { type: "tool_use", id: "tu_1", name: "search", input: { q: "docs" } },
      { type: "text", text: "Done." },
    ],
    stopReason: "tool_use",
    usage: { inputTokens: 12, outputTokens: 30 },
  });
});

test("drops extra fields, including extra fields inside blocks", () => {
  const data = raw();
  data.content[0].citations = [];
  const parsed = parseChatResponse(data) as any;
  assert.equal(parsed.extra_field, undefined);
  assert.deepEqual(parsed.content[0], { type: "text", text: "Let me look that up. " });
});

test("accepts an empty content array", () => {
  const data = raw();
  data.content = [];
  data.stop_reason = "end_turn";
  assert.deepEqual(parseChatResponse(data).content, []);
});

test("rejects a body that isn't an object", () => {
  rejects([1, 2], "(root): expected object, got array", "(root)");
  rejects(null, "(root): expected object, got null", "(root)");
  rejects("<html>Bad Gateway</html>", "(root): expected object, got string", "(root)");
});

test("rejects missing or mistyped top-level fields", () => {
  const noModel = raw();
  delete noModel.model;
  rejects(noModel, "model: expected string, got undefined", "model");

  const badContent = raw();
  badContent.content = "Hello";
  rejects(badContent, "content: expected array, got string", "content");

  const noUsage = raw();
  delete noUsage.usage;
  rejects(noUsage, "usage: expected object, got undefined", "usage");
});

test("rejects mistyped usage numbers with a nested path", () => {
  const data = raw();
  data.usage.input_tokens = "12";
  rejects(data, "usage.input_tokens: expected number, got string", "usage.input_tokens");
});

test("rejects bad content blocks with an indexed path", () => {
  const unknownType = raw();
  unknownType.content[1] = { type: "image", source: {} };
  rejects(unknownType, 'content[1].type: unknown block type "image"', "content[1].type");

  const noText = raw();
  noText.content[2] = { type: "text" };
  rejects(noText, "content[2].text: expected string, got undefined", "content[2].text");

  const badInput = raw();
  badInput.content[1].input = "q=docs";
  rejects(badInput, "content[1].input: expected object, got string", "content[1].input");

  const notObject = raw();
  notObject.content[0] = "Hello";
  rejects(notObject, "content[0]: expected object, got string", "content[0]");
});

test("rejects an unknown stop reason", () => {
  const data = raw();
  data.stop_reason = "paused";
  rejects(data, 'stop_reason: unknown value "paused"', "stop_reason");
});

test("textOf joins only the text blocks", () => {
  assert.equal(textOf(parseChatResponse(raw())), "Let me look that up. Done.");
});
