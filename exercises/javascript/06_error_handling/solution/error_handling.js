/** An HTTP error that remembers its status code. */
export class HttpError extends Error {
  constructor(status, message) {
    super(message);
    this.name = "HttpError";
    this.status = status;
  }
}

/** JSON.parse(text), or `fallback` if the text isn't valid JSON. */
export function parseJsonOr(text, fallback) {
  try {
    return JSON.parse(text);
  } catch {
    return fallback;
  }
}

/** True only for an HttpError with status 429 or >= 500. */
export function isRetryable(error) {
  return error instanceof HttpError && (error.status === 429 || error.status >= 500);
}

/** Call fn(attempt), retrying retryable errors with doubling waits (100, 200, 400 ms ...). */
export async function withRetries(fn, { retries = 2, sleep } = {}) {
  for (let attempt = 1; ; attempt++) {
    try {
      return await fn(attempt);
    } catch (err) {
      if (!isRetryable(err) || attempt > retries) throw err;
      await sleep(100 * 2 ** (attempt - 1));
    }
  }
}
