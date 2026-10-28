import { test } from "node:test";
import assert from "node:assert/strict";
import { HttpError, isRetryable, parseJsonOr, withRetries } from "./error_handling.js";

// A fake sleep that records how long it was asked to wait, without waiting.
function fakeSleep() {
  const waits = [];
  return { waits, sleep: async (ms) => { waits.push(ms); } };
}

// A function that throws the given errors in turn, then returns "ok".
function failing(...errors) {
  const attempts = [];
  const fn = async (attempt) => {
    attempts.push(attempt);
    if (errors.length) throw errors.shift();
    return "ok";
  };
  return { fn, attempts };
}

test("HttpError is an Error with a status and a name", () => {
  const err = new HttpError(503, "Service unavailable");
  assert.ok(err instanceof HttpError);
  assert.ok(err instanceof Error);
  assert.equal(err.status, 503);
  assert.equal(err.message, "Service unavailable");
  assert.equal(err.name, "HttpError");
});

test("parseJsonOr parses valid JSON", () => {
  assert.deepEqual(parseJsonOr('{"a": [1, 2]}', null), { a: [1, 2] });
});

test("parseJsonOr returns the fallback for invalid JSON", () => {
  assert.equal(parseJsonOr("{not json", "fallback"), "fallback");
  assert.deepEqual(parseJsonOr("", []), []);
});

test("isRetryable is true for 429 and 5xx HttpErrors only", () => {
  assert.equal(isRetryable(new HttpError(429, "slow down")), true);
  assert.equal(isRetryable(new HttpError(500, "oops")), true);
  assert.equal(isRetryable(new HttpError(529, "overloaded")), true);
  assert.equal(isRetryable(new HttpError(400, "bad request")), false);
  assert.equal(isRetryable(new HttpError(404, "not found")), false);
  assert.equal(isRetryable(new Error("plain")), false);
  assert.equal(isRetryable("a thrown string"), false);
  assert.equal(isRetryable({ status: 500 }), false);
});

test("withRetries returns at once when fn succeeds", async () => {
  const { sleep, waits } = fakeSleep();
  const { fn, attempts } = failing();
  assert.equal(await withRetries(fn, { sleep }), "ok");
  assert.deepEqual(attempts, [1]);
  assert.deepEqual(waits, []);
});

test("withRetries retries retryable errors with doubling waits", async () => {
  const { sleep, waits } = fakeSleep();
  const { fn, attempts } = failing(new HttpError(503, "a"), new HttpError(429, "b"), new HttpError(500, "c"));
  assert.equal(await withRetries(fn, { retries: 3, sleep }), "ok");
  assert.deepEqual(attempts, [1, 2, 3, 4]);
  assert.deepEqual(waits, [100, 200, 400]);
});

test("withRetries rethrows the last error when retries run out", async () => {
  const { sleep, waits } = fakeSleep();
  const last = new HttpError(500, "third");
  const { fn, attempts } = failing(new HttpError(500, "first"), new HttpError(500, "second"), last);
  await assert.rejects(withRetries(fn, { sleep }), (err) => err === last);
  assert.deepEqual(attempts, [1, 2, 3], "retries: 2 is the default, so 3 attempts in all");
  assert.deepEqual(waits, [100, 200]);
});

test("withRetries does not retry a non-retryable error", async () => {
  const { sleep, waits } = fakeSleep();
  const bad = new HttpError(400, "bad request");
  const { fn, attempts } = failing(bad);
  await assert.rejects(withRetries(fn, { retries: 5, sleep }), (err) => err === bad);
  assert.deepEqual(attempts, [1]);
  assert.deepEqual(waits, []);
});
