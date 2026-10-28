<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

So far your programs have run in a terminal. To let a website, a mobile app or another service use your AI feature, you need to put it behind a web API. FastAPI is the most popular Python framework for this in AI work: it uses type hints and Pydantic models (which you already know) to validate requests, and it generates interactive documentation for free. In this lesson you will build a small API you can call from a browser and from code.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What a web API is, from the server's side.
- How to define routes with path operations.
- How path parameters, query parameters and request bodies work.
- How FastAPI uses Pydantic models to validate input and shape output.
- How to return errors with the right status codes.
- How the automatic OpenAPI docs work.
- How to test an API with TestClient.

### Key ideas

- **An API is a set of URLs that accept requests and return data.** In the Working with APIs lesson you were the client. Now you are the server: you decide which paths exist, which HTTP methods they accept (`GET` to read, `POST` to create) and what they return, usually JSON.
- **A route is a decorated function.** `@app.get("/items/{item_id}")` above a function tells FastAPI to call it for that URL. Function parameters become path parameters (in the URL path) or query parameters (after `?`), and their type hints are enforced.
- **Request bodies are Pydantic models.** Declare a parameter as `req: ExtractRequest` and FastAPI parses the JSON body, validates it, and returns a clear `422` error if it does not match. Use `response_model` to control exactly what goes back to the client.
- **Status codes communicate outcomes.** `200` means OK, `201` means created, `404` means not found, `422` means invalid input, and `500` means the server broke. Raise `HTTPException(status_code=404, detail="...")` to return an error on purpose.
- **Docs are generated for you.** FastAPI builds an OpenAPI description of your API and serves interactive docs at `/docs`, where you can try every endpoint in the browser. Good type hints and docstrings make these docs better.
- **Async is optional but useful.** You can write routes with `def` or `async def`. Model API calls spend most of their time waiting on the network, so `async def` with an async client lets one server handle many requests at once, building on the Async Basics lesson.
- **Test without a running server.** FastAPI's `TestClient` calls your app directly from pytest. In tests, replace the real model call with a fake one so tests are fast, free and deterministic.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Python types intro](https://fastapi.tiangolo.com/python-types/) in the FastAPI docs for a quick refresher on type hints as FastAPI uses them.
1. Work through the [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/), typing every example yourself.
   - Do the pages from "First Steps" through "Request Body," then "Response Model," "Handling Errors" and "Testing."
   - Run the server with `uv run fastapi dev main.py` and try each endpoint at `/docs`.
1. Read [FastAPI's testing guide](https://fastapi.tiangolo.com/tutorial/testing/) again closely, and write tests for the endpoints you built.
1. Practice: build a small API with a `POST /summarize` endpoint that accepts `{"text": "...", "max_sentences": 3}`, calls a model to summarize the text, and returns `{"summary": "...", "input_tokens": 123}`. Reject empty text and `max_sentences` above 10 using Pydantic constraints. Write tests that use a fake summarizer instead of the real API.

</div>
