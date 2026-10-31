### Introduction

In JavaScript Fundamentals you built pages by hand: select an element, listen for an event, then change the page yourself with `textContent` or `appendChild`. That works for one button and one result. It gets painful fast for a chat app. Every new message has to be added to the list, the input must be cleared, the Send button disabled while waiting, an error shown and later hidden, and all of these have to agree with each other. Forget one update and the page shows something that isn't true.

React turns this around. Instead of writing the steps that change the page, you describe what the page *should look like* for the current data, and React works out the changes. When the data changes, React redraws the parts that need it. This is the most widely used way to build web interfaces, and most AI products you use, chat apps included, have a React front end. It is also what the Docs Chatbot UI project at the end of this section asks for.

This lesson teaches the core of React with TypeScript, and ends with a chat interface that talks to a FastAPI backend like the ones you built in the Backend section.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- How to create a React and TypeScript project with Vite.
- Components as functions, and JSX/TSX for describing the page.
- Passing data into components with props.
- Remembering data with state and `useState`, and handling events.
- Rendering lists with keys, and lifting state up to share it.
- What effects are for, and when you don't need one.
- Calling your FastAPI backend from a React app.

### Creating a project with Vite

React is a library, not a whole toolchain. Browsers can't run TypeScript or JSX directly, so something has to translate your code into plain JavaScript and serve it while you work. That something is a *build tool*, and the standard choice today is [Vite](https://vite.dev/) (pronounced "veet"). It starts a development server in well under a second and reloads the page the moment you save a file.

Create a project with the React and TypeScript template. You need Node.js installed, as in JavaScript Fundamentals.

```bash
npm create vite@latest chat-ui -- --template react-ts
cd chat-ui
npm install
npm run dev
```

The `--` passes `--template react-ts` through `npm` to Vite's project creator, so it doesn't stop to ask which framework you want. Open the address it prints (usually `http://localhost:5173`) and you'll see a starter page. At the time of writing this creates a project on React 19, Vite 8 and TypeScript 7.

The files that matter:

- `index.html` is the single HTML page. It has one empty `<div id="root">`, and React fills it.
- `src/main.tsx` finds that div and tells React to render the `App` component into it.
- `src/App.tsx` is the starter component. You'll replace it.
- `package.json` lists your dependencies and the scripts: `npm run dev` for the development server, `npm run build` to type-check and produce optimized files in `dist/` for deployment.

`main.tsx` wraps your app in `<StrictMode>`. In development only, Strict Mode deliberately runs some of your code twice to expose bugs. Keep it; you'll see why in the section on effects.

### Components are functions

A React *component* is a function that returns a description of some UI. Its name starts with a capital letter. Here is the smallest useful one:

```tsx
function Greeting() {
  const name = "Ada";
  return <h1>Hello, {name}!</h1>;
}
```

That `<h1>` inside JavaScript is *JSX*, a syntax that lets you write HTML-like markup in your code. In a TypeScript file it's called TSX, and the file ends in `.tsx`. JSX is not a string and not real HTML: the build tool turns each tag into an ordinary function call that creates an object describing the element. A few differences from HTML follow from that:

- Curly braces `{ }` switch back to JavaScript. Anything inside is an expression whose value is shown: `{name}`, `{2 + 2}`, `{items.length}`.
- Attributes are written in camelCase, and `class` becomes `className` because `class` is a reserved word in JavaScript: `<div className="message">`.
- Every tag must close, including `<input />` and `<br />`.
- A component returns one root element. To return two siblings without an extra `<div>`, wrap them in an empty *fragment*, `<>...</>`.

You use a component like a tag: `<Greeting />`. Building an interface means writing many small components and putting them inside each other, just as you split a Python program into functions.

JSX also protects you. Text you put in `{ }` is always displayed as text, never run as HTML, so `{modelReply}` is as safe as setting `textContent`. The way around this protection is deliberately named `dangerouslySetInnerHTML`. Don't use it for model output.

### Props pass data in

A component that always says "Ada" isn't very useful. *Props* (short for properties) are the arguments of a component. You pass them like HTML attributes, and the component receives them as one object. With TypeScript you describe that object's shape with a type, as you learned in TypeScript Basics:

```tsx
type MessageProps = {
  role: "user" | "assistant";
  text: string;
};

function Message({ role, text }: MessageProps) {
  return (
    <div className={`message message--${role}`}>
      <strong>{role === "user" ? "You" : "Assistant"}</strong>
      <p>{text}</p>
    </div>
  );
}

// Used elsewhere:
// <Message role="user" text="What is RAG?" />
```

The `{ role, text }` in the parameter list is destructuring, which pulls the two fields out of the props object. Now TypeScript checks every use of `<Message>`: forget `text`, or pass `role="admin"`, and your editor underlines it in red before you ever run the code.

Props flow one way, from parent to child. A component must never change its own props. If a parent passes `text="hi"`, the child shows "hi" and that's it.

### State remembers things

Props come from outside. *State* is data a component owns and changes over time: what's typed in a box, the list of messages, whether a request is in flight. You create state with the `useState` *hook*. Hooks are special React functions whose names start with `use`, and you call them at the top level of a component, never inside an `if` or a loop.

```tsx
import { useState } from "react";

function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>Clicked {count} times</button>;
}
```

`useState(0)` returns a pair: the current value and a *setter* function. Calling `setCount(5)` doesn't change `count` on the spot. It tells React "the state is now 5, please render again." React calls `Counter` again, this time `useState` returns 5, and React updates the button text. This is the core loop of React: **an event changes state, the state change causes a re-render, and the render describes the new page.** You never touch the DOM yourself.

Two rules save a lot of confusion:

- **Treat state as read-only.** To add a message, don't `messages.push(m)`. Create a new array: `setMessages([...messages, m])`. React notices a change by comparing the old and new value; if you change the old array in place, it looks the same and React may skip the update.
- **Use the updater form when the new value depends on the old one.** `setMessages(prev => [...prev, m])` hands you the latest value, even if several updates happen before the next render. This matters in async code, where a variable captured earlier may be stale by the time the request finishes.

A plain variable such as `let count = 0` inside a component doesn't work as state: it's reset on every render, and changing it doesn't trigger one.

### Events and forms

You attach event handlers with props such as `onClick`, `onChange` and `onSubmit`, passing a function (not calling one: `onClick={handleClick}`, not `onClick={handleClick()}`).

For text inputs, React's usual pattern is a *controlled input*: the input's value lives in state, and every keystroke updates it.

```tsx
const [draft, setDraft] = useState("");

<input value={draft} onChange={(e) => setDraft(e.target.value)} />
```

Now `draft` is always exactly what's in the box, so you can validate it, clear it after sending (`setDraft("")`) or disable a button when it's empty. Forms still submit and reload the page by default, just as in plain JavaScript, so call `e.preventDefault()` in `onSubmit`.

### Lists and keys

To show a list, turn an array of data into an array of elements with `map`:

```tsx
<ul>
  {messages.map((m) => (
    <li key={m.id}>{m.text}</li>
  ))}
</ul>
```

Each item needs a `key` prop, a value that's unique among its siblings and stays the same for that item across renders. React uses keys to match the items in the new list against the old one, so it can tell "one message was added at the end" from "every message changed." Use a real ID, such as a database ID or one you create with `crypto.randomUUID()` when the message is made. Don't use the array index if items can be inserted, removed or reordered: React will then attach the wrong state to the wrong item, which shows up as text boxes that keep the wrong content. React warns in the browser console when you forget a key.

### Lifting state up

Suppose you split the chat into two components: a `MessageList` that shows the conversation and a `ChatInput` that sends new messages. The input needs to *add* to the list, and the list needs to *show* it. Siblings can't reach into each other. The answer is to **lift the state up**: move `messages` into their closest common parent, `App`. `App` passes the array down to `MessageList` as a prop, and passes a function down to `ChatInput` that the input calls when the user sends something.

This gives every piece of data exactly one owner, the "single source of truth." Data flows down through props; requests to change it flow up through callback functions. When something on screen is wrong, you know which component's state to look at. You'll see this shape in the full example below.

### Effects and when you need them

Rendering should be a *pure* calculation: given props and state, return JSX, with no side effects. But sometimes a component has to reach outside React, for example to scroll a container, connect to a server, or start a timer. That's what `useEffect` is for. It runs your code *after* React has updated the page.

```tsx
useEffect(() => {
  bottomRef.current?.scrollIntoView({ behavior: "smooth" });
}, [messages]);
```

The array at the end is the *dependency list*: React runs the effect after the first render and again whenever a value in the list changes. Here, every time `messages` changes, the chat scrolls to the newest message. An empty list `[]` means "only after the first render." An effect can return a *cleanup* function, which React calls before running the effect again and when the component disappears, so you can cancel a request or stop a timer.

In development, Strict Mode runs each effect, its cleanup, then the effect again, right at the start. If that double run causes a bug, such as two requests whose answers race each other, your effect is missing a cleanup, and Strict Mode just showed you.

The most common React mistake is using effects where you don't need them. Two rules from the React docs cover most cases:

- **If you can calculate something from props or state, calculate it during render.** Don't keep `messageCount` in state and update it in an effect; write `const messageCount = messages.length`.
- **If something happens because the user did something, do it in the event handler.** Sending a chat message is a response to a click, so the `fetch` belongs in `onSubmit`, not in an effect that watches some "shouldSend" state.

Effects are for synchronizing with something outside React. If there is no outside system involved, you probably don't need one.

### Calling your FastAPI backend

Your React app runs in the browser on port 5173; your FastAPI backend runs on port 8000. Different ports are different *origins*, so the browser's CORS rule from HTML and CSS Essentials would block the request. In development, the simplest fix is to let Vite *proxy* API requests: the browser talks only to Vite, and Vite forwards anything under `/api` to FastAPI. Replace `vite.config.ts` with:

```ts
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { "/api": "http://127.0.0.1:8000" }, // forward /api/* to FastAPI
  },
});
```

When you deploy, either serve the built `dist/` files from the same domain as the API, or add FastAPI's `CORSMiddleware` with your front end's exact origin.

Here is a minimal backend to talk to. It uses the Anthropic SDK; [On other providers](#on-other-providers) shows the same route for OpenAI-compatible APIs. Create it in a separate folder with `uv init chat-api`, then `uv add "fastapi[standard]" anthropic`, and run it with `uv run fastapi dev main.py`. It takes the whole conversation each time, because the model has no memory between calls (see System Prompts and Conversations).

```python
import os
from typing import Literal

import anthropic
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
app = FastAPI()


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=50)


class ChatReply(BaseModel):
    reply: str


@app.post("/api/chat")
def chat(req: ChatRequest) -> ChatReply:
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=2000,
            messages=[m.model_dump() for m in req.messages],
        )
    except anthropic.APIError:
        raise HTTPException(status_code=502, detail="The model call failed.")
    text = "".join(b.text for b in response.content if b.type == "text")
    return ChatReply(reply=text)
```

The request and response shapes are the *contract* between your front end and back end. The TypeScript types in the next section mirror these Pydantic models, so both sides agree on what travels over the wire.

### A chat message list in TypeScript

Now put it all together. Replace `src/App.tsx` with this. The starter `src/App.css` is no longer imported, so you can delete it.

```tsx
import { useEffect, useRef, useState } from "react";

type Role = "user" | "assistant";
type ChatMessage = { id: string; role: Role; content: string };

// (1) A child component: receives data through props, owns no state.
function MessageList({ messages }: { messages: ChatMessage[] }) {
  const bottomRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" }); // (2) sync with the DOM
  }, [messages]);

  if (messages.length === 0) return <p className="empty">Ask me anything.</p>;
  return (
    <div className="messages">
      {messages.map((m) => (
        <div key={m.id} className={`message message--${m.role}`}>  {/* (3) stable key */}
          <strong>{m.role === "user" ? "You" : "Assistant"}</strong>
          <p style={{ whiteSpace: "pre-wrap" }}>{m.content}</p>   {/* text, never HTML */}
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  );
}

// (4) Another child: tells its parent about new text through a callback prop.
function ChatInput({ onSend, disabled }: { onSend: (text: string) => void; disabled: boolean }) {
  const [draft, setDraft] = useState("");
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (!draft.trim()) return;
        onSend(draft.trim());
        setDraft("");
      }}
    >
      <input value={draft} onChange={(e) => setDraft(e.target.value)} aria-label="Message" />
      <button disabled={disabled || !draft.trim()}>Send</button>
    </form>
  );
}

// (5) The parent owns the shared state and passes it down.
export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function send(text: string) {  // (6) the request lives in the event handler
    const userMessage: ChatMessage = { id: crypto.randomUUID(), role: "user", content: text };
    const history = [...messages, userMessage];
    setMessages(history);
    setPending(true);
    setError(null);
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: history.map(({ role, content }) => ({ role, content })) }),
      });
      if (!res.ok) throw new Error(`The server answered ${res.status}.`);
      const data: { reply: string } = await res.json();
      setMessages((prev) => [...prev, { id: crypto.randomUUID(), role: "assistant", content: data.reply }]);  // (7)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setPending(false);
    }
  }

  return (
    <main>
      <h1>Chat</h1>
      <MessageList messages={messages} />
      {pending && <p className="status">Thinking…</p>}           {/* (8) conditional rendering */}
      {error && <p className="error" role="alert">{error}</p>}
      <ChatInput onSend={send} disabled={pending} />
    </main>
  );
}
```

1. `MessageList` only displays what it's given. Components like this are easy to reason about and to reuse.
1. `useRef` holds a reference to a real DOM element without causing re-renders. Scrolling is a genuine side effect on something outside React, so it's a fair use of `useEffect`.
1. Each message gets an ID when it's created, so keys stay stable as the list grows.
1. `ChatInput` owns its own `draft` state, because nobody else needs it. It reports finished messages upward through `onSend`.
1. `App` owns `messages`, `pending` and `error`, because more than one child needs them. That's lifting state up.
1. Sending happens because the user submitted the form, so the `fetch` is in the handler, not in an effect. The `res.ok` check catches `422` and `502` responses, which `fetch` doesn't treat as errors.
1. The updater form appends the reply to whatever the list holds *now*, not to the `messages` value captured when `send` started.
1. `{pending && <p>…</p>}` shows the element only when `pending` is true. For either-or choices, use the ternary `a ? <X /> : <Y />`.

With both servers running, open `http://localhost:5173` and have a conversation. Then run `npm run build`: it type-checks the whole project with TypeScript before building, so a mismatched prop fails the build instead of failing in front of a user.

This version waits for the full reply. In Streaming in the Browser you'll read the answer token by token; in React, that means appending each token to the last message's `content` with the updater form.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Install React Developer Tools

The free [React Developer Tools](https://react.dev/learn/react-developer-tools) browser extension adds a Components tab to your browser's developer tools. Click any component to see its current props and state. When the screen shows something wrong, check the state first: if the state is right, the bug is in your JSX; if it's wrong, the bug is in whatever set it.

</div>

### On other providers

Your React code never talks to a model provider. It talks to your own `/api/chat` contract, a list of messages in and `{ reply }` out, so switching providers changes only the backend, and the browser never has to know. That's also why the API key stays safe on the server. The message list itself carries over almost unchanged: OpenAI's Chat Completions API and the OpenAI-compatible servers used for open models take the same `role` and `content` dictionaries. Three things differ. The reply text is in `choices[0].message.content` instead of a list of content blocks. `max_tokens` is required by the Anthropic API but optional elsewhere. And a system prompt, which you'll add in the Assignment, is a separate `system` argument for Claude but the first message in the list, with role `"system"`, for OpenAI-style APIs (see [OpenAI's text generation guide](https://developers.openai.com/api/docs/guides/text)). Here is the same route on any OpenAI-compatible API, shown with a local open model through [Ollama's OpenAI-compatible API](https://docs.ollama.com/api/openai-compatibility):

```python
import openai  # uv add openai

MODEL = os.environ.get("MIMIR_MODEL", "qwen3:8b")
client = openai.OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")  # OpenAI() for OpenAI

@app.post("/api/chat")
def chat(req: ChatRequest) -> ChatReply:
    try:
        response = client.chat.completions.create(
            model=MODEL, messages=[m.model_dump() for m in req.messages],  # same message shape
        )
    except openai.APIError:
        raise HTTPException(status_code=502, detail="The model call failed.")
    return ChatReply(reply=response.choices[0].message.content or "")
```

The Pydantic models, the Vite proxy and every line of `App.tsx` stay exactly as they are.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Quick Start](https://react.dev/learn) and then the [Describing the UI](https://react.dev/learn/describing-the-ui) chapter of the official React docs. They are the best free React course there is, with small interactive challenges at the end of each page.
   - Do at least the first challenge on each page. The docs write JavaScript; adding the types is good TypeScript practice.
   - Pay special attention to "Rendering Lists" and "Keeping Components Pure".
1. Read the [Adding Interactivity](https://react.dev/learn/adding-interactivity) chapter, especially "State: A Component's Memory", "Updating Arrays in State" and "Queueing a Series of State Updates". These cover the two state rules from this lesson in depth.
1. Read [Sharing State Between Components](https://react.dev/learn/sharing-state-between-components) and [You Might Not Need an Effect](https://react.dev/learn/you-might-not-need-an-effect). The second one is the page most React developers wish they'd read sooner.
1. Skim [Using TypeScript](https://react.dev/learn/typescript) in the React docs and the [Getting Started](https://vite.dev/guide/) page of the Vite guide, so you know where props types, event types and the dev server's options are documented.
1. Practice: build the chat app from this lesson, with the FastAPI backend, then extend it.
   - Add a "New chat" button that clears the conversation. Which component should it live in, and why?
   - Show a word count of the conversation under the list. Calculate it during render, without new state or an effect.
   - Add a system prompt selector (for example "concise" or "friendly") whose value is sent with each request, and update the Pydantic model to accept it.
   - Disable the input and show a clear message when the conversation reaches the backend's 50-message limit.
   - Run `npm run build` and fix any type errors it reports.
1. Practice: if you want more TypeScript reps first, work through the [typescript exercise set](https://github.com/espiNovah/project-mimir/tree/main/exercises/typescript). From the `exercises/` folder, run `npm test -- typescript/<exercise>` and make the tests pass.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What is JSX, and why is putting model output inside curly braces safe?](#components-are-functions)
- [What is the difference between props and state?](#props-pass-data-in)
- [What happens, step by step, when you call a state setter?](#state-remembers-things)
- [Why does every item in a rendered list need a stable key?](#lists-and-keys)
- [Where should state live when two sibling components need it?](#lifting-state-up)
- [When do you need useEffect, and where should a chat request be sent from instead?](#effects-and-when-you-need-them)
- [How does a Vite proxy let your React app call FastAPI without CORS errors?](#calling-your-fastapi-backend)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Thinking in React](https://react.dev/learn/thinking-in-react) walks through designing a small app from a mockup: splitting it into components and deciding where state lives.
- [Synchronizing with Effects](https://react.dev/learn/synchronizing-with-effects) explains effects, cleanups and the Strict Mode double run in full.
- The [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/) is the community reference for typing props, events, refs and hooks.
- Vite's [server proxy option](https://vite.dev/config/server-options#server-proxy) documents rewriting paths and proxying WebSockets.
