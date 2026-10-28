def drop_empty_replies(replies: list[str]) -> list[str]:
    """Return a new list without empty or whitespace-only replies. Don't modify `replies`."""
    for reply in replies:
        if not reply.strip():
            replies.remove(reply)
    return replies
