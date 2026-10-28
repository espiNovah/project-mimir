def start_conversation(system: str, messages: list | None = []) -> list[dict]:
    """Return a history list starting with the system message.

    If the caller passes `messages`, the system message is added to that list.
    Otherwise a new list is created.
    """
    messages.append({"role": "system", "content": system})
    return messages


def add_message(history: list[dict], role: str, content: str) -> list[dict]:
    """Append one message to history and return it."""
    history.append({"role": role, "content": content})
    return history
