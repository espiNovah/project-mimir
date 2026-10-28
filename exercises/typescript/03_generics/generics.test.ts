import { test } from "node:test";
import assert from "node:assert/strict";
import { chunk, first, groupBy, tryResult } from "./generics.ts";

test("first returns the first item or undefined", () => {
  assert.equal(first(["a", "b"]), "a");
  assert.deepEqual(first([{ id: 1 }, { id: 2 }]), { id: 1 });
  assert.equal(first([]), undefined);
});

test("chunk splits into fixed-size batches", () => {
  assert.deepEqual(chunk([1, 2, 3, 4, 5], 2), [[1, 2], [3, 4], [5]]);
  assert.deepEqual(chunk(["a", "b", "c"], 3), [["a", "b", "c"]]);
  assert.deepEqual(chunk(["a"], 10), [["a"]]);
  assert.deepEqual(chunk([], 4), []);
});

test("chunk rejects sizes that aren't whole numbers >= 1", () => {
  assert.throws(() => chunk([1, 2], 0), RangeError);
  assert.throws(() => chunk([1, 2], -1), RangeError);
  assert.throws(() => chunk([1, 2], 1.5), RangeError);
});

test("groupBy groups items by key, keeping order", () => {
  const docs = [
    { source: "faq.md", text: "q1" },
    { source: "guide.md", text: "intro" },
    { source: "faq.md", text: "q2" },
  ];
  assert.deepEqual(groupBy(docs, (d) => d.source), {
    "faq.md": [docs[0], docs[2]],
    "guide.md": [docs[1]],
  });
});

test("groupBy works with number keys and empty input", () => {
  assert.deepEqual(groupBy(["a", "bb", "cc", "ddd"], (w) => w.length), {
    1: ["a"],
    2: ["bb", "cc"],
    3: ["ddd"],
  });
  assert.deepEqual(groupBy([], (x: string) => x), {});
});

test("tryResult wraps a returned value", () => {
  assert.deepEqual(tryResult(() => JSON.parse('{"a": 1}')), { ok: true, value: { a: 1 } });
});

test("tryResult catches a thrown Error", () => {
  const result = tryResult(() => JSON.parse("{oops"));
  assert.equal(result.ok, false);
  if (!result.ok) assert.ok(result.error instanceof SyntaxError);
});

test("tryResult wraps a thrown non-Error in an Error", () => {
  const result = tryResult(() => {
    throw "rate limited";
  });
  assert.equal(result.ok, false);
  if (!result.ok) {
    assert.ok(result.error instanceof Error);
    assert.equal(result.error.message, "rate limited");
  }
});
