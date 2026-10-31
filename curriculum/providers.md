### Provider Comparison

The lessons use the Anthropic Messages API, but the same ideas work on every major provider. The names and shapes differ, though. Keep this page open when you port code to the OpenAI API or to an open model served by Ollama. For which model to use, see [Current Models](#/models).

**Last checked:** 2026-10-31. These APIs change often. Before you rely on a detail, check the official docs linked in each section.

### The four APIs at a glance

| | Anthropic Messages | OpenAI Chat Completions | OpenAI Responses | Ollama (local) |
| --- | --- | --- | --- | --- |
| Python client | `anthropic.Anthropic()` | `openai.OpenAI()` | `openai.OpenAI()` | `openai.OpenAI(base_url="http://localhost:11434/v1/", api_key="ollama")` |
| Call | `client.messages.create(...)` | `client.chat.completions.create(...)` | `client.responses.create(...)` | Chat Completions or Responses |
| Docs | [Messages API](https://platform.claude.com/docs/en/api/messages) | [Chat Completions reference](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create) | [Migrate to Responses](https://developers.openai.com/api/docs/guides/migrate-to-responses) | [OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility) |

- **Chat Completions vs Responses.** OpenAI now recommends the Responses API for new work, and some newer OpenAI models support tool calling only through Responses. Chat Completions is still the shape most other providers copy, so this page covers both.
- **Ollama** implements Chat Completions and a stateless subset of Responses (no `previous_response_id`). The `api_key` is required by the client but ignored. Ollama also offers [Anthropic API compatibility](https://docs.ollama.com/api/anthropic-compatibility), so the Anthropic SDK can talk to a local model too.
- **Gemini** has an [OpenAI-compatible endpoint](https://ai.google.dev/gemini-api/docs/openai): use the OpenAI client with `base_url="https://generativelanguage.googleapis.com/v1beta/openai/"` and a Gemini API key. It supports streaming, function calling, images and structured output.

```python
import os
from openai import OpenAI

# The same code can target OpenAI, Ollama or Gemini; only these lines change.
client = OpenAI(base_url="http://localhost:11434/v1/", api_key="ollama")
MODEL = os.environ.get("MIMIR_MODEL", "llama3.2")
```

### Messages and the system prompt

| | Anthropic | Chat Completions | Responses |
| --- | --- | --- | --- |
| System prompt | Top-level `system=` parameter | A message with `role: "developer"` (or `"system"`) | Top-level `instructions=` |
| Roles in the list | `user`, `assistant` | `developer`/`system`, `user`, `assistant`, `tool` | Typed input items; messages use `user`, `assistant`, `developer` |
| Content | A string, or a list of typed blocks (`text`, `image`, `document`, `tool_use`, `tool_result`) | A string, or a list of content parts | A string, or a list of items |
| Output limit | `max_tokens` is **required** | `max_completion_tokens` is optional (`max_tokens` is deprecated) | `max_output_tokens` is optional |
| Conversation state | You resend the history | You resend the history | Resend it, or chain with `previous_response_id` (stored server-side) |

```python
# Anthropic
client.messages.create(model=MODEL, max_tokens=1024, system="Be brief.",
                       messages=[{"role": "user", "content": "Hi"}])
# Chat Completions (and Ollama)
client.chat.completions.create(model=MODEL, messages=[
    {"role": "developer", "content": "Be brief."}, {"role": "user", "content": "Hi"}])
# Responses
client.responses.create(model=MODEL, instructions="Be brief.", input="Hi")
```

Current Claude models reject `temperature`, `top_p` and `top_k` (a 400 error), so remove sampling settings when you port code to Claude. Older OpenAI code often sets them.

### Reading the response

| | Anthropic | Chat Completions | Responses |
| --- | --- | --- | --- |
| Text | Join the `text` blocks in `response.content` | `response.choices[0].message.content` | `response.output_text` (SDK helper) |
| Why it stopped | `response.stop_reason` | `response.choices[0].finish_reason` | `response.status` plus `response.incomplete_details.reason` |
| Normal finish | `end_turn` (or `stop_sequence`) | `stop` | `status == "completed"` |
| Hit the output limit | `max_tokens` | `length` | `incomplete`, reason `max_output_tokens` |
| Wants a tool | `tool_use` | `tool_calls` | `function_call` items in `response.output` |
| Refused or filtered | `refusal` | `content_filter`, or `message.refusal` with structured output | `incomplete`, reason `content_filter`; or a `refusal` content item |
| Other | `pause_turn` (server tool still running), `model_context_window_exceeded` | | |

Never assume the text is the first block. Claude can return thinking or tool blocks first, and a Responses `output` list can start with reasoning items.

### Tool calls

| | Anthropic | Chat Completions | Responses |
| --- | --- | --- | --- |
| Define a tool | `{"name", "description", "input_schema"}` | `{"type": "function", "function": {"name", "description", "parameters"}}` | `{"type": "function", "name", "description", "parameters"}` (flat) |
| The call | A `tool_use` block with `id`, `name`, and `input` (already a dict) | `message.tool_calls[i]` with `id` and `function.arguments` (a JSON **string**) | A `function_call` item with `call_id`, `name`, `arguments` (a JSON string) |
| Return the result | A `tool_result` block with `tool_use_id`, inside a **`user`** message | A message with `role: "tool"` and `tool_call_id` | A `function_call_output` item with `call_id` |
| Report a failure | `"is_error": true` on the `tool_result` | Put the error in the content string | Put the error in the output string |
| Parallel calls | On by default; return **all** results in one `user` message | On by default; one `tool` message per call; `parallel_tool_calls=False` to stop | On by default; `parallel_tool_calls=False` to stop |
| Force a tool | `tool_choice` `any`/`tool`, but some current Claude models reject forced choice | `tool_choice="required"` or a named function | Same as Chat Completions |

Ollama follows Chat Completions here, but its OpenAI-compatible endpoint ignores `tool_choice`. Small local models also call tools less reliably, so test your loop on them. See [Ollama tool calling](https://docs.ollama.com/capabilities/tool-calling).

```python
import json

# Chat Completions: arguments arrive as a string, so parse them.
for call in response.choices[0].message.tool_calls or []:
    args = json.loads(call.function.arguments)
    messages.append({"role": "tool", "tool_call_id": call.id,
                     "content": json.dumps(run_tool(call.function.name, args))})
```

Docs: [Claude tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview), [OpenAI function calling](https://developers.openai.com/api/docs/guides/function-calling).

### Structured output

| | Anthropic | Chat Completions | Responses | Ollama |
| --- | --- | --- | --- | --- |
| Schema-guaranteed output | `output_config={"format": {"type": "json_schema", "schema": ...}}` | `response_format={"type": "json_schema", "json_schema": {"name", "schema", "strict": True}}` | `text={"format": {"type": "json_schema", "name", "schema", "strict": True}}` | `response_format` with a JSON schema |
| Strict tool inputs | `"strict": true` on the tool | `"strict": true` in `function` | `"strict": true`; Responses tries strict mode by default | Not documented |
| JSON mode (valid JSON, any shape) | None; use a schema | `{"type": "json_object"}`; the prompt must mention "JSON" | `{"type": "json_object"}` | `response_format` JSON mode |
| SDK helper | `client.messages.parse(...)` | `client.chat.completions.parse(...)` | `client.responses.parse(...)` | OpenAI client helpers |

Strict modes on both providers need `"additionalProperties": false` on every object. OpenAI strict mode also needs every property listed in `required`; mark optional fields by allowing `null`. Validate the result yourself on open models.

Docs: [Claude structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs), [OpenAI structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs), [Ollama structured outputs](https://docs.ollama.com/capabilities/structured-outputs).

### Streaming

| | Anthropic | Chat Completions | Responses |
| --- | --- | --- | --- |
| Turn it on | `client.messages.stream(...)` or `stream=True` | `stream=True` | `stream=True` |
| Events | `message_start`, `content_block_start`, `content_block_delta`, `content_block_stop`, `message_delta`, `message_stop`, plus `ping` and `error` | Chunks with no event names; ends with `data: [DONE]` | `response.created`, `response.output_text.delta`, `response.completed`, `error` and more |
| Text deltas | `content_block_delta` with a `text_delta`, or the `stream.text_stream` helper | `chunk.choices[0].delta.content` | `response.output_text.delta` events |
| Tool argument deltas | `input_json_delta` | `delta.tool_calls[i].function.arguments` pieces | `response.function_call_arguments.delta` |
| Stop reason and usage | In `message_delta` | `finish_reason` on the last chunk; usage only with `stream_options={"include_usage": True}` | In `response.completed` |

```python
# Chat Completions and Ollama
for chunk in client.chat.completions.create(model=MODEL, messages=messages, stream=True):
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

Docs: [Claude streaming](https://platform.claude.com/docs/en/build-with-claude/streaming), [OpenAI streaming](https://developers.openai.com/api/docs/guides/streaming-responses).

### Usage and caching

| | Anthropic | Chat Completions | Responses |
| --- | --- | --- | --- |
| Input tokens | `usage.input_tokens` (**uncached part only**) | `usage.prompt_tokens` (includes cached) | `usage.input_tokens` (includes cached) |
| Output tokens | `usage.output_tokens` | `usage.completion_tokens` | `usage.output_tokens` |
| Cache reads | `usage.cache_read_input_tokens` | `usage.prompt_tokens_details.cached_tokens` | `usage.input_tokens_details.cached_tokens` |
| Cache writes | `usage.cache_creation_input_tokens` | `prompt_tokens_details.cache_write_tokens` | `input_tokens_details.cache_write_tokens` |
| How caching starts | **Opt-in**: a top-level `cache_control` (automatic) or `cache_control` on blocks (explicit breakpoints) | **On by default** for supported models; newer models also accept explicit breakpoints | Same as Chat Completions |

On Claude, total prompt size is `input_tokens + cache_creation_input_tokens + cache_read_input_tokens`. If you port a cost tracker, don't add OpenAI's `cached_tokens` on top of `prompt_tokens`; they are already counted there. Cache prices, minimum prefix sizes and lifetimes differ by model on both providers. Ollama runs locally, so there is no cache billing to track; when streaming, ask for usage with `stream_options={"include_usage": True}`.

Docs: [Claude prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching), [OpenAI prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching).

### Images and PDFs

| | Anthropic | Chat Completions | Responses | Ollama |
| --- | --- | --- | --- | --- |
| Image | `{"type": "image", "source": {"type": "base64", "media_type", "data"}}` (or a `url` source) | `{"type": "image_url", "image_url": {"url": ...}}` with a URL or a base64 data URL | `{"type": "input_image", "image_url": ...}` | `image_url` with a base64 data URL only; needs a vision model |
| PDF | `{"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data"}}` | `{"type": "file", "file": {"file_data" or "file_id"}}`, PDF only | `{"type": "input_file", ...}`, more file types | Not in the compatibility layer; extract the text yourself |

Docs: [Claude vision](https://platform.claude.com/docs/en/build-with-claude/vision), [Claude PDF support](https://platform.claude.com/docs/en/build-with-claude/pdf-support), [OpenAI images](https://developers.openai.com/api/docs/guides/images-vision), [OpenAI file inputs](https://developers.openai.com/api/docs/guides/file-inputs).

### Errors and rate limits

| | Anthropic | OpenAI |
| --- | --- | --- |
| Python error classes | `anthropic.BadRequestError`, `AuthenticationError`, `RateLimitError`, `InternalServerError`, `APIConnectionError`, base `APIStatusError` | `openai.` classes with the same names |
| Rate limited | 429, type `rate_limit_error` | 429, type `rate_limit_error` |
| Overloaded | 529, `overloaded_error` | 503 |
| Wait time | `retry-after` header in seconds, when present | `Retry-After` header in seconds, when present |
| Limit headers | `anthropic-ratelimit-requests-remaining`, `anthropic-ratelimit-input-tokens-remaining`, and similar; resets are RFC 3339 timestamps | `x-ratelimit-remaining-requests`, `x-ratelimit-remaining-tokens`, and similar; resets are durations such as `6m0s` |

Both SDKs retry connection errors, rate-limit errors and server errors on their own, twice by default, with a 10-minute default timeout. Because the class names match, a most-specific-first `except` chain ports by changing the module name. A local Ollama server has no rate limits, but it can be slow, so keep your timeouts.

Docs: [Claude errors](https://platform.claude.com/docs/en/api/errors), [Claude rate limits](https://platform.claude.com/docs/en/api/rate-limits), [OpenAI error codes](https://developers.openai.com/api/docs/guides/error-codes), [OpenAI rate limits](https://developers.openai.com/api/docs/guides/rate-limits).

### Porting checklist

1. Keep the model ID and base URL in config (`MIMIR_MODEL`, an env var for the base URL), never in code paths.
1. Move the system prompt: `system=` ↔ a `developer` message ↔ `instructions=`.
1. Set the output limit: Claude requires `max_tokens`; on OpenAI use `max_completion_tokens` or `max_output_tokens`.
1. Rewrite tool definitions (`input_schema` ↔ `parameters`) and parse OpenAI arguments with `json.loads`.
1. Change how tool results go back: `tool_result` blocks in one `user` message ↔ `tool` messages ↔ `function_call_output` items.
1. Map stop reasons: `end_turn`/`stop`, `max_tokens`/`length`, `tool_use`/`tool_calls`, and handle refusals.
1. Remove `temperature`/`top_p`/`top_k` when moving to current Claude models.
1. Fix usage math, especially cached tokens, and rerun your cost and eval numbers.
1. Swap error classes and rate-limit header names.
1. Rerun your eval set on the new provider. Same prompt, different model, different behavior.

### What doesn't carry over

- **Server-side tools.** Claude's web search, web fetch and code execution, and OpenAI's web search, file search and code interpreter (Responses only), run on the provider's servers with different names and result shapes. Ollama's local server has none; write your own tools.
- **Stored state.** Responses' `previous_response_id` and Conversations have no Anthropic equivalent, and Ollama doesn't support them.
- **Claude features:** adaptive thinking and `effort`, `cache_control` breakpoints, `pause_turn`, and citations on documents.
- **OpenAI features:** JSON mode, `n` for several completions (Chat Completions only), and reasoning items you pass back.
- **Same idea, different shape.** Both providers offer file uploads, batch processing, compaction and tool search, but the parameters and endpoints differ. Port these by reading both docs side by side.
- **Open-model limits.** Local models vary in tool calling, vision and context length, and Ollama's OpenAI layer leaves out some fields, such as `tool_choice` and `logprobs`. Check the model card and the compatibility page before you depend on a feature.
