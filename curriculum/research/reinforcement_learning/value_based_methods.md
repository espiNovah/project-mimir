### Introduction

The Bellman equations established in [MDPs and Bandits](#/lesson/research/reinforcement_learning/mdps_and_bandits) characterize the mathematical conditions that an optimal value function must satisfy. However, knowing the equations is not enough: an agent needs an algorithm to find or approximate those values.

This lesson explores value-based reinforcement learning algorithms across two regimes:
1. **Model-based dynamic programming:** When the full transition dynamics `P(s' | s, a)` and reward function `R(s, a)` are known, we can compute optimal policies using iterative contraction mappings.
2. **Model-free reinforcement learning:** When transition dynamics are unknown and the agent can only interact with an environment through experience, we turn to Monte Carlo and Temporal-Difference (TD) methods.

You will trace the algorithmic lineage from tabular TD(0) to on-policy SARSA and off-policy Q-learning, uncover why pairing neural networks with value iteration can cause catastrophic divergence (the "deadly triad"), and examine how Deep Q-Networks (DQN) engineered the breakthroughs that launched modern deep RL.

### Dynamic programming: policy iteration and value iteration

When the environment's transition probabilities `P(s' | s, a)` and reward model `R(s, a, s')` are completely known, the reinforcement learning problem reduces to a Markov Decision Process planning problem solvable via **dynamic programming (DP)**.

#### Iterative policy evaluation

Given a fixed policy `π`, how do we compute its state-value function `V^π(s)`? We turn the Bellman expectation equation into an iterative update rule:

```text
V_{k+1}(s) = Σ_a π(a | s) Σ_{s'} P(s' | s, a) [ R(s, a, s') + γ * V_k(s') ]
```

Starting from an arbitrary initial value function `V_0` (such as all zeros), we repeatedly update `V(s)` across all states `s ∈ S`. Because the Bellman backup operator is a **γ-contraction mapping** under the infinity norm:

```text
|| T^π(U) - T^π(V) ||_∞ <= γ * || U - V ||_∞
```

The Banach Fixed-Point Theorem guarantees that `V_k` converges geometrically to the unique true value function `V^π` as `k → ∞`.

#### Policy iteration

Once we have evaluated the current policy `π` to find `V^π`, we can strictly improve it by acting greedily with respect to the state-action values `Q^π(s, a)`:

```text
π'(s) = argmax_a Q^π(s, a) = argmax_a Σ_{s'} P(s' | s, a) [ R(s, a, s') + γ * V^π(s') ]
```

According to the **Policy Improvement Theorem**, `V^{π'}(s) >= V^π(s)` for all `s ∈ S`. If the policy does not change, then `π'` is guaranteed to be an optimal policy `π*`.

**Policy iteration** alternates between two phases until convergence:
1. **Policy Evaluation:** Compute `V^π` for the current policy `π` (running iterative backups until `max_s |V_{k+1}(s) - V_k(s)| < θ`).
2. **Policy Improvement:** Greedily update `π(s) ← argmax_a Q^π(s, a)` for all `s`.

#### Value iteration

Running policy evaluation to complete convergence in every iteration is computationally wasteful. **Value iteration** truncates policy evaluation to a single sweep, directly combining evaluation and greedy improvement into the Bellman optimality backup:

```text
V_{k+1}(s) = max_a Σ_{s'} P(s' | s, a) [ R(s, a, s') + γ * V_k(s') ]
```

Value iteration updates the value table directly until `max_s |V_{k+1}(s) - V_k(s)|` falls below a small tolerance `θ`. Once converged, the optimal policy is extracted in a single greedy pass.

### Monte Carlo vs temporal-difference learning

In real-world applications, we rarely know `P(s' | s, a)` or `R(s, a)`. The agent must learn purely from sampled sequences of experience `(S_0, A_0, R_1, S_1, A_1, R_2, ...)`.

#### Monte Carlo methods

**Monte Carlo (MC)** methods learn directly from complete episodes of experience. The agent runs an episode to termination, records the actual discounted return `G_t`:

```text
G_t = R_{t+1} + γ * R_{t+2} + γ^2 * R_{t+3} + ... + γ^{T-t-1} * R_T
```

and updates the value estimate toward the observed return:

```text
V(S_t) ← V(S_t) + α * [ G_t - V(S_t) ]
```

- **Unbiased:** The expected value of `G_t` is exactly `V^π(S_t)`.
- **High variance:** Because `G_t` accumulates rewards and stochastic transitions across the entire trajectory, returns exhibit substantial variance.
- **Requires episodic tasks:** Learning cannot occur online or during infinite-horizon tasks; the agent must wait until the episode terminates.

#### Temporal-difference learning (TD(0))

**Temporal-Difference (TD)** learning combines the sampling of Monte Carlo with the bootstrapping of dynamic programming. Instead of waiting for the full return `G_t`, TD(0) updates its value estimate after a single step using the immediate reward and its current estimate of the next state's value:

```text
Target: R_{t+1} + γ * V(S_{t+1})
TD Error: δ_t = R_{t+1} + γ * V(S_{t+1}) - V(S_t)
Update: V(S_t) ← V(S_t) + α * δ_t
```

- **Biased:** The target uses `V(S_{t+1})`, which is an imperfect estimate early in training.
- **Low variance:** The update depends only on a single transition `(S_t, A_t, R_{t+1}, S_{t+1})` rather than an entire random rollout.
- **Online and incremental:** The agent learns after every action step, enabling real-time continuous control.

| Dimension | Dynamic Programming | Monte Carlo (MC) | Temporal-Difference (TD) |
| :--- | :--- | :--- | :--- |
| **Model required?** | Yes (`P` and `R` known) | No (model-free) | No (model-free) |
| **Bootstrapping?** | Yes (updates from estimates) | No (actual full returns) | Yes (updates from estimates) |
| **Sampling?** | No (exhaustive expectation) | Yes (complete episodes) | Yes (step-by-step samples) |
| **Variance / Bias** | Zero variance, zero bias | High variance, zero bias | Low variance, initial bias |
| **Episodic only?** | Either | Episodic only | Both episodic and continuing |

### SARSA vs Q-learning: on-policy vs off-policy

To control an agent without an environment model, we must learn action values `Q(s, a)` rather than state values `V(s)`, because without `P(s' | s, a)` we cannot compute `argmax_a Σ_{s'} P(s' | s, a) V(s')`.

#### SARSA: on-policy TD control

SARSA updates the state-action value based on the transition tuple `(S_t, A_t, R_{t+1}, S_{t+1}, A_{t+1})`:

```text
Q(S_t, A_t) ← Q(S_t, A_t) + α * [ R_{t+1} + γ * Q(S_{t+1}, A_{t+1}) - Q(S_t, A_t) ]
```

Notice that `A_{t+1}` is the action **actually taken** by the agent's behavior policy (for example, chosen via `ε`-greedy exploration). Because SARSA evaluates the policy that is actively generating the data, it is an **on-policy** algorithm.

#### Q-learning: off-policy TD control

Watkins proposed **Q-learning** (1989), which changes the target from the action actually taken to the maximum possible action value from state `S_{t+1}`:

```text
Q(S_t, A_t) ← Q(S_t, A_t) + α * [ R_{t+1} + γ * max_a Q(S_{t+1}, a) - Q(S_t, A_t) ]
```

Q-learning is **off-policy**: the target policy is the purely greedy policy `argmax_a Q(S_{t+1}, a)`, even though the agent's behavior policy is exploring using `ε`-greedy actions.

#### The Cliff Walking benchmark

The difference between on-policy and off-policy control is illustrated by Sutton and Barto's **Cliff Walking** environment. The agent moves on a 4x12 grid. The bottom row contains the Start tile, a cliff of 10 pit tiles (falling yields reward -100 and resets to Start), and the Goal tile. Stepping on any other tile yields -1.

- **Q-learning** learns the optimal shortest path: walking directly along the edge of the cliff. However, during training with `ε > 0`, random exploratory actions occasionally cause it to fall off the cliff, yielding a low average online return during training.
- **SARSA** accounts for its own exploration: knowing that with probability `ε` it will take a random step, it learns the safer path around the top edge of the grid, avoiding catastrophic cliff falls during training.

### Tabular Q-learning implementation

Here is a self-contained implementation of tabular Q-learning with an `ε`-greedy exploration schedule:

```python
import numpy as np

class TabularQLearning:
    def __init__(
        self,
        num_states: int,
        num_actions: int,
        alpha: float = 0.1,
        gamma: float = 0.99,
        epsilon: float = 1.0,
        epsilon_min: float = 0.01,
        epsilon_decay: float = 0.995,
    ):
        self.num_states = num_states
        self.num_actions = num_actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.q_table = np.zeros((num_states, num_actions), dtype=np.float32)

    def select_action(self, state: int, evaluate: bool = False) -> int:
        """Epsilon-greedy action selection."""
        if not evaluate and np.random.rand() < self.epsilon:
            return np.random.randint(self.num_actions)
        return int(np.argmax(self.q_table[state]))

    def update(
        self, state: int, action: int, reward: float, next_state: int, done: bool
    ) -> float:
        """Bellman optimality update for Q(s, a)."""
        current_q = self.q_table[state, action]
        if done:
            target = reward
        else:
            target = reward + self.gamma * np.max(self.q_table[next_state])
        
        td_error = target - current_q
        self.q_table[state, action] += self.alpha * td_error
        return float(td_error)

    def decay_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
```

### Deep Q-networks (DQN) and the deadly triad

In continuous or high-dimensional environments (such as Atari games with `210 x 160` RGB pixels), state tables are infeasible. We must replace the lookup table with a function approximator: a neural network parameterized by `θ`, `Q(s, a; θ)`.

#### The deadly triad

Richard Sutton identified that combining three elements creates severe training instability and risk of divergence:
1. **Function approximation:** Using non-linear models (deep neural networks) instead of tabular representations.
2. **Bootstrapping:** Updating value estimates toward other value estimates rather than ground-truth Monte Carlo returns.
3. **Off-policy learning:** Training on data collected under a behavior distribution that differs from the target policy.

When all three are present, errors in value estimates can compound exponentially. Overestimating a value at state `s'` increases the target for state `s`, which through gradient updates raises the value of `s'`, creating an uncontrolled positive feedback loop.

![DQN Architecture: Experience Replay and Target Network](assets/images/dqn_architecture.svg)

#### Mnih et al.'s breakthroughs: replay buffer and target network

In 2013 and 2015, DeepMind stabilized deep Q-learning by introducing two core engineering components:

1. **Experience Replay Buffer (`D`):**
   - In standard RL, transitions `(s_t, a_t, r_{t+1}, s_{t+1})` are generated sequentially, creating strong temporal autocorrelation. Successive states violate the standard i.i.d. (independent and identically distributed) assumption of stochastic gradient descent.
   - The replay buffer stores the last `N` transitions (e.g. `1,000,000`). At each training step, the agent draws a random mini-batch of transitions from the buffer. This breaks temporal correlations and enables transitions to be reused across many gradient updates.

2. **Separate Target Network (`Q(s, a; θ⁻)`):**
   - In naive deep Q-learning, the network parameters `θ` update both the current prediction `Q(s, a; θ)` and the target `r + γ * max_a' Q(s', a'; θ)`. The agent chases a constantly moving target.
   - DQN maintains a separate target network with frozen parameters `θ⁻`. Every `C` steps (or via Polyak averaging `θ⁻ ← τ*θ + (1-τ)*θ⁻`), the weights of the online network are copied to the target network. The target remains stable during intermediate training steps:
     ```text
     L(θ) = E_{(s, a, r, s')} [ ( r + γ * max_a' Q(s', a'; θ⁻) - Q(s, a; θ) )^2 ]
     ```

#### Double DQN: mitigating maximization bias

Standard Q-learning has an inherent positive maximization bias. Because the target uses `max_a' Q(s', a')`, any noisy or overestimated Q-value will be systematically selected, causing values to drift upward.

Hasselt et al. (2015) introduced **Double DQN**, which decouples the action selection from action evaluation:
- Use the **online network `θ`** to select the best action.
- Use the **target network `θ⁻`** to evaluate that action's value.

```text
Target_DoubleDQN = r + γ * Q( s', argmax_a Q(s', a; θ); θ⁻ )
```

This simple modification prevents overestimation cascades and improves performance across almost all deep RL benchmarks.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read chapters 4 to 6 of [Sutton and Barto: Reinforcement Learning: An Introduction](http://incompleteideas.net/book/the-book-2nd.html).
   - Chapter 4 (Dynamic Programming), chapter 5 (Monte Carlo Methods), and chapter 6 (Temporal-Difference Learning).
   - Carefully review section 6.5 (Cliff Walking) and section 11.3 (The Deadly Triad).
2. Watch lectures 3 to 6 of [David Silver's UCL RL Course](https://www.youtube.com/playlist?list=PLqYmG7hTraZDM-OYHWgPebj2MfCFzFObQ): planning by dynamic programming, model-free prediction, model-free control, and value function approximation.
3. Complete Unit 2 and Unit 3 of the [Hugging Face Deep RL Course](https://huggingface.co/learn/deep-rl-course/unit0/introduction):
   - Unit 2 implements Q-learning on FrozenLake and Taxi-v3.
   - Unit 3 introduces Deep Q-Networks on Space Invaders.
4. Read the seminal paper [Human-level control through deep reinforcement learning](https://www.nature.com/articles/nature14236) (Mnih et al., Nature 2015) or its arXiv precursor [Playing Atari with Deep Reinforcement Learning](https://arxiv.org/abs/1312.5602).
5. Implement value iteration for Gymnasium's [FrozenLake-v1](https://gymnasium.farama.org/environments/toy_text/frozen_lake/) using the environment's internal transition table (`env.unwrapped.P`), and verify that your extracted optimal policy reaches >70% success rate on slippery ice.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The Berkeley CS188 Reinforcement Learning Notes](https://inst.eecs.berkeley.edu/~cs188/textbook/rl/): Intuitive, visual explanations of value iteration, Q-learning, and approximate RL.
- [Gymnasium FrozenLake Q-learning Tutorial](https://gymnasium.farama.org/tutorials/training_agents/frozenlake_q_learning/): Official tutorial on tabular Q-learning with modern Gymnasium APIs.
- [CleanRL DQN Implementation](https://github.com/vwxyzjn/cleanrl/blob/master/cleanrl/dqn_atari.py): Single-file, readable, benchmarked PyTorch implementation of DQN for Atari.

### Knowledge check

Use these questions to verify your understanding of value-based methods:

1. [Under what condition does iterative policy evaluation guaranteed to converge to the true value function V^π?](#dynamic-programming-policy-iteration-and-value-iteration)
2. [What is the key theoretical tradeoff between Monte Carlo returns and Temporal-Difference targets regarding bias and variance?](#monte-carlo-vs-temporal-difference-learning)
3. [Why does Q-learning learn an optimal policy even when the agent is taking random exploratory actions, whereas SARSA accounts for exploration?](#sarsa-vs-q-learning-on-policy-vs-off-policy)
4. [What are the three components of the "deadly triad", and why do they cause value estimates to diverge?](#deep-q-networks-dqn-and-the-deadly-triad)
5. [How does Double DQN solve the maximization bias problem in standard Q-learning?](#deep-q-networks-dqn-and-the-deadly-triad)
