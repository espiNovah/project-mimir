<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Every real AI application stores things: users, conversations, extraction results, feedback, eval scores. Most of that data lives in a relational database, and the language for talking to relational databases is SQL (Structured Query Language). SQL is more than fifty years old and still everywhere, including inside vector databases you will meet in the RAG section. This lesson gets you comfortable reading and writing everyday queries.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What a relational database is: tables, rows, columns and keys.
- How to read data with `SELECT`, filter it with `WHERE` and sort it with `ORDER BY`.
- How to combine tables with joins.
- How to summarize data with aggregates and `GROUP BY`.
- How to create tables and insert, update and delete rows.
- Why SQLite is great for learning and PostgreSQL is common in production.

### Key ideas

- **Data lives in tables.** A table is like a spreadsheet with strict rules: every row has the same columns, and every column has a type. A *primary key* is a column (usually `id`) that uniquely identifies each row.
- **Relationships use foreign keys.** Instead of copying a user's name into every message, a `messages` table stores a `user_id` that points to a row in `users`. This keeps data consistent and small.
- **SELECT is most of what you will write.** `SELECT columns FROM table WHERE condition ORDER BY column LIMIT n` covers a surprising amount of real work. SQL is *declarative*: you describe the result you want and the database figures out how to get it.
- **Joins combine related tables.** `INNER JOIN` keeps rows that match on both sides; `LEFT JOIN` keeps every row from the left table even when nothing matches, filling the gaps with `NULL`. `NULL` means "unknown," and comparisons with it need `IS NULL`, not `= NULL`.
- **Aggregates summarize.** `COUNT`, `SUM`, `AVG`, `MIN` and `MAX` with `GROUP BY` answer questions like "how many thumbs-down ratings did each prompt version get?" Use `HAVING` to filter groups after aggregation.
- **Schema changes and writes.** `CREATE TABLE` defines structure; `INSERT`, `UPDATE` and `DELETE` change rows. An `UPDATE` or `DELETE` without a `WHERE` clause affects every row, so always double-check.
- **Never build SQL by gluing strings.** Inserting user input directly into a query string allows *SQL injection*, where an attacker's input runs as code. Use parameterized queries (placeholders like `?`) or a library that does it for you, such as SQLModel in a later lesson.
- **SQLite and PostgreSQL.** SQLite is a database in a single file, built into Python's standard library, ideal for learning and small apps. PostgreSQL is a full database server used by many production systems, and it can store vectors with the pgvector extension.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Complete [SQLBolt](https://sqlbolt.com/), a set of short interactive lessons that run in your browser.
   - Do all the lessons through "Dropping tables." Each one takes a few minutes, and the exercises check your answers as you type.
1. Read the [PostgreSQL tutorial](https://www.postgresql.org/docs/current/tutorial.html) from the official docs.
   - Read chapter 2, "The SQL Language," for a second explanation of the same ideas from the database's own authors. Skim chapter 3 for the names of advanced features such as transactions.
1. Read the introduction and the first examples of [Python's sqlite3 module docs](https://docs.python.org/3/library/sqlite3.html) to see how to run SQL from Python.
   - Pay attention to the section on placeholders and why they prevent SQL injection.
1. Practice: in Python, create a SQLite database with two tables, `prompts` (id, name, text) and `runs` (id, prompt_id, input, output, correct). Insert your results from the Prompt Lab project, then write queries for: accuracy per prompt, the five slowest or longest outputs, and every input that all prompts got wrong.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Select Star SQL](https://selectstarsql.com/) is a free interactive book that teaches SQL with a real dataset, good if you want more practice with harder queries.
