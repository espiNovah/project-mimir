### Introduction

Most engineering interview loops include a **system design** round. Instead of writing code, you get a vague prompt like "design a URL shortener" or "design a notification service," a whiteboard (usually a shared drawing tool), and about 45 minutes. You talk through how you'd build it: which boxes, which arrows, what happens when traffic grows a hundredfold, and what breaks first.

AI engineering roles increasingly add an AI-specific version of this round, which the next lesson covers. Many loops still include the general one, though, and the AI version is built on the same parts: load balancers, caches, queues and databases. The good news is that you've already used most of these parts. You put an API behind a load balancer in Deploying Your API, ran Postgres in Persisting Data with Postgres, moved slow work off the request path in Job Queues and Workers, and wrote retry and rate-limit logic in Timeouts, Retries and Rate Limits. This lesson gives you the vocabulary and a repeatable routine for talking about those parts at a larger scale, out loud, under time pressure.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What a system design round looks like and what it grades.
- A six-step approach you can reuse on any prompt.
- Back-of-the-envelope estimates for traffic and storage.
- Load balancers, stateless services, caching and queues.
- SQL versus NoSQL, replication and sharding, at a conceptual level.
- Consistency and availability trade-offs, and rate limiting.
- A worked example: a URL shortener from requirements to deep dive.

### What the interview tests

A system design round has no single correct answer, and interviewers know you can't build a real system in 45 minutes. They're watching how you think. Most rubrics, whatever the company calls them, grade four things:

- **Problem navigation.** Do you turn a vague prompt into clear requirements, or do you start drawing boxes at once?
- **A working design.** Does your high-level design actually meet the requirements, end to end?
- **Depth and trade-offs.** Can you go deep on one or two parts and explain why you chose one option over another, including what your choice costs?
- **Communication.** Can the interviewer follow you? Do you check in, take hints, and adjust?

For a junior or career-changer candidate, the bar is lower than for a senior engineer. Nobody expects you to know how a database stores pages on disk. They do expect a sensible, complete design, honest trade-offs, and the habit of asking "what happens when this fails?" That habit is exactly what you built in the Production path.

Two traps sink most beginners. The first is **diving into details too early**, such as spending 15 minutes on the database schema before there's a design at all. The second is **name-dropping without reasons**: "we'll use Kafka and Cassandra" means nothing unless you can say what problem each one solves here. A design made of boring, well-justified parts beats a design made of fashionable ones.

### A repeatable approach

Use the same six steps every time, and say them out loud at the start so the interviewer knows where you're going. Times are for a 45-minute round. Adjust them if the round is shorter.

1. **Requirements and scale (about 5 minutes).** Split them in two. **Functional requirements** are what the system does: "users can create a short link" and "visiting the short link redirects to the original." **Non-functional requirements** are how well it does it: latency, availability, consistency and scale. Ask how many users and requests there are, and whether reads or writes dominate. Write the answers down where the interviewer can see them. Pick three or four functional requirements and explicitly set the rest aside ("I'll leave analytics out unless you want it").
1. **API (about 3 minutes).** Write the main endpoints as you would in FastAPI: method, path, inputs and outputs. This pins down what the system actually does and often surfaces missing requirements.
1. **Data model (about 3 minutes).** List the main **entities** (the things you store, such as users, links and clicks) and their key fields. You don't need a full schema yet.
1. **High-level design (about 10 minutes).** Draw the simplest set of boxes that satisfies every functional requirement: client, load balancer, service, database. Walk one request through it from start to finish. Don't optimize yet.
1. **Deep dive (about 15 minutes).** Now return to the non-functional requirements. Where does the design fail at the stated scale? Pick the one or two hardest problems and solve them properly. The interviewer will often steer you here, so follow their lead.
1. **Trade-offs and wrap-up (about 5 minutes).** Summarize what you built, what you gave up, and what you'd do next: monitoring, failure handling, and the parts you skipped.

This mirrors the talk-out-loud routine from Coding Interviews: clarify, solve simply, then improve. The simple design comes first because it proves you can solve the problem at all, and because every improvement needs something to improve on.

### Back-of-the-envelope estimates

Interviewers often ask "roughly how much traffic is that?" A **back-of-the-envelope estimate** is quick, rounded arithmetic that tells you the order of magnitude: whether you need one server or a thousand, one database or a cluster. Being off by a factor of two doesn't matter. Being off by a factor of a thousand does.

A few numbers make the arithmetic easy:

- A day has 86,400 seconds. Round it to **100,000 (10⁵)**. A month is roughly **2.5 million seconds**.
- **Peak traffic** is usually 2 to 5 times the average. Design for the peak.
- Reading from memory takes well under a microsecond, a network round trip inside a data center takes roughly half a millisecond, and a disk seek or a cross-continent round trip takes tens of milliseconds or more. The famous "latency numbers every programmer should know" list in the Assignment has the details.
- A single well-written API server handles hundreds to a few thousand simple requests per second. A single Postgres instance on good hardware handles thousands of simple queries per second, and stores terabytes.

Here's an example. "100 million new short links a month, and each is read 100 times on average." Writes: 100,000,000 ÷ 2,500,000 seconds ≈ **40 writes per second**. Reads: 100 × 40 = **4,000 reads per second**, or up to 20,000 at peak. Storage: say 500 bytes per link, so 100 million × 500 bytes = 50 GB a month, or about **3 TB over five years**.

Now say what the numbers mean: "40 writes per second is easy for one database. 20,000 reads per second at peak is a lot for one database but easy for a cache. 3 TB fits on one machine but is getting big, so I'll mention sharding later." The arithmetic is only useful once you turn it into a design decision.

### Load balancers and stateless services

A **load balancer** sits in front of a group of identical servers and spreads incoming requests across them. It also runs **health checks**: it pings each server regularly and stops sending traffic to any that fail. You've already used one, because Render, Fly and Cloud Run all put a managed load balancer in front of your app. Common strategies are round robin (take turns) and least connections (send to the least busy server).

Adding servers behind a load balancer is called **horizontal scaling**. Buying a bigger machine is **vertical scaling**. Vertical scaling is simpler and works surprisingly far, but it has a ceiling and leaves a single point of failure. Horizontal scaling has no practical ceiling, but it only works if your servers are **stateless**: no request depends on something stored in one particular server's memory or local disk. If a user's session lives in server A's memory and the next request goes to server B, the user is logged out.

The fix is to push state out into shared stores: sessions and short-lived data in Redis, durable data in Postgres, files in object storage such as S3. That's the "processes are stateless" rule from the twelve-factor app, and it's why your FastAPI app read everything it needed from the database or the request. In an interview, saying "the API servers are stateless, so we can add more behind the load balancer as traffic grows" answers a whole class of scaling questions in one sentence.

### Caching and invalidation

A **cache** keeps a copy of data somewhere faster than its original source, usually in memory. When most traffic is reads, and the same items are read again and again, a cache takes most of the load off the database. Caches appear at many layers: in the browser, at a **CDN** (content delivery network, a set of servers around the world that hold copies of static files close to users), in Redis next to your service, and inside the database itself.

The most common pattern is **cache-aside**. The service checks the cache first. On a **hit**, it returns the cached value. On a **miss**, it reads from the database, stores the result in the cache, and returns it. The fraction of requests served from the cache is the **hit rate**, and it's the number that matters: a 95% hit rate means the database sees only 5% of the reads.

The hard part is **invalidation**: making sure the cache doesn't serve stale data after the original changes. Three standard answers:

- **A TTL (time to live).** Every entry expires after, say, five minutes. It's simple, and data is at most five minutes stale. Ask whether that's acceptable.
- **Delete on write.** When the service updates the database, it deletes the cache entry, so the next read fetches the fresh value.
- **Write-through.** The service writes to the cache and the database together. Reads are always fresh, but writes are slower.

Also mention **eviction**: a cache has limited memory, so when it fills up it removes something, usually the least recently used entry (LRU). And watch for the **thundering herd**: when a very popular entry expires, thousands of requests miss at once and all hit the database together. Common fixes are letting one request refill the entry while others wait, or adding a little random jitter to TTLs so entries don't all expire at the same moment. You met response caching and semantic caching for model calls in Caching and Model Choice. The same ideas apply here, just with database rows instead of model outputs.

### Queues and async work

Some work shouldn't happen while the user waits: sending an email, resizing an image, calling a slow model, or fanning one event out to a million followers. A **message queue** lets the request handler drop a job on the queue and return immediately, while separate **workers** pull jobs off and process them. This is exactly what you built with Redis and arq in Job Queues and Workers.

Queues give you three things worth naming in an interview:

- **Faster responses.** The user gets "accepted" in milliseconds instead of waiting for slow work.
- **Absorbing spikes.** If traffic jumps tenfold for a minute, the queue grows and the workers catch up afterward, instead of the system falling over. The queue acts as a buffer.
- **Independent scaling and retries.** You can add workers without touching the API, and a failed job can be retried without the user resubmitting.

The cost is complexity. Most queues guarantee **at-least-once delivery**, meaning a job may run twice (for example, if a worker crashes after doing the work but before confirming it). So jobs must be **idempotent**: running one twice has the same effect as running it once. You used idempotency keys for this in Timeouts, Retries and Rate Limits and Durable Execution. Jobs that keep failing go to a **dead-letter queue** for a human to inspect, rather than retrying forever. And always say how you'd monitor **queue depth**: a queue that keeps growing means the workers can't keep up.

### Choosing a database

You'll often be asked "SQL or NoSQL?" A **relational (SQL) database** such as Postgres stores data in tables with a fixed schema, supports joins across tables, and offers **transactions**, which make a group of changes happen all together or not at all. **NoSQL** is a loose name for everything else. The main kinds are key-value stores (Redis, DynamoDB), document stores (MongoDB), and wide-column stores (Cassandra). They typically give up joins and some transaction guarantees in exchange for a flexible schema or easier horizontal scaling.

A good default answer: **start with Postgres unless you have a specific reason not to.** It handles relational data, JSON documents (with its `jsonb` type), full-text search and vectors (with pgvector), and it scales further than most interview prompts need. Reasons to reach for something else include a pure key-value access pattern at very high write volume, where a key-value store is simpler to scale, or a need for very fast reads of temporary data, where Redis is the right tool alongside the main database. Whatever you pick, justify it from the access patterns you wrote down in the data-model step, not from popularity.

### Replication and sharding

At some point one database machine isn't enough, either because it can't handle the reads, can't handle the writes, can't hold the data, or is a single point of failure. Two techniques address this, and you only need them at the level of a diagram.

**Replication** keeps copies of the same data on several machines. In the common setup, one **primary** accepts writes and streams changes to one or more **read replicas**. Reads can go to the replicas, which multiplies read capacity, and if the primary dies a replica can be promoted to take over. You saw this with managed Postgres in Managed Postgres and Backups. The catch is **replication lag**: a replica may be a fraction of a second behind, so a user who just updated their profile might read the old version from a replica. A standard fix is to send a user's reads to the primary for a short time after they write.

**Sharding** (also called partitioning) splits the data itself across machines. Each shard holds a subset, such as users whose ID hashes to shard 1, 2 or 3. Sharding scales writes and storage, which replication doesn't. It also makes life harder: queries that span shards are slow, and choosing a **shard key** matters a lot. A good key spreads load evenly and keeps data that's queried together on the same shard. A bad key creates a **hot shard**: if you shard by country, the shard for the biggest country gets most of the traffic. In an interview, mention sharding only when your estimates call for it, and name the shard key and why you chose it.

### Consistency and availability

When data lives on several machines, they can disagree for a moment. **Strong consistency** means every read sees the latest write. **Eventual consistency** means replicas catch up "soon," and reads in the meantime may be stale.

The **CAP theorem** is the formal version of this trade-off. When a **network partition** happens, meaning some machines can't reach others, a distributed system must choose between staying **consistent** (refusing some requests rather than risking stale answers) and staying **available** (answering everything, even if some answers are stale). Partitions are rare but unavoidable, so the real question for each piece of data is: when things go wrong, is it worse to be wrong or to be down?

Answer that per feature, not for the whole system. A bank balance or an inventory count for the last item in stock needs strong consistency. A like count, a follower list or a "last seen" timestamp can be eventually consistent, because a few seconds of staleness hurts nobody. Saying "I'd keep payments strongly consistent in Postgres, but the view counter can be eventually consistent and live in Redis" shows exactly the judgment interviewers look for.

### Rate limiting

A **rate limiter** caps how many requests a client can make in a time window, such as 100 requests per minute per API key. It protects your service from abuse, from runaway client bugs and from one customer starving the others. When a client goes over the limit, the server returns HTTP 429 (Too Many Requests), ideally with a `Retry-After` header. You've been on the other side of this: model APIs rate-limit you, and you wrote backoff in Timeouts, Retries and Rate Limits.

The algorithm interviewers most often expect is the **token bucket**. Each client has a bucket that holds up to `capacity` tokens and refills at a steady rate. Each request takes one token, and if the bucket is empty, the request is rejected. It allows short bursts (up to the bucket size) while enforcing an average rate. Here it is in a few lines, runnable with `uv run bucket.py`:

```python
import time


class TokenBucket:
    """Allow `rate` requests per second on average, with bursts up to `capacity`."""

    def __init__(self, rate: float, capacity: int):
        self.rate = rate
        self.capacity = capacity
        self.tokens = float(capacity)  # start full
        self.updated = time.monotonic()

    def allow(self) -> bool:
        now = time.monotonic()
        # Refill based on how much time has passed, without exceeding capacity.
        self.tokens = min(self.capacity, self.tokens + (now - self.updated) * self.rate)
        self.updated = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


bucket = TokenBucket(rate=2, capacity=5)  # 2 per second, bursts of 5
burst = [bucket.allow() for _ in range(7)]
assert burst == [True] * 5 + [False] * 2  # the burst is capped at 5
time.sleep(1)
assert bucket.allow() and bucket.allow()  # about 2 tokens refilled after 1 second
print("all passed")
```

In a real system with many API servers, the bucket can't live in one server's memory, for the same reason sessions can't. The counts go in a shared store such as Redis, updated atomically. Mention that, plus where the limiter sits (at the load balancer or API gateway, or inside the service), and you've covered what most interviewers want.

### Worked example: a URL shortener

Here's the six-step approach applied to a classic prompt, compressed to its main points.

**Requirements.** Functional: create a short link for a long URL; visiting the short link redirects to the long URL; optionally a custom alias and an expiry date. Non-functional: redirects must be fast (under about 100 ms) and highly available, since a broken link is very visible; creating links can be a little slower. Scale is from the estimates section: 40 writes per second, about 4,000 reads per second on average and 20,000 at peak, and 3 TB over five years. Reads outnumber writes 100 to 1.

**API.** `POST /links` with `{"url": ..., "alias": optional, "expires_at": optional}` returns `{"short_url": ...}`. `GET /{code}` returns an HTTP 302 redirect to the long URL, or 404.

**Data model.** One table, `links`: `code` (primary key), `long_url`, `created_at`, `expires_at`, `owner_id`.

**High-level design.**

```text
                 +---------------+
  browser -----> | load balancer |
                 +-------+-------+
                         |
             +-----------+-----------+
             |  link service (x N)   |   stateless, add more as traffic grows
             +-----+-----------+-----+
                   |           |
        1. check   |           |  2. on a miss, read
                   v           v
            +-----------+   +----------------------+
            |   Redis   |   |  Postgres primary    | <- all writes
            |  (cache)  |   |  + 2 read replicas   | <- cache-miss reads
            +-----------+   +----------------------+
                                       |
           click events ---> queue ---> analytics worker (optional)
```

A redirect request goes through the load balancer to any link service instance, which checks Redis for the code. On a hit, it redirects immediately. On a miss, it reads from a Postgres replica, stores the result in Redis, and redirects. Creating a link writes to the Postgres primary.

**Deep dive 1: generating short codes.** Codes use base62 (a–z, A–Z, 0–9). Seven characters give 62⁷, about 3.5 trillion codes, far more than the 6 billion needed over five years. Option A: hash the long URL and take the first seven characters. It's simple, but different URLs can collide, so you must check and retry. Option B: a global counter, encoded in base62. It never collides, but the counter is a single point of contention and makes codes guessable. A common compromise is for each service instance to reserve a block of 1,000 counter values at a time from the database, so the counter is touched rarely. Say which you'd pick and why.

**Deep dive 2: fast, available redirects.** The cache is the main answer: popular links are read far more than others, so a hit rate above 90% is realistic, and Redis handles 20,000 reads per second easily. Links rarely change, so a long TTL is fine, and deleting the cache entry when a link is edited or expires handles invalidation. Read replicas absorb the misses and provide failover. Three terabytes fits on one Postgres primary for now; if growth continued, you'd shard by `code`, which spreads evenly because codes are effectively random.

**Trade-offs.** Click analytics go through a queue so they never slow down a redirect, and they're eventually consistent, which is fine. Creating links needs a rate limiter per user, because a URL shortener is a favorite tool for spammers. Also mention monitoring cache hit rate, redirect latency at the 99th percentile and queue depth, plus what you skipped (custom domains and abuse detection).

That's a complete answer. Notice that nothing in it is exotic. It's the parts from this lesson, chosen for reasons the estimates made visible.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Draw before you decorate

Get every box and arrow of the simple design on the board before adding caches, replicas or queues. If you run out of time with a complete simple design, you still pass the "working design" bar. If you run out of time halfway through a beautiful sharding scheme with no API, you don't.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Hello Interview's System Design in a Hurry](https://www.hellointerview.com/learn/system-design/in-a-hurry/introduction), starting with the introduction and then the [delivery framework](https://www.hellointerview.com/learn/system-design/in-a-hurry/delivery). The pages are free (the site sells premium extras you don't need). The framework is close to the six steps in this lesson and gives concrete phrasing for each one.
1. Read the [System Design Primer](https://github.com/donnemartin/system-design-primer), which is the classic free reference for every building block in this lesson.
   - Read the sections on load balancers, horizontal scaling, caching, asynchronism, databases (replication, sharding, SQL versus NoSQL) and the CAP theorem. Skip the rest for now.
1. Bookmark the [latency numbers every programmer should know](https://gist.github.com/jboner/2841832). You don't need to memorize them, but you should know which operations are nanoseconds, which are microseconds and which are milliseconds.
1. Read Stripe's [Scaling your API with rate limiters](https://stripe.com/blog/rate-limiters), a short practitioner write-up of the different kinds of limiters a real API runs and why.
1. Practice a full design. Set a 45-minute timer and design a **notification service** that sends email and push notifications to 10 million users (assume 50 million notifications a day, a mix of instant and scheduled messages). Use the six steps, write the estimates down with your arithmetic, and draw the diagram as a text block or on paper.
   - Then compare your design with the primer's [Pastebin solution](https://github.com/donnemartin/system-design-primer/blob/master/solutions/system_design/pastebin/README.md) and Hello Interview's [URL shortener breakdown](https://www.hellointerview.com/learn/system-design/problem-breakdowns/bitly). Neither is a notification service, but both show how a full answer moves from requirements to deep dives. Note one thing they did that you didn't.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What are the six steps of the repeatable approach, and why does the simple design come before the deep dive?](#a-repeatable-approach)
- [Roughly how many requests per second is 100 million requests a month, and how did you work it out?](#back-of-the-envelope-estimates)
- [Why must services be stateless before you can scale them horizontally?](#load-balancers-and-stateless-services)
- [What are three ways to keep a cache from serving stale data, and what does each cost?](#caching-and-invalidation)
- [Why do queued jobs need to be idempotent?](#queues-and-async-work)
- [What problem does sharding solve that replication doesn't, and what makes a good shard key?](#replication-and-sharding)
- [Which data in a shopping app would you keep strongly consistent, and which could be eventually consistent?](#consistency-and-availability)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The Tech Interview Handbook's system design page](https://www.techinterviewhandbook.org/system-design/) collects further free guides and practice prompts, from the same site as the coding interview resources.
- [AWS's caching best practices](https://aws.amazon.com/caching/best-practices/) covers cache-aside, write-through, TTLs and the thundering herd in more depth, and the advice applies to any cache.
- [The Google SRE book's chapter on handling overload](https://sre.google/sre-book/handling-overload/) explains how a large production system decides which requests to reject when it can't serve them all, a good next step after rate limiting.
- [The twelve-factor app's page on processes](https://12factor.net/processes) is the short, classic statement of why services should be stateless.
