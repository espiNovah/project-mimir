### Introduction

Now that you can describe the shape of your data, you need the model to actually produce it. There are three ways to do that: ask nicely in the prompt and hope, use the provider's native *structured outputs* feature that forces the response to match a schema, or use a library that wraps either approach with validation and retries. This lesson covers all three, and when each one is the right call. You'll finish with a small, reusable extraction function that you'll build on in the Messy-Text Extractor project.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why prompt-only JSON breaks in production.
- How native schema-constrained output works.
- How to get structured output through a tool definition.
- How to feed validation errors back to the model in a retry loop.
- How libraries such as Instructor package the same loop.
- The difference between a valid shape and a correct answer.
- How to design schemas that help the model rather than trap it.

### Why prompt-only JSON breaks

The obvious approach is to write "Respond only with JSON in this format: ..." and call `json.loads` on the reply. Try it a few times and it will seem to work. Run it a few thousand times and you'll collect a zoo of failures: a friendly sentence before the JSON ("Sure! Here's the data:"), the JSON wrapped in a markdown code fence, a trailing comma, a field renamed from `start_date` to `date`, a number written as `"about 40"`, or the answer cut off halfway because it ran out of tokens.

Each failure is rare, maybe one or two percent of calls. But "rare" is a problem at scale. If your app processes 5,000 documents a day, a 1% failure rate is 50 crashes a day. You can patch around some of these with string cleanup, but you're guessing at what the model might do next. You want a guarantee.

### Native structured outputs

Most major providers now offer *structured outputs*, sometimes called *constrained decoding*. You send a JSON Schema along with the request. While the model generates its answer one token at a time, the provider only allows tokens that keep the output valid under your schema. The model literally can't write a stray sentence or forget a closing brace, so the reply always parses and always has the right fields and types.

With Claude's Python SDK, you can pass a Pydantic model directly. Create a project with `uv init`, run `uv add anthropic pydantic python-dotenv`, and try this:

```python
import os
from typing import Literal

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
client = anthropic.Anthropic()


class Ticket(BaseModel):
    summary: str = Field(description="One sentence describing the problem")
    category: Literal["billing", "bug", "account", "other"]
    urgent: bool


response = client.messages.parse(
    model=MODEL,
    max_tokens=2000,
    messages=[{
        "role": "user",
        "content": "Classify this support email:\n\nhi, i was charged TWICE "
                   "for march and my rent is due tomorrow, please fix asap!!",
    }],
    output_format=Ticket,          # the SDK sends Ticket's schema with the request
)

ticket = response.parsed_output    # a validated Ticket object, not a string
print(ticket.category, ticket.urgent)
print(ticket.summary)
```

`messages.parse()` converts your model to a JSON Schema, sends it in the request's `output_config.format` field, and validates the reply into a `Ticket` for you.

Three things to know about this guarantee:

- **Only a subset of JSON Schema is supported.** Claude's structured outputs, for example, don't enforce numeric bounds (`minimum`, `maximum`) or string lengths. The SDK moves those into the field descriptions and checks them after the response arrives. Your Pydantic validators, which the model never sees, are also only checked afterward. So a reply can be schema-valid and still fail *your* validation.
- **Some responses can't match.** If the model refuses a request, or hits `max_tokens` partway through, the output may not match the schema. Check `response.stop_reason` before trusting the result.
- **It's provider-specific.** `messages.parse()` and `output_config.format` are Claude's names for this feature. The idea is the same everywhere, and OpenAI, Google and Ollama offer equivalents, but parameter names and supported keywords differ. Check your provider's list of supported schema features; [On other providers](#on-other-providers) compares them.

### Structured output through a tool

Before native structured outputs existed, the standard trick was to define a *tool* (a function the model can ask your code to call) whose input schema is the shape you want. When the model "calls" the tool, its arguments are your structured data. You'll learn tool use properly in the Agentic Systems path, but it's worth seeing now, because you'll meet this pattern in older code and in providers without native structured outputs.

```python
# Continues from the example above (same client, MODEL and Ticket).
from anthropic import transform_schema

record_tool = {
    "name": "record_ticket",
    "description": "Save the classified support ticket.",
    "strict": True,                          # arguments must match the schema exactly
    "input_schema": transform_schema(Ticket),
}

response = client.messages.create(
    model=MODEL,
    max_tokens=2000,
    tools=[record_tool],
    messages=[{
        "role": "user",
        "content": "Use the record_ticket tool to classify this email:\n\n"
                   "my password reset link says expired every time",
    }],
)

call = next((b for b in response.content if b.type == "tool_use"), None)
if call is None:
    raise RuntimeError("The model answered in text instead of calling the tool")
ticket = Ticket.model_validate(call.input)   # validate the arguments ourselves
print(ticket)
```

`strict: True` (Claude-specific; OpenAI has a similar flag) gives tool arguments the same schema guarantee as native structured outputs. Note the check for a missing `tool_use` block. Some providers let you *force* a tool call, but several newer Claude models reject forced tool choice, so the portable approach is to ask for the tool in the prompt and handle the case where the model doesn't use it. For plain extraction, prefer native structured outputs. Reach for tools when the model should decide *whether* to produce structured data, or choose between several shapes.

### Retrying with validation errors

Native structured outputs guarantee the *shape*. They can't guarantee your custom rules, like "the end date must be on or after the start date." When validation fails, the best fix is surprisingly simple: show the model its previous answer and the exact `ValidationError`, and ask it to try again. Pydantic's error messages say which field is wrong and why, which is exactly what the model needs.

This complete script extracts an event and retries at most twice. Save it as `extract_event.py`:

```python
import logging
import os
from datetime import date

import anthropic
from anthropic import transform_schema
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError, model_validator

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
MAX_RETRIES = 2                       # 1 first try + 2 retries = 3 calls at most

logging.basicConfig(level=logging.INFO, filename="extract.log")
log = logging.getLogger("extract")
client = anthropic.Anthropic()


class Event(BaseModel):
    name: str
    start_date: date
    end_date: date
    location: str | None = Field(default=None, description="City or venue; null if not stated")

    @model_validator(mode="after")
    def ends_after_start(self) -> "Event":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


# transform_schema() turns the Pydantic model into a schema the API accepts.
FORMAT = {"type": "json_schema", "schema": transform_schema(Event)}


def extract(text: str, doc_id: str = "?") -> Event:
    messages = [{
        "role": "user",
        "content": "Extract the event described below. Use null for anything "
                   f"the text doesn't state.\n\n<text>\n{text}\n</text>",
    }]
    for attempt in range(1 + MAX_RETRIES):
        response = client.messages.create(
            model=MODEL,
            max_tokens=2000,
            messages=messages,
            output_config={"format": FORMAT},
        )
        if response.stop_reason in ("max_tokens", "refusal"):
            raise RuntimeError(f"{doc_id}: stopped early ({response.stop_reason})")

        raw = next(b.text for b in response.content if b.type == "text")
        try:
            return Event.model_validate_json(raw)       # our own rules run here
        except ValidationError as err:
            log.warning("doc=%s attempt=%d error=%s", doc_id, attempt, err)
            # Show the model its own answer and exactly what was wrong with it.
            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": f"Your JSON failed validation:\n{err}\n\n"
                           "Fix these problems and return the corrected JSON.",
            })
    raise ValueError(f"{doc_id}: still invalid after {MAX_RETRIES} retries")


if __name__ == "__main__":
    post = ("PyData Lagos is back!! 3 days of talks + sprints, kicking off "
            "Nov 14th 2026 and wrapping up the 16th. Venue TBA, follow us for news")
    print(extract(post, doc_id="example-1"))
```

A few details worth copying into your own code:

- The loop builds a *conversation*: the original request, the model's failed answer (the full `response.content`, as you learned in System Prompts and Conversations), and a user message with the error. The model sees what it did and why it was wrong.
- Retries are **capped**. If three attempts fail, something is wrong with the input, the prompt or the schema, and calling again just burns money. Raise an error and move on.
- Every failure is **logged** with the document ID and attempt number, using the `logging` module from Debugging and Logging. Those logs are your raw material for error analysis: if one rule fails on a third of documents, fix the prompt or the schema rather than relying on retries.

To test this loop without spending money, use the fakes and `monkeypatch` techniques from Testing with pytest: replace `client` with a fake whose `messages.create` returns an invalid answer first and a valid one second, then assert that `extract` returns the valid one.

### Libraries that do it for you

You'll often see [Instructor](https://python.useinstructor.com/) used for this job. It wraps many providers behind one interface: you pass a Pydantic model and a `max_retries` number, and it extracts the output, validates it, and runs the same feed-the-error-back loop automatically. It's a good choice when you switch between providers or want less code. Writing the loop yourself once, as above, means you'll understand exactly what the library is doing, and you can debug it when it misbehaves.

### Valid is not correct

A guarantee that the output matches the schema says nothing about whether the values are *true*. Ask for an `email` field on a text that contains no email address, and a model under pressure may produce a plausible, made-up one, perfectly valid and completely wrong. Retries don't help here, because nothing failed validation.

The only way to know whether extraction is correct is to compare outputs against answers you labeled by hand, using the eval methods from the Measuring Quality section. That's what the Messy-Text Extractor project measures, field by field.

### Designing schemas for honesty

The schema is part of your prompt, so design it to make honest answers easy:

- **Allow "not present."** Make a field optional (`str | None = None`) when the information may be missing, and say "use null if not stated" in the prompt. Required fields with no escape hatch push a model to invent data.
- **Give enums an exit.** Add `"other"` or `"unknown"` to categories so the model isn't forced into a wrong bucket. Structured outputs don't guarantee the *capitalization* of enum values on every provider, so compare labels case-insensitively.
- **Describe intent.** `Field(description="Total including tax, as printed")` removes guesswork that a bare name like `total` leaves in.
- **Order fields deliberately.** Models write fields in order, so a short `evidence` field that quotes the relevant sentence, placed before the answer, gives the model a moment to look before it commits. Keep it short. Current models already think before answering, and some providers may refuse a schema field that asks for the model's full step-by-step reasoning.

### On other providers

The ideas in this lesson transfer completely: constrain the shape, validate your own rules afterward, feed errors back with a capped, logged retry, and remember that valid is not correct. The names and fine print differ. OpenAI's version is also called **Structured Outputs**: in Chat Completions you pass `response_format={"type": "json_schema", "json_schema": {..., "strict": True}}`, or let the SDK do it with `client.chat.completions.parse(response_format=Ticket)` and read `message.parsed`, much like Claude's `parsed_output`. OpenAI's strict mode requires every field to be listed as required (an optional field becomes a type that allows `null`) and supports a different subset of keywords than Claude, including numeric bounds such as `minimum`. A safety refusal shows up in `message.refusal` instead of the parsed object, and a cut-off answer has `finish_reason == "length"`, the equivalent of Claude's `max_tokens` stop reason. The retry loop needs one change: append the failed answer as `{"role": "assistant", "content": message.content}`, since Chat Completions replies are a string, not a list of content blocks. The older **JSON mode** (`{"type": "json_object"}`) only guarantees valid JSON, not your schema, so treat it like prompt-only JSON plus validation. The tool route works too: OpenAI tools put the schema under `function.parameters`, also take `"strict": True`, and return the arguments as a JSON *string* in `message.tool_calls`. On open models, Ollama turns a schema in `response_format` (or its own `format` field) into **grammar-constrained decoding**, where the server masks out any token that would break the schema, the same technique as llama.cpp's [GBNF grammars](https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md). A small local model will always give you the shape, but its values are noticeably less accurate, which is why the Messy-Text Extractor project has you measure both. Read OpenAI's [structured outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs) (assigned below) and Ollama's [structured outputs page](https://docs.ollama.com/capabilities/structured-outputs). Instructor, from [Libraries that do it for you](#libraries-that-do-it-for-you), wraps all of these behind one call; its [Ollama page](https://python.useinstructor.com/integrations/ollama/) shows the local setup. Here is the ticket example on a local model:

```python
# ticket_other.py  (uv add openai pydantic; ollama pull qwen3:4b). Ticket is the model from above.
import os

from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")  # OpenAI(): reads OPENAI_API_KEY
completion = client.chat.completions.parse(
    model=os.environ.get("MIMIR_MODEL", "qwen3:4b"),  # or an OpenAI model ID
    messages=[{"role": "user", "content": "Classify this support email:\n\nhi, i was charged "
               "TWICE for march and my rent is due tomorrow, please fix asap!!"}],
    response_format=Ticket,           # the SDK sends Ticket's schema as a strict json_schema
)
message = completion.choices[0].message
if message.refusal or completion.choices[0].finish_reason != "stop":
    raise RuntimeError(f"no usable answer: {message.refusal or completion.choices[0].finish_reason}")
print(message.parsed)                 # a validated Ticket, as with Claude's parsed_output
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) in the Claude docs.
   - Read the overview, the JSON outputs examples (including the Pydantic version in Python), and the sections on JSON Schema limitations and invalid outputs. Skim the strict tool use part; you'll use tools in the Agentic Systems path.
1. Read [OpenAI's structured outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs) to see the same feature from another provider.
   - Focus on the introduction, the comparison with plain JSON mode and the list of supported schemas.
1. Read the [Instructor documentation home page](https://python.useinstructor.com/) and follow its quick start, then read its page on [retrying](https://python.useinstructor.com/concepts/retrying/).
   - Pay attention to how it handles validation errors and retries. Note that it works with many providers through the same code.
1. Practice: take the recipe model from the previous lesson, including its "no empty ingredient list" validator. Extract a recipe from five messy blog posts three ways: prompt-only JSON parsed with `json.loads`, native structured outputs with a retry loop like the one in this lesson, and Instructor.
   - Count, for each approach, how many outputs failed to parse, failed validation, or needed a retry.
   - Write one pytest test that checks your retry loop with a fake client, without calling the API.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Why is a 1% JSON failure rate a real problem in production?](#why-prompt-only-json-breaks)
- [How do native structured outputs guarantee that the reply matches a schema, and what can still go wrong?](#native-structured-outputs)
- [When would you get structured data through a tool instead of native structured outputs?](#structured-output-through-a-tool)
- [What goes into the retry message, and why should retries be capped and logged?](#retrying-with-validation-errors)
- [What does a library like Instructor add on top of a provider's API?](#libraries-that-do-it-for-you)
- [Why doesn't schema-valid output mean the extracted values are correct?](#valid-is-not-correct)
- [Name three ways to design a schema that discourages invented values.](#designing-schemas-for-honesty)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Pydantic's error reference](https://pydantic.dev/docs/validation/latest/errors/errors/) explains how to read and customize `ValidationError` messages, including turning them into JSON for logging.
