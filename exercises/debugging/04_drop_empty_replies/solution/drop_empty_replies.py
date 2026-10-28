# Bug: removing items from the list while looping over it shifts the remaining items left,
# so the loop skips the item after each removal. It also changed the caller's list.
# Build a new list instead.


def drop_empty_replies(replies: list[str]) -> list[str]:
    """Return a new list without empty or whitespace-only replies. Don't modify `replies`."""
    return [reply for reply in replies if reply.strip()]
