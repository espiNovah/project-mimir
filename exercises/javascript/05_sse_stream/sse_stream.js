/**
 * Yield one { event, data } object per complete server-sent event message.
 * `stream` is a ReadableStream of bytes (Uint8Array chunks), like `response.body`.
 */
export async function* readEvents(stream) {
  throw new Error("TODO: decode, buffer, split on blank lines, parse each message");
}

/**
 * Read token/done/error events and return { text, stopReason }.
 * Throw on an error event, or if the stream ends before a done event.
 */
export async function collectAnswer(stream) {
  throw new Error("TODO: use `for await (const { event, data } of readEvents(stream))`");
}
