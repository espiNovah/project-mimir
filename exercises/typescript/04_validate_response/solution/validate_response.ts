export const STOP_REASONS = ["end_turn", "max_tokens", "stop_sequence", "tool_use"] as const;
export type StopReason = (typeof STOP_REASONS)[number];

export type ContentBlock =
  | { type: "text"; text: string }
  | { type: "tool_use"; id: string; name: string; input: Record<string, unknown> };

export interface ChatResponse {
  id: string;
  model: string;
  content: ContentBlock[];
  stopReason: StopReason;
  usage: { inputTokens: number; outputTokens: number };
}

/** Thrown when the response does not have the expected shape. */
export class ValidationError extends Error {
  path: string;
  constructor(path: string, problem: string) {
    super(`${path}: ${problem}`);
    this.name = "ValidationError";
    this.path = path;
  }
}

/** Like typeof, but says "array" and "null" instead of "object". */
export function typeOf(value: unknown): string {
  if (value === null) return "null";
  if (Array.isArray(value)) return "array";
  return typeof value;
}

type Json = Record<string, unknown>;

/** A type guard: true for a plain object (not null, not an array). */
function isRecord(value: unknown): value is Json {
  return typeOf(value) === "object";
}

function at(parent: string, key: string): string {
  return parent ? `${parent}.${key}` : key;
}

function record(value: unknown, path: string): Json {
  if (!isRecord(value)) throw new ValidationError(path || "(root)", `expected object, got ${typeOf(value)}`);
  return value;
}

function str(obj: Json, key: string, parent = ""): string {
  const value = obj[key];
  if (typeof value !== "string") throw new ValidationError(at(parent, key), `expected string, got ${typeOf(value)}`);
  return value;
}

function num(obj: Json, key: string, parent = ""): number {
  const value = obj[key];
  if (typeof value !== "number") throw new ValidationError(at(parent, key), `expected number, got ${typeOf(value)}`);
  return value;
}

function parseBlock(value: unknown, path: string): ContentBlock {
  const block = record(value, path);
  const type = str(block, "type", path);
  if (type === "text") return { type, text: str(block, "text", path) };
  if (type === "tool_use") {
    return {
      type,
      id: str(block, "id", path),
      name: str(block, "name", path),
      input: record(block.input, at(path, "input")),
    };
  }
  throw new ValidationError(at(path, "type"), `unknown block type ${JSON.stringify(type)}`);
}

function parseStopReason(obj: Json): StopReason {
  const value = str(obj, "stop_reason");
  if (!(STOP_REASONS as readonly string[]).includes(value)) {
    throw new ValidationError("stop_reason", `unknown value ${JSON.stringify(value)}`);
  }
  return value as StopReason;
}

/** Check `data` and turn it into a ChatResponse, or throw a ValidationError. */
export function parseChatResponse(data: unknown): ChatResponse {
  const obj = record(data, "");
  const id = str(obj, "id");
  const model = str(obj, "model");
  if (!Array.isArray(obj.content)) {
    throw new ValidationError("content", `expected array, got ${typeOf(obj.content)}`);
  }
  const content = obj.content.map((block, i) => parseBlock(block, `content[${i}]`));
  const stopReason = parseStopReason(obj);
  const usage = record(obj.usage, "usage");
  return {
    id,
    model,
    content,
    stopReason,
    usage: {
      inputTokens: num(usage, "input_tokens", "usage"),
      outputTokens: num(usage, "output_tokens", "usage"),
    },
  };
}

/** The text of every text block, joined with "". */
export function textOf(response: ChatResponse): string {
  return response.content
    .filter((block) => block.type === "text")
    .map((block) => block.text)
    .join("");
}
