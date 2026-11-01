### Introduction

Throughout Foundations and Core, you ran open-weight models locally using [Ollama](https://ollama.com/). Ollama is an excellent developer tool: a single command downloads a model, loads it into unified memory on your laptop, and serves a local HTTP endpoint.

However, desktop runners like Ollama are designed for a single user sitting at a workstation. When you deploy an AI application to hundreds of concurrent users, desktop runners collapse: requests queue up sequentially, GPU cores sit idle waiting for memory transfers, and throughput slows to a crawl.

Production serving of open models requires an entirely different software stack. High-throughput serving engines like [vLLM](https://docs.vllm.ai/), TGI, and SGLang use continuous batching, memory-paged key-value caches, and tensor parallelism to serve dozens of simultaneous requests per GPU.

This lesson bridges the gap between running models locally on your machine and deploying open models in production. You will learn why autoregressive decoding is memory-bandwidth bound, how PagedAttention revolutionized GPU memory management, how to calculate exactly how many concurrent users a GPU can handle, and what a GPU-hour really buys compared to commercial APIs.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The distinction between desktop inference runners (Ollama) and production serving engines (vLLM).
- Why autoregressive text generation is memory-bandwidth bound rather than compute bound.
- The Key-Value (KV) cache and how PagedAttention eliminates internal and external memory fragmentation.
- Static versus continuous (iteration-level) batching.
- Model quantization formats: GGUF, AWQ, GPTQ, and FP8.
- How to calculate GPU VRAM requirements for model weights, KV caches, and concurrency limits.
- Measuring serving performance: Time to First Token (TTFT), Inter-Token Latency (ITL), tokens per second, and dollar economics per million tokens.

### From desktop development to production serving

When evaluating open models, software engineers often confuse **local runners** with **production serving engines**.

- **Desktop runners (Ollama, llama.cpp):** Optimized for low latency for a single stream on consumer hardware (such as Apple Silicon or desktop Nvidia cards). They use quantized GGUF weights, handle prompt evaluation and generation sequentially, and prioritize zero-setup developer convenience.
- **Serving engines (vLLM, SGLang, TensorRT-LLM):** Engineered for maximum token throughput under high concurrency in cloud data centers. They expose an OpenAI-compatible HTTP interface (`/v1/chat/completions`), manage thousands of dynamic requests simultaneously, and saturate server-grade GPUs (like Nvidia A10G, L4, A100, and H100).

![Comparison between sequential batching and continuous iteration-level batching in vLLM](assets/images/continuous_batching_vllm.svg)

If you deploy Ollama behind a web app that receives 20 concurrent queries, request 20 will wait until requests 1 through 19 finish generating. A serving engine processes all 20 requests in interleaved parallel batches.

### Why inference is memory bound: the KV cache

To understand why LLM serving requires specialized engines, you must understand the **Key-Value (KV) cache**.

In [Building a Tiny GPT](#/paths/ml), you learned that calculating attention requires computing queries, keys, and values across all tokens:

```text
Attention(Q, K, V) = softmax((Q @ K.T) / sqrt(d_k)) @ V
```

During generation, the model predicts one token at a time. When generating token 51, the keys and values for tokens 1 through 50 have already been computed. Recomputing them from scratch at every single step would require `O(N^2)` matrix operations per token.

Instead, the model caches the `K` and `V` vectors for all past tokens in GPU VRAM. At each new step:
1. The model computes `Q`, `K`, and `V` for only the newest single token.
2. It appends the new `K` and `V` to the **KV cache**.
3. It attends over the cached keys and values to predict the next token.

This optimization speeds up computation, but introduces a massive memory bottleneck:
- Generating each token requires loading the entire model's weights from GPU VRAM into the compute cores once.
- Generating a single token from an 8-billion parameter model requires reading 16 GB of memory just to perform a few arithmetic operations per weight.
- Autoregressive generation is not limited by how fast the GPU can multiply numbers (FLOPS); it is limited by **memory bandwidth** (how fast data can be read from VRAM).

Furthermore, the KV cache grows dynamically with every token generated, consuming gigabytes of memory as sequence lengths and concurrency increase.

### PagedAttention and continuous batching

Traditional serving engines suffered from two major limitations:

#### 1. Memory fragmentation and waste
Before 2023, systems allocated a contiguous block of VRAM for each request's KV cache based on the maximum context length (for example, reserving 4,096 tokens worth of memory upfront). If the user only asked a 50-token question and got a 100-token answer, 96% of that reserved memory was wasted.

In 2023, researchers at UC Berkeley introduced **PagedAttention** (the core algorithm behind vLLM), inspired by virtual memory paging in operating systems:
- The KV cache is divided into fixed-size blocks (typically 16 or 32 tokens).
- Blocks are allocated dynamically on demand as tokens are generated, and do not need to be contiguous in physical memory.
- A page table maps logical sequence tokens to physical GPU memory frames.
- PagedAttention eliminates memory fragmentation, allowing serving engines to fit 2x to 4x more concurrent requests into the exact same GPU VRAM.

#### 2. Continuous batching
In traditional batching, requests are grouped together. If Request A finishes after 20 tokens while Request B needs 500 tokens, Request A's slot sits empty and wasted until Request B completes.

**Continuous batching** (or iteration-level batching) operates at the level of individual token iterations:
- At every single step of the model's forward pass, the engine evaluates a batch containing the next token for every active sequence.
- When any sequence finishes (hits an end-of-sequence token or stop word), it is immediately evicted from the batch.
- A new incoming request from the queue takes its place on the very next token iteration.

This keeps GPU compute units saturated at close to 100% capacity continuously.

### Quantization formats: GGUF, AWQ, and FP8

To reduce memory bandwidth pressure and fit larger models into smaller GPUs, open models are quantized to lower bit precision:

| Format | Typical Precision | Primary Use Case | Hardware Target |
| --- | --- | --- | --- |
| **BF16 / FP16** | 16-bit float | Training, zero-loss reference serving | Cloud GPUs (A100, H100) |
| **FP8** | 8-bit float | Production cloud serving with modern architectures | Nvidia Ada / Hopper (L4, H100) |
| **AWQ / GPTQ** | 4-bit integer | Cloud serving on constrained memory budgets | Nvidia Ampere / Ada (T4, A10G, RTX) |
| **GGUF** | 2-bit to 8-bit int | Single-user local desktop inference | Apple Silicon, CPUs, llama.cpp |

- **GGUF (GPT-Generated Unified Format):** Built for `llama.cpp` and Ollama. It packs tokenizers, metadata, and quantized tensors into a single file. Highly optimized for CPU and Apple Silicon memory architectures, but not the standard for high-concurrency cloud servers.
- **AWQ (Activation-aware Weight Quantization):** Protects the top 1% of salient weights that carry the most information while compressing the remaining 99% to 4-bit. It runs exceptionally fast in vLLM on cloud GPUs.
- **FP8 (8-bit Floating Point):** The emerging standard for modern enterprise hardware (Nvidia L4, H100). It cuts memory in half compared to 16-bit with virtually zero degradation in model reasoning capability, and requires no custom calibration datasets.

### Calculating GPU VRAM and concurrency capacity

Before launching a GPU instance on AWS, GCP, or RunPod, you must calculate whether your model and target concurrency will fit in memory.

Total VRAM required is:

```text
Total VRAM = Model Weights + KV Cache + Activation / CUDA Overhead (≈ 2 GB)
```

#### 1. Model weights
```text
Weight Memory = Parameter Count * Bytes per Parameter
```
- An 8B model in 16-bit (2 bytes): `8 * 2 = 16 GB`
- An 8B model in 8-bit (1 byte): `8 * 1 = 8 GB`
- An 8B model in 4-bit (0.5 bytes): `8 * 0.5 = 4 GB`

#### 2. KV cache per token
For a transformer model, each token in context stores a key vector and a value vector across every layer:

```text
KV Cache per Token (bytes) = 2 * (num_layers * num_kv_heads * head_dim) * precision_bytes
```

For Llama-3.1-8B (32 layers, 8 KV heads with Grouped-Query Attention, head dimension 128, 16-bit precision):

```text
KV per Token = 2 * (32 * 8 * 128) * 2 bytes = 131,072 bytes ≈ 128 KB per token
```

For a 2,048-token conversation:
- `128 KB * 2,048 tokens ≈ 256 MB` per concurrent active stream.

#### Sizing an example deployment:
Suppose you rent an **Nvidia A10G GPU (24 GB VRAM)** costing roughly \$1.00 per hour, serving an 8B model quantized with 4-bit AWQ:

```text
Total VRAM:            24 GB
Model weights (4-bit): -5.5 GB
CUDA / Runtime buffer: -2.0 GB
Available for KV Cache: 16.5 GB (16,500 MB)

Max concurrent 2k streams = 16,500 MB / 256 MB ≈ 64 concurrent streams!
```

A single \$1/hour GPU can actively generate text for 64 users simultaneously without queueing.

### Benchmarking throughput and cost per token

When evaluating serving infrastructure, track four primary metrics:

1. **Time to First Token (TTFT):** The time from when a user submits a prompt until the first token streams back. This measures **prefill** latency (how fast the engine processes the prompt tokens).
2. **Inter-Token Latency (ITL):** The time elapsed between consecutive tokens during generation. For human reading comfort, an ITL under 30 to 50 milliseconds (20 to 33 tokens/sec) feels instant.
3. **Total Throughput:** The total number of tokens generated across all concurrent users per second (e.g., 800 tokens/sec across 40 users).
4. **Cost per Million Tokens:**

```text
Cost per MTok = (Hourly GPU Cost / Tokens Generated per Hour) * 1,000,000
```

If your 24 GB GPU ($1.00/hour) generates an average of 400 tokens per second across its active users:
- In one hour, it generates `400 * 3,600 = 1,440,000 tokens` (1.44 MTok).
- Cost per million tokens: `$1.00 / 1.44 ≈ $0.69 per million tokens`.

Compare this to commercial APIs: if a hosted frontier model costs \$0.80 to \$3.00 per million tokens, running an open model at steady utilization can be significantly cheaper, while guaranteeing complete data privacy, zero data retention, and custom low-rank adapters.

### Launching and calling a vLLM server

vLLM exposes a standard drop-in replacement for the OpenAI API. You launch it from the command line:

```bash
# Launching an open 8B model with vLLM
vllm serve meta-llama/Llama-3.1-8B-Instruct \
    --dtype bfloat16 \
    --max-model-len 4096 \
    --gpu-memory-utilization 0.90 \
    --port 8000
```

Once running, any code that uses the official OpenAI client or an open-source framework calls it simply by changing the `base_url`:

```python
# test_vllm_client.py: Calling a self-hosted vLLM engine
import os
from openai import OpenAI

# Connect to the local or cloud vLLM server
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="EMPTY"  # vLLM requires no API key by default
)

response = client.chat.completions.create(
    model="meta-llama/Llama-3.1-8B-Instruct",
    messages=[
        {"role": "system", "content": "You are a concise production support assistant."},
        {"role": "user", "content": "Explain what continuous batching is in two sentences."}
    ],
    temperature=0.2,
    max_tokens=150,
)

print(response.choices[0].message.content)
```

Because vLLM speaks the standard OpenAI wire protocol, your frontend interfaces, streaming readers, agent tool-use loops, and eval harnesses from the AI Engineering Core and Agentic Systems paths connect to self-hosted open models without changing a single line of application logic.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [vLLM Quickstart and Engine Arguments documentation](https://docs.vllm.ai/en/latest/).
   - Note the roles of `--gpu-memory-utilization`, `--max-model-len`, and `--max-num-seqs`.
1. Read the original research paper on PagedAttention: [Efficient Memory Management for Large Language Model Serving with PagedAttention (Kwon et al., 2023)](https://arxiv.org/abs/2309.06180).
   - Read Sections 1 through 3. Examine Figure 2 to understand how internal and external memory fragmentation waste VRAM in naive serving systems.
1. Inspect the [vLLM GitHub repository](https://github.com/vllm-project/vllm).
   - Review `vllm/entrypoints/openai/` to see how FastAPI powers the OpenAI-compatible HTTP server.
1. Write a Python script named `vram_calculator.py`:
   - Accept parameters: model parameter count (e.g. 8 billion), bit precision (16, 8, or 4), number of layers (32), number of KV heads (8), head dimension (128), context length (4096), and target concurrency (e.g. 32 streams).
   - Calculate and print: weight memory (GB), KV cache per stream (MB), total KV cache for all streams (GB), and minimum recommended GPU VRAM including a 2 GB system buffer.

</div>

### Knowledge check

The questions below confirm that you have mastered the core ideas in this lesson. Click any question to review the section that explains it.

- [Why is desktop inference with Ollama unsuitable for high-concurrency production deployments?](#from-desktop-development-to-production-serving)
- [Why is autoregressive token generation memory-bandwidth bound rather than compute bound?](#why-inference-is-memory-bound-the-kv-cache)
- [How does PagedAttention eliminate memory waste when managing the KV cache?](#pagedattention-and-continuous-batching)
- [What is continuous batching and how does it prevent idle GPU cycles?](#pagedattention-and-continuous-batching)
- [How do you calculate the VRAM required to serve an open model under concurrent user load?](#calculating-gpu-vram-and-concurrency-capacity)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [SGLang](https://github.com/sgl-project/sglang) is an alternative high-throughput serving engine with specialized optimizations for multi-turn structured generation and reasoning models.
- [Hugging Face Text Generation Inference (TGI)](https://github.com/huggingface/text-generation-inference) is an enterprise containerized serving solution developed by Hugging Face.
- [SemiAnalysis: The Inference Cost Economics of LLMs](https://semianalysis.com/) offers detailed economic breakdowns of GPU cluster leasing versus frontier API pricing.