### Current Models

Model names and prices change every few months, so lessons and projects don't hard-code them. When a lesson says "the cheap model" or "the capable model," use the one listed here.

**Last checked:** 2026-10-28. If this date is more than three months old, check the provider pages linked below before you start a project, and open an issue or pull request if something has changed.

### Which model to use

| Role in this curriculum | Claude model ID | When to use it |
| --- | --- | --- |
| **Cheap model** (default for development) | `claude-haiku-5-5` | Almost everything while you build and test. Fast and inexpensive. |
| **Capable model** | `claude-sonnet-5-5` | Final demo runs, hard multi-step agent tasks, and as an LLM judge. |
| **Most capable model** | `claude-opus-5-5` | Rarely needed in this curriculum. Try it when the capable model genuinely can't do a task, and compare cost. |

At the time of writing, the cheap model costs $0.10 per million input tokens and $0.50 per million output tokens, and the capable model costs $2 and $10. Always confirm on the [Claude pricing page](https://platform.claude.com/docs/en/about-claude/pricing) and the [models overview](https://platform.claude.com/docs/en/about-claude/models/overview).

### Using these IDs in code

Keep the model ID in one place in your project, so you can switch models by changing one line or one environment variable:

```python
import os

MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
```

### Other providers and open models

The skills in this curriculum transfer across providers. Several projects ask you to run your code against a second provider or an open-weight model, so you learn where providers differ. The [Provider Comparison](#/providers) page puts the Claude, OpenAI and Ollama APIs side by side for porting code.

- **Another hosted provider:** any provider with an OpenAI-compatible API works. Check its own models page for current IDs and prices.
- **Open-weight models on your own machine:** install [Ollama](https://ollama.com/) and pick a current small model from the [Ollama library](https://ollama.com/library) that fits your RAM. Ollama serves an OpenAI-compatible API, and it also offers [Anthropic API compatibility](https://docs.ollama.com/api/anthropic-compatibility), so many projects run locally for free.
- **Provider-specific features:** some features, such as server-side tools, tool search, compaction and prompt caching details, exist only on certain providers or work differently across them. Lessons label these as provider-specific.
