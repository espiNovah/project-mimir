### Introduction

An API that forgets everything when it restarts is not very useful. The prompt library you built in FastAPI Basics kept its data in a Python dictionary, so every restart wiped it. You need to store results so users can come back for them, and so you can analyze what your model did later.

From this lesson on, the curriculum's default database is **PostgreSQL** (usually just "Postgres"): a free, open-source relational database that runs everywhere from your laptop to every major cloud. It speaks the SQL you learned in SQL Fundamentals, and later it will also store your vectors for RAG. To talk to it from Python you'll use **SQLModel**, a library from the creator of FastAPI that lets one Python class act as both a Pydantic model and a database table. In this lesson you will connect your API to Postgres and create, read, update and delete records.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What an ORM is and what it saves you from writing.
- How to start a local Postgres database.
- How to define tables as SQLModel classes, separate from your API input and output models.
- How engines and sessions connect your code to a database.
- How a `get_session` dependency gives each request its own session.
- How to create, read, update and delete records from FastAPI routes.
- What to store about every model call, and how to test against a throwaway database.

### What an ORM does

In SQL Fundamentals you wrote SQL strings by hand and passed values through `?` placeholders. That works, but in an application it gets repetitive: every table needs `INSERT`, `SELECT`, `UPDATE` and `DELETE` statements, and you have to convert every row into a Python object and back again.

An **ORM** (object-relational mapper) does that conversion for you. You describe each table once as a Python class. Then you create rows by creating objects, and you query by writing Python expressions that the ORM turns into safe, parameterized SQL. You still need to understand SQL, because the ORM is generating it and you will read it when something is slow or wrong, but you write far less of it.

SQLModel sits on top of two libraries you have already met or will meet constantly. **SQLAlchemy** is the mature, widely used ORM that does the actual database work. **Pydantic** does validation. A SQLModel class is both at once, which is why it fits so neatly with FastAPI.

### Starting Postgres

You need a Postgres server running on your computer. Pick one of these:

- **With Docker** (recommended, since you learned it in Docker and Docker Compose). Start a throwaway Postgres in one command:

  ```bash
  docker run --name mimir-postgres -d -p 5432:5432 \
    -e POSTGRES_USER=mimir -e POSTGRES_PASSWORD=mimir -e POSTGRES_DB=mimir \
    postgres:17
  ```

  If your project already has a `compose.yaml` with a `db` service from that lesson, `docker compose up -d db` does the same job. Stop the container with `docker stop mimir-postgres` and start it again with `docker start mimir-postgres`; your data survives until you remove the container.
- **Without Docker.** Install Postgres directly from the [official downloads page](https://www.postgresql.org/download/) (on a Mac, Postgres.app is the easiest option listed there). Then create a user and database named `mimir` with password `mimir` to match this lesson.

Your code finds the database through a **connection URL**, which packs the driver, user, password, host, port and database name into one string:

```text
postgresql+psycopg://mimir:mimir@localhost:5432/mimir
```

The `postgresql+psycopg` part tells SQLAlchemy to use the **psycopg** driver, the library that actually speaks Postgres's network protocol. Keep the URL in an environment variable called `DATABASE_URL`, as you learned in API Keys and Secrets. The password is a secret, and a deployed app will point at a different database without any code changes.

Add the libraries to your project from FastAPI Basics:

```bash
uv add sqlmodel "psycopg[binary]"
```

### Tables are SQLModel classes

A table is a SQLModel class with `table=True`. Put this in `models.py`:

```python
from sqlmodel import Field, SQLModel


class PromptBase(SQLModel):                    # fields shared by every model below
    name: str = Field(min_length=1, max_length=100, index=True)
    text: str = Field(min_length=1)


class Prompt(PromptBase, table=True):          # the database table
    id: int | None = Field(default=None, primary_key=True)


class PromptCreate(PromptBase):                # what a client sends to create
    pass


class PromptPublic(PromptBase):                # what the API returns
    id: int


class PromptUpdate(SQLModel):                  # what a client sends to edit
    name: str | None = Field(default=None, min_length=1, max_length=100)
    text: str | None = None
```

`Prompt` becomes a table called `prompt` with three columns. `primary_key=True` makes `id` the primary key, and because it defaults to `None`, Postgres assigns the next number when you insert a row. `index=True` adds an index on `name`, which speeds up lookups by name, as you saw in SQL Fundamentals.

The other three classes have no `table=True`, so they are plain data models, just like the Pydantic models in FastAPI Basics. This is the "separate what you store from what you expose" idea, now with a reason that bites: a table class will soon hold fields a client must never see or set, such as an owner ID or a raw model response. `PromptCreate` has no `id`, so a client can't choose one. `PromptPublic` has a required `id`, so responses always include it. `PromptUpdate` makes every field optional, so a client can change just one.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Table models don't validate

For speed, SQLModel skips validation when you create a `table=True` object directly. `Prompt(name="")` succeeds without complaint. Validate through a data model instead: let FastAPI check the request as a `PromptCreate`, then convert it with `Prompt.model_validate(prompt_create)`.

</div>

### Engines and sessions

Two objects connect your code to the database. The **engine** knows how to reach it: it holds the URL and a pool of open connections that it reuses, because opening a new connection for every query is slow. You create exactly one engine for your whole app.

A **session** is a unit of work. You `add` objects to it, and nothing reaches the database until you `commit`, at which point everything is saved together in one transaction, the all-or-nothing idea from SQL Fundamentals. After a commit, `refresh` reloads an object from the database so it picks up values the database generated, such as the new `id`. If something fails before you commit, the session discards your changes when it closes. Sessions are short-lived: one per request is the usual pattern.

### The get session dependency

In FastAPI Basics you used `Depends` to hand a summarizer to a route. A database session is handed out the same way. Put this in `database.py`:

```python
import os
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+psycopg://mimir:mimir@localhost:5432/mimir"
)
engine = create_engine(DATABASE_URL)            # one engine for the whole app


def get_session():
    with Session(engine) as session:            # opened when a request arrives
        yield session                           # the route runs here
                                                # closed when the response is done


SessionDep = Annotated[Session, Depends(get_session)]
```

`get_session` is a **generator dependency**: because it uses `yield` instead of `return`, FastAPI runs the code before `yield` when a request comes in, passes the session to your route, and runs the rest (here, closing the session as the `with` block ends) after the route finishes. Every request gets its own fresh session, and no request can forget to close one. `SessionDep` is just a short name for the annotated type, so routes can write `session: SessionDep`.

### A complete CRUD walkthrough

**CRUD** stands for create, read, update and delete, the four basic things you do with stored records. Here is the prompt library again, now backed by Postgres. Replace `main.py`:

```python
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from sqlmodel import SQLModel, select

from database import SessionDep, engine
from models import Prompt, PromptCreate, PromptPublic, PromptUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)       # create missing tables at startup
    yield


app = FastAPI(title="Prompt Library", lifespan=lifespan)


@app.post("/prompts", status_code=201, response_model=PromptPublic)
def create_prompt(prompt: PromptCreate, session: SessionDep):
    db_prompt = Prompt.model_validate(prompt)  # validated data -> table object
    session.add(db_prompt)                     # stage the INSERT
    session.commit()                           # run it in a transaction
    session.refresh(db_prompt)                 # load the new id
    return db_prompt


def get_or_404(session: SessionDep, prompt_id: int) -> Prompt:
    prompt = session.get(Prompt, prompt_id)    # look up by primary key
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt


@app.get("/prompts/{prompt_id}", response_model=PromptPublic)
def read_prompt(prompt_id: int, session: SessionDep):
    return get_or_404(session, prompt_id)


@app.get("/prompts", response_model=list[PromptPublic])
def list_prompts(session: SessionDep, limit: Annotated[int, Query(ge=1, le=100)] = 10):
    statement = select(Prompt).order_by(Prompt.id).limit(limit)
    return session.exec(statement).all()


@app.patch("/prompts/{prompt_id}", response_model=PromptPublic)
def update_prompt(prompt_id: int, changes: PromptUpdate, session: SessionDep):
    prompt = get_or_404(session, prompt_id)
    prompt.sqlmodel_update(changes.model_dump(exclude_unset=True))
    session.commit()                           # the session already tracks it
    session.refresh(prompt)
    return prompt


@app.delete("/prompts/{prompt_id}", status_code=204)
def delete_prompt(prompt_id: int, session: SessionDep) -> None:
    prompt = get_or_404(session, prompt_id)
    session.delete(prompt)
    session.commit()
```

The pieces worth slowing down for:

- **`lifespan`** runs once when the server starts. (FastAPI's own SQL tutorial uses `@app.on_event("startup")` for this, an older style that FastAPI now marks as deprecated.) `create_all` creates any tables that don't exist yet. It never changes a table that already exists, so if you add a column later, `create_all` won't add it. Migrations with Alembic, two lessons from now, solves that properly.
- **`response_model=PromptPublic`** is needed here because the routes return `Prompt` table objects, not `PromptPublic` ones. FastAPI reads the fields it needs from the table object and sends only those.
- **Create** follows a fixed rhythm: validate, `add`, `commit`, `refresh`, return. You'll write it many times.
- **Read one** uses `session.get(Model, id)`, the fastest lookup there is. It returns `None` when the row doesn't exist, so the small `get_or_404` helper turns that into a `404` for the read, update and delete routes alike.
- **Read many** builds a `select` statement and runs it with `session.exec(...).all()`. Always cap `limit`, so no client can ask for the whole table at once. To return later pages, add an `offset: int = 0` parameter and chain `.offset(offset)` onto the statement. That's **pagination**: returning a page of rows at a time. `order_by` matters too, because without it a database may return rows in any order, and the pages would shuffle.
- **Update** uses `PATCH`, the HTTP method for changing part of a record. `exclude_unset=True` keeps only the fields the client actually sent, so `{"text": "new"}` changes the text and leaves the name alone. `sqlmodel_update` copies those values onto the object. There's no `add` this time: the object came from this session, so the session already tracks it and `commit` saves the change. (FastAPI's tutorial calls `add` here anyway, which is harmless.)
- **Delete** returns `204 No Content`, the usual code for "done, nothing to send back."

Run `uv run fastapi dev main.py`, create a few prompts at `/docs`, stop the server and start it again. Your prompts are still there. To see the raw rows, open `psql`, Postgres's command-line client, inside the container with `docker exec -it mimir-postgres psql -U mimir` (or `docker compose exec db psql -U mimir` if you used Compose) and run `SELECT * FROM prompt;`. Type `\q` to quit.

### Storing model outputs

For AI apps, what you store about each model call matters as much as the answer itself. Save the input, the raw output, the parsed result, the model name, the prompt version, the token counts, a timestamp and a status. You will need every one of them later: to debug a bad answer, to compute what each request cost, and to build eval datasets from real traffic. Here is a table for the summaries in this lesson's practice:

```python
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime
from sqlmodel import Field, SQLModel


class Summary(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    input_text: str
    summary: str | None = None              # None when the call failed
    model: str
    prompt_version: str
    input_tokens: int = 0
    output_tokens: int = 0
    status: str = Field(default="done", index=True)
    error: str | None = None
    raw_response: dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), sa_type=DateTime(timezone=True)
    )
```

Two columns use `sa_type` to pick a specific SQLAlchemy column type. `raw_response` is a **JSON column**: a nested dictionary stored in one column, which is the simplest way to keep a full model response or a nested extraction result. That is fine for most projects. Split it into proper tables only when you find yourself filtering on fields inside it often. `created_at` uses a time-zone-aware timestamp, so times stay correct when your server and your users are in different zones.

### Queries are Python

`select(Prompt)` builds a `SELECT` statement, and you narrow it with methods that mirror SQL clauses. For example, inside a route that has a `session`, this finds the newest failed summaries and a prompt by name:

```python
from sqlmodel import col, select

newest_failures = select(Summary).where(Summary.status == "failed").order_by(
    col(Summary.created_at).desc()
)
failed = session.exec(newest_failures).all()

first_match = session.exec(select(Prompt).where(Prompt.name == "summarize")).first()
```

`Summary.status == "failed"` looks like a comparison, but on a table class it builds a SQL condition. `.all()` returns a list of objects, and `.first()` returns one object or `None`. SQLModel turns the values into parameters, exactly like the `?` placeholders in SQL Fundamentals, so a user typing `' OR '1'='1` into a search box can't change your query. `col()` wraps a column when you need a column method such as `.desc()` and want your editor's type checker to stay happy.

### Testing with a throwaway database

Tests should never touch your real data. Because the session comes from a dependency, a test can override it to use a fresh database every time. The quickest option is an in-memory SQLite database, which needs nothing running and vanishes when the test ends. Save this as `test_main.py`:

```python
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from database import get_session
from main import app


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",                                    # in memory, gone after the test
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,                           # share one connection
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        app.dependency_overrides[get_session] = lambda: session
        yield TestClient(app)
    app.dependency_overrides.clear()


def test_create_read_update_delete(client):
    body = {"name": "summarize", "text": "Summarize: {text}"}
    created = client.post("/prompts", json=body)
    assert created.status_code == 201
    prompt_id = created.json()["id"]

    updated = client.patch(f"/prompts/{prompt_id}", json={"text": "TL;DR: {text}"})
    assert updated.json() == {"id": prompt_id, **body, "text": "TL;DR: {text}"}

    assert client.delete(f"/prompts/{prompt_id}").status_code == 204
    assert client.get(f"/prompts/{prompt_id}").status_code == 404
```

The test never starts the lifespan (that only happens when you use `TestClient` in a `with` block), so it doesn't need Postgres running at all.

<div class="lesson-note lesson-note--tip" markdown="1">

#### SQLite in tests, Postgres in production

SQLite and Postgres agree on almost everything an app like this does, but not on everything. They differ on JSON operators, full-text search and some type handling. Once your app relies on a Postgres-only feature, point the test fixture at a separate test database instead, such as `postgresql+psycopg://mimir:mimir@localhost:5432/mimir_test`, and call `SQLModel.metadata.drop_all(engine)` before `create_all` so each test run starts clean.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [SQLModel tutorial](https://sqlmodel.tiangolo.com/tutorial/) from its introduction through the sections on creating tables, creating rows, reading data, filtering with `where`, updating and deleting. It explains each operation in this lesson step by step and shows the SQL it generates.
   - The tutorial uses SQLite so you don't need a server. Everything carries over to Postgres by changing the URL.
   - Skip the relationship attributes chapters for now unless your project needs them.
1. Work through [FastAPI's SQL databases tutorial](https://fastapi.tiangolo.com/tutorial/sql-databases/), which uses SQLModel.
   - Build both versions on the page: the single model version and the improved version with multiple models.
   - When it works, switch it from SQLite to your Postgres URL.
1. Read the "FastAPI and Pydantic" and "Testing" parts of the [SQLModel tutorial](https://sqlmodel.tiangolo.com/tutorial/) when you reach them, and note how the tests use an in-memory SQLite database and `dependency_overrides`.
1. Practice: add a Postgres database to your summarizer API from [FastAPI Basics](#/lessons/core/fastapi-basics).
   - Store every summary in a table like `Summary` above, with its input, output, model name, prompt version and token counts. Store failed calls too, with their error.
   - Add `GET /summaries/{id}` and `GET /summaries?limit=10`, newest first, and return `404` for unknown IDs.
   - Write tests that use a fresh in-memory database and your fake summarizer. Check that a summary is stored, that it can be fetched back, and that an unknown ID returns `404`.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What does an ORM save you from writing, and why do you still need to know SQL?](#what-an-orm-does)
- [What is the difference between a class with table=True and one without, and why have both?](#tables-are-sqlmodel-classes)
- [What is the difference between an engine and a session?](#engines-and-sessions)
- [How does the get_session dependency make sure every request's session gets closed?](#the-get-session-dependency)
- [Why do you call commit and then refresh after adding a new object?](#a-complete-crud-walkthrough)
- [What should you store about every model call, and why?](#storing-model-outputs)
- [How can your tests use a database without touching your real data?](#testing-with-a-throwaway-database)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The official PostgreSQL tutorial](https://www.postgresql.org/docs/current/tutorial.html) is a short, readable introduction to Postgres itself, including `psql`.
- [SQLAlchemy's ORM quick start](https://docs.sqlalchemy.org/en/21/orm/quickstart.html) shows the library underneath SQLModel. It's useful when you need a feature SQLModel doesn't wrap.
