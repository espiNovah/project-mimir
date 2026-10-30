### Introduction

Your code can be rebuilt from Git in minutes. Your data can't. If a deploy goes wrong, you roll back to the previous image and nobody remembers it by lunch. If a migration locks your busiest table for ten minutes, or someone runs `DELETE` without a `WHERE`, or a free database quietly expires, the users' prompts, summaries and accounts are gone unless you planned for that moment ahead of time.

You already know a lot of Postgres. You've stored data through SQLModel, changed the schema with Alembic, added pgvector, run it all in Docker Compose, and deployed it on Render's managed Postgres. This lesson covers what changes once real people depend on that database: choosing where it runs, sharing a limited number of connections between many app instances, changing the schema without stopping the app, and, most important of all, getting the data back. You'll finish by running a **restore drill**, a rehearsal of the worst day, on your own laptop with Docker, where mistakes cost nothing.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What a managed Postgres service does for you, and how Cloud SQL, Neon, Supabase and Render compare.
- Why Postgres runs out of connections, and how pool sizes and connection poolers fix it.
- Which migrations lock tables, and how to write ones that don't block your app.
- The expand and contract pattern for renaming and removing columns safely.
- The difference between a backup and point-in-time recovery, and what RPO and RTO mean.
- How to back up with `pg_dump`, restore with `pg_restore`, and prove the restore worked.

### What a managed database does for you

In Deploying Your API you met the idea of a **managed database**: the provider installs Postgres, runs it on its own servers, applies security patches and hands you a connection URL. It's worth spelling out the rest of what you're paying for (or getting free), because it's what you'd have to build yourself on a bare server:

- **Automated backups**, kept somewhere other than the database's own disk.
- **Point-in-time recovery**, which lets you rewind the database to a chosen second. More on this below.
- **High availability**, a standby copy in another data center that takes over if the main one fails. This is almost always a paid extra.
- **Maintenance**: minor-version upgrades and restarts, usually inside a maintenance window you choose.
- **Monitoring**: CPU, storage, slow queries and connection counts on a dashboard.

What a managed service does *not* do is make your schema changes safe, keep your connection count sensible, or check that a backup can actually be restored. Those stay your job, and they're the rest of this lesson.

### Choosing a provider

Four providers cover what most small teams use. All four run ordinary Postgres, so your SQLModel code, Alembic migrations and pgvector work on each of them; only the connection URL changes. Free-tier limits change often, so treat the notes below as the shape of each offer and check the current numbers on the provider's pricing page before you rely on them.

| Provider | Free tier, roughly | Good fit when |
| --- | --- | --- |
| **Render Postgres** | A small free database with no backups that expires about 30 days after you create it | Your app already runs on Render, as yours does from Deploying Your API |
| **Neon** | A permanent free plan with small storage (about 1 GB per project); the database scales to zero when idle, and restore features are mostly on paid plans | You want a free database that doesn't expire, plus cheap copies ("branches") for testing |
| **Supabase** | A permanent free project with small storage (about 500 MB) that pauses after a week of no activity and has no automatic backups; adds auth, storage and an API on top of Postgres | You want those extra services too, or a web dashboard for your data |
| **Google Cloud SQL** | No always-free tier, but new Google Cloud accounts get trial credit | Your app runs on Google Cloud, as in One Real Cloud, and you want private networking and IAM in one place |

Some questions decide most choices. Is the database **in the same region** as your app? Every query crosses that distance, and a database on another continent can add 100 ms or more to each one. Does it support the **extensions** you need? (All four support pgvector.) What are the **backup and recovery** terms on the plan you'll actually pay for? And how do you **connect**: Cloud SQL, for example, is usually reached from Cloud Run through Google's Cloud SQL connector rather than a plain public URL.

For this curriculum, any of them works. If your Render free database is about to expire, moving it to Neon's free plan is a perfectly good choice, and it's also great practice for the restore drill at the end of this lesson.

<div class="lesson-note lesson-note--warning" markdown="1">

#### A free database is not a backed-up database

Render's and Supabase's free databases have no automatic backups at all, and other free plans keep only a few hours of history, if any. Until you pay for a plan with backups, the `pg_dump` files you make yourself are the only copy of your data. Treat free databases as demos, and say so in your README.

</div>

### Connection pooling

Every connection to Postgres is a separate process on the database server, using several megabytes of memory. Postgres caps the total with a setting called `max_connections`, which defaults to 100, and small managed plans often allow fewer. Go over the cap and new connections fail with `FATAL: sorry, too many clients already`.

Your app doesn't open a connection per request. SQLAlchemy keeps a **connection pool**, a small set of open connections that requests borrow and return. By default the pool holds 5 connections and can open 10 extra ("overflow") under load, so one app process may hold up to 15. Now do the arithmetic for production: 4 API instances, each running 2 worker processes, plus a job worker, plus Alembic during a deploy, is 9 or more processes at up to 15 connections each. That's 135, past the default cap, and autoscaling platforms like Cloud Run can add instances faster than you expect.

There are two fixes, and you usually want both. First, **size each pool on purpose**, so the worst case fits under the cap:

```python
# database.py: an engine sized for production. (uv add sqlmodel "psycopg[binary]")
import os

from sqlmodel import create_engine

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(
    DATABASE_URL,
    pool_size=int(os.environ.get("DB_POOL_SIZE", "5")),  # connections kept open per process
    max_overflow=2,       # extra connections allowed during a burst, closed afterwards
    pool_timeout=10,      # wait at most 10 s for a free connection, then raise an error
    pool_recycle=300,     # replace connections older than 5 minutes; idle ones get cut by proxies
    pool_pre_ping=True,   # check a connection is alive before using it (from Deploying Your API)
    # Only for a pooler in transaction mode (see below): turn off psycopg's prepared statements,
    # because the next query may run on a different server connection that never saw them.
    # connect_args={"prepare_threshold": None},
)
```

With `pool_size=5` and `max_overflow=2`, each process holds at most 7 connections, so you can say exactly how many processes fit: about 12 under a cap of 100, leaving room for you to connect with `psql` during an incident. Put the size in an environment variable so you can tune it per environment without a code change.

Second, put a **connection pooler** between the app and the database. A pooler such as **PgBouncer** accepts thousands of cheap client connections and shares a few real database connections between them. In **transaction mode**, a client gets a real connection only for the length of one transaction, then hands it back. Neon and Supabase both run a pooler for you and give you a second, "pooled" connection URL; on Render or Cloud SQL you'd run PgBouncer yourself. Transaction mode has one catch: anything that lives on a server connection between transactions doesn't survive. That includes session settings (`SET ...`), advisory locks and, depending on the pooler, prepared statements, which is why the commented-out `connect_args` line exists. Run Alembic migrations over the **direct** URL, not the pooled one, because migrations use session settings and long transactions.

### How migrations lock tables

In Migrations with Alembic you learned to make every migration reversible and to ship schema changes in an order that old code can survive. In production there's a second danger: **locks**. Postgres protects a table while its structure changes by taking a lock on it, and most `ALTER TABLE` commands take the strongest kind, an `ACCESS EXCLUSIVE` lock, which blocks every read and write on that table until the change finishes.

For many changes that's harmless, because the change is instant. For others, Postgres has to read or rewrite every row while holding the lock, and on a large table that can take minutes, during which your API's requests pile up and time out. Here are the common ones:

| Change | What happens | Safe alternative |
| --- | --- | --- |
| Add a nullable column, or one with a constant default | Instant (Postgres 11 and later) | Already safe |
| Add a column whose default is computed per row, such as `gen_random_uuid()` | Rewrites the whole table | Add it nullable, backfill in batches, then add the default |
| Change a column's type | Usually rewrites the whole table | Expand and contract (next section) |
| `SET NOT NULL` | Scans every row while blocking everything | Add a `CHECK` constraint `NOT VALID`, validate it, then set `NOT NULL` |
| `CREATE INDEX` | Blocks writes until the index is built | `CREATE INDEX CONCURRENTLY` |
| Add a foreign key | Scans the table to check every row | Add it `NOT VALID`, then `VALIDATE CONSTRAINT` |

There's a trap even with the instant changes. A lock request waits in a queue behind any running query that touches the table, and every query that arrives after it waits behind *it*. So an instant `ALTER TABLE` stuck behind one slow report query can freeze all traffic to that table for as long as the report runs. The defense is a **lock timeout**: if the migration can't get its lock within a few seconds, it gives up and fails, and you try again later. A failed migration is annoying; a frozen production table is an incident.

Here is an Alembic migration that adds an index to a busy table without blocking writes:

```python
"""add an index on summary.user_id without blocking writes"""
from alembic import op

revision = "b7c1d2e3f4a5"
down_revision = "a1b2c3d4e5f6"


def upgrade() -> None:
    # Fail after 5 s instead of queueing behind a slow query and freezing the table.
    # (A plain SET lasts for the whole session, so it still applies inside the block below.)
    op.execute("SET lock_timeout = '5s'")
    # CONCURRENTLY can't run inside a transaction, and Alembic wraps each migration
    # in one, so step outside it for this operation.
    with op.get_context().autocommit_block():
        op.create_index(
            "ix_summary_user_id", "summary", ["user_id"],
            postgresql_concurrently=True,
            if_not_exists=True,  # safe to rerun if a previous attempt got partway
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_summary_user_id", table_name="summary",
            postgresql_concurrently=True, if_exists=True,
        )
```

A concurrent build takes longer and does more work, but reads and writes keep flowing the whole time. If it fails partway, it leaves an **invalid** index behind; drop it and run the migration again.

Making an existing column required follows the same idea of splitting one slow, locking step into fast ones. Run this in a migration with `op.execute`, after a backfill has filled every row:

```sql
-- 1. Instant: the constraint applies to new writes, but existing rows aren't checked yet.
ALTER TABLE summary ADD CONSTRAINT summary_latency_ms_not_null
    CHECK (latency_ms IS NOT NULL) NOT VALID;
-- 2. Scans the table, but with a weaker lock that lets reads and writes continue.
ALTER TABLE summary VALIDATE CONSTRAINT summary_latency_ms_not_null;
-- 3. Instant: Postgres 12+ sees the valid constraint and skips its own scan.
ALTER TABLE summary ALTER COLUMN latency_ms SET NOT NULL;
ALTER TABLE summary DROP CONSTRAINT summary_latency_ms_not_null;
```

On your laptop with 50 rows, none of this matters, and that's exactly why the habits are worth building now. Before running a migration against production, ask two questions: what lock does each statement take, and how long will it hold it?

### Expand and contract

Some changes can't be made safe with clever SQL, because old code and new code disagree about the schema. Renaming `prompt.text` to `prompt.body` is the classic example: the moment the column is renamed, every running copy of the old code breaks, and during a rolling deploy some of the old code is always still running. You also lose the ability to roll back, which Environments and Releases depends on.

The **expand and contract** pattern (also called "parallel change") splits the change into steps that each keep old and new code working:

1. **Expand.** A migration adds the new `body` column, nullable. Old code ignores it.
1. **Write to both.** Deploy code that writes every new or edited prompt to both `text` and `body`, and still reads `text`.
1. **Backfill.** Copy `text` into `body` for existing rows, in batches of a few thousand rows per transaction, so no single update holds locks for long.
1. **Switch reads.** Deploy code that reads `body`. It still writes both columns, so rolling back to the previous version is still safe.
1. **Contract.** Once you're sure you won't roll back, deploy code that stops touching `text`, then a final migration drops it.

That's four or five deploys instead of one. It feels slow, but each step is small and reversible, and at no point does a deploy or a rollback break the app. Most teams use this pattern for any rename, type change or column removal on a table that matters.

### Backups and point-in-time recovery

Two numbers describe how much a failure can hurt. The **recovery point objective (RPO)** is how much recent data you can afford to lose: if you back up once a night and the disk dies at 6 p.m., you lose almost a day of data. The **recovery time objective (RTO)** is how long you can afford to be down while you restore. Write both down for your app before you choose a backup plan, even if the answers are "a day" and "a few hours."

There are two kinds of backup:

- A **logical backup** is what `pg_dump` makes: a file of the SQL (or a compressed archive of it) needed to recreate your tables and data at one moment. It's portable, so you can restore it into a different provider or a newer Postgres version, and you can make one yourself on any plan. Its RPO is the time since the last dump, and it gets slow for very large databases.
- A **physical backup** copies the database's files directly. On its own it's also a snapshot of one moment. Combined with Postgres's **write-ahead log (WAL)**, the record of every change that Postgres writes before applying it, it allows **point-in-time recovery (PITR)**: restore the last snapshot, then replay the log up to any chosen second. If someone drops a table at 14:03:12, you restore to 14:03:11.

PITR is what managed providers sell on their paid plans, usually with a retention window of a few days to a few weeks. It gives you an RPO of seconds and protects against mistakes, not just hardware failures. Check what your plan includes: backups that only cover hardware failure won't help when the problem is a bad `UPDATE` that ran perfectly.

Keep your own logical dumps as well, even when the provider does PITR. They're your copy if you lose access to the account, if the provider has an outage, or if you want to move. The old **3-2-1 rule** is a good target: three copies, on two kinds of storage, one of them somewhere else. A dump contains everything in the database, including emails and private user content, so store it encrypted with restricted access, never in Git, and delete old ones on a schedule.

### A restore drill

A backup you have never restored is a hope, not a backup. Dumps fail in surprising ways: the file is empty because a command errored halfway, the restore needs an extension the new server doesn't have, or the `pg_dump` you used is older than the server and refuses to run. You want to find these out on a calm afternoon, not during an incident. A **restore drill** is a timed rehearsal: back up, restore into a fresh server, check that the data is all there, and note how long it took. That time is your real RTO.

This script runs the drill against the Compose database from your LLM-Powered API project. Put it in `scripts/restore_drill.sh`, add `backups/` to `.gitignore`, and run it with `bash scripts/restore_drill.sh` while `docker compose up` is running:

```bash
#!/usr/bin/env bash
# restore_drill.sh: back up the Compose database, restore it into a brand-new server,
# and check that every table came back.
set -euo pipefail                      # stop on the first error, unset variable or failed pipe

mkdir -p backups
DUMP="backups/mimir-$(date +%Y%m%d-%H%M%S).dump"

echo "1. Back up the running database"
# -T: no terminal, so the binary dump isn't mangled. --format=custom makes a compressed
# archive that pg_restore can restore selectively. Using the container's own pg_dump
# guarantees its version matches the server.
docker compose exec -T db pg_dump -U mimir -d mimir --format=custom > "$DUMP"
ls -lh "$DUMP"

echo "2. Start an empty server, as if the old one were gone"
# Use the same image as your db service (pgvector/pgvector:pg17 if you added pgvector).
docker run --rm -d --name restore-drill -e POSTGRES_PASSWORD=drill -p 5433:5432 \
  pgvector/pgvector:pg17 > /dev/null
trap 'docker stop restore-drill > /dev/null' EXIT    # always clean up, even on failure
# Ask over TCP: during first-time setup the server only listens on a local socket.
until docker exec restore-drill pg_isready -h 127.0.0.1 -U postgres -q; do sleep 1; done

echo "3. Restore"
start=$(date +%s)
docker exec restore-drill createdb -U postgres mimir
# --no-owner: the new server has no "mimir" role, so let the restoring user own everything.
docker exec -i restore-drill pg_restore -U postgres -d mimir --no-owner --exit-on-error < "$DUMP"
echo "Restore took $(( $(date +%s) - start )) seconds"

echo "4. Verify"
uv run python scripts/verify_restore.py \
  "postgresql://mimir:mimir@localhost:5432/mimir" \
  "postgresql://postgres:drill@localhost:5433/mimir"
```

A successful `pg_restore` only proves the commands ran. The verification step checks the result, by comparing every table's row count and the Alembic version between the original and the copy:

```python
# scripts/verify_restore.py: compare two databases table by table.
# usage: uv run python scripts/verify_restore.py ORIGINAL_URL RESTORED_URL
import sys

import psycopg
from psycopg import sql


def snapshot(url: str) -> tuple[dict[str, int], str]:
    """Return ({table: row count}, alembic version) for the public schema."""
    with psycopg.connect(url) as conn:
        tables = [row[0] for row in conn.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_type = 'BASE TABLE' ORDER BY table_name"
        )]
        counts = {}
        for table in tables:
            # sql.Identifier quotes the name safely; never build SQL with f-strings.
            query = sql.SQL("SELECT count(*) FROM {}").format(sql.Identifier(table))
            counts[table] = conn.execute(query).fetchone()[0]
        version = conn.execute("SELECT version_num FROM alembic_version").fetchone()[0]
    return counts, version


original, original_version = snapshot(sys.argv[1])
restored, restored_version = snapshot(sys.argv[2])

ok = original == restored and original_version == restored_version
for table in sorted(original.keys() | restored.keys()):
    a, b = original.get(table), restored.get(table)
    print(f"{'ok  ' if a == b else 'DIFF'} {table:24} {a!s:>8} {b!s:>8}")
print(f"alembic version: {original_version} -> {restored_version}")
print("RESTORE VERIFIED" if ok else "RESTORE FAILED")
sys.exit(0 if ok else 1)
```

Run it once as written. Then break it on purpose, so you've seen each failure before it matters: restore into plain `postgres:17` instead of the pgvector image (the restore fails at `CREATE EXTENSION vector`), or delete a few rows from the original between the dump and the check (the script reports `DIFF`). Row counts are a quick check, not a complete one. For a project that matters, also spot-check a few real records, and run your app's smoke test against the restored copy.

The same dump works against a managed database. Give `pg_dump` the provider's external connection URL, which starts with `postgresql://`, not the `postgresql+psycopg://` form SQLAlchemy uses. Run it from a container whose Postgres version is at least the server's, for example `docker run --rm postgres:17 pg_dump "$RENDER_EXTERNAL_URL" --format=custom > backups/render.dump`. Restoring that file into a new Neon or Render database is exactly how you move providers, or rescue a free database before it expires.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Backup and Restore](https://www.postgresql.org/docs/current/backup.html) in the PostgreSQL documentation, the authoritative description of the three kinds of backup.
   - Read the chapter introduction and the section on SQL dumps closely. Skim the section on continuous archiving and point-in-time recovery for the idea; providers run that machinery for you.
1. Read [Zero-downtime Postgres schema migrations need lock_timeout and statement_timeout](https://postgres.ai/blog/20210923-zero-downtime-postgres-schema-migrations-lock-timeout-and-retries) from Postgres.ai. It explains the lock queue trap with diagrams, and how retries make a short lock timeout practical.
1. Read the documentation for [PgBouncer's pooling modes](https://www.pgbouncer.org/features.html), so you know what session, transaction and statement pooling each break.
   - Then skim the connection pooling page of one provider you might use, such as [Neon's connection pooling guide](https://neon.com/docs/connect/connection-pooling), and find its pooled URL and its connection limits.
1. Practice: run a restore drill.
   - Seed your LLM-Powered API's Compose database with at least a few hundred rows across its tables (a short script is fine).
   - Add `restore_drill.sh` and `verify_restore.py` to your repo, run the drill, and paste the output, including the restore time, into a `RESTORE.md` runbook.
   - Break it in each of the two ways described in [A restore drill](#a-restore-drill), and write one sentence in the runbook on what each failure looked like.
   - Write down your app's RPO and RTO, and which backups (yours and your provider's) meet them.
1. Practice: a lock-safe migration.
   - In the same project, write an Alembic migration that adds an index with `CREATE INDEX CONCURRENTLY` and a lock timeout, and a second one that makes a column `NOT NULL` with the `CHECK ... NOT VALID` steps. Run `uv run alembic upgrade head`, then `downgrade -1` twice and `upgrade head` again.
1. If your Render free database from Deploying Your API is still running, dump it and restore it into a second free database (a new Render database or a Neon project), point your app at the copy, and check that the smoke test passes. You'll have practiced a real provider migration.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What does a managed Postgres service do for you, and what stays your job?](#what-a-managed-database-does-for-you)
- [Which questions should you ask when choosing between Render, Neon, Supabase and Cloud SQL?](#choosing-a-provider)
- [Why can an app with several instances run out of database connections, and how do pool sizes and a pooler help?](#connection-pooling)
- [Why can even an instant ALTER TABLE freeze a busy table, and what does a lock timeout do about it?](#how-migrations-lock-tables)
- [What are the steps of expand and contract for renaming a column, and why does it keep rollbacks safe?](#expand-and-contract)
- [What is the difference between a logical backup and point-in-time recovery, and what do RPO and RTO measure?](#backups-and-point-in-time-recovery)
- [Why isn't a successful pg_restore enough to prove that a backup works?](#a-restore-drill)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Explicit Locking](https://www.postgresql.org/docs/current/explicit-locking.html) in the PostgreSQL docs lists every lock mode and which commands take it, the reference behind the table in this lesson.
- [pg_dump](https://www.postgresql.org/docs/current/app-pgdump.html) and [pg_restore](https://www.postgresql.org/docs/current/app-pgrestore.html) document every option, including dumping or restoring single tables.
- [Squawk](https://squawkhq.com/) is an open-source linter that reads migration SQL and warns about statements that take dangerous locks. It can run in CI.
- [Parallel Change](https://martinfowler.com/bliki/ParallelChange.html) by Martin Fowler describes expand and contract in general terms, beyond databases.
- [Neon's guide to branching](https://neon.com/docs/introduction/branching) shows how copy-on-write branches give you a full copy of production data for testing a risky migration first.
