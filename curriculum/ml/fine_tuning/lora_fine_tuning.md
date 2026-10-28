<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Fully fine-tuning a model means updating all of its weights, which for even a 3B-parameter model needs more GPU memory than any free tier provides. LoRA (Low-Rank Adaptation) gets around this: it freezes the original weights and trains a tiny set of extra ones. Combined with 4-bit quantization (QLoRA), you can fine-tune a small open model on a free Colab or Kaggle GPU in under an hour.

This lesson covers how LoRA works and the tools that make it practical, so you're ready to run the comparison in Fine-Tune a Small Model.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Full fine-tuning versus parameter-efficient fine-tuning (PEFT).
- How LoRA works: low-rank adapter matrices.
- QLoRA: training adapters on top of a 4-bit quantized model.
- Supervised fine-tuning (SFT) and formatting training data as chat examples.
- The key hyperparameters: rank, alpha, learning rate, epochs.
- The tools: TRL, PEFT and Unsloth.
- Evaluating, saving, merging and serving an adapter.

### Key ideas

- **Parameter-efficient fine-tuning trains a small number of new weights and freezes the rest.** That slashes GPU memory and produces a small file (often tens of megabytes) that sits on top of the unchanged base model.
- **LoRA adds a pair of thin matrices next to selected weight matrices.** Instead of learning a full update to a large `d × d` matrix, it learns two matrices of shape `d × r` and `r × d` whose product is the update, with a small rank `r` such as 8 or 16. You learned the shapes rule in Matrices and Probability; this is that rule turned into a memory saving.
- **QLoRA loads the frozen base model in 4-bit precision** and trains LoRA adapters in higher precision. It's the standard recipe for fine-tuning on a single consumer or free-tier GPU.
- **Supervised fine-tuning learns from input-output pairs.** For classification, each training example is a chat: a short instruction plus the message as the user turn, and the correct label as the assistant turn. Use the model's chat template, and compute the loss only on the answer tokens when your tool supports it.
- **A few hyperparameters matter most.** Rank (`r`) and alpha control adapter capacity and scaling; the learning rate is usually higher than for full fine-tuning (around `1e-4` to `2e-4` is a common starting point); one to three epochs is typical. More epochs on small data overfits, which you'll see as validation loss rising.
- **TRL, PEFT and Unsloth do the heavy lifting.** PEFT implements LoRA. TRL's `SFTTrainer` runs supervised fine-tuning. Unsloth wraps both with memory and speed optimizations and publishes ready-made free notebooks.
- **An adapter is only good if your eval says so.** Evaluate on the frozen test set, then either load the adapter on top of the base model or merge it in and export it (for example to GGUF for Ollama) to serve it.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Work through the [fine-tuning chapter of the Hugging Face LLM Course](https://huggingface.co/learn/llm-course/chapter11/1), the core reading for this lesson.
   - Read every page on chat templates, supervised fine-tuning and LoRA, and run the notebooks on a free GPU.
1. Read the [Hugging Face PEFT documentation](https://huggingface.co/docs/peft/index) for how LoRA adapters are configured, saved and loaded.
   - Read the quicktour and the LoRA conceptual guide.
1. Skim the [TRL documentation](https://huggingface.co/docs/trl/index), focusing on the `SFTTrainer` page and the dataset formats it accepts.
1. Read the [Unsloth fine-tuning guide](https://unsloth.ai/docs/get-started/fine-tuning-llms-guide), a beginner-friendly, practical walkthrough with free Colab and Kaggle notebooks.
   - Read the sections on choosing a model, preparing a dataset and hyperparameters. Then run one of their small-model notebooks end to end so you know your GPU setup works before the project.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The LoRA paper](https://arxiv.org/abs/2106.09685) by Hu et al. is short and readable once you know the shapes rule.
- [The Hugging Face smol course](https://huggingface.co/learn/smol-course) is a free, hands-on course on aligning and fine-tuning small models.
