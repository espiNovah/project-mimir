# 06 · JSON from a model reply

**Lesson:** [Regular Expressions](https://espinovah.github.io/project-mimir/#/lessons/foundations/regular-expressions)

## Task

You asked a model for JSON. Sometimes you get plain JSON, and sometimes it's wrapped in a Markdown code fence with a sentence around it:

~~~text
Sure! Here is the data:

```json
{"label": "billing", "confidence": 0.9}
```
~~~

As the lesson says, a regex is fine for stripping the fence, but the inside should go to `json.loads`. Write `parse_json_reply(reply)`:

- If the reply contains a fenced block (three backticks, optionally followed by `json`), parse the text inside the **first** fence.
- Otherwise, parse the whole reply (after stripping whitespace).
- If what you parse isn't valid JSON, let `json.loads` raise its `json.JSONDecodeError`.

```python
parse_json_reply('{"label": "billing"}')                   # {'label': 'billing'}
parse_json_reply('Here:\n```json\n{"label": "bug"}\n```')  # {'label': 'bug'}
```

## Hints

- By default `.` doesn't match a newline. The flag `re.DOTALL` changes that, and you need it because the JSON spans several lines.
- Use a lazy quantifier, `.*?`, so the match stops at the first closing fence rather than the last one.
- `(?:json)?` makes the language tag optional without creating a group.
- Don't try to parse the JSON itself with a regex.

## Run the tests

```bash
cd exercises
uv run pytest regex/06_json_from_reply
```

Stuck? Make the tests pass first, then compare with `solution/json_from_reply.py`.
