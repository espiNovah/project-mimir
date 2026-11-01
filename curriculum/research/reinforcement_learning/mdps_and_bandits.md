### Introduction

An agent that interacts with an external system—reading a file, running a shell command, observing the output, and selecting the next tool—is engaged in **sequential decision making**.

In supervised learning, models learn from static, pre-labeled pairs: an input `x` has a known target label `y`. In sequential real-world environments, however, no supervisor provides the exact right tool call at step 3. The agent must explore actions, observe intermediate consequences, and learn entirely from a delayed reward signal: Did the program compile? Did the SQL query answer the user's question? Did the transaction succeed?

**Reinforcement Learning (RL)** is the mathematical framework for solving sequential decision problems under uncertainty.

In this lesson, you will learn the foundational formalisms of reinforcement learning: the exploration-exploitation trade-off in multi-armed bandits, the Markov Decision Process (MDP), policies, returns, state and action value functions, and the recursive Bellman equations that govern optimal behavior.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Prerequisites

This section assumes you have completed [ML Foundations](#/paths/ml), particularly [Neural Networks & Transformers](#/paths/ml), and the mathematical principles of expectation and probability in [Math for Research](#/paths/research).

</div>

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The exploration-exploitation dilemma and multi-armed bandits.
- Action-value estimation: sample averages, epsilon-greedy, optimistic initialization, and Upper Confidence Bounds (UCB).
- The formal Markov Decision Process (MDP): states, actions, transition dynamics, reward functions, and discount factor gamma.
- Returns, discounting, episodic versus continuing horizons, and the danger of reward hacking.
- Policies (deterministic vs stochastic), the state-value function `V(s)`, and the action-value function `Q(s, a)`.
- The Bellman Expectation Equations and the Bellman Optimality Equations.

### The exploration-exploitation trade-off and multi-armed bandits

Before examining full multi-step environments, we examine the problem of trial-and-error learning in its purest form: the **multi-armed bandit**.

Imagine standing in front of a slot machine with `k` distinct levers (arms). Pulling arm `a` yields a numerical reward sampled from a stationary probability distribution with mean `q*(a) = E[R | A = a]`. You do not know the true means. You have 1,000 pulls. How do you maximize your total reward?

This creates the fundamental **exploration-exploitation dilemma**:
- **Exploitation:** Pull the arm that currently has the highest estimated reward based on past experience.
- **Exploration:** Pull arms with lower estimates or fewer trials to discover if their true mean is actually higher.

If you only exploit, you can become trapped pulling a mediocre arm forever. If you only explore, you waste trials collecting data on demonstrably poor arms.

#### Balancing strategies:

1. **Epsilon-Greedy (`ε-greedy`):**
Maintain an empirical average of rewards for each action: `Q(a) = (sum of rewards from a) / (times a was selected)`.
- With probability `1 - ε`, select the greedy action: `argmax_a Q(a)`.
- With probability `ε`, select an action uniformly at random.

2. **Optimistic Initial Values:**
Initialize all action-value estimates to an unrealistically high number (e.g. `Q_0(a) = +5.0` when actual rewards are in `[0, 1]`). Whichever arm is pulled initially produces a disappointing reward, causing its estimate to drop and driving the agent to systematically explore every other arm during early steps.

3. **Upper Confidence Bound (UCB):**
Rather than exploring completely at random, UCB acts greedily with respect to an **uncertainty bound**:

```text
A_t = argmax_a [ Q_t(a) + c * sqrt(ln(t) / N_t(a)) ]
```

- `Q_t(a)` is the current estimated value of arm `a`.
- `N_t(a)` is the number of times arm `a` has been pulled so far.
- `t` is the total number of steps elapsed across all arms.
- `c` is an exploration parameter.

If an arm has rarely been pulled, `N_t(a)` is small, so the square root term is large. As an arm is pulled more frequently, uncertainty shrinks. UCB dynamically focuses exploration on actions that have high potential payoff or high statistical uncertainty.

### Markov Decision Processes (MDPs)

In multi-armed bandits, actions do not change the environment: pulling arm 3 does not alter the state of the machine.

In a **Markov Decision Process (MDP)**, actions have lasting consequences: an action yields an immediate reward **and** transitions the environment into a new state.

![Markov Decision Process: The Agent-Environment Loop & Bellman Backup](assets/images/mdp_agent_environment.svg)

Formally, a finite MDP is defined as a 5-tuple `(S, A, P, R, γ)`:

1. **State space `S`:** The set of all valid environment states.
2. **Action space `A`:** The set of all available actions.
3. **Transition probability function `P`:** The environment dynamics:
```text
P(s' | s, a) = P(S_{t+1} = s' | S_t = s, A_t = a)
```
4. **Reward function `R`:** The expected immediate scalar reward:
```text
R(s, a) = E[R_{t+1} | S_t = s, A_t = a]
```
5. **Discount factor `γ` (gamma):** A real number in `[0, 1)`.

#### The Markov Property
An environment satisfies the **Markov Property** if the future depends only on the current state and action, and is conditionally independent of all past history:

```text
P(S_{t+1} = s', R_{t+1} = r | S_t, A_t, S_{t-1}, A_{t-1}, ..., S_0, A_0) = P(S_{t+1} = s', R_{t+1} = r | S_t, A_t)
```

The current state `S_t` must summarize all past information necessary to predict the future. In language model agents, the "state" is the full context window (system prompt, conversation turns, and tool outputs).

### Returns, discounting, and reward design

The agent's objective is to maximize the expected **cumulative return** `G_t`:

```text
G_t = R_{t+1} + γ * R_{t+2} + γ^2 * R_{t+3} + ... = sum_{k=0}^{inf} γ^k * R_{t+k+1}
```

The discount factor `γ` serves three crucial purposes:
- **Mathematical convergence:** For continuing tasks (infinite horizon), `γ < 1` guarantees that the sum of rewards remains finite as long as immediate rewards are bounded.
- **Uncertainty preference:** Rewards received sooner are more certain than rewards far in the future.
- **Short-term vs long-term horizon:** When `γ = 0`, the agent is completely myopic, caring only about the immediate reward `R_{t+1}`. As `γ -> 1`, the agent becomes far-sighted, willing to sacrifice immediate points to achieve large delayed payoffs.

#### The danger of reward hacking
In supervised learning, loss functions are fixed. In reinforcement learning, the designer defines the reward function.

If you incentivize a web-browsing agent with a reward for "visiting unique pages," it will learn to endlessly click through site navigational footers and pagination links without solving the user's task. An agent optimizes the literal mathematical reward signal, not your unstated intentions.

### Policies and value functions

A **policy** `π` defines the agent's behavior:

- **Deterministic policy:** `a = π(s)` maps a state directly to a single action.
- **Stochastic policy:** `π(a | s) = P(A_t = a | S_t = s)` assigns a probability distribution over actions for each state. (Language models are stochastic policies over next-token actions).

To evaluate how good a state or action is under a policy `π`, we define **value functions**:

1. **State-Value Function `V^π(s)`:** The expected return starting from state `s` and following policy `π` thereafter:
```text
V^π(s) = E_π [ G_t | S_t = s ]
```

2. **Action-Value Function `Q^π(s, a)`:** The expected return starting from state `s`, taking arbitrary action `a`, and following policy `π` thereafter:
```text
Q^π(s, a) = E_π [ G_t | S_t = s, A_t = a ]
```

Notice the direct relationship between `V` and `Q`:
```text
V^π(s) = sum_a π(a | s) * Q^π(s, a)
```

### The Bellman equations and optimality

The foundational insight of modern dynamic programming and reinforcement learning (Richard Bellman, 1957) is that value functions can be defined **recursively**.

The value of the current state equals the expected immediate reward plus the discounted value of the next state:

```text
V^π(s) = sum_a π(a | s) * sum_{s', r} P(s', r | s, a) * [ r + γ * V^π(s') ]
```

Similarly, the Bellman equation for `Q^π(s, a)` is:

```text
Q^π(s, a) = sum_{s', r} P(s', r | s, a) * [ r + γ * sum_{a'} π(a' | s') * Q^π(s', a') ]
```

#### Bellman Optimality Equations
An **optimal policy** `π*` achieves the maximum possible expected return from every state: `V*(s) = max_π V^π(s)` for all `s`.

At optimality, an agent does not average over its policy; it takes the single best action:

```text
V*(s) = max_a sum_{s', r} P(s', r | s, a) * [ r + γ * V*(s') ]
Q*(s, a) = sum_{s', r} P(s', r | s, a) * [ r + γ * max_{a'} Q*(s', a') ]
```

Once the optimal action-value function `Q*(s, a)` is known, acting optimally is trivial: in any state `s`, simply select the action that maximizes `Q*(s, a)`:

```text
π*(s) = argmax_a Q*(s, a)
```

The challenge of reinforcement learning is that the transition probabilities `P(s' | s, a)` and reward function `R(s, a)` are usually unknown. In the next lesson, you will learn how **Value-Based Methods** (such as Q-Learning and SARSA) learn `Q*` directly from trial-and-error experience.

### Python implementation: The 10-Armed Bandit

The script below demonstrates the exploration-exploitation trade-off by comparing greedy, epsilon-greedy, and Upper Confidence Bound (UCB) algorithms across a testbed of 10-armed bandits:

```python
# bandit_testbed.py: Comparing Epsilon-Greedy and UCB on a 10-armed bandit
import numpy as np

def run_bandit_experiment(arms=10, steps=1000, runs=1000):
    np.random.seed(42)
    
    # Track average reward per step for 3 strategies
    rewards_eps0 = np.zeros(steps)
    rewards_eps01 = np.zeros(steps)
    rewards_ucb = np.zeros(steps)
    
    for _ in range(runs):
        # Sample true mean rewards for 10 arms from N(0, 1)
        q_true = np.random.randn(arms)
        
        # 1. Greedy (eps = 0.0)
        q_est = np.zeros(arms)
        n_pulls = np.zeros(arms)
        for t in range(steps):
            a = np.argmax(q_est)
            r = q_true[a] + np.random.randn()
            n_pulls[a] += 1
            q_est[a] += (r - q_est[a]) / n_pulls[a]
            rewards_eps0[t] += r
            
        # 2. Epsilon-Greedy (eps = 0.1)
        q_est = np.zeros(arms)
        n_pulls = np.zeros(arms)
        for t in range(steps):
            if np.random.rand() < 0.1:
                a = np.random.randint(arms)
            else:
                a = np.argmax(q_est)
            r = q_true[a] + np.random.randn()
            n_pulls[a] += 1
            q_est[a] += (r - q_est[a]) / n_pulls[a]
            rewards_eps01[t] += r
            
        # 3. Upper Confidence Bound (c = 2.0)
        q_est = np.zeros(arms)
        n_pulls = np.zeros(arms)
        for t in range(steps):
            if t < arms:
                a = t  # Pull each arm once initially
            else:
                ucb_values = q_est + 2.0 * np.sqrt(np.log(t + 1) / n_pulls)
                a = np.argmax(ucb_values)
            r = q_true[a] + np.random.randn()
            n_pulls[a] += 1
            q_est[a] += (r - q_est[a]) / n_pulls[a]
            rewards_ucb[t] += r

    # Average over runs
    rewards_eps0 /= runs
    rewards_eps01 /= runs
    rewards_ucb /= runs
    
    print(f"Final Step Average Reward:")
    print(f"  Greedy (eps=0):     {rewards_eps0[-1]:.3f}")
    print(f"  Eps-Greedy (eps=0.1): {rewards_eps01[-1]:.3f}")
    print(f"  UCB (c=2.0):        {rewards_ucb[-1]:.3f}")

if __name__ == "__main__":
    run_bandit_experiment()
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read Chapters 1, 2, and 3 of Sutton and Barto's [Reinforcement Learning: An Introduction](http://incompleteideas.net/book/the-book-2nd.html) (2nd Edition).
   - Chapter 1: The reinforcement learning problem.
   - Chapter 2: Multi-armed bandits, incremental update formulas, and UCB.
   - Chapter 3: Finite Markov Decision Processes, policies, and the Bellman equations.
1. Watch Lectures 1 and 2 of [David Silver's Reinforcement Learning Course](https://www.youtube.com/playlist?list=PLqYmG7hTraZDM-OYHWgPebj2MfCFzFObQ).
   - Lecture 1: Introduction to RL.
   - Lecture 2: Markov Decision Processes (review slides on [David Silver's teaching page](https://www.davidsilver.uk/teaching/)).
1. Read the [MDP chapter of the Berkeley CS188 textbook](https://inst.eecs.berkeley.edu/~cs188/textbook/mdp/).
   - Inspect the Gridworld worked examples to build intuition for how discount factor `gamma` influences path choices around hazardous states.
1. Read [Spinning Up in Deep RL: Key Concepts](https://spinningup.openai.com/en/latest/spinningup/rl_intro.html) from OpenAI.
   - Note the distinction between model-free and model-based RL, and how policies are parameterized with neural networks.
1. Read [The Multi-Armed Bandit Problem and Its Solutions](https://lilianweng.github.io/posts/2018-01-23-multi-armed-bandit/) by Lilian Weng for derivations of UCB and Thompson sampling.

</div>

### Knowledge check

The questions below confirm that you have mastered the core ideas in this lesson. Click any question to review the section that explains it.

- [What is the exploration-exploitation dilemma in multi-armed bandits?](#the-exploration-exploitation-trade-off-and-multi-armed-bandits)
- [How does Upper Confidence Bound (UCB) balance exploration and exploitation?](#the-exploration-exploitation-trade-off-and-multi-armed-bandits)
- [What is the Markov Property, and why must environment states satisfy it?](#markov-decision-processes-mdps)
- [What is the difference between the state-value function V(s) and the action-value function Q(s, a)?](#policies-and-value-functions)
- [What recursive relationship does the Bellman equation express?](#the-bellman-equations-and-optimality)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Stanford CS234: Reinforcement Learning](https://web.stanford.edu/class/cs234/) provides syllabus, lecture slides, and problem sets from Emma Brunskill's graduate RL course.
- [Foundations of Deep Reinforcement Learning (Graesser & Keng)](https://www.deeplearningfoundations.com/) is a clear, code-focused guide covering tabular and deep RL algorithms.
- [Gymnasium Documentation (Farama Foundation)](https://gymnasium.farama.org/) is the standard open-source API standard for reinforcement learning environments.