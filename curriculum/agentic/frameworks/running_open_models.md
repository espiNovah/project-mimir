### Introduction

So far every model you've called lived on someone else's servers. Open-weight models are different: anyone can download the weights (the billions of numbers a model learned in training) and run them on their own hardware. That matters for privacy, because the data never leaves your machine. It matters for cost, because there's no per-token bill. It also lets an agent work offline, and it keeps you free of any one provider. The tradeoff is real, though: a model small enough for a laptop is much less capable than a frontier model, and it's especially weaker at the thing agents need most, which is calling tools reliably over many steps.

This lesson gets an open model running on your computer and plugs it into the agent loop you already wrote. You'll learn enough to choose a model on purpose and to measure what it costs you in quality and speed. In "Port Your Agent", you'll run your agent on an open model and compare it with a hosted one, so treat this lesson as the setup for that project. Running open models for many users at once on GPU servers is a different job, and the ML elective's "Serving Open Models" lesson covers it.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What "open weights" means, and why a license still matters.
- The Hugging Face Hub, model cards, and base versus instruct models.
- Chat templates, and why the wrong one makes a model seem broken.
- How model size, quantization and context length decide what fits on your machine.
- Running a model locally with Ollama.
- Pointing your existing agent loop at a local model.
- Choosing an open model for an agent, and measuring it.

### Open weights are not open everything

A **closed** model, like the ones behind the big provider APIs, is only reachable through its owner's API. An **open-weight** model publishes its weights so you can download them. Families you'll often see include Qwen, Llama, Gemma, Mistral, DeepSeek and gpt-oss, each released in several sizes. "Open weights" is not the same as "open source": most releases don't include the training data or the full training code, so you can run and fine-tune the model but not rebuild it from scratch.

Open also doesn't mean "do whatever you like." Every model comes with a **license**. Some are permissive, such as Apache 2.0 and MIT, and allow commercial use with few conditions. Others are custom community licenses that ban some uses, require attribution, or add conditions for very large companies. Before you build a product on a model, read its license the way you'd read a dependency's license in a real job. Someone at your employer will ask.

### The Hugging Face Hub and model cards

The [Hugging Face Hub](https://huggingface.co/models) is to models what GitHub is to code. Almost every open model is published there, with a page called a **model card**. A good card tells you:

- **Size**, in parameters, such as 1.7B (1.7 billion) or 8B.
- **Context length**: the most tokens the model can handle at once.
- **License.**
- **Intended use and limitations**, including languages and known weak spots.
- **The recommended prompt format**, and settings such as temperature.
- **Benchmarks.** Treat these as a hint, not a verdict. They're chosen by the people releasing the model, and they rarely look like your task.

You'll also see the same model in several variants. A **base** model was only trained to continue text. Ask it a question and it may continue with three more questions, because that's what text on the internet often does. An **instruct** (or chat) model was further trained to follow instructions and take turns in a conversation. For agents you always want an instruct model, and for agents you want one whose card says it was trained for **tool calling** (also called function calling).

### Chat templates

A hosted API takes a list of messages with roles, as you've been sending since your first API call. Underneath, the model only ever sees one long string of tokens. A **chat template** is the rule that turns your list of messages, and any tool definitions, into that string, using special marker tokens the model learned in training. Each model family has its own template. Use the wrong one, or none, and a perfectly good model rambles, ignores the system prompt, or never stops. This is the most common reason a local model "seems dumb."

The good news is that tools like Ollama apply the right template for you. It's still worth seeing one once, because it demystifies what "the conversation" really is. This script uses the Transformers library, Hugging Face's Python library for running models. Run it in Colab or locally with `uv add transformers torch`. The first run downloads about 1.5 GB.

```python
# chat_template.py: see the string a model actually reads, then generate a reply
from transformers import AutoTokenizer, pipeline

MODEL = "Qwen/Qwen3-0.6B"  # a tiny instruct model that runs on a laptop CPU

messages = [
    {"role": "system", "content": "Answer in one short sentence."},
    {"role": "user", "content": "What is the capital of Kenya?"},
]

tokenizer = AutoTokenizer.from_pretrained(MODEL)
prompt = tokenizer.apply_chat_template(
    messages,
    tokenize=False,              # give us text, not token IDs, so we can read it
    add_generation_prompt=True,  # end with the marker that means "assistant, your turn"
)
print(prompt)

chat = pipeline("text-generation", model=MODEL)  # applies the same template internally
result = chat(messages, max_new_tokens=300)
print(result[0]["generated_text"][-1]["content"])  # the last message is the model's reply
```

The printed prompt shows marker tokens such as `<|im_start|>system` around each message. That's the whole trick: roles are just text the model was trained to recognize. Qwen3 is a reasoning model, so its reply may begin with a `<think>` section before the answer. Tool definitions get rendered into this string too, which is why the model card's tool-calling instructions matter.

### What fits on your machine

To run a model, its weights must fit in memory: your GPU's memory (VRAM) if you have a suitable GPU, or ordinary RAM otherwise. Apple Silicon Macs share one pool of memory between CPU and GPU, which makes them good at this.

A rough rule: at 16-bit precision, each parameter takes 2 bytes, so each billion parameters needs about 2 GB. An 8B model needs about 16 GB just for its weights, more than most laptops can spare. **Quantization** fixes that. It stores each weight with fewer bits, such as 8 or 4 instead of 16, rounding the numbers carefully. A 4-bit version of that 8B model needs roughly 5 GB, and it loses only a little quality. Below 4 bits, quality drops faster. Quantized files usually use the **GGUF** format, and names like `Q4_K_M` describe the scheme (here, about 4 bits per weight). Ollama downloads a 4-bit version by default.

The weights aren't the only cost. Every token in the context needs working memory too, called the **KV cache**, and it grows with context length. That's why local runtimes keep the context window small by default, which turns out to matter a lot for agents.

| Model size | Approx. download at 4-bit | Comfortable on |
| --- | --- | --- |
| 1–2B | 1–2 GB | almost any laptop with 8 GB RAM |
| 3–4B | 2–3 GB | a laptop with 8–16 GB RAM |
| 7–8B | 5–6 GB | 16 GB RAM, or a GPU with 8 GB or more |
| 14B and up | 9 GB and up | 32 GB RAM, or a large GPU |

Speed is measured in **tokens per second**. A small model on a modern laptop might write 20–60 tokens per second; on a CPU-only machine, it may be under 10. An agent run with ten steps can then take minutes.

### Running a model with Ollama

[Ollama](https://ollama.com/) is a free tool that downloads quantized models, runs them, and serves them over a local HTTP API. Install it from [the Ollama download page](https://ollama.com/download), then:

```bash
ollama pull qwen3:4b          # download a 4B model that supports tool calling (about 2.5 GB)
ollama run qwen3:4b --verbose "Explain a context window in two sentences."
#   --verbose prints timing stats, including "eval rate": your tokens per second
ollama ps                     # what's loaded, how much memory, CPU or GPU, and the CONTEXT size
ollama list                   # every model you've downloaded
```

The [Ollama model library](https://ollama.com/library) lists the available models and sizes. Each family has tags like `qwen3:1.7b` or `qwen3:8b`, and models trained for tool calling carry a "tools" label. While Ollama runs, it serves an API at `http://localhost:11434`. It speaks its own native API, an **OpenAI-compatible** API under `/v1`, and an **Anthropic-compatible** Messages API. That last one means the code you've written all along can talk to a local model by changing only where the client sends requests.

<div class="lesson-note lesson-note--warning" markdown="1">

#### The small default context window

Ollama picks a default context length from your GPU memory, and on most laptops it's only 4,096 tokens. An agent's system prompt, tool definitions and growing history pass that within a few steps, and the input gets cut to fit without an error. The symptom is an agent that suddenly forgets its task or its tools. Check the CONTEXT column in `ollama ps`, and raise it by starting the server with `OLLAMA_CONTEXT_LENGTH=32768 ollama serve` (or the slider in the Ollama app's settings) if your memory allows.

</div>

### Your agent loop on a local model

Here is a compact version of the loop from the Tool Use section, with the two tools from `tools.py` in the Claude Agent SDK lesson (`calculate` and `save_note`). The only new idea is at the top: if `MIMIR_BASE_URL` is set, the same Anthropic client sends its requests to that server instead. Put `tools.py` next to it, run `uv add anthropic python-dotenv`, and save this as `local_agent.py`:

```python
"""local_agent.py: the raw agent loop, runnable against Claude or a local Ollama model."""
import os
import sys
import time

import anthropic
from dotenv import load_dotenv

import tools  # calculate() and save_note(), from the Claude Agent SDK lesson

load_dotenv()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
BASE_URL = os.environ.get("MIMIR_BASE_URL")  # e.g. http://localhost:11434 for Ollama
# (1) Ollama ignores the key, but the client insists on having one.
client = anthropic.Anthropic(base_url=BASE_URL, api_key="ollama") if BASE_URL else anthropic.Anthropic()

TOOLS = [
    {"name": "calculate", "description": "Apply one arithmetic operation (+, -, *, /) to two "
     "numbers. Use it for all math instead of doing it in your head.",
     "input_schema": {"type": "object", "properties": {
         "a": {"type": "number"}, "op": {"type": "string", "enum": ["+", "-", "*", "/"]},
         "b": {"type": "number"}}, "required": ["a", "op", "b"]}},
    {"name": "save_note", "description": "Save text to a Markdown note in the workspace. "
     "Pass a bare file name like 'answer.md'.",
     "input_schema": {"type": "object", "properties": {
         "filename": {"type": "string"}, "text": {"type": "string"}},
         "required": ["filename", "text"]}},
]
FUNCTIONS = {"calculate": tools.calculate, "save_note": tools.save_note}


def run(task: str, max_steps: int = 10) -> None:
    messages = [{"role": "user", "content": task}]
    start, out_tokens = time.perf_counter(), 0
    for step in range(1, max_steps + 1):
        reply = client.messages.create(model=MODEL, max_tokens=4000, tools=TOOLS, messages=messages)
        out_tokens += reply.usage.output_tokens
        messages.append({"role": "assistant", "content": reply.content})
        if reply.stop_reason != "tool_use":
            print("".join(b.text for b in reply.content if b.type == "text"))
            break
        results = []
        for block in reply.content:
            if block.type != "tool_use":
                continue
            print(f"  step {step}: {block.name} {block.input}")
            try:  # (2) small models send bad arguments more often; never let that crash the loop
                output = FUNCTIONS[block.name](**block.input)
            except Exception as e:
                output = f"Error: {type(e).__name__}: {e}. Check the tool's parameters."
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": output,
                            "is_error": output.startswith("Error")})
        messages.append({"role": "user", "content": results})
    else:
        print(f"Stopped: hit the {max_steps}-step limit.")
    seconds = time.perf_counter() - start
    print(f"[{MODEL}] {step} steps, {out_tokens} output tokens, {seconds:.1f} s")  # (3)


if __name__ == "__main__":
    run(" ".join(sys.argv[1:]) or "What is 1234 * 5678 minus 99? Save the result to answer.md.")
```

Run it twice, once hosted and once local:

```bash
uv run local_agent.py
MIMIR_BASE_URL=http://localhost:11434 MIMIR_MODEL=qwen3:4b uv run local_agent.py
```

1. **One switch.** The model name and server come from environment variables, so the code that talks to a hosted model and to a local one is identical. That's the habit "Port Your Agent" rewards: keep tools, tasks and the loop the same, and change only configuration.
1. **Defensive tool dispatch.** Small models more often invent a parameter name, send a number as a string, or call a tool that doesn't exist. The `try` turns each mistake into an error result the model can read and fix, which you learned in Tool Errors and Parallel Calls.
1. **Measure every run.** Steps, tokens and wall-clock time, printed for both runs, are the start of a comparison table.

Compatibility layers cover the common path, not every feature. Ollama's Anthropic-compatible API supports messages, streaming, tools and thinking, but not `tool_choice`, prompt caching (`cache_control`), PDFs or token counting, and server tools such as hosted web search don't exist locally. If your agent relies on a provider-only feature, give the local version a plain replacement, such as a web search tool that calls a search API, and note the difference in your results.

### Choosing an open model for an agent

Pick candidates in this order, then let your own tests decide:

1. **Tool calling.** The model must be trained for it. In Ollama's library, look for the "tools" label; on Hugging Face, check the model card.
1. **Fit.** Choose the largest size that fits in memory with room for a useful context window, using the table above. A 4B model with a 16k context usually beats an 8B model squeezed into 4k for agent work.
1. **License** that allows your use.
1. **Context length** the model actually supports, which may be larger than what you can afford to run.
1. **Recency.** Open models improve quickly. A current 4B model can beat a two-year-old 13B one, so check release dates.

Then **measure, don't assume.** Run the same tasks you'd run on a hosted model, several times each, because a model that passes once may fail the next time (the pass^k idea from Agent Eval Fundamentals). Record the success rate, the steps per task and the tokens per second. Expect a small local model to skip tools and guess, repeat the same call, or stop early. Those are the failure patterns to look for in your traces. The honest result is often "the local model handles the simple tasks and fails the multi-step ones," and that's a useful finding: it tells you which parts of a product could run locally and cheaply.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Prepare for Port Your Agent now

Pull one tool-calling model that fits your machine, raise the context length, and run your agent's test tasks against it once. Finding out now that your laptop needs a smaller model saves a frustrating evening later. If your computer can't run any model at a usable speed, Ollama also offers hosted cloud models through the same API, and other providers host open models too.

</div>

### On other providers

This whole lesson is about another provider: your own machine. The Anthropic-compatible endpoint is a convenience offered by Ollama, and most open-model tools speak the **OpenAI** Chat Completions format instead, including LM Studio, llama.cpp's server and vLLM, which you'll meet in the ML elective. So it's worth knowing that shape too. Messages are `{"role", "content"}` dictionaries, but the system prompt is the first message rather than a separate field. Tool definitions put the JSON Schema under `function.parameters`. A tool request comes back in `message.tool_calls`, each call's arguments arrive as a JSON *string* you must parse, and you reply with a `{"role": "tool", "tool_call_id": ...}` message per call. Here's one step of the same loop through Ollama's [OpenAI-compatible API](https://docs.ollama.com/api/openai-compatibility); the full round trip is in OpenAI's [function calling guide](https://developers.openai.com/api/docs/guides/function-calling):

```python
import json
from openai import OpenAI  # uv add openai
from tools import calculate

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
tool = {"type": "function", "function": {"name": "calculate", "description": "Do one arithmetic operation.",
        "parameters": {"type": "object", "properties": {"a": {"type": "number"},
        "op": {"type": "string"}, "b": {"type": "number"}}, "required": ["a", "op", "b"]}}}
messages = [{"role": "user", "content": "What is 1234 * 5678?"}]
reply = client.chat.completions.create(model="qwen3:4b", messages=messages, tools=[tool]).choices[0].message
messages.append(reply)
for call in reply.tool_calls or []:  # then call the API again, as in the loop above
    args = json.loads(call.function.arguments)  # a JSON string, not a dict
    messages.append({"role": "tool", "tool_call_id": call.id, "content": calculate(**args)})
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [Ollama documentation](https://docs.ollama.com/) to install Ollama and run your first local model. This is the tool you'll use for the rest of the path.
   - Follow the quickstart, then read the pages on [OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility), [Anthropic compatibility](https://docs.ollama.com/api/anthropic-compatibility) and [context length](https://docs.ollama.com/context-length).
   - Browse the [Ollama model library](https://ollama.com/library) and pick a tool-calling instruct model that fits your machine.
1. Read the model card of a small open model, such as [Qwen3-1.7B](https://huggingface.co/Qwen/Qwen3-1.7B), on the Hugging Face Hub, to practice reading cards before you trust a model.
   - Find its license, its context length, its recommended settings, and what it says about tool calling and thinking.
1. Work through chapter 2 of the [Hugging Face LLM Course](https://huggingface.co/learn/llm-course), the official free course for the Transformers library, to see what tools like Ollama do for you. Run the code in Colab. Chapter 1 is a useful refresher on how transformer models work, if you want it.
1. Read the [chat templates guide](https://huggingface.co/docs/transformers/chat_templating) in the Transformers docs, and run `chat_template.py` from this lesson. Then change the messages, add an assistant turn, and see how the printed string changes.
1. Run your agent on a local model and measure it.
   - Set up `local_agent.py` with `tools.py`, or adapt your own loop from Agent Loop From Scratch the same way.
   - Write five tasks with automatic pass or fail checks, at least two of which need more than one tool call. Run each task three times on the [cheap model](#/models) and three times on your local model.
   - Make a table with success rate, average steps, average time and tokens per second for each. Read the traces of the local model's failures and name the failure pattern for each one. Keep this setup: it's the start of "Port Your Agent".

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Why doesn't "open weights" mean you can use a model for anything?](#open-weights-are-not-open-everything)
- [What is the difference between a base model and an instruct model, and which does an agent need?](#the-hugging-face-hub-and-model-cards)
- [What does a chat template do, and what happens when the wrong one is used?](#chat-templates)
- [Roughly how much memory does an 8B model need at 16-bit and at 4-bit precision?](#what-fits-on-your-machine)
- [Why can a small default context window break an agent without any error message?](#running-a-model-with-ollama)
- [How can the same agent loop talk to both a hosted model and a local one?](#your-agent-loop-on-a-local-model)
- [What should you check when choosing an open model for an agent, and how do you decide in the end?](#choosing-an-open-model-for-an-agent)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The Hugging Face Transformers documentation](https://huggingface.co/docs/transformers/index) is the full reference for loading, running and fine-tuning models in Python.
- [llama.cpp](https://github.com/ggml-org/llama.cpp) is the open-source engine underneath many local tools; its README explains GGUF and quantization types in more depth.
- [LM Studio](https://lmstudio.ai/) is a free desktop app for downloading and chatting with local models, with an OpenAI-compatible server, if you prefer a graphical interface to Ollama.
