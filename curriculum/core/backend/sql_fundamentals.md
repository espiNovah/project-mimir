### Introduction

Every real AI application stores things: users, conversations, extraction results, thumbs-up and thumbs-down ratings, eval scores. Most of that data lives in a **relational database**, and the language for talking to relational databases is **SQL** (Structured Query Language, usually pronounced "sequel" or "S-Q-L"). SQL is more than fifty years old and still everywhere, including inside the vector store you'll use in the RAG section, which is a Postgres extension.

In this lesson you'll learn to read and write everyday queries, to connect tables with keys and joins, and to get a first feel for what makes a query fast or slow. You'll practice with SQLite, a tiny database that's already built into Python. From the Docker lesson on, the curriculum switches to PostgreSQL, and almost everything you learn here carries over unchanged.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What tables, rows, columns, primary keys and foreign keys are.
- How to read data with `SELECT`, filter it with `WHERE` and sort it with `ORDER BY`.
- How to summarize data with aggregates and `GROUP BY`.
- How to combine tables with joins, and what `NULL` means.
- How to insert, update and delete rows safely.
- What indexes do and how to read a query plan with `EXPLAIN`.
- What transactions are and why they matter.

### Tables, rows and keys

A **table** is like a spreadsheet with strict rules. Every row has the same columns, and every column has a type, such as `INTEGER` or `TEXT`. A **database** is a collection of tables, and the **schema** is the description of which tables exist and what columns they have.

Here is the schema for a small chat app, which the rest of this lesson uses:

```sql
CREATE TABLE users (
    id    INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    name  TEXT NOT NULL
);

CREATE TABLE messages (
    id      INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    role    TEXT NOT NULL,      -- 'user' or 'assistant'
    content TEXT NOT NULL,
    tokens  INTEGER NOT NULL,
    rating  INTEGER             -- 1 = thumbs up, -1 = thumbs down, NULL = not rated
);
```

A **primary key** is a column whose value uniquely identifies each row. By convention it's called `id`, and the database fills it in for you when you insert a row. No two users can share an `id`, so "user 2" always means exactly one person.

A **foreign key** is a column that points at a primary key in another table. `messages.user_id` holds the `id` of the user who owns the message. Instead of copying Grace's name and email into every one of her messages, you store the number `2`. If Grace changes her email, you update one row in `users` and every message still points to the right person. `REFERENCES users(id)` asks the database to enforce the link: it will refuse a message whose `user_id` doesn't exist.

The other constraints are guardrails too. `NOT NULL` means the column must have a value, and `UNIQUE` means no two rows may share it. A database that enforces rules like these protects your data from your own bugs.

### Reading data with SELECT

Most of the SQL you write will be `SELECT` statements. The shape is:

```sql
SELECT name, email          -- which columns
FROM users                  -- which table
WHERE name <> 'Alan'        -- which rows (<> means "not equal")
ORDER BY name ASC           -- in what order (ASC or DESC)
LIMIT 10;                   -- at most how many
```

`SELECT *` returns every column, which is handy for exploring but wasteful in application code. `WHERE` supports the comparisons you'd expect (`=`, `<>`, `<`, `>=`), combined with `AND`, `OR` and `NOT`, plus a few extras: `role IN ('user', 'assistant')`, `tokens BETWEEN 100 AND 500` and `content LIKE '%contract%'`, where `%` matches any run of characters.

SQL is **declarative**. You describe the result you want, not the steps to get it, and the database decides how to find the rows. That's very different from a Python loop, and it's what lets the database get faster without you changing your query, as you'll see with indexes.

One value needs special care. **`NULL`** means "unknown" or "missing," and it isn't equal to anything, not even another `NULL`. `WHERE rating = NULL` matches nothing. Write `WHERE rating IS NULL` or `WHERE rating IS NOT NULL` instead.

### Summarizing with GROUP BY

**Aggregate functions** turn many rows into one value: `COUNT`, `SUM`, `AVG`, `MIN` and `MAX`. On their own they summarize the whole table. With `GROUP BY` they summarize each group separately:

```sql
-- How many rated replies, and what's the average rating, per user?
SELECT user_id, COUNT(*) AS rated, AVG(rating) AS avg_rating
FROM messages
WHERE role = 'assistant' AND rating IS NOT NULL
GROUP BY user_id
HAVING COUNT(*) >= 2
ORDER BY avg_rating DESC;
```

Read it in the order the database runs it: take `messages`, keep rows that pass `WHERE`, split them into one group per `user_id`, compute the aggregates for each group, keep groups that pass `HAVING`, then sort. `WHERE` filters rows *before* grouping, and `HAVING` filters groups *after*. `AS` gives a result column a name.

This is the query shape behind most AI dashboards: thumbs-down rate per prompt version, tokens per day, errors per model.

### Combining tables with joins

A **join** combines rows from two tables that match on some condition, usually a foreign key matching a primary key:

```sql
SELECT u.name, m.content, m.rating
FROM messages AS m
INNER JOIN users AS u ON u.id = m.user_id
WHERE m.rating = -1;
```

`AS m` and `AS u` are short aliases, so `m.content` means "the `content` column from `messages`." An **`INNER JOIN`** keeps only rows that have a match on both sides.

A **`LEFT JOIN`** keeps every row from the left table even when nothing on the right matches, filling the right side's columns with `NULL`. That's how you find things that are missing:

```sql
-- Every user and how many tokens they've used, including users with no messages
SELECT u.name, COUNT(m.id) AS n_messages, COALESCE(SUM(m.tokens), 0) AS total_tokens
FROM users AS u
LEFT JOIN messages AS m ON m.user_id = u.id
GROUP BY u.id
ORDER BY total_tokens DESC;
```

A user with no messages still appears, with `n_messages` of 0. `COALESCE(x, 0)` returns the first value that isn't `NULL`, so a missing sum becomes 0. Change `LEFT JOIN` to `INNER JOIN` and that user disappears, a classic source of quietly wrong reports.

### Changing data

`INSERT` adds rows, `UPDATE` changes them and `DELETE` removes them:

```sql
INSERT INTO users (email, name) VALUES ('alan@example.com', 'Alan');

UPDATE messages SET rating = 1 WHERE id = 4;

DELETE FROM messages WHERE user_id = 3;
```

The `WHERE` clause is doing the important work in the last two. An `UPDATE` or `DELETE` *without* a `WHERE` affects every row in the table, and there's no undo button. A good habit: write the `SELECT` with the same `WHERE` first, check that it returns exactly the rows you mean, then change `SELECT` to `DELETE`.

`CREATE TABLE` defines a table, and `DROP TABLE` deletes it along with all its data. Changing tables that already hold real data is a job for migrations, which you'll meet in the Migrations with Alembic lesson.

### Indexes and EXPLAIN

Imagine `messages` has ten million rows and you run `SELECT * FROM messages WHERE user_id = 2`. Without help, the database must look at every row to find Grace's. That's a **full table scan**, and it gets slower as the table grows.

An **index** is a separate, sorted lookup structure, like the index at the back of a book. With an index on `user_id`, the database jumps straight to the matching rows:

```sql
CREATE INDEX idx_messages_user_id ON messages (user_id);
```

You can ask the database how it plans to run a query. In SQLite, prefix the query with `EXPLAIN QUERY PLAN`:

```text
sqlite> EXPLAIN QUERY PLAN SELECT * FROM messages WHERE user_id = 2;
`--SCAN messages                                                  (before the index)

`--SEARCH messages USING INDEX idx_messages_user_id (user_id=?)    (after the index)
```

`SCAN` means "read the whole table"; `SEARCH ... USING INDEX` means "jump to the matching rows." Postgres has the same idea with `EXPLAIN` (and `EXPLAIN ANALYZE`, which actually runs the query and reports timings), where you'll see words like `Seq Scan` and `Index Scan`.

Indexes aren't free. Each one takes disk space and must be updated on every insert, so you don't index everything. Primary keys and `UNIQUE` columns get an index automatically. Add one yourself for columns you often filter, join or sort on, such as foreign keys, and confirm with `EXPLAIN` that the database uses it. Because SQL is declarative, your query doesn't change at all; the database just picks a faster path.

### Transactions

A **transaction** groups several statements so they succeed or fail together. The classic example is a bank transfer: subtract from one account and add to another. If the program crashes between the two, money vanishes. Wrapped in a transaction, either both changes are saved or neither is:

```sql
BEGIN;
UPDATE accounts SET credits = credits - 10 WHERE id = 1;
UPDATE accounts SET credits = credits + 10 WHERE id = 2;
COMMIT;    -- or ROLLBACK; to undo everything since BEGIN
```

`COMMIT` makes the changes permanent and visible to everyone else. `ROLLBACK` throws them away. In an AI app the same pattern applies when you save a conversation turn: the user's message, the model's reply and the token usage should be stored together or not at all. Transactions are the "A" (atomicity) in **ACID**, the set of guarantees that makes relational databases trustworthy.

### Running SQL from Python

Python's built-in `sqlite3` module runs SQL against a database stored in a single file. This script builds the chat database from this lesson and runs two queries. Save it as `sql_demo.py` and run it with `uv run sql_demo.py`:

```python
import sqlite3

conn = sqlite3.connect("chat.db")          # creates the file if it doesn't exist
conn.execute("PRAGMA foreign_keys = ON")   # SQLite only enforces foreign keys when asked

conn.executescript("""
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE, name TEXT NOT NULL
);
CREATE TABLE messages (
    id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id),
    role TEXT NOT NULL, content TEXT NOT NULL, tokens INTEGER NOT NULL, rating INTEGER
);
""")

# `with conn:` is a transaction: it commits if the block succeeds, rolls back if it raises
with conn:
    conn.executemany(
        "INSERT INTO users (email, name) VALUES (?, ?)",
        [("ada@example.com", "Ada"), ("grace@example.com", "Grace"), ("alan@example.com", "Alan")],
    )
    conn.executemany(
        "INSERT INTO messages (user_id, role, content, tokens, rating) VALUES (?, ?, ?, ?, ?)",
        [
            (1, "user", "What is a vector?", 6, None),
            (1, "assistant", "A list of numbers that...", 120, 1),
            (2, "user", "Summarize this contract", 900, None),
            (2, "assistant", "The contract says...", 340, -1),
            (2, "assistant", "Here is a shorter summary...", 150, 1),
        ],
    )

# Parameterized query: the driver fills in ? safely. Never use an f-string here.
email = "grace@example.com"
print(conn.execute("SELECT id, name FROM users WHERE email = ?", (email,)).fetchone())

for row in conn.execute("""
    SELECT u.name, COUNT(m.id), COALESCE(SUM(m.tokens), 0) AS total_tokens
    FROM users AS u LEFT JOIN messages AS m ON m.user_id = u.id
    GROUP BY u.id ORDER BY total_tokens DESC
"""):
    print(row)   # ('Grace', 3, 1390), then ('Ada', 2, 126), then ('Alan', 0, 0)

conn.close()
```

Look closely at the `?` placeholders. It's tempting to write `f"SELECT ... WHERE email = '{email}'"`, but if `email` comes from a user, they can type `' OR '1'='1` and change what your query does. That's **SQL injection**, one of the oldest and most damaging security bugs. With placeholders, the driver sends the value separately from the SQL, so it can never run as code. The ORM you'll use in Persisting Data with Postgres does this for you automatically.

You can also explore the file interactively with the `sqlite3` command-line tool (`sqlite3 chat.db`), which is preinstalled on macOS and most Linux systems, or with a free GUI like DB Browser for SQLite.

### SQLite now, Postgres soon

**SQLite** is a whole database in one file, with no server to install. It's perfect for learning, for tests and for small apps. It's also more forgiving than most databases: it doesn't strictly enforce column types by default and only checks foreign keys when you turn that on.

**PostgreSQL** (Postgres for short) is a database *server*: a separate program that many apps and users can connect to at once over the network. It's strict about types, handles many simultaneous writers, and has extensions like pgvector for storing embeddings. That's why it's the default database for the rest of this curriculum. In the Docker and Docker Compose lesson you'll start Postgres with one command, and from then on your apps use it.

The SQL in this lesson works in both, with small differences. Postgres uses `SERIAL` or `GENERATED ... AS IDENTITY` for auto-incrementing IDs, `$1` or `%s` placeholders instead of `?` depending on the driver, and `EXPLAIN` instead of `EXPLAIN QUERY PLAN`. When something behaves differently, check the docs for the database you're using.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Complete [SQLBolt](https://sqlbolt.com/), a set of short interactive lessons that run in your browser, so you get dozens of repetitions on the syntax from this lesson.
   - Do all the lessons through "Dropping tables." Each one takes a few minutes, and the exercises check your answers as you type.
1. Read the [PostgreSQL tutorial](https://www.postgresql.org/docs/current/tutorial.html) from the official docs for a second explanation of the same ideas from the database's own authors.
   - Read chapter 2, "The SQL Language." In chapter 3, read "Foreign Keys" and "Transactions" closely, and skim the rest for the names of advanced features.
1. Read the introduction and tutorial of [Python's sqlite3 module docs](https://docs.python.org/3/library/sqlite3.html) to see how to run SQL from Python.
   - Pay attention to the how-to on placeholders and why they prevent SQL injection, and to the section on transaction control.
1. Read the first two chapters of [Use The Index, Luke](https://use-the-index-luke.com/), a free book that explains indexes better than anything else, then skim [SQLite's EXPLAIN QUERY PLAN page](https://www.sqlite.org/eqp.html) so you can read `SCAN` and `SEARCH` lines.
1. Practice: in Python, create a SQLite database with two tables, `prompts` (id, name, text) and `runs` (id, prompt_id, input, output, correct), with `runs.prompt_id` as a foreign key. Insert your results from the Prompt Lab project inside one transaction, using placeholders. Then write queries for:
   - accuracy per prompt, using `GROUP BY`;
   - the five longest outputs, with the name of the prompt that produced them, using a join;
   - every input that all prompts got wrong, using `GROUP BY` and `HAVING`;
   - any prompt that has no runs yet, using a `LEFT JOIN`.
   - Finally, run `EXPLAIN QUERY PLAN` on a query that filters `runs` by `prompt_id`, add an index, and run it again to see `SCAN` turn into `SEARCH`.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What's the difference between a primary key and a foreign key?](#tables-rows-and-keys)
- [Why does `WHERE rating = NULL` match nothing, and what should you write instead?](#reading-data-with-select)
- [What's the difference between `WHERE` and `HAVING`?](#summarizing-with-group-by)
- [When would you use a `LEFT JOIN` instead of an `INNER JOIN`?](#combining-tables-with-joins)
- [What does an index do, and how can you check that a query uses it?](#indexes-and-explain)
- [What problem does a transaction solve?](#transactions)
- [Why should you use placeholders instead of building SQL with f-strings?](#running-sql-from-python)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Select Star SQL](https://selectstarsql.com/) is a free interactive book that teaches SQL with a real dataset, good if you want more practice with harder queries.
- [Using EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html) in the Postgres docs shows how to read Postgres query plans, which you'll want once your app runs on Postgres.
- [SQLite's transaction docs](https://www.sqlite.org/lang_transaction.html) explain exactly when SQLite starts and ends transactions.
