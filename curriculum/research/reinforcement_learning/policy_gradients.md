### Introduction

Value-based methods like Q-learning must first learn the expected return for every possible action before deriving a policy by taking the greedy `argmax`. While effective in discrete domains with small action sets, value-based methods face fundamental limitations:
1. They cannot easily scale to continuous action spaces (such as robotics torque controls) or combinatorially large action spaces (such as generating tokens from a 128,000-word vocabulary).
2. They cannot natively represent stochastic policies, which are required in competitive games with imperfect information (such as poker).
3. A tiny perturbation in estimated Q-values can cause a discontinuous change in the greedy action selected, inducing training instability.

**Policy gradient methods** overcome these hurdles by parameterizing the policy directly as `π_θ(a | s)`. Instead of estimating values to pick actions, we perform gradient ascent directly on the expected cumulative return `J(θ)`.

This lesson derives the Policy Gradient Theorem from first principles, examines why REINFORCE exhibits severe variance, introduces variance-reduction baselines and actor-critic architectures, and details Proximal Policy Optimization (PPO)—the algorithm that enabled early breakthroughs in conversational AI and RLHF.

### Parameterized policies and the objective function

We parameterize a stochastic policy `π_θ(a | s)` using weights `θ`:
- For **discrete actions**, the neural network outputs logits `z = f_θ(s)` passed through a softmax:
  ```text
  π_θ(a_i | s) = exp(z_i) / Σ_j exp(z_j)
  ```
- For **continuous actions**, the network outputs the mean `μ_θ(s)` and standard deviation `σ_θ(s)` of a Gaussian distribution:
  ```text
  a ~ Normal( μ_θ(s), σ_θ(s)^2 )
  ```

Let `τ = (s_0, a_0, r_1, s_1, a_1, ..., s_T)` denote an entire trajectory. The probability of trajectory `τ` under policy `θ` and environment transition dynamics `P` is:

```text
P(τ; θ) = μ(s_0) * Π_{t=0}^{T-1} [ π_θ(a_t | s_t) * P(s_{t+1} | s_t, a_t) ]
```

The objective is to maximize the expected total discounted return over trajectories:

```text
J(θ) = E_{τ ~ π_θ} [ R(τ) ] = ∫ P(τ; θ) * R(τ) dτ
```

where `R(τ) = Σ_{t=0}^T γ^t r_{t+1}`.

### The policy gradient theorem and the log-derivative trick

To optimize `J(θ)` via gradient ascent, we compute `∇_θ J(θ)`:

```text
∇_θ J(θ) = ∇_θ ∫ P(τ; θ) * R(τ) dτ = ∫ ∇_θ P(τ; θ) * R(τ) dτ
```

We cannot evaluate this integral directly because `∇_θ P(τ; θ)` is not a valid probability distribution. Here enters the **log-derivative trick** (also known as the likelihood ratio or REINFORCE trick):

```text
∇_θ P(τ; θ) = P(τ; θ) * [ ∇_θ P(τ; θ) / P(τ; θ) ] = P(τ; θ) * ∇_θ log P(τ; θ)
```

Substituting this identity converts the integral back into an expectation:

```text
∇_θ J(θ) = ∫ P(τ; θ) * ∇_θ log P(τ; θ) * R(τ) dτ = E_{τ ~ π_θ} [ ∇_θ log P(τ; θ) * R(τ) ]
```

Now expand the log-probability of the trajectory `τ`:

```text
log P(τ; θ) = log μ(s_0) + Σ_{t=0}^{T-1} log π_θ(a_t | s_t) + Σ_{t=0}^{T-1} log P(s_{t+1} | s_t, a_t)
```

Taking the gradient with respect to `θ`:
- `∇_θ log μ(s_0) = 0` (initial state distribution does not depend on `θ`).
- `∇_θ log P(s_{t+1} | s_t, a_t) = 0` (environment physics do not depend on `θ`).

The unknown transition dynamics vanish completely:

```text
∇_θ log P(τ; θ) = Σ_{t=0}^{T-1} ∇_θ log π_θ(a_t | s_t)
```

This leads to the **Policy Gradient Theorem**:

```text
∇_θ J(θ) = E_{τ ~ π_θ} [ Σ_{t=0}^{T-1} ∇_θ log π_θ(a_t | s_t) * G_t ]
```

where `G_t = Σ_{k=t}^T γ^{k-t} r_{k+1}` is the return following step `t` (causality dictates that actions taken at time `t` cannot be reinforced by rewards received prior to time `t`).

### REINFORCE and variance reduction via baselines

The classic **REINFORCE** algorithm (Williams, 1992) approximates `∇_θ J(θ)` using Monte Carlo samples of complete episodes:

```text
θ ← θ + α * Σ_{t=0}^T ∇_θ log π_θ(a_t | s_t) * G_t
```

#### The variance problem

Because `G_t` accumulates random rewards over an entire rollout, empirical returns vary widely from run to run. Even if an action was mediocre, if the rest of the rollout happened to hit high rewards by chance, REINFORCE will strongly increase the probability of that mediocre action.

#### Subtracting a baseline

To reduce variance without introducing bias, we subtract a state-dependent baseline `b(s)` from the return:

```text
∇_θ J(θ) = E [ ∇_θ log π_θ(a_t | s_t) * (G_t - b(s_t)) ]
```

**Proof that baseline leaves expectation unbiased:**
For any baseline function `b(s)` that does not depend on action `a`:

```text
E_{a ~ π_θ} [ ∇_θ log π_θ(a | s) * b(s) ] = b(s) * Σ_a π_θ(a | s) * [ ∇_θ π_θ(a | s) / π_θ(a | s) ]
                                          = b(s) * Σ_a ∇_θ π_θ(a | s)
                                          = b(s) * ∇_θ [ Σ_a π_θ(a | s) ]
                                          = b(s) * ∇_θ [ 1 ] = 0
```

The optimal choice for `b(s)` is an estimate of the state value `V(s)`. The term `G_t - V(s_t)` is an empirical sample of the **advantage function**:

```text
A(s, a) = Q(s, a) - V(s)
```

If `A(s_t, a_t) > 0`, the action performed better than the average action from that state, and its log-probability is increased. If `A(s_t, a_t) < 0`, its probability is decreased.

### Actor-critic architectures and generalized advantage estimation (GAE)

Instead of waiting until the end of an episode to compute Monte Carlo returns `G_t`, **Actor-Critic** methods train two separate models:
1. **The Actor `π_θ(a | s)`:** The parameterized policy that selects actions.
2. **The Critic `V_ϕ(s)`:** A learned value network parameterized by `ϕ` that evaluates states.

The one-step TD error from the critic serves as an immediate estimate of the advantage:

```text
δ_t^V = r_{t+1} + γ * V_ϕ(s_{t+1}) - V_ϕ(s_t)
```

#### Generalized Advantage Estimation (GAE)

Schulman et al. (2015) introduced **GAE**, which computes an exponentially weighted average of multi-step TD advantages, governed by hyperparameter `λ ∈ [0, 1]`:

```text
Â_t^{GAE(γ, λ)} = Σ_{l=0}^{T-t-1} (γ * λ)^l * δ_{t+l}^V
```

- When `λ = 0`: `Â_t = δ_t^V = r_{t+1} + γ V(s_{t+1}) - V(s_t)` (one-step TD, lowest variance, highest bias).
- When `λ = 1`: `Â_t = Σ_{l=0}^{T-t-1} γ^l r_{t+l+1} - V(s_t)` (Monte Carlo advantage, zero bias, highest variance).
- Intermediate values (typically `λ = 0.95`, `γ = 0.99`) achieve an optimal Pareto tradeoff between variance and bias.

### Trust regions and proximal policy optimization (PPO)

In supervised learning, if a gradient update takes a slightly sub-optimal step, the loss increases slightly, and the next mini-batch can recover. In reinforcement learning, a single oversized policy update can cause performance to collapse: the altered policy visits poor states, gathers uninformative data, and cannot recover.

**Trust Region Policy Optimization (TRPO)** constrained policy updates using the Kullback-Leibler (KL) divergence:

```text
maximize_θ E [ ( π_θ(a | s) / π_{θ_old}(a | s) ) * Â ]  subject to  E [ D_KL( π_{θ_old} || π_θ ) ] <= δ
```

While theoretically grounded, TRPO requires computing second-order Fisher Information matrix inversions (conjugate gradient).

#### PPO clipped objective

Schulman et al. (2017) proposed **Proximal Policy Optimization (PPO)**, achieving trust-region stability with first-order stochastic gradient descent.

Define the probability ratio:

```text
r_t(θ) = π_θ(a_t | s_t) / π_{θ_old}(a_t | s_t)
```

At the beginning of an update epoch, `r_t(θ_old) = 1.0`. PPO penalizes changes that push `r_t(θ)` far from 1 using a **clipped surrogate objective**:

```text
L^{CLIP}(θ) = E_t [ min( r_t(θ) * Â_t,  clip( r_t(θ), 1 - ε, 1 + ε ) * Â_t ) ]
```

![PPO Clipped Surrogate Objective](assets/images/ppo_clipping_objective.svg)

The `min` operator acts as a pessimistic bound:
1. **Positive Advantage (`Â > 0`):** The action yielded better-than-average return. The objective increases as `r_t(θ)` grows, but is capped at `(1 + ε) * Â`. The policy is not rewarded for pushing `r_t(θ)` beyond `1 + ε`.
2. **Negative Advantage (`Â < 0`):** The action was worse than average. The objective decreases as `r_t(θ)` grows. If `r_t(θ)` drops below `1 - ε`, clipping prevents further penalization, but the objective can still decrease indefinitely if the action becomes *more* likely.

PPO trains on the joint loss:

```text
L^{PPO}(θ, ϕ) = E_t [ L^{CLIP}(θ) - c_1 * ( V_ϕ(s_t) - V_t^{target} )^2 + c_2 * S[π_θ](s_t) ]
```

where `S[π_θ]` is the entropy of the policy (encouraging exploration) and `c_1, c_2` are weighting coefficients.

### PyTorch implementation: REINFORCE with baseline

Here is a clean PyTorch implementation of REINFORCE with a learned state-value baseline:

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical

class PolicyNetwork(nn.Module):
    def __init__(self, obs_dim: int, action_dim: int, hidden_dim: int = 128):
        super().__init__()
        self.actor = nn.Sequential(
            nn.Linear(obs_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, action_dim),
        )
        self.critic = nn.Sequential(
            nn.Linear(obs_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, 1),
        )

    def forward(self, state: torch.Tensor):
        logits = self.actor(state)
        value = self.critic(state)
        return Categorical(logits=logits), value

def train_step(
    model: PolicyNetwork,
    optimizer: optim.Optimizer,
    states: list[torch.Tensor],
    actions: list[int],
    rewards: list[float],
    gamma: float = 0.99,
):
    # Compute discounted returns G_t
    discounted_returns = []
    g = 0.0
    for r in reversed(rewards):
        g = r + gamma * g
        discounted_returns.insert(0, g)
    
    returns = torch.tensor(discounted_returns, dtype=torch.float32)
    # Normalize returns for training stability
    returns = (returns - returns.mean()) / (returns.std() + 1e-8)

    state_tensor = torch.stack(states)
    action_tensor = torch.tensor(actions, dtype=torch.long)

    dist, values = model(state_tensor)
    log_probs = dist.log_prob(action_tensor)
    values = values.squeeze(-1)

    # Advantage: return minus baseline V(s)
    advantages = returns - values.detach()

    # Actor loss (policy gradient) and Critic loss (MSE)
    actor_loss = -(log_probs * advantages).mean()
    critic_loss = nn.functional.mse_loss(values, returns)
    total_loss = actor_loss + 0.5 * critic_loss

    optimizer.zero_grad()
    total_loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=0.5)
    optimizer.step()

    return actor_loss.item(), critic_loss.item()
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read chapter 13 (Policy Gradient Methods) of [Sutton and Barto: Reinforcement Learning: An Introduction](http://incompleteideas.net/book/the-book-2nd.html).
   - Trace the proof of the Policy Gradient Theorem in section 13.2 carefully line by line.
   - Note why the gradient of the state distribution `∇_θ d^π(s)` does not appear in the final expectation.
2. Read [Part 3: Intro to Policy Optimization](https://spinningup.openai.com/en/latest/spinningup/rl_intro3.html) from OpenAI's Spinning Up.
   - Verify how the trajectory-level policy gradient reduces to advantage-weighted log-probabilities.
3. Complete Unit 4 (REINFORCE) and Unit 8 (PPO) of the [Hugging Face Deep RL Course](https://huggingface.co/learn/deep-rl-course/unit0/introduction).
4. Read the original PPO paper: [Proximal Policy Optimization Algorithms](https://arxiv.org/abs/1707.06347) (Schulman et al., 2017).
5. Read [The 37 Implementation Details of Proximal Policy Optimization](https://iclr-blog-track.github.io/2022/03/25/ppo-implementation-details/) and summarize the five details with the largest impact on policy convergence.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Policy Gradient Algorithms](https://lilianweng.github.io/posts/2018-04-08-policy-gradient/) by Lilian Weng: Detailed, unified mathematical survey of REINFORCE, DDPG, TRPO, and PPO.
- [High-Dimensional Continuous Control Using Generalized Advantage Estimation](https://arxiv.org/abs/1506.02438): Schulman et al.'s original derivation of GAE.
- [CleanRL PPO Implementation](https://github.com/vwxyzjn/cleanrl/blob/master/cleanrl/ppo.py): Heavily referenced, single-file PyTorch implementation documenting all standard PPO engineering tricks.

### Knowledge check

Use these questions to verify your understanding of policy gradient methods:

1. [Why can policy gradient methods directly handle continuous action spaces while value-based methods struggle?](#introduction)
2. [How does the log-derivative trick allow us to compute gradients of expected returns without differentiating through the environment transition dynamics?](#the-policy-gradient-theorem-and-the-log-derivative-trick)
3. [Why does subtracting an arbitrary state-dependent baseline b(s) leave the expected policy gradient completely unbiased?](#reinforce-and-variance-reduction-via-baselines)
4. [What role does the lambda hyperparameter play in Generalized Advantage Estimation (GAE)?](#actor-critic-architectures-and-generalized-advantage-estimation-gae)
5. [In PPO's clipped surrogate objective, why does the loss stop rewarding probability ratio increases beyond 1 + epsilon when advantage is positive?](#trust-regions-and-proximal-policy-optimization-ppo)
