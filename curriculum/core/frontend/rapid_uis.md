<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Writing HTML, CSS and JavaScript by hand gives you full control, but sometimes you just need a working interface by this afternoon. Streamlit and Gradio are Python libraries that build web interfaces from plain Python code, with ready-made chat components. They are the standard way AI engineers build demos, internal tools and prototypes. This lesson shows how both work and how to choose between them.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What Streamlit and Gradio are and how they differ.
- How Streamlit's rerun model and session state work.
- How to build a chat interface with Streamlit's chat elements.
- How to build a chat interface with Gradio.
- How to stream model output in both.
- How to deploy a demo for free.

### Key ideas

- **Both turn Python into a web app.** You write Python functions and widget calls; the library generates the page, the server and the browser code. You never touch JavaScript, which is ideal for demos and internal tools.
- **Streamlit reruns your script top to bottom.** Every time a user interacts with a widget, Streamlit runs your whole script again. That is simple to reason about, but means anything you want to remember between interactions, such as the chat history, must go in `st.session_state`. Use caching (`st.cache_resource`) for expensive setup like loading an embedding model.
- **Streamlit has chat building blocks.** `st.chat_input` gives you a message box, `st.chat_message` renders a message bubble, and `st.write_stream` displays a stream of text as it arrives. A full chat app is about 30 lines.
- **Gradio is built around functions.** You wrap a Python function in an interface, and Gradio creates inputs and outputs for it. `gr.ChatInterface` turns a function that takes a message and history into a full chat app, and a function that `yield`s partial text streams automatically.
- **Pick by fit, not fashion.** Streamlit is strong for dashboards and multi-part apps with sidebars, charts and tables. Gradio is strong for model demos, has deep Hugging Face integration, and can expose your app as an API. Both are free and open source.
- **Free hosting makes demos shareable.** Streamlit Community Cloud deploys Streamlit apps from a GitHub repo, and Hugging Face Spaces hosts Gradio and Streamlit apps. Both have free tiers at the time of writing; check current limits, and store your API key in the platform's secrets settings, never in the repo.
- **Know when to graduate.** These libraries trade control for speed. When you need custom layouts, fine-grained streaming or many simultaneous users, a hand-built frontend talking to a FastAPI backend is the next step.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Skim the [Streamlit documentation home](https://docs.streamlit.io/) and read the "Get started" fundamentals.
   - Focus on the basic concepts page that explains the rerun model, and on session state and caching.
1. Follow the [Streamlit conversational apps tutorial](https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps).
   - Build the echo bot, then the streaming chatbot. Use the `anthropic` SDK with the [cheap model](#/models) instead of the provider used in the tutorial; the structure is the same.
   - Keep the [chat elements API reference](https://docs.streamlit.io/develop/api-reference/chat) open as you work.
1. Follow the [Gradio quickstart](https://www.gradio.app/guides/quickstart), then the [guide to creating a chatbot fast](https://www.gradio.app/guides/creating-a-chatbot-fast).
   - Build a streaming `gr.ChatInterface` that calls a model.
1. Read the deployment docs for [Streamlit Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud) and [Hugging Face Spaces](https://huggingface.co/docs/hub/spaces-overview), focusing on how each handles secrets.
1. Practice: build a minimal front end for your Messy-Text Extractor in both Streamlit and Gradio. Paste text, click a button, see the extracted fields as a table and the raw JSON. Write three sentences comparing the experience of building each.

</div>
