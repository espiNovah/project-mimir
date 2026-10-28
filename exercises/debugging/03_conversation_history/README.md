# 03 · Conversation history

**Lesson:** [Debugging and Logging](https://espinovah.github.io/project-mimir/#/lessons/foundations/debugging-and-logging)

## The bug report

`start_conversation(system)` creates a new chat history: a list of message dicts that starts with the system message. `add_message(history, role, content)` appends a message and returns the history.

A user reports that their second conversation "remembers" what was said in the first one:

```python
a = start_conversation("You are a helpful tutor.")
add_message(a, "user", "What is 2 + 2?")

b = start_conversation("You are a pirate.")
print(len(b))   # expected 1, prints 3
```

Each call to `start_conversation` must return a brand-new list, unless the caller passes one in on purpose.

## How to work on it

1. Run the tests and read the failures. Which input breaks, and what came out instead?
1. Set a breakpoint (or add `breakpoint()`) and watch the variables until you see where the program stops doing what you expect.
1. Write one sentence at the top of the file saying what the bug was, then fix it.

## Run the tests

```bash
cd exercises
uv run pytest debugging/03_conversation_history
```

Stuck? Make the tests pass first, then compare with `solution/conversation_history.py`.
