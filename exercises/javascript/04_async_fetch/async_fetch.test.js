import { test } from "node:test";
import assert from "node:assert/strict";
import { firstAvailable, getAll, getJson } from "./async_fetch.js";

// A fake fetch: looks the URL up in `routes` and returns a real Response object.
// It records every URL it was called with.
function fakeFetch(routes) {
  const calls = [];
  const fetchFn = async (url) => {
    calls.push(url);
    const route = routes[url] ?? { status: 404, body: { error: "not found" } };
    return new Response(JSON.stringify(route.body), {
      status: route.status ?? 200,
      headers: { "Content-Type": "application/json" },
    });
  };
  return { fetchFn, calls };
}

// Lets pending promise callbacks run.
const tick = () => new Promise((resolve) => setImmediate(resolve));

test("getJson returns the parsed body", async () => {
  const { fetchFn, calls } = fakeFetch({ "/models": { body: { data: ["small", "large"] } } });
  assert.deepEqual(await getJson("/models", fetchFn), { data: ["small", "large"] });
  assert.deepEqual(calls, ["/models"]);
});

test("getJson throws on a non-OK status", async () => {
  const { fetchFn } = fakeFetch({ "/down": { status: 503, body: {} } });
  await assert.rejects(getJson("/down", fetchFn), { message: "GET /down failed with 503" });
  await assert.rejects(getJson("/missing", fetchFn), { message: "GET /missing failed with 404" });
});

test("getAll returns bodies in the order of the URLs", async () => {
  const { fetchFn } = fakeFetch({ "/a": { body: 1 }, "/b": { body: 2 }, "/c": { body: 3 } });
  assert.deepEqual(await getAll(["/c", "/a", "/b"], fetchFn), [3, 1, 2]);
});

test("getAll starts every request before any of them finishes", async () => {
  const started = [];
  const release = [];
  const slowFetch = (url) => {
    started.push(url);
    return new Promise((resolve) => release.push(() => resolve(Response.json({ url }))));
  };
  const pending = getAll(["/a", "/b", "/c"], slowFetch);
  await tick();
  assert.deepEqual(started, ["/a", "/b", "/c"], "all three fetches should start at once");
  release.reverse().forEach((finish) => finish()); // finish them in reverse order
  assert.deepEqual(await pending, [{ url: "/a" }, { url: "/b" }, { url: "/c" }]);
});

test("getAll rejects if any request fails", async () => {
  const { fetchFn } = fakeFetch({ "/a": { body: 1 } });
  await assert.rejects(getAll(["/a", "/nope"], fetchFn), { message: "GET /nope failed with 404" });
});

test("firstAvailable falls back in order and stops at the first success", async () => {
  const { fetchFn, calls } = fakeFetch({
    "/primary": { status: 500, body: {} },
    "/backup": { body: { from: "backup" } },
    "/third": { body: { from: "third" } },
  });
  assert.deepEqual(await firstAvailable(["/primary", "/backup", "/third"], fetchFn), { from: "backup" });
  assert.deepEqual(calls, ["/primary", "/backup"]);
});

test("firstAvailable throws when every URL fails", async () => {
  const { fetchFn } = fakeFetch({});
  await assert.rejects(firstAvailable(["/x", "/y"], fetchFn), { message: "all URLs failed" });
});
