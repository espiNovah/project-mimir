# 04 · Prompt builder

**Lesson:** [Pythonic Python](https://espinovah.github.io/project-mimir/#/lessons/foundations/pythonic-python)

## Task

Practice `*args` and `**kwargs` with two helpers you'd find in a real LLM app:

- `build_prompt(*parts, sep="\n\n", **variables)` joins any number of text parts (skipping empty ones) with `sep`, then fills `{placeholders}` using the keyword arguments.
- `call_with_defaults(func, *args, **kwargs)` calls `func` with everything it was given, but adds `temperature=0.0` if the caller didn't pass a temperature.

```python
build_prompt("Hello {name}.", "", "Bye.", name="Ada")   # "Hello Ada.\n\nBye."
call_with_defaults(fake_model, "hi")                     # fake_model("hi", temperature=0.0)
```

## Hints

- Inside the function, `parts` is a tuple and `variables` is a dict.
- `"Hi {name}".format(**{"name": "Ada"})` unpacks a dict into keyword arguments.
- `dict.setdefault(key, value)` only sets the key if it's missing.

## Run the tests

```bash
cd exercises
uv run pytest pythonic-python/04_prompt_builder
```

Stuck? Make the tests pass first, then compare with `solution/`.
