### Introduction

Pretrained language models are next-token predictors. After pretraining on web crawl data, an autoregressive model will readily complete sentences, mimic internet forums, or hallucinate plausible fiction, but it does not reliably follow user instructions, refuse harmful prompts, or solve multi-step mathematical proofs.

Transforming a base predictive model into an instruction-following assistant or an autonomous reasoning engine is the task of **post-training**, and reinforcement learning (RL) is its core engine.

This lesson explores how modern language models are framed as stochastic policies in a Markov Decision Process:
1. **The classical three-stage RLHF pipeline:** Supervised fine-tuning (SFT), reward modeling via the Bradley-Terry preference model, and PPO with a Kullback-Leibler (KL) divergence penalty.
2. **Direct Preference Optimization (DPO):** The mathematical insight that eliminates the separate reward model and online rollouts entirely.
3. **Verifiable rewards and Group Relative Policy Optimization (GRPO):** How DeepSeek-R1 and modern reasoning models use programmatic ground-truth feedback (unit tests and symbolic math) to incentivize long-horizon thinking without human annotators or critic networks.

### The language model as a policy

We can formalize autoregressive generation as an episodic MDP:
- **State `s_t`:** The initial prompt `x` concatenated with all tokens generated up to time step `t`: `s_t = (x, y_1, y_2, ..., y_{t-1})`.
- **Action `a_t`:** The single token `y_t` selected from the model vocabulary `V` (where `|V|` is typically 32,000 to 128,000).
- **Policy `π_θ(a_t | s_t)`:** The conditional next-token probability distribution produced by the transformer's final linear projection and softmax:
  ```text
  π_θ(y_t | x, y_{<t}) = softmax( W_head · h_t )
  ```
- **Transition dynamics:** Deterministic string concatenation: `s_{t+1} = (s_t, y_t)`.
- **Episode termination:** Generation ends when the model emits the special End-of-Sequence token `[EOS]` or reaches the context length limit `T`.
- **Reward `R`:** In standard language tasks, intermediate tokens receive zero reward (`r_t = 0` for `t < T`). A scalar feedback reward is assigned only at the terminal state upon completion of the entire response `y`.

Because the vocabulary is large, standard Q-learning is unviable. The policy gradient framework derived in [Policy Gradients](#/lesson/research/reinforcement_learning/policy_gradients) provides the natural foundation for training LLMs.

### The three-stage RLHF pipeline

Introduced in InstructGPT (Ouyang et al., 2022), Reinforcement Learning from Human Feedback consists of three sequential phases:

![Post-Training Alignment Paradigms for Large Language Models](assets/images/rlhf_dpo_grpo_pipeline.svg)

#### Stage 1: Supervised Fine-Tuning (SFT)

A base foundation model is trained on tens of thousands of high-quality human demonstrations `(prompt, response)` using standard cross-entropy loss. This teaches the model the conversational format (user turn vs. assistant turn) and basic task compliance.

#### Stage 2: Bradley-Terry reward modeling

Human annotators cannot reliably assign absolute numerical scores (e.g. "is this response a 7.4 or an 8.1?"). However, humans are reliable at comparing pairs: given prompt `x` and two model completions `y_w` (preferred/winning) and `y_l` (rejected/losing), which one is better?

Under the **Bradley-Terry preference model**, the probability that response `y_w` is preferred over `y_l` is parameterized by a scalar reward model `r_ϕ(x, y)`:

```text
P( y_w > y_l | x ) = σ( r_ϕ(x, y_w) - r_ϕ(x, y_l) )
```

where `σ(z) = 1 / (1 + exp(-z))` is the sigmoid function. The reward model (typically an SFT checkpoint with its final unembedding head replaced by a single scalar output) is trained by minimizing the negative log-likelihood:

```text
L_{RM}(ϕ) = - E_{(x, y_w, y_l) ~ D} [ log σ( r_ϕ(x, y_w) - r_ϕ(x, y_l) ) ]
```

#### Stage 3: PPO with the KL divergence leash

Once `r_ϕ` is frozen, the language model policy `π_θ` is fine-tuned to maximize the expected reward across a wide distribution of prompts.

However, optimizing solely against the reward model leads to **reward hacking** (Goodhart's Law: *"When a measure becomes a target, it ceases to be a good measure"*). Without constraints, the policy exploits imperfections in the neural reward model, producing repetitive, verbose, or unnatural gibberish that tricks the scalar scorer.

To prevent this drift, RLHF constrains the active policy `π_θ` using a **per-token Kullback-Leibler (KL) penalty** relative to the initial frozen SFT reference policy `π_ref`:

```text
max_θ  E_{x ~ D, y ~ π_θ(·|x)} [ r_ϕ(x, y) - β * D_KL( π_θ(y | x) || π_ref(y | x) ) ]
```

where `β` acts as an adjustable leash:
- High `β`: The model stays glued to the SFT distribution, preventing hallucination and reward hacking.
- Low `β`: The model explores aggressively to maximize reward, risking distribution collapse.

In practice, the per-token KL divergence is calculated directly from the log-ratio:

```text
r_augmented(x, y) = r_ϕ(x, y) - β * [ log π_θ(y | x) - log π_ref(y | x) ]
```

The PPO algorithm updates `π_θ` using this augmented reward.

### Direct preference optimization (DPO)

While RLHF with PPO was effective, it was notoriously complex and resource-intensive: training required running four distinct neural models concurrently in GPU memory (the active policy `π_θ`, the frozen reference model `π_ref`, the reward model `r_ϕ`, and the value critic network `V_ψ`).

In 2023, Rafailov et al. introduced **Direct Preference Optimization (DPO)**, showing that the KL-constrained RLHF objective can be solved analytically.

#### Mathematical derivation

Recall the KL-constrained objective:

```text
max_π  E_{x ~ D} [ E_{y ~ π(·|x)} [ r(x, y) ] - β * D_KL( π(y | x) || π_ref(y | x) ) ]
```

By expanding the definition of KL divergence and applying Jensen's inequality, this optimization problem has a unique closed-form global maximum:

```text
π*(y | x) = (1 / Z(x)) * π_ref(y | x) * exp( (1 / β) * r(x, y) )
```

where `Z(x) = Σ_y π_ref(y | x) exp( (1 / β) * r(x, y) )` is the partition function.

We can invert this equation to express the ground-truth reward function `r(x, y)` purely in terms of the optimal policy `π*` and the reference policy `π_ref`:

```text
r(x, y) = β * log( π*(y | x) / π_ref(y | x) ) + β * log Z(x)
```

Now, substitute this expression directly into the Bradley-Terry preference objective `σ( r(x, y_w) - r(x, y_l) )`:

```text
r(x, y_w) - r(x, y_l) = β * log( π*(y_w | x) / π_ref(y_w | x) ) - β * log( π*(y_l | x) / π_ref(y_l | x) )
```

The partition function `Z(x)` depends only on the prompt `x` and cancels out completely!

This gives the **DPO loss function**:

```text
L_{DPO}(θ; π_ref) = - E_{(x, y_w, y_l)} [ log σ( β * log( π_θ(y_w | x) / π_ref(y_w | x) ) - β * log( π_θ(y_l | x) / π_ref(y_l | x) ) ) ]
```

DPO requires no reward model, no critic network, and zero autoregressive token generation during training. It runs as a standard supervised cross-entropy-style batch loss directly over offline preference pairs.

```python
import torch
import torch.nn.functional as F

def compute_dpo_loss(
    policy_chosen_logps: torch.Tensor,
    policy_rejected_logps: torch.Tensor,
    ref_chosen_logps: torch.Tensor,
    ref_rejected_logps: torch.Tensor,
    beta: float = 0.1,
) -> torch.Tensor:
    """Computes the Direct Preference Optimization loss."""
    pi_logratios = policy_chosen_logps - policy_rejected_logps
    ref_logratios = ref_chosen_logps - ref_rejected_logps

    logits = beta * (pi_logratios - ref_logratios)
    loss = -F.logsigmoid(logits).mean()
    return loss
```

### Verifiable rewards and GRPO (DeepSeek-R1)

While preference models work well for general conversational tone, they break down on objective reasoning domains (such as competitive mathematics and software engineering). Neural reward models are easily fooled by verbose proofs that end in incorrect arithmetic, or buggy code with confident docstrings.

#### Verifiable rule-based rewards

In domains where correctness can be mechanically checked, we replace neural reward models with deterministic verification functions:
- **Unit test execution:** Run generated code in a sandboxed interpreter against test suites (reward = 1.0 if all tests pass; 0.0 otherwise).
- **Symbolic math equivalence:** Parse candidate answers using SymPy or Math-Verify (reward = 1.0 if mathematical equality holds with ground truth; 0.0 otherwise).
- **Format compliance:** Enforce `<think>...</think><answer>...</answer>` XML tag structure.

#### Group Relative Policy Optimization (GRPO)

Introduced in DeepSeekMath (Shao et al., 2024) and scaled in DeepSeek-R1 (2025), **GRPO** removes the need for a separate value critic network `V_ϕ(s)` entirely:

1. For each training prompt `x`, the model samples a group of `G` completions: `{y_1, y_2, ..., y_G} ~ π_{θ_old}(· | x)`.
2. Each completion receives an automated rule-based score `{r_1, r_2, ..., r_G}`.
3. The advantage `A_i` of output `y_i` is computed by standardizing rewards relative to the group mean and standard deviation:
   ```text
   A_i = (r_i - mean({r_1, ..., r_G})) / (std({r_1, ..., r_G}) + 1e-8)
   ```
4. The policy is updated using a PPO-style clipped surrogate loss computed over the token sequences, regularized by an analytical token-level KL penalty against the reference model.

Eliminating the critic network frees roughly 50% of GPU training VRAM, enabling training across hundreds of billions of parameters. Furthermore, training models purely with verifiable rewards causes long chains of thought, self-correction, and backtracking behaviors to emerge autonomously without human demonstration data.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Training language models to follow instructions with human feedback](https://arxiv.org/abs/2203.02155) (InstructGPT).
   - Review sections 1 to 3 and Figure 2. Note how the Bradley-Terry loss maps pairwise human comparisons into a scalar reward space.
2. Read [Direct Preference Optimization: Your Language Model is Secretly a Reward Model](https://arxiv.org/abs/2305.18290) (Rafailov et al., 2023).
   - Work through Section 4's derivation step-by-step with pen and paper, confirming why the partition function `Z(x)` vanishes.
3. Read [DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning](https://arxiv.org/abs/2501.12948).
   - Read Section 2 on DeepSeek-R1-Zero. Note the emergence of the "aha moment" where the model learns to rethink its intermediate calculations.
4. Consult Nathan Lambert's free [RLHF Book](https://rlhfbook.com/) as your comprehensive guide to modern alignment.
   - Read the chapters on Reward Modeling and Direct Alignment Algorithms.
5. Explore the [Hugging Face TRL Library Documentation](https://huggingface.co/docs/trl/index).
   - Inspect the implementation of `DPOTrainer` and `GRPOTrainer`.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Illustrating Reinforcement Learning from Human Feedback (RLHF)](https://huggingface.co/blog/rlhf): Hugging Face's illustrated guide to the 3-stage alignment process.
- [Constitutional AI: Harmlessness from AI Feedback](https://arxiv.org/abs/2212.08073): Anthropic's methodology for training harmless models using AI feedback (RLAIF) governed by principles.
- [DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models](https://arxiv.org/abs/2402.03300): The original derivation and implementation of GRPO.
- [Open R1 GitHub Repository](https://github.com/huggingface/open-r1): Hugging Face's fully open reproduction of the DeepSeek-R1 training pipeline.

### Knowledge check

Use these questions to verify your understanding of RL for LLMs:

1. [How is next-token text generation mathematically formulated as an episodic Markov Decision Process?](#the-language-model-as-a-policy)
2. [What is the purpose of the per-token KL divergence penalty in the standard PPO RLHF objective?](#the-three-stage-rlhf-pipeline)
3. [How does Direct Preference Optimization (DPO) derive an exact loss function without requiring an explicit reward model or critic network?](#direct-preference-optimization-dpo)
4. [Why do neural reward models struggle with mathematics and code generation, and how do verifiable rewards resolve this?](#verifiable-rewards-and-grpo-deepseek-r1)
5. [How does Group Relative Policy Optimization (GRPO) calculate advantage estimates without a value network?](#verifiable-rewards-and-grpo-deepseek-r1)
