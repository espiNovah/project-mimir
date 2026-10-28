### Introduction

Your Chat With Your Docs system answers with citations, and your RAG Eval Harness proves how well it works. Now you will give it a face that anyone can use from a link. In this project you will build a chat interface that streams answers, shows clickable citations that reveal the source passage, logs thumbs-up and thumbs-down feedback you can feed back into your evals, and is deployed somewhere public.

When you finish this project, you have completed the AI Engineering Core path: a working, measured, shareable AI application that you built from the ground up.

### Before you start

- Create a new GitHub repository called `mimir-docs-chatbot-ui`. Install your Chat With Your Docs project as a dependency so the UI calls the same retrieval and answer code.
- Choose your approach:
  - **Rapid UI:** Streamlit or Gradio, deployed to Streamlit Community Cloud or Hugging Face Spaces. This is the faster path.
  - **Custom UI:** a FastAPI backend with an SSE streaming endpoint and an HTML, CSS and JavaScript frontend, deployed to any host with a free tier. This is more work and teaches more.
- Check the current free tier of the host you pick, and how it handles secrets. Your model API key goes in the host's secrets settings, never in the repository.
- Your documents and vector index must be available to the deployed app. Either commit a small prebuilt index, or run ingestion when the app starts.

<div class="lesson-note lesson-note--critical" markdown="1">

#### A public link spends your money

Anyone with the link can make your app call a model on your API key. Before you share it, set a spending limit in your provider's console, cap the length of questions and answers, and consider a simple per-session limit on the number of questions.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Build a chat interface where a user types a question and sees the conversation history. The answer must stream token by token as the model generates it.
1. Show citations for every answer. Each citation must be clickable (or expandable) and reveal the source passage text and the document it came from. Answers where the system said "I don't know" should be clearly displayed as such.
1. Add thumbs-up and thumbs-down buttons to each answer, with an optional comment box. Log every rating with the question, the answer, the cited chunk IDs, a timestamp and a prompt or system version, to a database or a JSON Lines file that survives restarts of your app.
1. Write a small script that converts logged thumbs-down entries into candidate test cases in the format of your RAG Eval Harness dataset, so real user feedback can grow your eval set.
1. Handle errors in the interface: if retrieval or the model call fails, show a readable message instead of a stack trace, and keep the rest of the conversation intact.
1. Add basic cost protection: a maximum question length and a limit on questions per session.
1. Deploy the app to a public URL and confirm it works from a device other than your own computer.
1. Push your project to GitHub with a README that explains what it does, how to run it, and what you learned.

#### Extra credit

- Add a Stop button that cancels a streaming answer and stops the model call on the server.
- Show a simple admin page with feedback counts over time and the most recent thumbs-down answers.
- Get five people to use your app, collect their feedback, add at least five new cases to your eval set from it, and rerun your RAG Eval Harness.

</div>

### Submitting your work

A strong submission puts the live link at the top of the README, followed by a short GIF or video showing a streamed answer, a citation being opened, and a feedback click. Explain your architecture in a few lines, report your latest eval numbers from the RAG Eval Harness, and include a sample of the feedback log. If the free host puts the app to sleep when idle, say so, and how long the first load takes.
