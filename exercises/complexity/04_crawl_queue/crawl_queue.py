def crawl_order(start: str, links: dict[str, list[str]]) -> list[str]:
    """Return pages in breadth-first order from start, visiting each page once."""
    queue = [start]
    seen = {start}
    order = []
    while queue:
        page = queue.pop(0)
        order.append(page)
        for nxt in links.get(page, []):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return order
