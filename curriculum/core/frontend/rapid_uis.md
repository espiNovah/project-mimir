### Introduction

You've now built interfaces the full way: HTML and CSS for the page, JavaScript and TypeScript for behavior, React for components, Next.js for the app, and server-sent events for streaming. That stack gives you full control, and it's what most production AI products use. It also takes days to build something good.

Sometimes you need a working interface by this afternoon. You want to show a teammate whether your docs chatbot is any good, let a domain expert label fifty outputs, or check that an idea is worth building properly. **Streamlit** and **Gradio** are Python libraries that build a web interface from plain Python code, with ready-made chat components. You write no HTML, CSS or JavaScript at all. They are the standard way AI engineers build demos, internal tools and prototypes.

This lesson shows how both work by building the same chat page over your Chat With Your Docs system, in about 40 lines each. Just as important, it shows where these tools stop, so you know when a prototype is enough and when it's time for React.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why a prototype interface comes before the real one.
- How Streamlit's rerun model, session state and caching work.
- How to build a streaming chat page over your RAG system in Streamlit.
- How to build the same chat page in Gradio.
- How to choose between Streamlit and Gradio.
- How to share a demo safely, with secrets and spending limits.
- When a prototype is enough and when you need a React frontend.

### Why prototype first

A **prototype** is a version of your product built to answer a question, not to last. "Do people understand the citations?" "Is retrieval good enough that anyone would use this?" "Which of these three answer formats do our support staff prefer?" You can't answer those in a terminal, because the people you need to ask won't use one. But you also don't want to spend three days on a React app only to learn the answers are bad.

A Python UI library closes that gap. The interface calls the same functions your command-line tool calls, so there's nothing new to wire up: no API endpoints, no CORS, no build step. You get feedback in an hour, and the time you *do* spend later on a React frontend goes into a product you now know is worth building.

The trade is control. These libraries decide what the page looks like and how it behaves. You can adjust a lot, but when you need something they don't offer, you fight the library. Keep that in mind; you'll come back to it at the end of the lesson.

### How Streamlit runs your script

Streamlit has one idea that you must understand before anything else makes sense: **every time a user interacts with the page, Streamlit runs your whole script again, from top to bottom.** Type a message and press Enter, and the script reruns. Click a button, and it reruns. Each call such as `st.title(...)` or `st.markdown(...)` draws something on the page during that run.

That model is wonderfully simple. There are no callbacks or event handlers to learn, and your script reads like a normal Python program. But it has two consequences:

1. **Ordinary variables are forgotten.** A list you create at the top of the script is a brand-new empty list on every run. Anything you want to remember between interactions, such as the chat history, goes in **`st.session_state`**, a dictionary-like object that survives reruns. Each browser tab gets its own session state, so two users never see each other's conversations.
1. **Expensive setup runs every time unless you cache it.** Loading an embedding model or a cross-encoder can take seconds. Wrap that work in a function decorated with **`@st.cache_resource`**, and Streamlit runs it once and reuses the result on every later run, for every user. Use it for things you'd create once and share, like model clients, database connections and the reranker from Hybrid Search and Reranking. (Its sibling, `@st.cache_data`, caches the *data* a function returns, such as a loaded CSV.)

Streamlit also has chat building blocks. **`st.chat_input`** draws a message box pinned to the bottom of the page and returns the text the user just sent, or `None` if they didn't send anything on this run. **`st.chat_message("user")`** or `st.chat_message("assistant")` draws a message bubble with an avatar, and anything you draw inside its `with` block appears in the bubble. **`st.write_stream`** takes a stream of text, shows it piece by piece as it arrives, and returns the full text at the end.

### A chat page in Streamlit

Here is a complete chat page for your docs chatbot. It reuses `SYSTEM`, `format_sources` and `label` from `grounded.py` in Citations and Grounding, and assumes your Chat With Your Docs project has a `retrieve(question)` function that runs hybrid search and reranking and returns a list of chunk dictionaries. Install Streamlit with `uv add streamlit` in that project.

```python
# app.py: a chat page for your docs chatbot.   run: uv run streamlit run app.py
import anthropic
import streamlit as st

from grounded import MODEL, SYSTEM, format_sources, label
from rag import retrieve        # your hybrid search + rerank: question -> list of chunk dicts

st.title("Ask the docs")


@st.cache_resource              # make one client for the whole server, not one per rerun
def get_client():
    return anthropic.Anthropic()


def show_sources(chunks: list[dict]) -> None:
    with st.expander(f"Sources ({len(chunks)})"):
        for n, chunk in enumerate(chunks, start=1):
            st.markdown(f"**[{n}] {label(chunk)}**")
            st.text(chunk["content"])       # st.text shows plain text, no Markdown


if "messages" not in st.session_state:      # survives reruns, one per browser tab
    st.session_state.messages = []

for message in st.session_state.messages:   # the script reruns on every input: redraw history
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            show_sources(message["sources"])

if question := st.chat_input("Ask about the docs", max_chars=500):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        try:
            with st.spinner("Searching..."):
                chunks = retrieve(question)
            prompt = f"<sources>\n{format_sources(chunks)}\n</sources>\n\nQuestion: {question}"
            with get_client().messages.stream(
                model=MODEL, max_tokens=4000, system=SYSTEM,
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                text = st.write_stream(stream.text_stream)   # shows tokens as they arrive
        except anthropic.APIError as error:
            st.error(f"The model call failed, please try again. ({type(error).__name__})")
            st.stop()
        show_sources(chunks)
    st.session_state.messages.append({"role": "assistant", "content": text, "sources": chunks})
```

Run it with `uv run streamlit run app.py` (with your `.env` loaded, as in Your First API Call) and a browser tab opens. Follow one interaction through the rerun model:

- **First run.** Session state has no `messages`, so the script creates an empty list. The history loop draws nothing. `st.chat_input` returns `None`, so the `if` block is skipped. You see a title and an empty message box.
- **You send a question.** The whole script runs again. `messages` already exists, so it is *not* reset. The history loop draws nothing yet. This time `st.chat_input` returns your question, so the `if` block runs: it saves and draws your message, retrieves chunks, streams the answer into an assistant bubble with `st.write_stream`, shows the sources, and saves the answer.
- **You send a second question.** The script reruns again, and now the history loop redraws the first exchange from session state before handling the new question. That loop is how the conversation stays on screen.

A few details are worth noticing. `max_chars=500` caps the length of a question, a small piece of cost protection. `stream.text_stream` is the same iterator of text pieces you used in Streaming Responses, and `st.write_stream` accepts it directly. The sources go inside `st.expander`, a collapsible box, so they're one click away without cluttering the answer, and `st.text` shows each chunk as plain text. Streamlit's `st.markdown` doesn't render raw HTML unless you pass `unsafe_allow_html=True`, which you should never do with model output.

This version sends each question to the model on its own, without the earlier turns, which is how your Chat With Your Docs CLI works too. A follow-up such as "and the Team plan?" won't make sense to it. Making follow-ups work is part of the Assignment.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Test it without a browser

Streamlit ships a testing tool, `streamlit.testing.v1.AppTest`, that runs your script, lets you type into `chat_input` from a pytest test, and inspect what was drawn. Combine it with the fake-client trick from Testing with pytest, and you can check that a question produces two chat bubbles and a sources expander without spending a cent. See [Streamlit's app testing guide](https://docs.streamlit.io/develop/concepts/app-testing).

</div>

### The same chatbot in Gradio

Gradio takes a different approach. Instead of a script that draws the page, you write a **function**, and Gradio builds an interface around it. For chat, that's `gr.ChatInterface`: you give it a function that takes the new message and the history and returns the reply, and it builds the whole page, including the message box, the bubbles and the history. Install it with `uv add gradio`.

```python
# gradio_app.py: the same chatbot in Gradio.   run: uv run python gradio_app.py
import anthropic
import gradio as gr

from grounded import MODEL, SYSTEM, format_sources, label
from rag import retrieve

client = anthropic.Anthropic()


def respond(message: str, history: list[dict]):
    """Gradio calls this with the new message and the chat so far."""
    chunks = retrieve(message)
    prompt = f"<sources>\n{format_sources(chunks)}\n</sources>\n\nQuestion: {message}"
    text = ""
    with client.messages.stream(
        model=MODEL, max_tokens=4000, system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for piece in stream.text_stream:
            text += piece
            yield text                       # each yield replaces the bubble: streaming
    sources = "\n".join(f"- [{n}] {label(c)}" for n, c in enumerate(chunks, start=1))
    yield f"{text}\n\n**Sources**\n{sources}"


demo = gr.ChatInterface(respond, title="Ask the docs")

if __name__ == "__main__":
    demo.launch()
```

Run it and open the local address it prints, usually `http://127.0.0.1:7860`. Notice what you *didn't* write: no session state, no history loop, no message drawing. Gradio keeps the history for you and passes it to `respond` as a list of dictionaries with `role` and `content` keys, in the same shape as a model API's messages, except that in current Gradio each `content` is itself a list of blocks like `{"type": "text", "text": "..."}`.

Streaming works because `respond` is a **generator** (you met them in Pythonic Python). Each time it yields, Gradio replaces the assistant's bubble with the new value. So you yield the text so far, not just the newest piece. The last yield adds the list of sources.

Gradio also gives you an API for free. Every Gradio app exposes its functions as an HTTP endpoint, and the `gradio_client` package can call them from Python. That's handy when a teammate wants to script against your demo.

### Streamlit or Gradio

Both are free, open source and good. Pick by fit:

- **Streamlit** is a page you write top to bottom, so it's strong when the interface is more than a chat box: a sidebar of settings, a table of retrieved chunks with their scores, charts of your eval results, several pages. Internal tools and dashboards usually suit it best.
- **Gradio** is a function with a face, so it's strong when the interface *is* the model: type something in, get something out. Chat, image or audio demos, and anything you want to post on Hugging Face, where Gradio is the native format. When you need more layout than `ChatInterface` offers, Gradio's `gr.Blocks` lets you arrange components yourself.

For a chatbot, either works. If you're unsure, use the one your team already uses; the second one will take you an hour to learn.

### Sharing a demo

A prototype is only useful if the right people can open it. Two free hosts cover most needs:

- **Streamlit Community Cloud** deploys a Streamlit app straight from a GitHub repository.
- **Hugging Face Spaces** hosts Gradio apps, Streamlit apps and more, also from a Git repository.

Both had free tiers at the time of writing, and both put idle apps to sleep, so the first visit after a while is slow. Check the current limits before you rely on them.

Three rules apply wherever you host:

1. **Your API key goes in the host's secrets settings, never in the repository.** Both hosts have a secrets page whose top-level values reach your app as environment variables, so `anthropic.Anthropic()` finds the key exactly as it does on your laptop, as you learned in API Keys and Secrets.
1. **A public link spends your money.** Anyone who has it can make your app call the model on your key. Set a spending limit in your provider's console, keep `max_chars` on the input, and consider a per-session limit on questions (a counter in `st.session_state` is enough).
1. **Your index has to be there too.** The deployed app needs your documents and vectors. For a small demo, point it at a hosted Postgres from Deploying Your API, or commit a small prebuilt index.

### Prototype or React

So when is a Streamlit or Gradio app enough, and when do you build the React frontend? A prototype is enough when:

- the users are you, your team, or a handful of testers who know it's a demo;
- the goal is learning something (is this useful, are the answers good) rather than running a product;
- the interface is standard: a chat box, a form, a table, some charts;
- a slow first load and the library's look are acceptable.

You need a hand-built frontend, like the Next.js app from Next.js and the AI SDK, when:

- **the interface is the product.** Customers expect your brand, your layout and polished details such as clickable citation markers inside the answer text, and you'll fight the library for each one.
- **you need real accounts.** Login, per-user data and permissions belong in your FastAPI backend from User Accounts and Auth, with a frontend that calls it. Bolting them onto a prototype gets messy fast.
- **many people use it at once.** Streamlit reruns a Python script per interaction, on your server. That's fine for ten users and wasteful for ten thousand. A React page does its work in the user's browser and calls a backend you can scale.
- **you need fine control of streaming and state**: cancel buttons that stop the model call, optimistic updates, offline behavior, or several streams at once.
- **other apps need the same backend.** A mobile app or a partner integration needs an API, which a React frontend forces you to build anyway.

In practice the two aren't rivals; they're stages. You prototype in Streamlit to learn what to build, then build it properly. That's exactly how the Docs Chatbot UI project works: a quick prototype first, then a TypeScript and React interface with login as the real deliverable. And the prototype keeps earning its place afterwards, as the internal tool where your team reads traces and labels answers.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read Streamlit's [basic concepts](https://docs.streamlit.io/get-started/fundamentals/main-concepts) from its [documentation](https://docs.streamlit.io/), then the concept pages on [caching](https://docs.streamlit.io/develop/concepts/architecture/caching) and [session state](https://docs.streamlit.io/develop/concepts/architecture/session-state).
   - These explain the rerun model in more depth. Pay attention to when to use `st.cache_resource` versus `st.cache_data`.
1. Follow the [Streamlit conversational apps tutorial](https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps).
   - Build the echo bot, then the streaming chatbot. Use the `anthropic` SDK with the [cheap model](#/models) instead of the provider used in the tutorial; the structure is the same, and `stream.text_stream` replaces their stream.
   - Keep the [chat elements API reference](https://docs.streamlit.io/develop/api-reference/chat) open as you work.
1. Follow the [Gradio quickstart](https://www.gradio.app/guides/quickstart), then the [guide to creating a chatbot fast](https://www.gradio.app/guides/creating-a-chatbot-fast).
   - Read the sections on the chat function, the history format and streaming.
1. Read the deployment docs for [Streamlit Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud) and [Hugging Face Spaces](https://huggingface.co/docs/hub/spaces-overview), focusing on how each handles secrets and what the free tier includes today.
1. Practice: put a face on your Chat With Your Docs system.
   - Build `app.py` from this lesson over your own `retrieve` function, then make follow-up questions work: send the last few turns as earlier messages, and retrieve with the new question plus the previous one.
   - Add a thumbs-up and thumbs-down under each answer with [`st.feedback`](https://docs.streamlit.io/develop/api-reference/widgets/st.feedback), and append each rating with the question, answer and cited chunk IDs to a JSON Lines file.
   - Build the Gradio version too, and write three sentences comparing the two.
   - Port your `label.py` tool from Error Analysis and Labeling to Streamlit, with Pass and Fail buttons and a notes box, so someone who doesn't use a terminal can label your traces.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What question is a prototype interface for, and why build one before a React frontend?](#why-prototype-first)
- [What happens every time a user interacts with a Streamlit app, and what are session state and st.cache_resource for?](#how-streamlit-runs-your-script)
- [Why does the Streamlit chat page loop over the saved messages at the top of every run?](#a-chat-page-in-streamlit)
- [How does a Gradio chat function stream its answer?](#the-same-chatbot-in-gradio)
- [When would you choose Streamlit, and when Gradio?](#streamlit-or-gradio)
- [What three rules apply when you share a demo publicly?](#sharing-a-demo)
- [Name three signs that it's time to replace a prototype with a React frontend.](#prototype-or-react)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Streamlit's secrets management guide](https://docs.streamlit.io/develop/concepts/connections/secrets-management) shows how `secrets.toml` and Community Cloud's secrets page work.
- [Gradio's key features guide](https://www.gradio.app/guides/key-features) covers queuing, streaming, progress bars and the automatic API page.
- [Hugging Face's Gradio Spaces guide](https://huggingface.co/docs/hub/spaces-sdks-gradio) walks through deploying a Gradio app to a Space.
