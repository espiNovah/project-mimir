### Introduction

So far your programs have run in a terminal. To let a website, a mobile app or another service use your AI feature, you need to put it behind a web API. FastAPI is the most popular Python framework for this in AI work: it uses type hints and Pydantic models (which you already know) to validate requests, and it generates interactive documentation for free. In this lesson you will build a small API you can call from a browser and from code, and you will test it without ever starting a server.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What a web API is, from the server's side.
- How to define routes with path operations.
- How path parameters, query parameters and request bodies work.
- How FastAPI uses Pydantic models to validate input and shape output.
- How to return errors with the right status codes.
- How the automatic OpenAPI docs work.
- How to test an API with TestClient, using a fake instead of a real model.

### From client to server

In the Working with APIs lesson you were the **client**: you sent an HTTP request to someone else's URL and read the JSON that came back. Now you are the **server**. A web API is a set of URLs that accept requests and return data, and you get to decide which URLs exist, which HTTP methods each one accepts and what it returns.

Recall the two methods you will use most:

- `GET` reads something. `GET /prompts/3` means "give me prompt number 3." A `GET` should never change anything on the server.
- `POST` creates something or triggers an action. `POST /prompts` with a JSON body means "store this new prompt." `POST /summarize` means "run a summary on this text."

The combination of a method and a path, such as `GET /prompts/{prompt_id}`, is called a **route**, and FastAPI calls the function that handles it a **path operation**. When a request arrives, FastAPI finds the matching route, turns the URL and the body into Python values, calls your function, and turns whatever the function returns back into JSON.

Every response also carries a **status code**, a three-digit number that tells the client how things went before it even looks at the body. You will mostly use these:

| Code | Meaning | When you use it |
| --- | --- | --- |
| `200` | OK | A normal successful read or action |
| `201` | Created | A `POST` that stored something new |
| `404` | Not Found | The client asked for an ID that doesn't exist |
| `422` | Unprocessable Content | The request was the wrong shape: a missing field, a wrong type, a value out of range |
| `500` | Internal Server Error | Your code crashed. You never return this on purpose |

Codes in the 400s mean "the client did something wrong." Codes in the 500s mean "the server did something wrong." Getting this right matters because the client's code, which might be your own frontend or another team's service, decides what to do based on the number.

### Setting up the project

Create a project and add FastAPI with its standard extras, which include the `fastapi` command, the Uvicorn web server and HTTPX (needed for testing):

```bash
uv init prompt-library
cd prompt-library
uv add "fastapi[standard]"
uv add --dev pytest
```

The smallest possible app is three lines plus a route. Put this in `main.py`:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

Start the development server:

```bash
uv run fastapi dev main.py
```

Open `http://127.0.0.1:8000/health` in your browser and you will see `{"status":"ok"}`. The `@app.get("/health")` line is a **decorator**: it registers the function below it as the handler for `GET /health`. The function itself is ordinary Python. FastAPI took the dictionary you returned and converted it to JSON. `fastapi dev` also watches your files and restarts the server whenever you save, so leave it running while you work. A `/health` route like this one looks trivial, but real deployments use it to check that your service is alive.

### A complete walkthrough

Here is a small but realistic API: a library where you can store prompts and fetch them back. Prompts are kept in a Python dictionary for now, which means they vanish when the server restarts. You will fix that in Persisting Data with Postgres. Replace `main.py` with this:

```python
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Prompt Library")


class PromptCreate(BaseModel):            # what a client sends
    name: str = Field(min_length=1, max_length=100)
    text: str = Field(min_length=1)
    tags: list[str] = []


class PromptPublic(BaseModel):            # what we send back
    id: int
    name: str
    text: str
    tags: list[str]


prompts: dict[int, PromptPublic] = {}     # a stand-in for a database


@app.post("/prompts", status_code=201)
def create_prompt(prompt: PromptCreate) -> PromptPublic:
    """Store a new prompt and return it with its ID."""
    new_id = len(prompts) + 1
    stored = PromptPublic(id=new_id, **prompt.model_dump())
    prompts[new_id] = stored
    return stored


@app.get("/prompts/{prompt_id}")
def read_prompt(prompt_id: int) -> PromptPublic:
    """Fetch one prompt by its ID."""
    if prompt_id not in prompts:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompts[prompt_id]


@app.get("/prompts")
def list_prompts(
    tag: str | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> list[PromptPublic]:
    """List prompts, optionally only those with a given tag."""
    matches = [p for p in prompts.values() if tag is None or tag in p.tags]
    return matches[:limit]
```

Walk through it from top to bottom:

- **Two models, two jobs.** `PromptCreate` describes the JSON a client must send. `PromptPublic` describes what the API returns, including the `id` the server assigns. Keeping them separate means a client can't choose its own ID, and later you can add internal fields to the stored data without leaking them.
- **`@app.post("/prompts", status_code=201)`** registers a `POST` route and changes the success code from the default `200` to `201 Created`.
- **`prompt: PromptCreate`** is a **request body** parameter. Because its type is a Pydantic model, FastAPI reads the request's JSON body, validates it against the model and hands your function a ready-made `PromptCreate` object.
- **`-> PromptPublic`** is the return type, and FastAPI uses it as the **response model**: it validates what you return and sends only the fields declared on `PromptPublic`.
- **`{prompt_id}` in the path** plus a matching function parameter, `prompt_id: int`, makes a **path parameter**. The type hint is enforced, so `GET /prompts/abc` is rejected before your code runs.
- **`raise HTTPException(...)`** stops the function and sends an error response with the status code and `detail` message you choose.
- **`tag` and `limit`** are not in the path, so FastAPI treats them as **query parameters**, the part of a URL after `?`. `GET /prompts?tag=writing&limit=5` calls `list_prompts(tag="writing", limit=5)`. Giving them defaults makes them optional.
- **The docstrings** show up as descriptions in the generated docs.

Try it from a second terminal while `fastapi dev` is running:

```bash
curl -X POST http://127.0.0.1:8000/prompts \
  -H "content-type: application/json" \
  -d '{"name": "summarize", "text": "Summarize this in 3 sentences: {text}", "tags": ["writing"]}'
```

### Validation and the 422 error

The biggest gift FastAPI gives you is that bad input never reaches your function. Send a prompt with an empty name:

```bash
curl -X POST http://127.0.0.1:8000/prompts \
  -H "content-type: application/json" \
  -d '{"name": "", "text": "hi"}'
```

You get a `422` and a body explaining exactly what was wrong (shortened here):

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "name"],
      "msg": "String should have at least 1 character",
      "input": ""
    }
  ]
}
```

`loc` says where the problem is (in the body, field `name`), and `msg` says what it is. This is the same Pydantic validation you learned in JSON Schema and Pydantic, applied at the edge of your app. The `Field(min_length=1)` constraint did the work. Constraints like `ge` (greater than or equal) and `le` (less than or equal) work the same way on numbers.

Query and path parameters get validated too. A plain type hint like `prompt_id: int` checks the type. To add constraints to a query parameter, wrap its type in `Annotated` with `Query(...)`, as `limit` does in the walkthrough. `GET /prompts?limit=500` now returns a `422`, which protects your server from a client asking for a million rows.

The rule of thumb: **declare what valid input looks like, and let FastAPI reject everything else.** Every check you express as a type or constraint is one you don't have to write, test and remember by hand.

### Response models and status codes

The response model is your output contract. If `read_prompt` accidentally returned an object with an extra `owner_email` field, FastAPI would drop it, because `PromptPublic` doesn't declare it. If it returned something missing a required field, FastAPI would raise an error instead of sending half-finished data. You can also declare the response model in the decorator, as in `@app.get("/prompts/{prompt_id}", response_model=PromptPublic)`. That form is useful when the function returns something other than the declared type, such as a dictionary or a database object, and you will see it in older tutorials. Either way, the effect is the same.

For errors, choose the code that tells the client what to do next. A `404` says "that ID doesn't exist, stop asking." A `422` says "fix your request and try again." A `500` is what happens when your code raises an exception you didn't catch. FastAPI turns it into a generic error so it doesn't leak your stack trace, but it means you have a bug to find in your logs. When a model call fails in a way you expected, such as a timeout or invalid output after every retry, catch it and raise a deliberate `HTTPException` (often `502` or `503`, meaning a service your server depends on failed) instead of letting it surface as a `500`.

### The automatic docs

With the server running, open `http://127.0.0.1:8000/docs`. FastAPI has generated an interactive page listing every route, its parameters, its request and response models and their constraints. Click a route, then **Try it out**, fill in the fields and press **Execute** to send a real request.

This page is built from an **OpenAPI** description of your API: a standard JSON document, served at `/openapi.json`, that lists every endpoint and schema. Other tools can read it to generate client libraries, and agent frameworks can turn it into tool definitions. You got it for free by writing type hints, Pydantic models and docstrings. The better those are, the better your docs. That's another reason to give every route a docstring and every field a sensible constraint.

### Sync or async routes

You can write a route with `def` or with `async def`. With plain `def`, FastAPI runs your function in a pool of worker threads, so a slow function doesn't freeze the whole server, but each waiting request occupies a thread. With `async def`, the function runs on the event loop you met in Async Basics, and while it `await`s a network call, the server is free to handle other requests.

Model API calls spend almost all of their time waiting for the network, so an AI endpoint is a natural fit for `async def` plus an async client, such as `anthropic.AsyncAnthropic()` or `httpx.AsyncClient()`. There is one trap: inside an `async def` route, never call something slow and blocking, such as the synchronous `anthropic.Anthropic()` client or `time.sleep()`. That blocks the event loop and stalls every other request. If a library you need only has a blocking interface, use a plain `def` route. When in doubt, plain `def` is the safe default.

### Testing with TestClient

You already know pytest. FastAPI's `TestClient` lets pytest call your app directly, with no server running and no network involved. It has the same `get` and `post` methods as HTTPX, and it returns responses with the same `status_code` and `.json()`. Save this as `test_main.py`:

```python
import pytest
from fastapi.testclient import TestClient

from main import app, prompts

client = TestClient(app)


@pytest.fixture(autouse=True)
def empty_library():
    prompts.clear()          # every test starts with no prompts


def test_create_then_read():
    body = {"name": "summarize", "text": "Summarize: {text}", "tags": ["writing"]}
    created = client.post("/prompts", json=body)
    assert created.status_code == 201
    assert created.json()["id"] == 1

    fetched = client.get("/prompts/1")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "summarize"


def test_unknown_id_returns_404():
    response = client.get("/prompts/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Prompt not found"}


@pytest.mark.parametrize("body", [{"name": "", "text": "hi"}, {"name": "x"}])
def test_invalid_body_returns_422(body):
    assert client.post("/prompts", json=body).status_code == 422


def test_limit_is_capped():
    assert client.get("/prompts?limit=500").status_code == 422
```

Run it with `uv run pytest`. The `autouse=True` fixture runs before every test without being requested, so tests can't leak prompts into each other. Notice what the tests cover: the happy path, a missing ID, and bad input, both an empty name and a missing field. Testing the error cases matters as much as testing success, because clients depend on getting the right status code.

### Faking the model in tests

Your real endpoints will call a model, and tests that call a real model are slow, cost money and give different answers each run. The fix is the **dependency injection** idea from Testing with pytest: instead of calling the model directly inside the route, ask for it as a parameter, and let tests pass in a fake.

FastAPI has this built in. `Depends` tells FastAPI to call a function and pass its result into your route, and `app.dependency_overrides` lets a test swap that function for another:

```python
from typing import Annotated, Callable

from fastapi import Depends

from llm import summarize_with_model   # your real model call, in your own module

Summarizer = Callable[[str, int], str]


def get_summarizer() -> Summarizer:
    return summarize_with_model


@app.post("/summarize")
def summarize(
    req: SummarizeRequest,
    summarizer: Annotated[Summarizer, Depends(get_summarizer)],
) -> SummarizeResponse:
    return SummarizeResponse(summary=summarizer(req.text, req.max_sentences))


# In test_main.py:
def fake_summarizer(text: str, max_sentences: int) -> str:
    return "A short summary."


app.dependency_overrides[get_summarizer] = lambda: fake_summarizer
```

In production, FastAPI calls `get_summarizer()` and your route gets the real function. In tests, it calls the override instead and your route gets the fake, which returns instantly and always says the same thing. The route's code doesn't change at all. You will use exactly this mechanism in the next lessons to hand each request a database session, and later to check API keys.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Python types intro](https://fastapi.tiangolo.com/python-types/) in the FastAPI docs for a quick refresher on type hints as FastAPI uses them. Pay attention to the section on `Annotated`, which FastAPI uses everywhere.
1. Work through the [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/), typing every example yourself. It covers each piece of this lesson in more depth, with many more variations.
   - Do the pages from "First Steps" through "Request Body," then "Response Model," "Handling Errors" and "Testing."
   - Run the server with `uv run fastapi dev main.py` and try each endpoint at `/docs`.
1. Read [FastAPI's testing guide](https://fastapi.tiangolo.com/tutorial/testing/) again closely, and write tests for the endpoints you built. Then read [Testing Dependencies with Overrides](https://fastapi.tiangolo.com/advanced/testing-dependencies/), which shows the `dependency_overrides` pattern from this lesson.
1. Practice: build a small API with a `POST /summarize` endpoint that accepts `{"text": "...", "max_sentences": 3}`, calls a model to summarize the text, and returns `{"summary": "...", "input_tokens": 123}`.
   - Reject empty text and `max_sentences` above 10 using Pydantic constraints.
   - Use the [cheap model](#/models) for the real call, and make the summarizer a dependency.
   - Write tests that use a fake summarizer instead of the real API, covering a successful summary and both kinds of invalid input.
   - Keep this project. You will add a database to it in Persisting Data with Postgres.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What is the difference between a 404, a 422 and a 500 status code?](#from-client-to-server)
- [How does FastAPI decide whether a function parameter is a path parameter, a query parameter or a request body?](#a-complete-walkthrough)
- [What happens when a client sends a request body that doesn't match your Pydantic model?](#validation-and-the-422-error)
- [Why use separate models for what a client sends and what your API returns?](#a-complete-walkthrough)
- [Where do FastAPI's interactive docs come from, and how do you make them better?](#the-automatic-docs)
- [When should a route use async def, and what must you never do inside one?](#sync-or-async-routes)
- [How do you test a route that calls a model without calling the real model?](#faking-the-model-in-tests)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [FastAPI's Dependencies tutorial](https://fastapi.tiangolo.com/tutorial/dependencies/) explains `Depends` in full, including dependencies that depend on other dependencies.
- [Concurrency and async / await](https://fastapi.tiangolo.com/async/) in the FastAPI docs is a friendly, detailed explanation of when to use `async def` and why.
- [Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/) shows how to split an API across several files with routers once `main.py` gets long.
