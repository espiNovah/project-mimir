### Introduction

This project answers a question you'll be asked on the job: "Should we fine-tune a small model, call a frontier model, or use something simpler?" You'll answer it with numbers. You'll fine-tune an open model of 3 billion parameters or fewer with LoRA on a free GPU, then compare it against a prompted frontier model and the classic classifier from Beat the Baseline, all on the same frozen test set. You'll measure accuracy, cost per 1,000 calls and latency, and finish with a written recommendation of which one to ship.

It brings together nearly everything in this path: evaluation discipline, baselines, running open models and LoRA fine-tuning.

### Before you start

- Create a new repo named `mimir-fine-tune-small-model`.
- Copy the frozen `data/train.csv`, `data/val.csv` and `data/test.csv` files from your Beat the Baseline repo, unchanged, along with `model.joblib`. Record the commit hash you copied them from in your README.
- Pick a base model with 3B parameters or fewer and a license that allows your use, for example a small instruct model such as [Qwen3-1.7B](https://huggingface.co/Qwen/Qwen3-1.7B) or a comparable recent model from the Hugging Face Hub. Check the model card.
- Get a free GPU: [Google Colab](https://colab.research.google.com/) or [Kaggle Notebooks](https://www.kaggle.com/docs/notebooks). The [Unsloth fine-tuning guide](https://unsloth.ai/docs/get-started/fine-tuning-llms-guide) has free notebooks you can adapt; using TRL and PEFT directly is also fine.
- Set `ANTHROPIC_API_KEY` (or another provider's key) in your environment for the prompted frontier model. A prompted classifier call with the Claude API looks like this:

```python
import os

import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

LABELS = ["card_arrival", "lost_or_stolen_phone", "..."]  # all labels from train.csv


def classify(message: str) -> str:
    response = client.messages.create(
        model="claude-haiku-5-5",
        max_tokens=20,
        system="Classify the customer message into exactly one of these intents. "
        "Reply with the intent name only.\n" + "\n".join(LABELS),
        messages=[{"role": "user", "content": message}],
    )
    return response.content[0].text.strip()
```

<div class="lesson-note lesson-note--critical" markdown="1">

#### The test set is sealed

Develop your prompt and choose fine-tuning settings using the validation set only. Run each system on the test set exactly once, at the end. If you tweak a prompt after looking at test results, the comparison is no longer fair, and you must say so in your README.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Convert your training split into chat-formatted supervised fine-tuning examples (instruction plus message as the user turn, label as the assistant turn) using the base model's chat template. Save a few formatted examples to `examples.jsonl` so reviewers can see the format.
1. Fine-tune your base model with LoRA (or QLoRA) on a free GPU. Log training and validation loss, and record the GPU type, training time, rank, learning rate and epochs. Save the adapter and push it to the Hugging Face Hub or attach it to a GitHub release.
1. Evaluate the base model without fine-tuning on the validation set using the same prompt format, so you can show what fine-tuning added.
1. Build the prompted frontier-model classifier. Iterate on its prompt using only the validation set, and save every prompt version you tried.
1. Write `evaluate.py` that runs all three systems (fine-tuned small model, prompted frontier model, Beat the Baseline classifier) on the test set and records, for each:
   - Accuracy and macro F1, plus the rate of invalid outputs (a label that isn't in the list counts as wrong).
   - Median and 95th-percentile latency per call.
   - Cost per 1,000 calls. For the API model, compute it from the real token counts and the provider's [published pricing](https://platform.claude.com/docs/en/about-claude/pricing). For the small model, estimate from the GPU's hourly price and your measured throughput, and state your assumptions.
1. Produce a results table and a short error analysis: which intents does each system get wrong, and do the systems fail in the same places?
1. Write a one-page recommendation in your README of which system you would ship for a support team handling 100,000 messages a month, and why. Address quality, cost, latency, privacy and maintenance, and say what result would change your mind.
1. Push your project to GitHub with a README that explains what it does, how to run it, and what you learned.

#### Extra credit

- Serve your fine-tuned model locally with Ollama (merge the adapter and export to GGUF) and measure latency on your own machine.
- Train on 10%, 25% and 100% of the training data and plot test accuracy against data size for the fine-tuned model alongside your baseline.
- Add a hybrid: use the cheap classifier when it's confident and fall back to the frontier model otherwise. Report accuracy and cost for the combination.

</div>

### Submitting your work

A strong submission has one results table a manager could read in ten seconds, backed by code that reproduces it. It proves the test set was untouched during development (frozen files, prompt history, validation-only tuning). Cost and latency numbers are measured, not guessed, and the assumptions are written down. The recommendation takes a clear position, including the honest possibility that the classic baseline is good enough to ship.
