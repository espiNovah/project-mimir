<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

The Bellman equations from MDPs and Bandits tell you what an optimal value function satisfies. This lesson covers the algorithms that find it: dynamic programming when you know the environment, and Monte Carlo and temporal-difference learning when you can only sample from it. You will end with Q-learning, the algorithm behind the first deep RL breakthroughs, and see why adding neural networks makes it both powerful and unstable.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Policy evaluation, policy iteration and value iteration.
- Monte Carlo methods that learn from complete episodes.
- Temporal-difference learning and bootstrapping.
- On-policy SARSA versus off-policy Q-learning.
- Function approximation and the deadly triad.
- Deep Q-networks, experience replay and target networks.

### Key ideas

- **Dynamic programming assumes a known model.** Policy evaluation applies the Bellman equation as an update until values stop changing. Policy iteration alternates evaluation with acting greedily. Value iteration folds both into one update using the max. These methods need the full transition function, so they work for small, known environments and serve as the ideal that sampling methods approximate.
- **Monte Carlo learns from complete episodes.** Run an episode, compute the actual return from each state, and average. This needs no model and is unbiased, but it has high variance and must wait until the episode ends.
- **Temporal-difference learning bootstraps.** TD(0) updates V(s) toward r + gamma V(s'), using its own current estimate of the next state. The gap between that target and the current estimate is the TD error. Bootstrapping introduces bias but reduces variance and lets the agent learn after every step. n-step methods and eligibility traces sit between TD and Monte Carlo.
- **SARSA and Q-learning differ in one term.** SARSA updates Q(s, a) toward r + gamma Q(s', a') using the action the agent actually takes next (on-policy). Q-learning uses the max over next actions (off-policy), so it learns the greedy policy's values even while exploring. Sutton and Barto's cliff-walking example shows the practical difference.
- **Tabular methods do not scale.** Real problems have too many states for a table, so you approximate Q with a parameterized function. Combining function approximation, bootstrapping and off-policy learning (the "deadly triad") can make values diverge.
- **DQN made it work with engineering.** Deep Q-networks stabilize learning with experience replay (training on random past transitions, not just the latest) and a target network (a slowly updated copy used to compute targets). This let one algorithm learn many Atari games from pixels.
- **RL results are noisy.** Two runs with different random seeds can produce very different learning curves. Always report several seeds, which you will do in the project.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read chapters 4 to 6 of [Sutton and Barto](http://incompleteideas.net/book/the-book-2nd.html).
   - Chapter 4 (Dynamic Programming), chapter 5 (Monte Carlo Methods) and chapter 6 (Temporal-Difference Learning). In chapter 6, work through the cliff-walking example in section 6.5 carefully.
   - Skim chapter 9's introduction and section 11.3 on the deadly triad.
1. Watch lectures 3 to 6 of [David Silver's RL course](https://www.youtube.com/playlist?list=PLqYmG7hTraZDM-OYHWgPebj2MfCFzFObQ): planning by dynamic programming, model-free prediction, model-free control and value function approximation.
1. Do units 2 and 3 of the [Hugging Face Deep RL Course](https://huggingface.co/learn/deep-rl-course/unit0/introduction). Unit 2 implements Q-learning from scratch on FrozenLake. Unit 3 introduces deep Q-learning.
1. Read the original [DQN paper, Playing Atari with Deep Reinforcement Learning](https://arxiv.org/abs/1312.5602), using the reading method from Reading Papers if you have already done that lesson. Identify exactly which two tricks stabilize training.
1. Practice: implement value iteration for Gymnasium's [FrozenLake environment](https://gymnasium.farama.org/environments/toy_text/frozen_lake/) using its transition table (`env.unwrapped.P`), print the optimal policy as a grid of arrows, and measure its success rate over 1,000 episodes on the slippery version.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The Berkeley CS188 reinforcement learning notes](https://inst.eecs.berkeley.edu/~cs188/textbook/rl/) give a compact treatment of model-based and model-free learning with worked examples.
- [Gymnasium's FrozenLake Q-learning tutorial](https://gymnasium.farama.org/tutorials/training_agents/frozenlake_q_learning/) shows tabular Q-learning with the current Gymnasium API and plots of the learned policy.
