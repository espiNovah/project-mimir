### Introduction

In this project you will implement two foundational RL algorithms yourself, tabular Q-learning and REINFORCE, train them on standard Gymnasium environments, and report the results the way an RL paper would: several random seeds, mean and standard deviation learning curves, and a controlled ablation. You will finish with a short report that ties what you observed to the chapters of Sutton and Barto that explain it.

Getting an RL algorithm to "work once" is easy. Showing that it works reliably, and understanding why a hyperparameter matters, is the actual research skill. RL is notorious for results that disappear when you change the seed, so this project trains you to measure carefully from the start.

### Before you start

- Create a new repo named `mimir-rl-from-scratch`. Set it up with `uv init` and add `gymnasium`, `numpy`, `matplotlib` and `pytest` with `uv add`. Add `torch` only if you want a neural network policy for REINFORCE.
- Read [Gymnasium's basic usage guide](https://gymnasium.farama.org/introduction/basic_usage/). Note that `env.reset(seed=...)` returns `(observation, info)` and `env.step(action)` returns five values: `observation, reward, terminated, truncated, info`. Older tutorials use a four-value API from the original OpenAI Gym; do not copy them without adapting.
- Read the docs for [FrozenLake](https://gymnasium.farama.org/environments/toy_text/frozen_lake/) and [CartPole](https://gymnasium.farama.org/environments/classic_control/cart_pole/), including their reward structure and when an episode ends.
- "From scratch" means you write the learning algorithm. You may use Gymnasium for environments, NumPy for math and PyTorch for a policy network and its gradients. Do not use RL libraries such as Stable-Baselines3 for your agents.
- Everything here runs on a laptop CPU in minutes. No GPU or API key needed.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Implement tabular Q-learning with epsilon-greedy exploration in `q_learning.py`. Make the learning rate, discount factor, epsilon schedule and number of episodes configurable from the command line or a config file.
1. Train Q-learning on `FrozenLake-v1` with `is_slippery=True` (the default 4x4 map). Every 100 training episodes, evaluate the greedy policy for 100 episodes with exploration turned off and record the success rate.
1. Implement REINFORCE in `reinforce.py` with a softmax policy (a linear policy in NumPy or a small network in PyTorch). Include a version with a baseline (a running average of returns, or a learned value function) and one without.
1. Train REINFORCE on `CartPole-v1` and record the episode return for every training episode.
1. Run each configuration with at least 5 random seeds. Seed everything: Python's `random`, NumPy, PyTorch if used, and `env.reset(seed=...)`. Save raw results to CSV files so the plots can be regenerated without retraining.
1. Plot learning curves showing the mean across seeds with a shaded band of one standard deviation. Produce one plot for Q-learning (evaluation success rate against episodes) and one for REINFORCE (smoothed return against episodes, with and without the baseline on the same axes).
1. Run one hyperparameter ablation of your choice, for example Q-learning's epsilon decay schedule, the discount factor, or REINFORCE's learning rate. Test at least three values, with every other setting and the seeds held fixed, and plot them on one chart.
1. Write `tests/` with at least two `pytest` tests, for example that a Q-learning update on a hand-built transition produces the value you computed by hand, and that your discounted-return function returns the right values for a short reward list.
1. Write `REPORT.md` (1 to 2 pages) that:
   - States your hypothesis for the ablation before showing the results.
   - Reports final performance as mean plus or minus standard deviation across seeds.
   - Explains your results using specific sections of [Sutton and Barto](http://incompleteideas.net/book/the-book-2nd.html), for example how exploration in chapter 2 and section 6.5 relates to your epsilon results, or how section 13.4 explains the effect of the baseline on variance.
   - Notes at least one surprising or unstable result and what you think caused it.
1. Push your project to GitHub with a README that explains what it does, how to reproduce every plot with one command each, and what you learned. Include the plots and a results table in the README.

#### Extra credit

- Implement SARSA and compare it with Q-learning on Gymnasium's `CliffWalking-v1`, reproducing the qualitative result of Sutton and Barto's cliff-walking example.
- Upgrade REINFORCE to an actor-critic with a learned value function and compare sample efficiency.
- Implement a small DQN with experience replay and a target network on CartPole, and show what happens to stability when you remove each of the two tricks.
- Use a statistical test or bootstrap confidence intervals to say whether your ablation's differences are significant.

</div>

### Submitting your work

A strong submission is reproducible and honest about variance. Someone should be able to clone the repo, run one command per plot, and get the same curves because every seed is fixed. The curves show bands, not single lines, and the report gives numbers with error bars. The best reports do not stop at "the baseline helped." They show how much it helped, across how many seeds, and connect it to the variance argument in the textbook. If something did not work, say so and explain what you tried. That is more convincing than a curve that looks too good.
