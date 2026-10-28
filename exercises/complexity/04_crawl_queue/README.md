# 04 · Crawl a docs site with a queue

**Lesson:** [Complexity and Core Data Structures](https://espinovah.github.io/project-mimir/#/lessons/foundations/complexity-and-core-data-structures)

## Task

A RAG system often starts by crawling a documentation site. `crawl_order(start, links)` visits pages **breadth first**: the start page, then every page it links to, then the pages those link to, and so on. `links` maps each page to the pages it links to, in order. Each page is visited once, even if many pages link to it. Return the pages in the order they were visited.

```python
links = {
    "index": ["install", "guide"],
    "install": ["guide", "faq"],
    "guide": ["api"],
}
crawl_order("index", links)   # ['index', 'install', 'guide', 'faq', 'api']
```

Pages that aren't keys in `links` have no outgoing links.

The starter is correct, but its queue is a list, and it takes the next page with `queue.pop(0)`. Fix it so a site with 200,000 pages crawls in well under a second.

## How the speed is tested

One test crawls an index page that links to 200,000 pages. The starter takes several seconds, because every `pop(0)` shifts the whole list. A fixed version takes a few hundredths of a second. The limit is a generous half second.

## Hints

- `collections.deque` is a queue with O(1) `append` and `popleft`.
- The `seen` set in the starter is already the right structure. Leave it.
- Mark a page as seen when you **add** it to the queue, not when you visit it, or it can be queued twice.

## Run the tests

```bash
cd exercises
uv run pytest complexity/04_crawl_queue
```

Before you change any code, write a comment at the top of the file with the Big-O of the starter and of the version you plan to write. Stuck? Make the tests pass first, then compare with `solution/crawl_queue.py`.
