### Introduction

In Persisting Data with Postgres, one line created your tables: `SQLModel.metadata.create_all(engine)`. It's perfect on day one. But apps change. Next week you'll want a `description` column on prompts, then a `user_id` on every record once you add accounts, then a new table for jobs. `create_all` can't help with any of that, because it only creates tables that don't exist yet. It never changes a table that's already there.

A **migration** is a small, versioned script that changes a database's schema (its tables, columns, indexes and constraints) from one version to the next, and can usually undo that change too. Migrations live in your Git repository next to your code, so every copy of your database (your laptop, a teammate's laptop, the deployed one) can be brought to exactly the same shape by running the same scripts in the same order. **Alembic**, written by the author of SQLAlchemy, is the standard migration tool for SQLAlchemy and SQLModel apps. In this lesson you'll set it up for the prompt library from the last lesson, change a table that already holds data, and run migrations in Docker Compose and on deploy.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why `create_all` stops being enough once real data exists.
- How to set up Alembic so it knows about your SQLModel tables.
- How autogenerate writes a migration for you, and why you must review it.
- How to move a database forward and back with upgrade and downgrade.
- How to write a data migration that fills in values for existing rows.
- How to run migrations in Docker Compose and as part of a deploy.
- The mistakes that bite most people, and how to avoid them.

### Why create all is not enough

Suppose your deployed prompt library has 500 prompts in it, and you add a field to the `Prompt` class. Restart the app, and `create_all` sees that a table called `prompt` already exists, so it does nothing. Your code now expects a column the database doesn't have, and the first query fails with `column prompt.description does not exist`.

You could fix it by hand: open `psql` and type `ALTER TABLE prompt ADD COLUMN description VARCHAR;`, the SQL command for changing an existing table. That works once, on one database. Now you have to remember to type the same thing on your teammate's database, the test database and the production one, in the right order, without typos, forever. Nobody can see which changes a given database has already had.

Migrations replace that memory with files. Each migration has a unique ID and records which migration came before it, so together they form a chain, from an empty database to the current schema. Alembic also creates a one-row table in your database called `alembic_version` that stores the ID of the last migration applied there. To bring any database up to date, Alembic reads that ID, finds every later migration in the chain, and runs them in order. Running it twice is harmless: the second time there's nothing left to apply.

### Setting up Alembic

In your prompt library project from Persisting Data with Postgres, add Alembic and create its folder:

```bash
uv add alembic
uv run alembic init migrations
```

This creates `alembic.ini` (settings) and a `migrations/` folder containing `env.py` (the script Alembic runs every time), `script.py.mako` (the template for new migration files) and an empty `versions/` folder where your migrations will go. Commit all of it.

Alembic needs to know two things that only your app knows: where the database is, and what the tables *should* look like. Open `migrations/env.py`, and change the top so it looks like this. Leave everything below it alone:

```python
# migrations/env.py (top of the file)
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from sqlmodel import SQLModel

import models  # noqa: F401  (importing registers every table on SQLModel.metadata)
from database import DATABASE_URL

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# (1) What the tables should look like, according to your code.
target_metadata = SQLModel.metadata
# (2) Where the database is: the same DATABASE_URL your app reads.
#     ConfigParser treats % specially, so any % in a password is doubled.
config.set_main_option("sqlalchemy.url", DATABASE_URL.replace("%", "%%"))
```

1. `SQLModel.metadata` is a registry that every `table=True` class adds itself to when its module is imported. That's why `import models` is there even though nothing uses the name. Forget it, and Alembic thinks your app has no tables at all.
1. The URL comes from `database.py`, which reads the `DATABASE_URL` environment variable. Leave the placeholder `sqlalchemy.url` line in `alembic.ini` alone; the line above overrides it, and the real password never ends up in a committed file.

Two more small edits. Autogenerated migrations refer to SQLModel's string type, so open `migrations/script.py.mako` and add `import sqlmodel` under `import sqlalchemy as sa`. Every future migration file then imports it. Finally, give every index and constraint a predictable name by adding this to `models.py`, above your table classes:

```python
from sqlmodel import Field, SQLModel

SQLModel.metadata.naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
```

Without this, Postgres invents names for unique constraints, and Alembic writes `op.drop_constraint(None, ...)` in your downgrade, which fails when you run it. With it, a unique constraint on `prompt.slug` is always called `uq_prompt_slug`, so a later migration can find it and drop it.

Last, delete the `SQLModel.metadata.create_all(engine)` line (and the `lifespan` function, if that was all it did) from `main.py`. From now on Alembic owns the schema. Your tests can keep calling `create_all` on their throwaway in-memory database, since that database is created fresh every time.

### Your first migration

**Autogenerate** compares two things: the tables your models describe and the tables that actually exist in the database. It then writes a migration that turns the second into the first. So start from an empty database. If your `db` container still has the table `create_all` made in the last lesson, reset it (this deletes its data):

```bash
docker compose down -v && docker compose up -d db
uv run alembic revision --autogenerate -m "create prompt table"
```

Alembic prints `Detected added table 'prompt'` and writes a file such as `migrations/versions/7920a5872ca4_create_prompt_table.py`. The hex prefix is the revision ID. Open it. Its `upgrade()` function calls `op.create_table("prompt", ...)` and `op.create_index(...)`, and `downgrade()` drops them again. `op` is Alembic's toolbox of schema operations.

Now apply it, and look at the result:

```bash
uv run alembic upgrade head      # apply every migration up to the newest ("head")
uv run alembic current           # which revision is this database at?
uv run alembic history           # the whole chain, newest first
```

`head` means the newest migration in the chain. After the upgrade, `docker compose exec db psql -U mimir -c '\dt'` lists two tables: `prompt` and `alembic_version`.

If you already have a database with real data, built by `create_all`, and you don't want to reset it, there's another way. Make sure its tables really match your models, then run `uv run alembic stamp head`. That writes the current revision into `alembic_version` without running anything, telling Alembic "this database is already up to date."

### Reviewing the generated migration

Autogenerate is a first draft written by a tool that can't read your mind. Read every migration before you run it, the way you'd review code a teammate (or an AI assistant) wrote. Three things it gets wrong most often:

- **Renames look like a drop and an add.** Rename `text` to `template` in your model and autogenerate writes `op.add_column("prompt", ... "template" ...)` followed by `op.drop_column("prompt", "text")`. Run that and every prompt's text is deleted. Replace both lines with `op.alter_column("prompt", "text", new_column_name="template")`.
- **It can't know about existing rows.** A new required column breaks on a table that has data, as the next section shows.
- **It can't see everything.** It misses some changes, such as certain type changes, and doesn't know about things like Postgres extensions or views. The Alembic docs list exactly what it does and doesn't detect.

Before you commit, `uv run alembic check` tells you whether your models and the database still differ. It's quick enough to add to CI later.

### A data migration

Now change a table that holds data. Insert two prompts through `/docs` first, such as "Summarize Text" and "Extract People". Then add two fields to `models.py`: an optional `description` on `PromptBase`, and a required, unique `slug` (a URL-friendly name like `summarize-text-1`) on `Prompt`:

```python
class PromptBase(SQLModel):
    name: str = Field(min_length=1, max_length=100, index=True)
    text: str = Field(min_length=1)
    description: str | None = None                  # new, optional


class Prompt(PromptBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    slug: str = Field(max_length=100, unique=True)  # new, required and unique
```

Run `uv run alembic revision --autogenerate -m "add description and slug"`, then `uv run alembic upgrade head`. It fails:

```text
psycopg.errors.NotNullViolation: column "slug" of relation "prompt" contains null values
[SQL: ALTER TABLE prompt ADD COLUMN slug VARCHAR(100) NOT NULL]
```

The draft asked Postgres to add a column that can't be empty to a table whose two existing rows have no value for it. (On Postgres, Alembic runs migrations inside a transaction, the all-or-nothing idea from SQL Fundamentals, so the `description` column it added first was rolled back too. Your database is unchanged.) The fix is a **data migration**: a migration that changes the data itself, not just the schema. Edit the file so it works in three steps:

```python
def upgrade() -> None:
    """Add description and slug, and fill slug for existing rows."""
    op.add_column("prompt", sa.Column("description", sqlmodel.AutoString(), nullable=True))

    # 1. Add slug as nullable, because existing rows have no value yet.
    op.add_column("prompt", sa.Column("slug", sqlmodel.AutoString(length=100), nullable=True))

    # 2. Data migration: build a slug from each name, e.g. "Summarize Text" -> "summarize-text-1".
    op.execute(
        """
        UPDATE prompt
        SET slug = lower(regexp_replace(name, '[^a-zA-Z0-9]+', '-', 'g')) || '-' || id
        """
    )

    # 3. Now every row has a slug, so the column can become required and unique.
    op.alter_column("prompt", "slug", nullable=False)
    op.create_unique_constraint(op.f("uq_prompt_slug"), "prompt", ["slug"])


def downgrade() -> None:
    """Undo upgrade() in reverse order. The slugs are lost, but names are untouched."""
    op.drop_constraint(op.f("uq_prompt_slug"), "prompt", type_="unique")
    op.drop_column("prompt", "slug")
    op.drop_column("prompt", "description")
```

Run `uv run alembic upgrade head` again and query the table: each row now has a slug such as `summarize-text-1`. Adding the id on the end keeps two prompts with the same name from producing the same slug and breaking the unique constraint. `op.execute` runs plain SQL, which is the safest way to change data inside a migration. Don't import your current model classes into a migration to do it: the models will keep changing, and an old migration must keep working against the schema as it was when the migration was written.

Your app needs one more change, too: `create_prompt` must now set a slug on new prompts (for example, from the name plus a few random characters from `secrets.token_hex(3)`), or inserts will fail. Migrations change the database, and your code still has to match.

### Upgrade and downgrade

You can move a database in either direction:

```bash
uv run alembic downgrade -1      # undo the most recent migration
uv run alembic upgrade +1        # apply the next one
uv run alembic downgrade base    # undo everything (an empty database)
uv run alembic upgrade head      # and all the way forward again
```

Run that round trip on your laptop for every migration you write. A downgrade that has never run is a downgrade that probably doesn't work. Be honest about what downgrades can do, though. Dropping the `slug` column throws away the slugs, and no downgrade can bring back data that a dropped column held. In production, teams usually fix a bad migration by writing a new migration that moves *forward*, and keep downgrades for development and emergencies. Back up a production database before a risky migration; you'll learn how in Managed Postgres and Backups in the Production path.

### Migrations in Compose and on deploy

During development, keep running `uv run alembic upgrade head` from your laptop against the `db` container, which listens on `localhost:5432`. When you run the whole stack in Compose, add a one-shot `migrate` service that uses the same image as the API, runs the migrations and exits. The API then waits for it to finish successfully. Add this to the `compose.yaml` from Docker and Docker Compose:

```yaml
services:
  migrate:
    build: .
    command: ["alembic", "upgrade", "head"]
    environment:
      DATABASE_URL: postgresql+psycopg://mimir:mimir@db:5432/mimir
    depends_on:
      db:
        condition: service_healthy

  api:
    # ...everything from before, plus:
    depends_on:
      migrate:
        condition: service_completed_successfully
```

The `alembic` command is available inside the image because the Dockerfile puts the project's virtual environment on the `PATH`, and `COPY . .` copies `alembic.ini` and `migrations/` in. If a migration fails, `migrate` exits with an error and the API never starts against a half-migrated database.

A deploy follows the same rule: **migrate once, before the new code starts serving.** Most hosts have a "release" or "pre-deploy" step for exactly this, and if the migration fails, the deploy stops and the old version keeps running. You'll set that up in Deploying Your API. Don't run migrations from inside the app at startup if you'll ever run more than one copy of it, since two copies migrating at the same moment can collide.

Write migrations so the old code keeps working while the new code rolls out. Adding a nullable column is safe: the old code simply ignores it. Dropping or renaming a column the old code still reads is not. For those, split the change across two deploys: first ship code that stops using the column, and then ship the migration that removes it.

### Common pitfalls

- **Editing a migration that has already run somewhere.** Alembic only checks the revision ID, not the contents, so an edited migration never re-runs on databases that already applied it. Once a migration is merged or deployed, write a new one instead.
- **An empty or destructive autogenerate.** If autogenerate wants to drop all your tables, `env.py` isn't importing your models. If it finds nothing, your database is probably already ahead, or you forgot to save `models.py`.
- **Multiple heads.** Two branches that each add a migration both point back to the same parent, and `alembic upgrade head` complains that there are multiple heads. Run `uv run alembic heads` to see them and `uv run alembic merge heads -m "merge"` to join them.
- **Wrong database.** Alembic migrates whatever `DATABASE_URL` points at. Run `uv run alembic current` first when you aren't sure.
- **SQLite can't alter much.** SQLite supports only a few `ALTER TABLE` operations, so many migrations that work on Postgres fail on it. That's one more reason Postgres is the default here; Alembic's "batch mode" exists if you ever must migrate SQLite.
- **Defaults that only exist in Python.** `Field(default=0)` fills the value in when *your code* creates an object. The database knows nothing about it, so existing rows don't get it. Use a data migration or `server_default` for those.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Work through the [Alembic tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html). It is the official walkthrough of everything in this lesson, from `alembic init` to relative upgrades and downgrades.
   - Read from the start through "Downgrading". You can skip "Using pyproject.toml for configuration", since this lesson uses `alembic.ini`.
   - The tutorial writes migrations by hand first, which is a good way to learn what the `op` functions do.
1. Read [Auto Generating Migrations](https://alembic.sqlalchemy.org/en/latest/autogenerate.html), which explains how autogenerate compares models with the database.
   - Focus on "What does Autogenerate Detect (and what does it not detect?)". Keep that list in mind whenever you review a migration.
1. Read [The Importance of Naming Constraints](https://alembic.sqlalchemy.org/en/latest/naming.html) to see why the naming convention in this lesson matters.
   - Read the opening section and "Integration of Naming Conventions into Operations, Autogenerate". The convention you added follows its example.
1. Read about `service_completed_successfully` and the other conditions in [Compose's depends_on reference](https://docs.docker.com/reference/compose-file/services/#depends_on). It's what makes the `migrate` service work.
1. Practice: put your summarizer API from Persisting Data with Postgres under Alembic.
   - Set up Alembic as in this lesson, delete `create_all` from the app, reset your local database, and generate and apply a first migration for your `Summary` table. Commit the migration file.
   - Add a column to `Summary`, such as a required `latency_ms` integer. Create a few rows first, then write a migration that adds it as nullable, backfills existing rows (use `0`, or `NULL` if you make it optional), and only then makes it required.
   - Run `uv run alembic downgrade base` and then `uv run alembic upgrade head`, and save the output. That's the "every migration applies in order" evidence later projects ask for.
   - Add the `migrate` service to your `compose.yaml`, and confirm `docker compose up --build` migrates a fresh database (`docker compose down -v` first) before the API starts.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Why doesn't create_all add a new column to an existing table, and how does Alembic know which migrations a database still needs?](#why-create-all-is-not-enough)
- [What two things does env.py give Alembic, and what goes wrong if it doesn't import your models?](#setting-up-alembic)
- [Why should you name constraints with a naming convention?](#setting-up-alembic)
- [What does autogenerate do with a renamed column, and how do you fix it?](#reviewing-the-generated-migration)
- [Why does adding a required column to a table with rows fail, and what three steps fix it?](#a-data-migration)
- [Why can't a downgrade always undo an upgrade?](#upgrade-and-downgrade)
- [When should migrations run during a deploy, and why not from inside the app at startup?](#migrations-in-compose-and-on-deploy)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The Alembic cookbook](https://alembic.sqlalchemy.org/en/latest/cookbook.html) has recipes for situations you'll eventually hit, including running migrations from your own Python code and testing them.
- [Alembic's operation reference](https://alembic.sqlalchemy.org/en/latest/ops.html) lists every `op` function and its arguments.
- [The PostgreSQL ALTER TABLE reference](https://www.postgresql.org/docs/current/sql-altertable.html) shows the SQL that your migrations generate, and notes which changes rewrite the whole table (slow on big tables).
