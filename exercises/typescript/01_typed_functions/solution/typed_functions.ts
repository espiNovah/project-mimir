export type Role = "system" | "user" | "assistant";

export interface Message {
  role: Role;
  content: string;
}

export interface Usage {
  inputTokens: number;
  outputTokens: number;
}

/** Dollars per million tokens. */
export interface Price {
  input: number;
  output: number;
}

/** One "role: content" line per message, joined with "\n". */
export function formatTranscript(messages: Message[]): string {
  return messages.map((m) => `${m.role}: ${m.content}`).join("\n");
}

/** The cost in dollars, given prices per million tokens. */
export function costUsd(usage: Usage, price: Price): number {
  return (usage.inputTokens * price.input + usage.outputTokens * price.output) / 1_000_000;
}

/** The last message, or the last one with `role` if given. */
export function lastMessage(messages: Message[], role?: Role): Message | undefined {
  return messages.findLast((m) => role === undefined || m.role === role);
}
