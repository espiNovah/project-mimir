import { test } from "node:test";
import assert from "node:assert/strict";
// `import * as` gives an object of everything a module exports. Unlike a named
// import, it doesn't crash when an export is missing, so the tests can tell you which.
import * as text from "./text.js";
import * as lib from "./index.js";

test("text.js exports slugify and truncate by name", () => {
  assert.equal(typeof text.slugify, "function", "text.js should export slugify");
  assert.equal(typeof text.truncate, "function", "text.js should export truncate");
});

test("text.js exports wordCount as its default export", () => {
  assert.equal(typeof text.default, "function", "text.js should have a default export");
  assert.equal(text.default("one two  three"), 3);
  assert.equal(text.wordCount, undefined, "wordCount should be the default export, not a named one");
});

test("slugify", () => {
  assert.equal(text.slugify("  Hello, World! 2025 "), "hello-world-2025");
  assert.equal(text.slugify("RAG vs. Fine-Tuning"), "rag-vs-fine-tuning");
  assert.equal(text.slugify("---"), "");
});

test("truncate leaves short text alone", () => {
  assert.equal(text.truncate("short", 5), "short");
  assert.equal(text.truncate("", 3), "");
});

test("truncate cuts long text to exactly max characters", () => {
  assert.equal(text.truncate("streaming", 6), "strea…");
  assert.equal(text.truncate("streaming", 6).length, 6);
});

test("index.js re-exports all three helpers by name", () => {
  assert.equal(lib.slugify, text.slugify, "index.js should re-export slugify");
  assert.equal(lib.truncate, text.truncate, "index.js should re-export truncate");
  assert.equal(lib.wordCount, text.default, "index.js should re-export the default as wordCount");
});
