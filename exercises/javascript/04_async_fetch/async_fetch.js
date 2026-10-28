// Every function takes the fetch function as an argument, so tests can pass a fake.

/** Fetch `url` and return its JSON body. Throw if the response isn't OK. */
export async function getJson(url, fetchFn) {
  throw new Error("TODO: await fetchFn(url), check res.ok, return await res.json()");
}

/** Fetch every URL in parallel; return their JSON bodies in the order of `urls`. */
export async function getAll(urls, fetchFn) {
  throw new Error("TODO: use Promise.all");
}

/** Try URLs in order and return the JSON of the first that succeeds. */
export async function firstAvailable(urls, fetchFn) {
  throw new Error("TODO: use a for...of loop with try/catch");
}
