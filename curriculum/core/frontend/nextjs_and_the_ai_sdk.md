### Introduction

In React Essentials you built a chat interface with Vite and React, talking to a FastAPI backend. That's two programs in two languages: a TypeScript front end and a Python back end. Many AI products are built a different way, with one TypeScript project that holds both the pages and the server code. The most popular framework for that is Next.js, and the most popular library for streaming chat on top of it is the Vercel AI SDK. Together they get a streaming chatbot running in about forty lines.

You will meet this stack constantly: in job postings, in starter templates, and in the code that coding assistants write when you ask for "a chat app." This lesson teaches what Next.js adds to React, how the AI SDK streams a model's answer into a `useChat` hook, and, just as important, when to use this stack and when to keep the Python backend you've spent the whole Backend, RAG and Evals sections building.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What a framework like Next.js adds on top of React.
- How the App Router turns folders into pages.
- The difference between server components and client components.
- How route handlers give a Next.js app its own API endpoints.
- How the AI SDK's `streamText` and `useChat` stream a chat answer.
- How to choose between Next.js with the AI SDK and React with your FastAPI backend.

### What Next.js adds to React

React is a *library*: it renders components and nothing else. Your Vite project added a build tool, and you made every other decision yourself. Next.js is a *framework*: a library plus a set of decisions and conventions about how a whole app fits together. On top of React it gives you:

- **Routing from folders.** Each URL of your site corresponds to a folder in your project, with no routing code to write.
- **Rendering on the server.** Pages can be rendered to HTML on the server, so they appear fast and search engines can read them, and components can read databases or secrets directly.
- **API endpoints in the same project.** You can write server code that answers `POST /api/chat` next to the page that calls it, in the same language.
- **One deployment.** `npm run build` produces one app that runs on Vercel (the company that makes Next.js), on any Node.js host, or in a Docker container.

The price is more to learn, and more "magic" that's only obvious once you know the conventions. Next.js changes quickly, so always check that a tutorial matches the current major version. At the time of writing that's Next.js 16, and this lesson uses the **App Router**, the current way of structuring a Next.js app. You will also see an older style called the Pages Router in tutorials; it uses a `pages/` folder instead of `app/`. Skip those tutorials for now.

Create a project. Accept the recommended defaults when asked (TypeScript, Tailwind CSS for styling, the App Router):

```bash
npx create-next-app@latest docs-chat
cd docs-chat
npm run dev
```

The dev server runs at `http://localhost:3000`.

### The App Router

In the App Router, the `app/` folder *is* your site map. A folder becomes a part of the URL, and a file called `page.tsx` inside it is the page shown there:

| File | URL |
| --- | --- |
| `app/page.tsx` | `/` |
| `app/about/page.tsx` | `/about` |
| `app/chats/[id]/page.tsx` | `/chats/42`, `/chats/abc`, ... |
| `app/api/chat/route.ts` | `/api/chat` (an API endpoint, no page) |

A folder name in square brackets, such as `[id]`, is a *dynamic segment*: it matches any value, and the page receives it as a parameter, much like a FastAPI path parameter.

`app/layout.tsx` is the *root layout*. It wraps every page with the shared `<html>` and `<body>` tags, and anything else that should appear everywhere, such as a header. Layouts in subfolders wrap only the pages below them. When you move between pages, the layout stays on screen and only the page part changes.

A `page.tsx` file must `export default` a component. That's all Next.js needs to know to show it.

### Server and client components

This is the idea that confuses newcomers most, so take it slowly. In the App Router, **every component is a server component unless you say otherwise.** A server component runs only on the server. Next.js runs it, turns the result into HTML and sends that to the browser. Its code is never sent to the browser at all.

That has two consequences:

- A server component can do things browser code must never do: read a secret environment variable, query your database, call a model with your API key. It can even be an `async` function that `await`s data before rendering.
- A server component can't be interactive. It has no `useState`, no `useEffect` and no `onClick`, because by the time anything happens in the browser, it has already finished running.

When a component needs interactivity, you put `"use client"` as the very first line of its file. That makes it a *client component*: it is rendered on the server once for the first view, then its JavaScript is sent to the browser, where it runs exactly like the components in React Essentials. Everything it imports becomes client code too.

The usual pattern is to keep pages as server components and make small, interactive pieces client components: a page that loads data on the server, with a `"use client"` chat box inside it.

<div class="lesson-note lesson-note--critical" markdown="1">

#### Secrets stay on the server

The rule from HTML and CSS Essentials still holds: anything the browser receives, every user can read. In Next.js, environment variables are only available to server code, unless their name starts with `NEXT_PUBLIC_`, which tells Next.js to copy the value into the browser bundle. Never give your API key a `NEXT_PUBLIC_` name, and never read it in a `"use client"` file. Keep it in `.env.local`, which `create-next-app` already lists in `.gitignore`.

</div>

### Route handlers

A *route handler* is a server-side API endpoint in a Next.js app. You create a file called `route.ts` and export a function named after the HTTP method it answers:

```ts
// app/api/health/route.ts  →  GET /api/health
export async function GET() {
  return Response.json({ status: "ok" });
}
```

Route handlers use the web's standard `Request` and `Response` objects, the same ones `fetch` uses in the browser. `await req.json()` reads a JSON body, and `Response.json(data, { status: 400 })` sends one back. This is Next.js's equivalent of a FastAPI route, but notice what's missing: there is no Pydantic doing validation for you. Anything a client sends arrives as untyped JSON, and a TypeScript type annotation on it is a promise you make, not a check that runs. For real input validation in TypeScript, use a schema library such as Zod.

Because a route handler runs on the server, it's where model calls belong. The browser calls `/api/chat`; the route handler holds the key and talks to the model.

### The AI SDK in one picture

The [AI SDK](https://ai-sdk.dev/) is a free, open-source TypeScript library from Vercel. Its current major version is AI SDK 7, and its API has changed a lot between major versions, so many tutorials and AI-generated snippets online use names that no longer exist (`useChat` returning `input` and `handleSubmit`, or `result.toDataStreamResponse()`). When something doesn't match, check the version first. The SDK has two halves:

- **AI SDK Core** runs on the server. `streamText` and `generateText` call a model through a *provider* package, such as `@ai-sdk/anthropic` for Claude or `@ai-sdk/openai`. Switching providers is mostly a one-line change, which is the library's main selling point.
- **AI SDK UI** runs in the browser. The `useChat` hook from `@ai-sdk/react` keeps the list of messages in state, sends them to your route handler, and updates the last message as the stream arrives.

Between the two travels the *UI message stream*: server-sent events (SSE), a format you'll take apart by hand in Streaming in the Browser, where each event is a small JSON object such as `{"type":"text-delta","delta":"Hello"}`. Messages in the UI are not plain strings. Each one has an `id`, a `role` and a list of `parts`: text parts, reasoning parts, tool calls, sources, files. You render the parts you care about.

Install the packages in your Next.js project and put your key in `.env.local`:

```bash
npm install ai @ai-sdk/react @ai-sdk/anthropic
echo 'ANTHROPIC_API_KEY=sk-ant-...your-key...' >> .env.local
```

The AI SDK's own quickstart uses the Vercel AI Gateway, a paid service that routes to many providers with one Vercel key. You don't need it. The `@ai-sdk/anthropic` package calls Anthropic directly with the key you already have, and reads it from `ANTHROPIC_API_KEY` automatically.

### A streaming chat route

Create `app/api/chat/route.ts`:

```ts
import { anthropic } from "@ai-sdk/anthropic";
import {
  convertToModelMessages,
  createUIMessageStreamResponse,
  streamText,
  toUIMessageStream,
  type UIMessage,
} from "ai";

const MODEL = process.env.MIMIR_MODEL ?? "claude-haiku-5-5";

export async function POST(req: Request) {
  const { messages }: { messages: UIMessage[] } = await req.json();  // (1)
  if (!Array.isArray(messages) || messages.length === 0 || messages.length > 50) {
    return Response.json({ error: "Send between 1 and 50 messages." }, { status: 400 });  // (2)
  }

  const result = streamText({
    model: anthropic(MODEL),                          // (3) the provider package picks the API
    instructions: "You are a concise, friendly assistant.",  // the system prompt
    messages: await convertToModelMessages(messages), // (4) UI messages → model messages
    maxOutputTokens: 2000,
    abortSignal: req.signal,                          // (5) stop the model if the user leaves
  });

  return createUIMessageStreamResponse({              // (6) stream SSE back to useChat
    stream: toUIMessageStream({
      stream: result.stream,
      onError: () => "The model call failed. Please try again.",  // (7)
    }),
  });
}
```

1. `useChat` sends the whole conversation as a JSON body with a `messages` array, because the model has no memory between calls. The type annotation only tells TypeScript what to expect; it checks nothing at run time.
1. A cheap length check, like the limits you added with Pydantic in the backend lessons. Without it, anyone could send a huge conversation and spend your money. For a public app, also check each message's shape with the SDK's `validateUIMessages` helper or a Zod schema.
1. `anthropic(MODEL)` creates a model object for Anthropic's Messages API. The model ID comes from an environment variable, with the [cheap model](#/models) as the default.
1. The browser's message format (with `id`s and `parts`) isn't what the model API takes. `convertToModelMessages` translates it.
1. `req.signal` is an `AbortSignal` that fires when the browser disconnects or the user clicks Stop. Passing it on cancels the model call, so you stop paying for tokens nobody will read.
1. `streamText` starts the call and returns immediately. `toUIMessageStream` turns the model's events into UI message events, and `createUIMessageStreamResponse` sends them as an SSE response with the right headers.
1. If the model call fails mid-stream, the browser gets an `error` event carrying this text. Returning a fixed message keeps internal error details, which can leak information, off the user's screen. Log the real error on the server.

You can watch the stream without a browser. The `-N` flag stops `curl` from buffering, so events print as they arrive:

```bash
curl -N localhost:3000/api/chat -H "Content-Type: application/json" \
  -d '{"messages":[{"id":"1","role":"user","parts":[{"type":"text","text":"Count to five"}]}]}'
```

### The chat page with useChat

Now replace `app/page.tsx`. It has to be a client component, because it holds state and handles clicks.

```tsx
"use client";

import { useChat } from "@ai-sdk/react";
import { useState } from "react";

export default function Chat() {
  const [input, setInput] = useState("");
  const { messages, sendMessage, status, stop, error } = useChat();  // (1) POSTs to /api/chat
  const busy = status === "submitted" || status === "streaming";     // (2)

  return (
    <main className="mx-auto max-w-xl p-6 space-y-4">
      {messages.map((message) => (
        <div key={message.id}>
          <strong>{message.role === "user" ? "You" : "Assistant"}</strong>
          {message.parts.map((part, i) =>
            part.type === "text" ? (                                  // (3)
              <p key={i} className="whitespace-pre-wrap">{part.text}</p>
            ) : null,
          )}
        </div>
      ))}

      {error && <p role="alert">Something went wrong. Try sending again.</p>}

      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (!input.trim()) return;
          sendMessage({ text: input });                                // (4)
          setInput("");
        }}
        className="flex gap-2"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          aria-label="Message"
          className="flex-1 border rounded p-2"
        />
        {busy ? (
          <button type="button" onClick={() => stop()}>Stop</button>  // (5)
        ) : (
          <button type="submit" disabled={!input.trim()}>Send</button>
        )}
      </form>
    </main>
  );
}
```

1. `useChat` owns the conversation state you managed yourself with `useState` in React Essentials. By default it sends requests to `/api/chat`.
1. `status` is `"submitted"` while waiting for the first token, `"streaming"` while tokens arrive, `"ready"` when it's done and `"error"` if something failed. Use it to show progress and to swap Send for Stop.
1. Each message is a list of parts. This page renders only text. Current Claude models may also send reasoning parts, and later you'll add tool and source parts. Text in `{ }` is shown as text, never as HTML, as you learned in React Essentials.
1. `sendMessage` adds the user's message to `messages`, sends the conversation, and appends a new assistant message that grows as the stream arrives. The input box stays your own state, so you're free to validate or clear it.
1. `stop()` aborts the request. On the server, `req.signal` fires and the model call is cancelled.

Run `npm run dev`, open `http://localhost:3000`, and the answer will appear token by token. You haven't written a single line of stream-parsing code: that's what the library is for.

To call a different endpoint, or send a login token, pass a transport: `useChat({ transport: new DefaultChatTransport({ api: "/api/my-chat", headers: () => ({ Authorization: `Bearer ${token}` }) }) })`, with `DefaultChatTransport` imported from `ai`.

### Choosing your architecture

You now know two ways to build a chat front end. Neither is "the right one"; they suit different projects.

**Next.js and the AI SDK, with the model call in a route handler.** Everything is one TypeScript project, deployed once. Streaming, stop buttons, tool calls and switching providers come built in. This is a great fit when the AI part is thin (a model call with a system prompt and a few tools), when the team writes TypeScript, or when you're building a product prototype fast.

**React (Vite or Next.js) calling your own FastAPI backend.** The front end only displays things; all the AI logic lives in Python. This is a better fit when the backend is where the real work is, and in this curriculum it is: your retrieval pipeline with pgvector and hybrid search, your citations, your JSONL traces, your eval harness, your auth and rate limits are all Python. Rewriting them in TypeScript just to use a front-end library would throw away tested code. Python also has the deeper ecosystem for data, ML and evals.

Ask three questions:

1. **Where does the important logic already live?** If it's in Python and has tests and evals, keep it there and let the front end call it.
1. **How many programs do you want to run and deploy?** One Next.js app is simpler to host than a front end plus an API plus a database. But if you already deploy the API, a static React front end is the smallest possible addition.
1. **Who else calls the backend?** A FastAPI backend can serve a web app, a mobile app, a Slack bot and your eval scripts at once. Logic inside a Next.js route handler serves only that app.

You can also mix them. A Next.js app can be just the front end, with its route handler forwarding requests to FastAPI so your Python backend stays private. And `useChat` doesn't care what language the server is written in: any backend that sends the AI SDK's documented UI message stream format works with it, and Vercel maintains an example with a FastAPI backend.

For the Docs Chatbot UI project, the recommended path is a React and TypeScript front end, built with Vite or Next.js, calling the FastAPI backend from your Chat With Your Docs project, because that's where your retrieval, citations and evals already are. After Streaming in the Browser you'll be able to read its stream yourself, with or without `useChat`.

### On other providers

This lesson is already the most provider-neutral code in the curriculum: the AI SDK hides each provider's request format, stream events and tool-call shapes behind the same `streamText` call and the same UI message stream, so `useChat` and your page don't change at all. Switching means installing a different provider package and changing the `model:` line in the route handler. For OpenAI, install `@ai-sdk/openai`, set `OPENAI_API_KEY`, and pass `openai(MODEL)`; note that this default factory uses OpenAI's newer Responses API, and `openai.chat(MODEL)` uses Chat Completions. For a local open model, point the [OpenAI-compatible provider](https://ai-sdk.dev/providers/openai-compatible-providers) at Ollama:

```ts
import { createOpenAICompatible } from "@ai-sdk/openai-compatible";

const ollama = createOpenAICompatible({
  name: "ollama",
  baseURL: "http://localhost:11434/v1",
  includeUsage: true,               // report token counts while streaming
});

// in the route handler: model: ollama(process.env.MIMIR_MODEL ?? "qwen3:4b"),
```

What doesn't carry over is anything you pass through `providerOptions`, such as Anthropic-specific settings: those are provider features, and the other provider ignores or rejects them. Small local models also follow tool and format instructions less reliably. The [OpenAI provider page](https://ai-sdk.dev/providers/ai-sdk-providers/openai) lists its options, and the [Provider Comparison](#/providers) page shows what the SDK is translating underneath.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Work through the [Next.js App Router getting started guide](https://nextjs.org/docs/app/getting-started), the official tutorial for the current version.
   - Read Installation, Project Structure, Layouts and Pages, Server and Client Components, and Route Handlers. Skim the rest so you know what's there.
1. Read the AI SDK's [Next.js App Router quickstart](https://ai-sdk.dev/docs/getting-started/nextjs-app-router).
   - It uses the Vercel AI Gateway. Use the `@ai-sdk/anthropic` provider from this lesson instead, so you need only the API key you already have.
   - Read through the section on tools. You'll build tool-using agents properly in the Agentic path.
1. Read the AI SDK's [Chatbot guide](https://ai-sdk.dev/docs/ai-sdk-ui/chatbot), up to and including "Request Configuration". It covers `status`, `stop`, errors and sending custom headers, which you'll need for login.
1. Skim the [Anthropic provider page](https://ai-sdk.dev/providers/ai-sdk-providers/anthropic) and the [stream protocol page](https://ai-sdk.dev/docs/ai-sdk-ui/stream-protocol). The second shows exactly what travels over the wire, which is how a non-JavaScript backend can talk to `useChat`.
1. Practice: build the chat app from this lesson, then extend it.
   - Get it streaming, and watch the raw events with the `curl -N` command above.
   - Add a "New chat" button. (Hint: `useChat` also returns `setMessages`.)
   - Show a "Thinking…" indicator while `status` is `"submitted"`.
   - Replace the array-length check with a Zod schema or `validateUIMessages`, and reject any single message longer than 4,000 characters with a `400`.
   - Set a wrong `ANTHROPIC_API_KEY` in `.env.local` and confirm the page shows your error message, not a stack trace.
   - Write a short paragraph in your README: for your Chat With Your Docs project, would you use this stack, a React front end calling FastAPI, or a mix? Use the three questions from [Choosing your architecture](#choosing-your-architecture).

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What does a framework like Next.js add on top of React?](#what-next-js-adds-to-react)
- [What can a server component do that a client component can't, and the other way around?](#server-and-client-components)
- [Why must an API key never be read in a "use client" file or given a NEXT_PUBLIC_ name?](#server-and-client-components)
- [What is a route handler, and what does it not do for you that FastAPI does?](#route-handlers)
- [What do streamText and useChat each do, and what travels between them?](#the-ai-sdk-in-one-picture)
- [Why does the route pass req.signal to streamText?](#a-streaming-chat-route)
- [When would you keep a React front end calling FastAPI instead of moving the model call into Next.js?](#choosing-your-architecture)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- The [Next.js Learn course](https://nextjs.org/learn) is a free, longer project-based tutorial that builds a full dashboard app with the App Router.
- The AI SDK's [Next.js and FastAPI example](https://github.com/vercel/ai/tree/main/examples/next-fastapi) shows `useChat` talking to a Python backend.
- [`useChat` reference](https://ai-sdk.dev/docs/reference/ai-sdk-ui/use-chat) lists every option and return value of the hook.
