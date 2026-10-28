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
  switch (event.type) {
    case "token":
      return { ...state, text: state.text + event.text };
    case "citations":
      return { ...state, sources: [...state.sources, ...event.sources] };
    case "done":
      return { ...state, status: "done" };
    case "error":
      return { ...state, status: "error", error: event.message };
    default: {
      // Compiles only if every member of StreamEvent has a case above.
      const unreachable: never = event;
      throw new Error(`unknown event type: ${(unreachable as { type: unknown }).type}`);
    }
  }
}

/** A display string for each kind of value. */
export function toDisplay(value: string | number | string[] | null): string {
  if (value === null) return "";
  if (Array.isArray(value)) return value.join(", ");
  if (typeof value === "number") return value.toLocaleString("en-US");
  return value;
}
