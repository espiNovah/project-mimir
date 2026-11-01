### Introduction

In [Fine-Tune, Prompt, or RAG?](#/paths/core), you learned when fine-tuning makes sense: when you need to teach a model a specific output format, reduce latency and token costs on high-volume tasks, or adapt a model to proprietary domain vocabulary that prompt engineering cannot reliably enforce.

Until recently, fine-tuning was expensive. Fully fine-tuning a model requires updating all of its internal parameters. For an 8-billion parameter model, storing the model weights, optimizer states (such as Adam's momentum and variance buffers), and activation gradients in memory requires more than 60 GB of GPU VRAM—far beyond what any consumer hardware or free cloud tier provides.

**LoRA (Low-Rank Adaptation)** changed this. Instead of modifying all original parameters, LoRA freezes the base model entirely and injects small, trainable low-rank adapter matrices next to selected weight layers. Combined with 4-bit model quantization (**QLoRA**), you can fine-tune capable open models on a single free Google Colab or Kaggle GPU in under an hour.

This lesson covers the mathematics and engineering behind LoRA and QLoRA, the dataset formats required for supervised fine-tuning, and the modern open-source toolchain (Hugging Face PEFT, TRL, and Unsloth) that you will use in [Project: Fine-Tune a Small Model](#/paths/ml).

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why full fine-tuning is memory-prohibitive, and how parameter-efficient fine-tuning (PEFT) solves this.
- The mathematical formulation of LoRA: low-rank matrix decomposition.
- QLoRA: combining 4-bit NormalFloat base model quantization with 16-bit LoRA adapters.
- Supervised fine-tuning (SFT) data preparation and the role of chat templates.
- Core fine-tuning hyperparameters: rank `r`, scaling factor `alpha`, learning rate, and epochs.
- The open-source tooling ecosystem: Hugging Face `peft`, `trl.SFTTrainer`, and `unsloth`.
- How to evaluate, save, merge, and export trained adapters to GGUF or vLLM.

### Full fine-tuning versus parameter-efficient fine-tuning

When a model is trained, the optimizer must store three pieces of data in GPU memory for every parameter:

1. **Model weight:** 2 bytes in half precision (FP16 or BF16).
2. **Gradient:** 2 bytes in FP16/BF16.
3. **Optimizer states:** 8 to 12 bytes in FP32 (AdamW stores the first moment and second moment of the gradient for every parameter).

For an 8-billion parameter model, full fine-tuning requires:

```text
Weights:          8B * 2 bytes  = 16 GB
Gradients:        8B * 2 bytes  = 16 GB
Optimizer states: 8B * 8 bytes  = 64 GB
Activations:                    ≈ 16 to 32 GB (depending on batch size and sequence length)
Total VRAM required:            > 110 GB
```

You would need multiple enterprise Nvidia A100 or H100 GPUs just to begin training.

**Parameter-Efficient Fine-Tuning (PEFT)** freezes the pre-trained model weights. Because the base model weights are frozen, we do not need to compute or store gradients or optimizer states for them. We only track gradients and optimizer states for a tiny set of new adapter parameters (typically less than 1% of the original model size). This reduces optimizer memory from dozens of gigabytes down to a few hundred megabytes.

### How LoRA works: low-rank matrix decomposition

In [Matrices and Probability](#/paths/ml), you learned that a dense neural network layer computes `y = W @ x`, where `W` has shape `(d_out, d_in)`.

During full fine-tuning, the network updates `W` by adding a learned matrix of weight adjustments, `ΔW`:

```text
W_new = W_base + ΔW
```

`ΔW` has the exact same large shape as `W_base`.

The insight behind LoRA (Hu et al., 2021) is that the weight updates during task adaptation have a very low **intrinsic rank**. That means you do not need a full-rank matrix to capture the changes needed for a specific task; you can approximate `ΔW` by decomposing it into the product of two much smaller, thin matrices, `B` and `A`:

```text
ΔW = B @ A
```

If `W` has shape `(4096, 4096)`:
- `W` contains `4096 * 4096 = 16,777,216` parameters.
- If we choose a rank `r = 16`:
  - `A` has shape `(16, 4096)`: `65,536` parameters.
  - `B` has shape `(4096, 16)`: `65,536` parameters.
  - Together, `A` and `B` contain `131,072` parameters—a **99.2% reduction** in trainable parameters for that layer!

![Low-Rank Adaptation (LoRA) architecture with frozen base weights and trainable adapter matrices](assets/images/lora_architecture.svg)

At the start of training:
- `A` is initialized from a Gaussian random distribution (mean 0, small variance).
- `B` is initialized to all zeros.
- Therefore, `B @ A = 0` at step zero, meaning the adapter starts by contributing nothing, and the model's behavior is initially identical to the base model.

During the forward pass:

```text
y = (W_base @ x) + (alpha / r) * (B @ A @ x)
```

The hyperparameter `alpha` is a constant scaling factor. Dividing `alpha` by `r` ensures that if you experiment with different values of rank `r`, you do not have to retune the learning rate.

```python
# A conceptual implementation of a LoRA Linear layer in PyTorch
import torch
import torch.nn as nn

class LoRALinear(nn.Module):
    def __init__(self, in_features: int, out_features: int, r: int = 16, lora_alpha: float = 32.0):
        super().__init__()
        # 1. Base linear layer (frozen)
        self.base_layer = nn.Linear(in_features, out_features, bias=False)
        self.base_layer.weight.requires_grad = False
        
        # 2. LoRA low-rank adapter matrices
        self.r = r
        self.scaling = lora_alpha / r
        self.lora_A = nn.Parameter(torch.randn(r, in_features) * 0.01)
        self.lora_B = nn.Parameter(torch.zeros(out_features, r))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Base forward pass
        base_out = self.base_layer(x)
        # Adapter forward pass: (x @ A.T) @ B.T
        lora_out = (x @ self.lora_A.T) @ self.lora_B.T * self.scaling
        return base_out + lora_out
```

### QLoRA: 4-bit base models and high-precision adapters

While LoRA eliminates optimizer memory, you still need to load the base model weights into VRAM. An 8-billion parameter model in 16-bit precision takes 16 GB of memory just to hold the weights. That barely fits on a 16 GB Nvidia T4 GPU (the standard free GPU on Colab and Kaggle), leaving zero room for activations or context.

**QLoRA (Quantized Low-Rank Adaptation)**, introduced by Dettmers et al. (2023), solves this by compressing the base model down to **4-bit precision**:

1. **4-bit NormalFloat (NF4):** A custom 4-bit data type mathematically optimized for normally distributed neural network weights.
2. **Double Quantization:** Quantizes the quantization constants themselves, saving an additional 0.37 bits per parameter.
3. **Paged Optimizers:** Uses Nvidia unified memory to automatically page optimizer states to CPU RAM during memory spikes, preventing out-of-memory (OOM) crashes.

In QLoRA:
- The base model weights are loaded and frozen in **4-bit NF4** (an 8B model takes only ~5.5 GB of VRAM).
- When a forward pass occurs, the 4-bit weights are dequantized on the fly to 16-bit BF16/FP16, multiplied by the input, and the result is computed.
- The LoRA adapter matrices (`A` and `B`) remain in full **16-bit precision**, so gradients and weight updates maintain numerical fidelity.

QLoRA enables high-quality fine-tuning of 7B–14B models on consumer GPUs or free cloud tiers with no measurable loss in accuracy compared to standard 16-bit LoRA.

### Preparing chat datasets and chat templates

Fine-tuning an LLM to follow instructions or format outputs is called **Supervised Fine-Tuning (SFT)**.

SFT requires training data formatted as multi-turn conversations. Every foundation model has a specific **chat template** (such as ChatML, Llama-3 format, or Mistral format) that wraps messages in special delimiter tokens:

```text
<|im_start|>system
You are a financial entity extractor. Return JSON only.<|im_end|>
<|im_start|>user
Invoice #4829 from Acme Corp: $1,250.00 due on Nov 15.<|im_end|>
<|im_start|>assistant
{"invoice": 4829, "vendor": "Acme Corp", "amount": 1250.0, "due": "2026-11-15"}<|im_end|>
```

Never hard-code delimiter strings by hand. Every model's tokenizer on Hugging Face includes its official chat template:

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-3B-Instruct")

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Summarize the incident report in two bullet points."},
    {"role": "assistant", "content": "- Database failover occurred at 02:14 UTC.\n- Recovery completed within 6 minutes."}
]

# Applies the exact special tokens for this specific model architecture
formatted_text = tokenizer.apply_chat_template(messages, tokenize=False)
```

In standard SFT, the loss should only be calculated on the **assistant's response tokens**. Masking the prompt tokens ensures the model is graded exclusively on generating the answer, rather than wasting model capacity learning to predict the user's prompt.

### Key hyperparameters: rank, alpha, and learning rate

When configuring a LoRA training run, four hyperparameters matter most:

1. **Rank (`r`):** The inner dimension of adapter matrices. Common choices are 8, 16, 32, or 64. For style adaptation, classification, or structured JSON formatting, `r = 16` is usually sufficient. Higher ranks increase adapter parameter count and memory usage without guaranteeing better performance.
2. **LoRA Alpha (`lora_alpha`):** The scaling multiplier. The standard rule of thumb is to set `lora_alpha = 2 * r` (for example, `r = 16`, `lora_alpha = 32`).
3. **Target Modules (`target_modules`):** Which linear layers receive LoRA adapters. In modern practice, apply LoRA to all linear projection layers in the transformer block: the attention projections (`q_proj`, `k_proj`, `v_proj`, `o_proj`) and the feed-forward projections (`gate_proj`, `up_proj`, `down_proj`).
4. **Learning Rate:** LoRA updates a small set of parameters from scratch, so it requires a higher learning rate than full fine-tuning. A learning rate between `1e-4` and `3e-4` with an AdamW or PagedAdamW optimizer is standard.
5. **Epochs:** 1 to 3 epochs. Training for more than 3 epochs on small domain datasets usually causes severe overfitting, leading to repetitive generations or degradation of the model's general reasoning abilities.

### The modern tooling stack: PEFT, TRL, and Unsloth

You rarely write LoRA loops from scratch in production. Three open-source libraries form the standard modern toolchain:

- **Hugging Face `peft`:** The foundational library that wraps any PyTorch model with LoRA, AdaLoRA, or prompt tuning configurations.
- **Hugging Face `trl` (Transformer Reinforcement Learning):** Provides `SFTTrainer`, a high-level trainer that integrates dataset packing, chat templates, and evaluation loops into a single interface.
- **Unsloth:** An open-source optimization framework that rewrites PyTorch transformer kernels in custom OpenAI Triton code. Unsloth cuts VRAM usage by up to 70% and accelerates training by 2x to 5x, making it the most popular choice for fine-tuning open models on single GPUs.

```python
# A complete SFT setup with Hugging Face TRL and PEFT
from peft import LoraConfig
from trl import SFTTrainer, SFTConfig

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

training_args = SFTConfig(
    output_dir="./mimir-lora-adapter",
    learning_rate=2e-4,
    num_train_epochs=2,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    warmup_ratio=0.03,
    logging_steps=10,
    fp16=True,
    max_seq_length=512,
)

# trainer = SFTTrainer(
#     model=model,
#     train_dataset=dataset,
#     peft_config=lora_config,
#     args=training_args,
# )
# trainer.train()
```

### Saving, merging, and evaluating adapters

When LoRA training finishes, the output is not a massive multi-gigabyte model checkpoint. It is a lightweight folder (usually 20 to 100 MB) containing `adapter_model.safetensors` and `adapter_config.json`.

You have two deployment options:

1. **Serve dynamically:** Load the frozen base model once in memory (using an engine like vLLM), and attach the small adapter at runtime. This allows a single running GPU server to serve dozens of specialized task adapters simultaneously.
2. **Merge weights:** Algebraically add `(alpha / r) * (B @ A)` back into `W_base`:

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM

base_model = AutoModelForCausalLM.from_pretrained("base-model-id")
model = PeftModel.from_pretrained(base_model, "./mimir-lora-adapter")

# Merges adapter weights into the base weights and unloads LoRA overhead
merged_model = model.merge_and_unload()
merged_model.save_pretrained("./merged-model-fp16")
```

Once merged, the model is a standard Hugging Face model with zero inference latency overhead. You can quantize it to GGUF format for local execution in Ollama, or deploy it to a high-throughput engine like vLLM, which you will explore in the next lesson.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the official [Hugging Face PEFT Conceptual Guide](https://huggingface.co/docs/peft/index).
   - Review how `get_peft_model` wraps a base transformer, and how `print_trainable_parameters()` verifies that under 1% of the model is trainable.
1. Work through the [Hugging Face TRL SFTTrainer documentation](https://huggingface.co/docs/trl/index).
   - Read the guides on dataset formatting and chat template integration.
1. Explore the [Unsloth documentation and notebook gallery](https://unsloth.ai/docs).
   - Review their guide on fine-tuning a small model (such as Llama 3.2 3B or Qwen 2.5 3B). Open one of their free Google Colab notebooks and run the first 50 steps on a sample dataset to verify that your GPU environment works.
1. Read the foundational research paper [LoRA: Low-Rank Adaptation of Large Language Models (Hu et al., 2021)](https://arxiv.org/abs/2106.09685).
   - Read sections 1 through 4. Focus on Section 4.1 regarding parameter budget and rank choice.
1. Write a Python script named `lora_param_counter.py`:
   - Calculate and print the exact parameter counts for a linear layer with `d_in = 4096` and `d_out = 4096`.
   - Calculate the parameter count of a LoRA adapter with `r = 8` and `r = 16`.
   - Print the percentage of parameters saved for both rank settings.

</div>

### Knowledge check

The questions below confirm that you have mastered the core ideas in this lesson. Click any question to review the section that explains it.

- [Why does full fine-tuning of an 8B parameter model require over 100 GB of GPU VRAM?](#full-fine-tuning-versus-parameter-efficient-fine-tuning)
- [How does low-rank matrix decomposition approximate weight updates with less memory?](#how-lora-works-low-rank-matrix-decomposition)
- [What is the difference between standard 16-bit LoRA and 4-bit QLoRA?](#qlora-4-bit-base-models-and-high-precision-adapters)
- [Why should the loss function only be computed on the assistant response tokens during SFT?](#preparing-chat-datasets-and-chat-templates)
- [What are the trade-offs between serving a dynamic LoRA adapter and merging weights into the base model?](#saving-merging-and-evaluating-adapters)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [QLoRA: Efficient Finetuning of Quantized LLMs (Dettmers et al., 2023)](https://arxiv.org/abs/2305.14314) is the paper that introduced 4-bit NormalFloat and paged optimizers.
- [Hugging Face Smol Course](https://huggingface.co/learn/smol-course) is a free comprehensive course on instruction tuning, alignment, and parameter-efficient methods for compact models.
- [Axolotl](https://github.com/axolotl-ai-cloud/axolotl) is a widely used configuration-driven framework for running production-grade LLM fine-tuning jobs.