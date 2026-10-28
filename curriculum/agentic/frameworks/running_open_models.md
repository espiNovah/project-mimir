<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

So far you have used models through a provider's API. Open-weight models are different: anyone can download the weights and run them on their own hardware. That matters for privacy (data never leaves your machine), cost (no per-token bill at high volume), offline use, and fine-tuning, which you'll do later in this section. It also comes with real tradeoffs, since small open models are usually less capable than frontier models.

This lesson shows you the two main ways to run open models: the Hugging Face ecosystem in Python, and Ollama for easy local inference.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Open-weight versus closed models, and what "open" does and doesn't mean.
- The Hugging Face Hub: models, model cards, licenses and datasets.
- Running a model in Python with the Transformers library.
- Base models versus instruct models, and chat templates.
- Quantization and how it shrinks models to fit your hardware.
- Running models locally with Ollama and its OpenAI-compatible API.

### Key ideas

- **Open weights means you can download and run the model, not always that you can do anything with it.** Each model has a license. Some are permissive (Apache 2.0, MIT); others restrict commercial use or require accepting terms. Read the model card before building on a model.
- **The Hugging Face Hub is the GitHub of models.** Each model page has a card describing its training, intended use, benchmarks and limitations. The Transformers library loads most of them with a few lines of Python using `AutoTokenizer` and `AutoModelForCausalLM`, or the higher-level `pipeline`.
- **Base models complete text; instruct models follow instructions.** For chat-style use, pick an instruct (or chat) variant, and format your messages with the model's chat template (`tokenizer.apply_chat_template`). Using the wrong format is a common reason a local model seems "dumb."
- **Model size determines the hardware you need.** Roughly, each billion parameters needs about 2 GB of memory at 16-bit precision. Quantization stores weights at lower precision (8-bit, 4-bit), cutting memory by two to four times with modest quality loss. That's how a 3B or 8B model runs on a laptop.
- **Ollama makes local inference a one-line command.** `ollama run <model>` downloads a quantized model and starts a chat. Ollama also serves a local HTTP API, including an OpenAI-compatible endpoint, so code you wrote against hosted APIs can often point at a local model by changing the base URL.
- **Measure, don't assume.** Local models trade quality for privacy and cost. Run the same eval you'd run on a hosted model, and measure tokens per second on your hardware before deciding.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Work through the opening chapters of the [Hugging Face LLM Course](https://huggingface.co/learn/llm-course), the official free course for the Hugging Face ecosystem.
   - Do chapter 1 (transformer models) and chapter 2 (using Transformers), running the code in Colab or Kaggle.
1. Read the [Ollama documentation](https://docs.ollama.com/) to install Ollama and run your first local model.
   - Follow the quickstart, then read the pages on the API and on OpenAI compatibility.
   - Browse the [Ollama model library](https://ollama.com/library) and pick a small instruct model (3B parameters or fewer) that runs on your machine.
1. Read the model card of a small open model, such as [Qwen3-1.7B](https://huggingface.co/Qwen/Qwen3-1.7B), on the Hugging Face Hub.
   - Find its license, its context length, its recommended chat format, and any limitations it lists.
1. Take five prompts from your Prompt Lab project and run them through a local model with Ollama and through a hosted model. Record each response, the latency, and your judgment of quality side by side in a small table.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The Hugging Face Transformers documentation](https://huggingface.co/docs/transformers/index) is the full reference for loading, running and fine-tuning models in Python.
