### Introduction

This is the final project of the Foundations path, and it brings together almost everything you've learned: Python, files and JSON, error handling, testing, HTTP, secrets and the model API. You'll build a chatbot that runs in your terminal and is pleasant and safe to use:

```text
$ uv run chatbot --system prompts/tutor.txt
Chatting with claude-haiku-5-5. Type /help for commands.

you> What's a list comprehension?
bot> Think of it as a recipe for building a list in one line...
     [turn: 412 in / 186 out, $0.000134 | session: $0.000134]

you> /save sessions/python-help.json
Saved 2 messages to sessions/python-help.json

you> /quit
```

It streams its replies, remembers the conversation and can save and reload it, shows what every turn costs, takes its personality from a configurable system prompt, and survives network problems and API errors without crashing.

It might look like a small program, but the problems it solves are the same ones inside every production AI app: managing conversation state, controlling cost and handling failure. You'll keep extending this kind of program throughout the curriculum. When you add tools to it, it becomes an agent.

### Before you start

- Create a new public GitHub repository named `mimir-terminal-chatbot` and clone it.
- Run `uv init --package`, then `uv add anthropic python-dotenv` and `uv add --dev pytest ruff`. Point a `chatbot` command at your main function in the `[project.scripts]` table of `pyproject.toml`, as you did for the Weather CLI.
- Add the `[tool.ruff]` and `[tool.ruff.lint]` settings and the `.github/workflows/ci.yml` file from Linting, Formatting and CI, as in your earlier projects. CI never needs your API key, because every test uses a fake backend.
- Set up your API key exactly as in API Keys and Secrets: `.env` in `.gitignore` *before* you create it, plus a committed `.env.example`. Check with `git status` before every commit.
- Use the [cheap model](#/models) while developing. A full day of testing should cost well under a dollar, but set a spend limit in the Console anyway.
- No budget for API credit? Use Ollama as described in Your First API Call. Your chatbot should then work with local models too; report "$0.00 (local)" for cost.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Keep the API out of your core logic

Put the parts that don't need the network into their own plain functions: calculating cost, saving and loading history, parsing commands like `/save path`. Those are easy to test with pytest, exactly like the parse functions in the Weather CLI. Keep the code that actually talks to the API small and behind one interface, a `ChatBackend` (requirement 1 below), and pass the backend in as an argument so tests can hand the chat loop a fake one, just like `FakeWeather` in the Testing with pytest lesson.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. **A `ChatBackend` interface.** Everything that talks to a model goes through one small class, `ChatBackend`, and the rest of the program only calls its methods. A good shape is a single method such as `chat(system: str, messages: list[dict], on_text: Callable[[str], None]) -> Reply`, which calls `on_text` with each streamed chunk and returns a `Reply` dataclass holding the full text and the input and output token counts.
   - Write `AnthropicBackend(ChatBackend)`, which wraps an `anthropic.Anthropic` client. Ollama works through the same class with a different `base_url`, as in Your First API Call.
   - Write `FakeBackend(ChatBackend)` in your tests, which returns canned replies (or raises the errors you tell it to) without any network. This is the dependency-injection pattern from Testing with pytest, using the inheritance from Classes and Objects. If you'd rather use `typing.Protocol`, that's fine too.
   - The chat loop, commands and cost meter take a `ChatBackend` as an argument and must never import `anthropic` themselves.
1. **Chat with streaming.** The bot reads a line from the user, streams the reply to the terminal as it's generated (inside `AnthropicBackend`, using `client.messages.stream`), and loops until the user quits. Empty input is ignored.
1. **Conversation memory.** The bot keeps the full conversation history and sends it with every request, so it can answer questions about earlier turns.
1. **Commands.** Support at least these, and show them with `/help`:
   - `/save PATH` writes the conversation history (and the system prompt and model) to a JSON file.
   - `/load PATH` replaces the current conversation with one from a saved file, and prints how many messages were loaded.
   - `/reset` clears the conversation and starts fresh.
   - `/cost` prints the session's total tokens and cost so far.
   - `/quit` exits cleanly (and so does Ctrl+D).
1. **Cost meter.** After every reply, print that turn's input tokens, output tokens and cost, and the running total for the session. Read token counts from the final message's `usage`. Keep prices in one clearly labeled place, with a comment saying where and when you got them, and support at least two models.
1. **Configurable personality and model.** Accept `--system PATH` to load the system prompt from a text file (with a sensible default if it's not given) and `--model NAME` to choose the model. Include at least two example system prompt files in a `prompts/` folder.
1. **Error handling with retry.** The program must never crash with a traceback because of the API or the network.
   - Retry rate limit (429), overloaded (529), server (5xx) and connection errors with exponential backoff and jitter, and respect `retry-after` when present. Show the user a short message while it waits.
   - Give a clear, specific message for an invalid API key, an unknown model name and a missing `.env` key, then exit or return to the prompt as appropriate.
   - Pressing Ctrl+C during a reply stops that reply and returns to the prompt.
   - Handle `/load` with a missing or invalid file gracefully.
   - When a reply fails completely, don't leave the history in a broken state (for example, with two user messages in a row and no answer between them).
1. **Tests.** Write pytest tests that run without an API key or network connection. At minimum:
   - Cost calculation for known token counts, for each model you support.
   - Saving a history to a file and loading it back gives an identical history (use pytest's `tmp_path` fixture).
   - Loading a corrupt or missing file raises your own clear error rather than a raw exception.
   - Command parsing, for example that `/save notes.json` gives you the command `save` and the argument `notes.json`.
   - Your retry logic: give it a fake function that fails twice with a retryable error and then succeeds, and check that it returns the result after three attempts; and that it does *not* retry a non-retryable error. (Patch out `time.sleep` with pytest's `monkeypatch` so the test runs instantly.)
   - One turn of the chat loop driven by a `FakeBackend`: after it, the history ends with your user message and the fake's reply, and the session cost matches the fake's token counts. Feed the input with `monkeypatch` or by passing your input-reading function in.
   - A turn where the `FakeBackend` raises a non-retryable error: the program prints a clear message and the history is left valid, with no unanswered user message.
1. **Lint, format and CI.** `uv run ruff check .` and `uv run ruff format --check .` must both pass, and a GitHub Actions workflow runs `uv sync --locked`, both ruff commands and `uv run pytest` on every push and pull request, with no API key.
1. **Measure it.** Hold one realistic 10-turn conversation and record every turn's input tokens, output tokens and cost in your README as a table. Explain why input tokens grow each turn, and what that would mean for a 100-turn conversation.
1. Push your project to GitHub with a README that explains what it does, how to install and run it (including setting up `.env` from `.env.example`), every command, your 10-turn measurements, how you tested it, and what you learned.

#### Evidence

- `uv run pytest` passes with no API key and no network (try it with Wi-Fi off), covering every test listed above, and the README includes its output.
- The GitHub Actions workflow runs ruff and pytest on every push, and the latest run on `main` passes. Show its status badge at the top of the README. (Linting, Formatting and CI)
- The README includes your 10-turn table of input tokens, output tokens and cost, with the prices you used and the date you looked them up.
- The README includes a short real terminal transcript showing a streamed reply, `/save` and `/load` with the message count, `/cost`, and one recovered failure, such as a retry message after you turn Wi-Fi off, or the clear message for an unknown model name.
- `git log -p | grep -i "sk-ant"` returns nothing, showing no real key was ever committed. Say in the README that you checked.

#### Extra credit

- Record a short terminal demo with [asciinema](https://asciinema.org/) or a GIF, showing streaming, a `/save` and `/load`, the cost meter and a recovered error (disconnect your Wi-Fi mid-conversation).
- Add a `--budget` option (for example `--budget 0.05`) that warns the user when the session cost passes the budget and refuses further requests once it's exceeded.
- Before each request, use `client.messages.count_tokens` to estimate the input cost and print it, then compare the estimate with the real `usage` afterward.
- When the conversation grows past a token limit you choose, automatically drop the oldest turns (in user/assistant pairs, so the history stays valid) and tell the user.
- Make the bot work with both Claude and a local Ollama model, switchable with a `--local` flag, and compare the quality and speed of their answers in your README.

</div>

### Submitting your work

A reviewer should be able to clone your repository, copy `.env.example` to `.env`, add a key and be chatting within two minutes. Make that easy with clear setup steps in your README. Show evidence that it works: a green CI badge, your table of measured costs for the 10-turn conversation, the output of `uv run pytest` passing, and ideally a short demo recording. Finally, double-check that no real API key appears anywhere in your repository or its history; reviewers will look. Congratulations on finishing Foundations. You've built a real LLM application from scratch, and you're ready for the AI Engineering Core path.
