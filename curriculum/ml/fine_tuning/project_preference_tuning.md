### Introduction

In [LoRA Fine-Tuning](#/paths/ml), you learned how Supervised Fine-Tuning (SFT) teaches an open model to adopt a specific format, personality, or tool-calling schema. However, SFT has a major limitation: it treats every token in a positive demonstration equally. It cannot learn from mistakes, and it cannot easily distinguish between a good response and an exceptional one.

**Direct Preference Optimization (DPO)** is the alignment technique that replaced complex Reinforcement Learning from Human Feedback (RLHF) pipelines across the AI industry.

Instead of training a separate reward model and running unstable PPO reinforcement learning loops, DPO mathematically re-formulates the preference objective. By comparing a **chosen** response against a **rejected** response for the exact same prompt, DPO optimizes the policy directly with a simple binary cross-entropy loss.

In this project, you will take an instruction-tuned small open model, train a LoRA preference adapter using Hugging Face TRL's `DPOTrainer` on a free GPU, track implicit reward margins, and measure the resulting head-to-head win rate against the base model using an automated judge.

### Before you start

- Create a new repository named `mimir-preference-tuning` and initialize it with `uv init`.
- Add dependencies: `uv add torch transformers trl peft datasets accelerate`.
- Get a free GPU: [Google Colab](https://colab.research.google.com/) or [Kaggle Notebooks](https://www.kaggle.com/code). An Nvidia T4 GPU is sufficient when using LoRA and 4-bit base weights.
- Choose a small base model (1B to 3B parameters) that has already undergone basic instruction tuning, such as `meta-llama/Llama-3.2-1B-Instruct` or `Qwen/Qwen2.5-1.5B-Instruct`.
- Choose a pairwise preference dataset: a curated subset of [Anthropic/hh-rlhf](https://huggingface.co/datasets/Anthropic/hh-rlhf), `HuggingFaceH4/ultrafeedback_binarized`, or a domain-specific preference dataset formatted as:

```json
{
  "prompt": "Explain what a database deadlock is.",
  "chosen": "A deadlock occurs when two transactions each hold a lock the other needs, causing both to wait indefinitely.",
  "rejected": "Deadlocks are bad database errors. You should avoid them by restarting your server whenever queries get stuck."
}
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Prepare your preference dataset:
   - Split your dataset into 800 training pairs and 100 validation pairs.
   - Verify that every example contains valid `prompt`, `chosen`, and `rejected` fields.
   - Apply your base model's chat template to both pairs so special tokens match training expectations.
1. Run pre-training evaluation:
   - Sample 30 prompts from the validation split.
   - Generate answers using the untuned base model at temperature 0.7. Save these outputs to `eval/baseline_generations.json`.
1. Train a DPO adapter using `trl.DPOTrainer`:
   - Configure a LoRA adapter (`r = 16`, `lora_alpha = 32`, targeting all linear projection layers).
   - Set key DPO hyperparameters:
     - `beta`: The temperature parameter controlling how strongly the model is penalized for drifting from the reference model (start with `beta = 0.1`).
     - `learning_rate`: DPO requires a very low learning rate (typically `5e-6` to `1e-5`).
     - `num_train_epochs`: 1 to 2 epochs.
   - Track `rewards/margins` during training. A healthy DPO run will show the implicit reward margin (`chosen_reward - rejected_reward`) steadily increasing above zero.
1. Save your trained adapter and loss logs to `logs/training_metrics.json`.
1. Run head-to-head win-rate evaluation:
   - Generate answers for the 30 evaluation prompts using your DPO-tuned model with the exact same seed and temperature.
   - Write an automated judge script (`eval/judge.py`) using the [cheap model](#/models).
   - For each prompt, present both answers blindly (randomizing whether Answer A is baseline or DPO) and have the judge select the superior response based on helpfulness, conciseness, and accuracy.
   - Compute the DPO model's win rate and calculate a 95% bootstrap confidence interval using the methods from [Eval Statistics](#/paths/core).
1. Push your project to GitHub with a README that explains your methodology, findings, and evaluation metrics.

#### Evidence

Your project repository must prove that preference alignment occurred and was objectively measured:

- `pytest` tests in `tests/` verifying:
  - Dataset formatting: confirms all pairs contain non-empty `prompt`, `chosen`, and `rejected` strings.
  - Blind evaluation harness: confirms answer order is randomly shuffled to prevent position bias in the judge.
  - Metric computation: win-rate calculator agrees with bootstrap confidence interval formulas.
- A GitHub Actions workflow running `ruff check .` and `pytest` on every push, with a passing status badge in your README.
- A plot (`rewards.png`) showing training step vs implicit reward margin (`chosen - rejected`), confirming that the margin became positive.
- A head-to-head win rate report in your README comparing the baseline SFT model against your DPO-aligned model, including a 95% bootstrap confidence interval.
- A table showing at least three concrete qualitative comparisons where DPO visibly improved the model's responses (such as removing fluff, correcting misconceptions, or refusing an unsafe instruction).

#### Extra credit

- Experiment with two different values of `beta` (e.g. `0.05` versus `0.3`). Document how `beta` affects response length and adherence to the reference model.
- Export your aligned model to 4-bit GGUF format and test it locally using Ollama.
- Merge the LoRA adapter with the base model and benchmark generation throughput before and after merging.

</div>

### Submitting your work

A strong submission demonstrates both mathematical understanding and rigorous evaluation discipline. Reviewers look for clean code, reproducible training arguments, a clear reward margin curve that demonstrates the model learned the preference signal, and an honest evaluation report that accounts for position bias and statistical significance.