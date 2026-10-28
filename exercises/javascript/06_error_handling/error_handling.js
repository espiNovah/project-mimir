/** An HTTP error that remembers its status code. */
export class HttpError extends Error {
  // TODO: a constructor(status, message) that sets this.status and this.name = "HttpError"
}

/** JSON.parse(text), or `fallback` if the text isn't valid JSON. */
export function parseJsonOr(text, fallback) {
  throw new Error("TODO: use try/catch");
}

/** True only for an HttpError with status 429 or >= 500. */
export function isRetryable(error) {
  throw new Error("TODO: use instanceof");
}

/** Call fn(attempt), retrying retryable errors with doubling waits (100, 200, 400 ms ...). */
export async function withRetries(fn, { retries = 2, sleep } = {}) {
  throw new Error("TODO: loop over attempts with try/catch");
}
