export type StreamEvent =
  | { type: "token"; text: string }
  | { type: "citations"; sources: string[] }
  | { type: "done"; stopReason: string }
  | { type: "error"; message: string };

export interface ChatState {
  text: string;
  sources: string[];
  status: "streaming" | "done" | "error";
  error?: string;
}

export function initialState(): ChatState {
  return { text: "", sources: [], status: "streaming" };
}

/** The new state after one event. Don't change `state`. */
export function applyEvent(state: ChatState, event: StreamEvent): ChatState {
  throw new Error("TODO: switch on event.type");
}

/** A display string for each kind of value. */
export function toDisplay(value: string | number | string[] | null): string {
  throw new Error("TODO: narrow with === null, Array.isArray and typeof");
}
