// Every function takes the fetch function as an argument, so tests can pass a fake.

/** Fetch `url` and return its JSON body. Throw if the response isn't OK. */
export async function getJson(url, fetchFn) {
  const res = await fetchFn(url);
  if (!res.ok) throw new Error(`GET ${url} failed with ${res.status}`);
  return await res.json();
}

/** Fetch every URL in parallel; return their JSON bodies in the order of `urls`. */
export async function getAll(urls, fetchFn) {
  return Promise.all(urls.map((url) => getJson(url, fetchFn)));
}

/** Try URLs in order and return the JSON of the first that succeeds. */
export async function firstAvailable(urls, fetchFn) {
  for (const url of urls) {
    try {
      return await getJson(url, fetchFn);
    } catch {
      // This one failed; try the next URL.
    }
  }
  throw new Error("all URLs failed");
}
