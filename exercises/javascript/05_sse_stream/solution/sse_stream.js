/** Parse one message (the text between blank lines). Return null if it has no data. */
function parseMessage(text) {
  let event = "message";
  const data = [];
  for (const line of text.split("\n")) {
    const colon = line.indexOf(":");
    if (colon === 0) continue; // a comment, such as a keep-alive ping
    const field = colon === -1 ? line : line.slice(0, colon);
    let value = colon === -1 ? "" : line.slice(colon + 1);
    if (value.startsWith(" ")) value = value.slice(1);
    if (field === "event") event = value;
    else if (field === "data") data.push(value);
  }
  return data.length ? { event, data: data.join("\n") } : null;
}

/**
 * Yield one { event, data } object per complete server-sent event message.
 * `stream` is a ReadableStream of bytes (Uint8Array chunks), like `response.body`.
 */
export async function* readEvents(stream) {
  let buffer = "";
  for await (const chunk of stream.pipeThrough(new TextDecoderStream())) {
    buffer += chunk;
    const parts = buffer.split("\n\n");
    buffer = parts.pop(); // the unfinished tail waits for the next chunk
    for (const part of parts) {
      const message = parseMessage(part);
      if (message) yield message;
    }
  }
  // Anything left in `buffer` is an unfinished message: drop it.
}

/**
 * Read token/done/error events and return { text, stopReason }.
 * Throw on an error event, or if the stream ends before a done event.
 */
export async function collectAnswer(stream) {
  let text = "";
  for await (const { event, data } of readEvents(stream)) {
    if (event === "token") text += JSON.parse(data);
    else if (event === "done") return { text, stopReason: JSON.parse(data).stop_reason };
    else if (event === "error") throw new Error(JSON.parse(data).message);
  }
  throw new Error("stream ended before done");
}
