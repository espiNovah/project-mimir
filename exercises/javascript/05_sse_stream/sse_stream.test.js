import { test } from "node:test";
import assert from "node:assert/strict";
import { collectAnswer, readEvents } from "./sse_stream.js";

// Build a fake response body: a ReadableStream of bytes from `text`, cut into
// chunks at the given BYTE offsets (so a cut can land inside a multi-byte character).
function streamFrom(text, cuts = []) {
  const bytes = new TextEncoder().encode(text);
  const edges = [0, ...cuts, bytes.length];
  const chunks = edges.slice(1).map((end, i) => bytes.slice(edges[i], end));
  return new ReadableStream({
    start(controller) {
      for (const chunk of chunks) controller.enqueue(chunk);
      controller.close();
    },
  });
}

async function collect(stream) {
  const out = [];
  for await (const message of readEvents(stream)) out.push(message);
  return out;
}

const BODY =
  'event: token\ndata: "Hello"\n\n' +
  ": keep-alive\n\n" +
  'event: token\ndata: " world"\n\n' +
  'event: done\ndata: {"stop_reason": "end_turn"}\n\n';

const EXPECTED = [
  { event: "token", data: '"Hello"' },
  { event: "token", data: '" world"' },
  { event: "done", data: '{"stop_reason": "end_turn"}' },
];

test("readEvents parses a stream delivered in one chunk", async () => {
  assert.deepEqual(await collect(streamFrom(BODY)), EXPECTED);
});

test("readEvents handles messages split across chunks", async () => {
  // Cuts inside a field name, inside the blank line, and inside a value.
  assert.deepEqual(await collect(streamFrom(BODY, [3, 27, 28, 50, 70])), EXPECTED);
});

test("readEvents handles a stream that arrives one byte at a time", async () => {
  const bytes = new TextEncoder().encode(BODY).length;
  const cuts = Array.from({ length: bytes - 1 }, (_, i) => i + 1);
  assert.deepEqual(await collect(streamFrom(BODY, cuts)), EXPECTED);
});

test("readEvents decodes a multi-byte character split between chunks", async () => {
  const text = 'event: token\ndata: "café 🎉"\n\n';
  const emojiStart = new TextEncoder().encode('event: token\ndata: "café ').length;
  const events = await collect(streamFrom(text, [emojiStart + 2]));
  assert.deepEqual(events, [{ event: "token", data: '"café 🎉"' }]);
});

test("readEvents defaults the event name to message", async () => {
  assert.deepEqual(await collect(streamFrom("data: hi\n\n")), [{ event: "message", data: "hi" }]);
});

test("readEvents joins multiple data lines and removes only one space", async () => {
  const events = await collect(streamFrom("data: line one\ndata:line two\ndata:   indented\n\n"));
  assert.deepEqual(events, [{ event: "message", data: "line one\nline two\n  indented" }]);
});

test("readEvents ignores unknown fields and skips messages with no data", async () => {
  const events = await collect(streamFrom("id: 7\nretry: 1000\n\nevent: ping\n\nid: 8\ndata: x\n\n"));
  assert.deepEqual(events, [{ event: "message", data: "x" }]);
});

test("readEvents drops an unfinished message at the end of the stream", async () => {
  const events = await collect(streamFrom('data: "complete"\n\ndata: "cut off'));
  assert.deepEqual(events, [{ event: "message", data: '"complete"' }]);
});

test("collectAnswer joins tokens and returns the stop reason", async () => {
  assert.deepEqual(await collectAnswer(streamFrom(BODY, [10, 40])), {
    text: "Hello world",
    stopReason: "end_turn",
  });
});

test("collectAnswer keeps newlines that were JSON-encoded in tokens", async () => {
  const body =
    'event: token\ndata: "# Title\\n\\nBody"\n\n' +
    'event: citations\ndata: ["doc-1"]\n\n' +
    'event: done\ndata: {"stop_reason": "max_tokens"}\n\n';
  assert.deepEqual(await collectAnswer(streamFrom(body)), {
    text: "# Title\n\nBody",
    stopReason: "max_tokens",
  });
});

test("collectAnswer throws the message of an error event", async () => {
  const body = 'event: token\ndata: "Partial"\n\nevent: error\ndata: {"message": "Model overloaded"}\n\n';
  await assert.rejects(collectAnswer(streamFrom(body)), { message: "Model overloaded" });
});

test("collectAnswer throws if the stream ends before done", async () => {
  await assert.rejects(collectAnswer(streamFrom('event: token\ndata: "Hi"\n\n')), {
    message: "stream ended before done",
  });
});
