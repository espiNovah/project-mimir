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

/** Check `data` and turn it into a ChatResponse, or throw a ValidationError. */
export function parseChatResponse(data: unknown): ChatResponse {
  throw new Error("TODO: check every field and build the typed object");
}

/** The text of every text block, joined with "". */
export function textOf(response: ChatResponse): string {
  throw new Error("TODO: filter the text blocks and join their text");
}
