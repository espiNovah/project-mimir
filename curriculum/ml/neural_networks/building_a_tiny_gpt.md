### Introduction

In [Transformers and Attention](#/paths/foundations), you learned what a transformer does from a high-level architectural view. Now you will build one.

A tiny generative pretrained transformer (GPT), trained on a few megabytes of text using a free GPU, uses the exact same core architecture as the frontier models you call through an API. It has fewer layers, smaller hidden dimensions, and uses characters instead of subword tokens, but the computational mechanics are identical.

Building a decoder-only transformer from scratch in PyTorch is widely regarded as a milestone in an AI engineer's education. It demystifies language models: you see that beneath the marketing terminology, an autoregressive language model is simply a sequence of matrix multiplications, causal attention masks, and softmax operations predicting the next token.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- How language modeling formalizes text generation as autoregressive next-token prediction.
- Why building a simple bigram baseline is essential before writing complex architectures.
- The mechanics of self-attention: how queries, keys, and values allow tokens to communicate.
- Why causal masking prevents tokens from attending to future positions during training.
- Multi-head attention, feed-forward sublayers, residual connections, and layer normalization.
- The key differences between a micro-GPT and multi-billion-parameter production assistants.

### Language modeling as next-token prediction

At its core, an autoregressive language model solves one problem: given an existing sequence of tokens, predict the probability distribution for the token that comes next:

```text
P(token_t | token_1, token_2, ..., token_{t-1})
```

To train a model to do this:
1. Take a continuous body of text (such as the works of Shakespeare or open-source documentation).
2. Convert text into a sequence of integer token IDs using a vocabulary.
3. Slice the sequence into chunks of maximum context length `T` (also called block size).
4. For every position `t` from 1 to `T-1`, the input is the prefix up to `t`, and the target label is the token at `t+1`.

Training minimizes **cross-entropy loss**: the average negative log-likelihood assigned to the correct next token across all positions.

Once trained, generating text is an autoregressive loop: pass a prompt into the model, evaluate the logits for the final position, apply softmax with a temperature parameter to get probabilities, sample the next token, append it to the prompt, and repeat.

### The bigram baseline

Before constructing a multi-layer transformer, always establish a simple baseline. This builds directly on the baseline habits you developed in [Overfitting and Baselines](#/paths/core).

The simplest language model is a **bigram model**: it predicts the next character using only the single character immediately preceding it, completely ignoring earlier context.

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class BigramLanguageModel(nn.Module):
    def __init__(self, vocab_size: int):
        super().__init__()
        # Each token directly looks up the logits for the next token
        self.token_embedding_table = nn.Embedding(vocab_size, vocab_size)

    def forward(self, idx: torch.Tensor, targets: torch.Tensor = None):
        # idx and targets are both (batch_size, time_steps)
        logits = self.token_embedding_table(idx)  # (batch_size, time_steps, vocab_size)
        
        if targets is None:
            loss = None
        else:
            B, T, C = logits.shape
            logits_flat = logits.view(B * T, C)
            targets_flat = targets.view(B * T)
            loss = F.cross_entropy(logits_flat, targets_flat)
            
        return logits, loss
```

If a vocabulary has 65 characters, uniform random guessing produces a loss of `-ln(1/65) ≈ 4.17`. A trained bigram model typically drops the validation loss to around `2.45`. The characters start forming alternating consonants and vowels, but cannot form coherent words because the model has no memory beyond one step. Any transformer architecture you build must decisively beat this baseline loss.

### Self-attention: queries, keys, and values

A bigram model fails because tokens cannot look back at earlier words. In a sentence like:

> "The developer debugged the application because **it** was failing."

To understand what "**it**" refers to, the model needs a mechanism to route information from "application" to "it".

**Self-attention** solves this by letting every token look at every preceding token and decide how much information to gather. Each token at position `t` emits three vectors:

1. **Query (`q`):** "What am I looking for?"
2. **Key (`k`):** "What do I contain?"
3. **Value (`v`):** "What information do I share if selected?"

To calculate how much token `i` attends to token `j`, we compute the dot product between the query of token `i` and the key of token `j`:

```text
attention_score[i, j] = (q_i · k_j) / sqrt(d_k)
```

Dividing by the square root of the head dimension `sqrt(d_k)` scales the variance so that dot products do not grow excessively large on high-dimensional vectors, which would cause the softmax to saturate and produce vanishing gradients.

We then apply softmax across all candidate positions `j` to get non-negative attention weights that sum to 1.0. Finally, the output for token `i` is the weighted sum of the value vectors `v_j`:

```text
Attention(Q, K, V) = softmax((Q @ K.T) / sqrt(d_k)) @ V
```

```python
# A single head of self-attention
class Head(nn.Module):
    def __init__(self, n_embd: int, head_size: int, block_size: int):
        super().__init__()
        self.key = nn.Linear(n_embd, head_size, bias=False)
        self.query = nn.Linear(n_embd, head_size, bias=False)
        self.value = nn.Linear(n_embd, head_size, bias=False)
        
        # Causal mask: lower-triangular matrix of ones
        self.register_buffer("tril", torch.tril(torch.ones(block_size, block_size)))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, T, C = x.shape
        k = self.key(x)    # (B, T, head_size)
        q = self.query(x)  # (B, T, head_size)
        
        # Compute attention scores ("affinities")
        wei = (q @ k.transpose(-2, -1)) * (k.shape[-1] ** -0.5)  # (B, T, T)
        
        # Causal masking: mask future positions with -infinity
        wei = wei.masked_fill(self.tril[:T, :T] == 0, float("-inf"))
        wei = F.softmax(wei, dim=-1)  # (B, T, T)
        
        # Weighted aggregation of values
        v = self.value(x)  # (B, T, head_size)
        out = wei @ v      # (B, T, head_size)
        return out
```

### Causal masking and multi-head attention

Notice the `masked_fill` line in the attention head above:

```text
wei.masked_fill(tril == 0, float("-inf"))
```

Because `exp(-inf) = 0`, applying softmax turns those masked future positions into exact zero probability.

This is **causal masking**. During training, we feed entire sequences of tokens to the model simultaneously for parallel efficiency. Without causal masking, token 3 would be able to see token 4's key and value directly, allowing the model to cheat on next-token prediction without learning anything generalizable. Causal masking ensures position `t` only receives information from positions `<= t`.

Rather than computing a single set of queries, keys, and values, modern transformers use **Multi-Head Attention**. Multiple heads run the attention calculation in parallel with smaller head dimensions, and their outputs are concatenated together:

```python
class MultiHeadAttention(nn.Module):
    def __init__(self, n_embd: int, n_head: int, block_size: int):
        super().__init__()
        head_size = n_embd // n_head
        self.heads = nn.ModuleList([Head(n_embd, head_size, block_size) for _ in range(n_head)])
        self.proj = nn.Linear(n_embd, n_embd)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Concatenate outputs from all attention heads along feature dimension
        out = torch.cat([h(x) for h in self.heads], dim=-1)
        return self.proj(out)
```

Having multiple attention heads allows the model to attend to different aspects of context simultaneously: one head might track grammatical subject-verb agreement, another might track proximity, and another might link pronouns to their antecedents.

### The transformer block: residual connections and layer norm

A standard transformer block consists of two sublayers wrapped in **residual connections** and **layer normalization**:

1. **Multi-Head Self-Attention:** Moves information across time positions.
2. **Feed-Forward Network (MLP):** Processes each token independently through a 2-layer expansion and contraction.

![Decoder transformer block with attention, MLP, and residual connections](assets/images/transformer_block.svg)

```text
FFN(x) = GELU(x @ W1 + b1) @ W2 + b2
```

Deep networks suffer from vanishing gradients when gradients pass through many sequential operations. **Residual connections** (or skip connections) bypass each sublayer:

```text
x = x + Sublayer(LayerNorm(x))
```

The addition operation acts as a gradient highway: during backpropagation, the gradient splits and passes straight through the addition unchanged (`d(x + f(x))/dx = 1 + f'(x)`), allowing gradients to flow back to the earliest layers without degradation.

**Layer Normalization** (`nn.LayerNorm`) normalizes activations across the feature dimension to have mean 0 and variance 1, stabilizing training dynamics across deep stacks.

```python
class Block(nn.Module):
    def __init__(self, n_embd: int, n_head: int, block_size: int):
        super().__init__()
        self.ln1 = nn.LayerNorm(n_embd)
        self.sa = MultiHeadAttention(n_embd, n_head, block_size)
        self.ln2 = nn.LayerNorm(n_embd)
        self.ffwd = nn.Sequential(
            nn.Linear(n_embd, 4 * n_embd),
            nn.GELU(),
            nn.Linear(4 * n_embd, n_embd),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Pre-layer normalization with residual connections
        x = x + self.sa(self.ln1(x))
        x = x + self.ffwd(self.ln2(x))
        return x
```

### From tiny GPT to production frontier models

Your tiny GPT and a production frontier model share the exact same underlying transformer block structure. The differences are not qualitative architectural secrets; they are engineering scale and training stages:

| Component | Tiny GPT (This Path) | Production Frontier LLM |
| --- | --- | --- |
| **Tokenizer** | Character-level (~65 tokens) | Byte-Pair Encoding (BPE) (32k–128k tokens) |
| **Parameters** | 1 to 10 million parameters | 8 billion to 1+ trillion parameters |
| **Context Length** | 64 to 256 characters | 8,000 to 1,000,000+ tokens |
| **Training Data** | 1 to 10 MB of text | 10 to 15+ trillion tokens of filtered web data |
| **Post-Training** | None (pure next-character generator) | SFT (Instruction tuning), RLHF, and DPO |

A base pretrained transformer is an autocomplete engine: given any text, it continues it in the most statistically likely manner. In Section 3, you will explore how open-source foundation models are adapted through parameter-efficient fine-tuning (LoRA) and serving engines to build practical applications.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Watch the transformer chapters from [3Blue1Brown's neural networks series](https://www.3blue1brown.com/topics/neural-networks).
   - Watch "Transformers, the tech behind LLMs" and [the attention chapter](https://www.3blue1brown.com/lessons/attention). Focus on how the query and key vectors calculate dot-product affinity scores.
1. Work through Andrej Karpathy's video: [Let's build GPT: from scratch, in code, spelled out](https://www.youtube.com/watch?v=kCc8FmEb1nY).
   - Code along in a Colab or Kaggle notebook with a GPU runtime.
   - Start by building the bigram model, calculate its train and validation loss, and confirm that your implementation reproduces Karpathy's results before introducing self-attention blocks.
1. Read [The Illustrated Transformer by Jay Alammar](https://jalammar.github.io/illustrated-transformer/).
   - Inspect the step-by-step tensor diagrams for matrix-form multi-head attention and the feed-forward sublayer.
1. Inspect the [nanoGPT repository](https://github.com/karpathy/nanoGPT).
   - Read `model.py` from top to bottom. Note how clean and concise a modern GPT implementation is (under 300 lines of PyTorch code).
1. Watch [Karpathy's Deep Dive into LLMs](https://www.youtube.com/watch?v=7xTGNNLPyMI) to connect pretraining to modern conversational assistants.
   - Note the distinction between the base pretraining phase and the supervised fine-tuning (SFT) phase.

</div>

### Knowledge check

The questions below confirm that you have mastered the core ideas in this lesson. Click any question to review the section that explains it.

- [What is the mathematical objective optimized during autoregressive language model training?](#language-modeling-as-next-token-prediction)
- [What roles do queries, keys, and values play in the self-attention calculation?](#self-attention-queries-keys-and-values)
- [Why is causal masking strictly necessary when training generative transformers?](#causal-masking-and-multi-head-attention)
- [How do residual connections prevent vanishing gradients in deep transformer architectures?](#the-transformer-block-residual-connections-and-layer-norm)
- [What are the primary differences between a character-level micro-GPT and a production frontier model?](#from-tiny-gpt-to-production-frontier-models)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Attention Is All You Need (Vaswani et al., 2017)](https://arxiv.org/abs/1706.03762) is the original research paper that introduced the transformer architecture.
- [Hugging Face: The Annotated Transformer](https://nlp.seas.harvard.edu/annotated-transformer/) provides a line-by-line PyTorch walkthrough of the original transformer paper.
- [TransformerLens](https://github.com/TransformerLensOrg/TransformerLens) is an open-source library designed for mechanistic interpretability of transformer activations and attention patterns.