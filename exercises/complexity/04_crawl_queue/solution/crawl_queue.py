# Starter: list.pop(0) is O(n), so the crawl was O(n^2) overall.
# This version: deque.popleft() is O(1), so the crawl is O(pages + links).
from collections import deque


def crawl_order(start: str, links: dict[str, list[str]]) -> list[str]:
    """Return pages in breadth-first order from start, visiting each page once."""
    queue = deque([start])
    seen = {start}
    order = []
    while queue:
        page = queue.popleft()
        order.append(page)
        for nxt in links.get(page, []):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return order
