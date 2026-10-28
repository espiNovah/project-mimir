<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

An API that forgets everything when it restarts is not very useful. You need to store results so users can come back for them, and so you can analyze what your model did later. SQLModel is a library from the creator of FastAPI that lets one Python class act as both a Pydantic model and a database table. In this lesson you will connect your API to a database and store and retrieve records.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What an ORM is and what it saves you from writing.
- How to define tables as SQLModel classes.
- How engines and sessions connect your code to a database.
- How to create, read, update and delete records from Python.
- How to separate database models from API input and output models.
- How to use a database session inside FastAPI routes.

### Key ideas

- **An ORM maps classes to tables.** An *object-relational mapper* lets you work with Python objects instead of writing SQL strings. SQLModel is built on SQLAlchemy (the underlying ORM) and Pydantic, so the same class validates data and stores it.
- **`table=True` makes a model a table.** `class Extraction(SQLModel, table=True)` with an `id: int | None = Field(default=None, primary_key=True)` defines a table. Without `table=True`, the class is a plain data model you use for requests and responses.
- **Engines and sessions.** The *engine* knows how to reach the database (a SQLite file URL during development, a PostgreSQL URL in production). A *session* is a unit of work: you `add` objects, `commit` to save them, and `refresh` to load generated values such as the new `id`.
- **Queries are Python.** `session.exec(select(Extraction).where(Extraction.status == "done"))` builds safe, parameterized SQL for you, so you get SQL injection protection without thinking about it.
- **Separate what you store from what you expose.** Use distinct models such as `ExtractionCreate` (what a client sends), `Extraction` (the table) and `ExtractionPublic` (what you return). This keeps secrets and internal fields out of responses.
- **Store model outputs with context.** For AI apps, save the input, the raw output, the parsed result, the model name, the prompt version, token counts, timestamps and status. You will need all of these to debug, compute costs and build evals later.
- **Structured results can live in JSON columns.** A nested extraction result can be stored as JSON in a single column. This is simple and fine for most projects; split it into proper tables only when you need to query inside it often.
- **Dependencies hand out sessions.** In FastAPI, a dependency function that yields a session gives each request its own session and closes it afterward. In tests you can override it to use a separate test database.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [SQLModel tutorial](https://sqlmodel.tiangolo.com/tutorial/) from its introduction through the sections on creating tables, creating rows, reading data, filtering with `where`, updating and deleting.
   - Skip the relationship attributes chapters for now unless your project needs them.
1. Work through [FastAPI's SQL databases tutorial](https://fastapi.tiangolo.com/tutorial/sql-databases/), which uses SQLModel.
   - Build both versions on the page: the single model version and the improved version with multiple models.
1. Read the "FastAPI and Pydantic" and "Testing" parts of the [SQLModel tutorial](https://sqlmodel.tiangolo.com/tutorial/) when you reach them, and note how the tests use an in-memory SQLite database.
1. Practice: add a database to your summarizer API from the last lesson. Store every summary with its input, output, model name and token counts. Add `GET /summaries/{id}` and `GET /summaries?limit=10`, return `404` for unknown IDs, and write tests that use a fresh in-memory database.

</div>
