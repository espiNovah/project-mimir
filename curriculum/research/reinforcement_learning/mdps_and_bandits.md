<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

An agent that acts, sees the result, and acts again is making sequential decisions. Reinforcement learning (RL) is the field that studies how to learn good decisions from that kind of experience, using a reward signal instead of labeled examples. It is also how today's reasoning models are post-trained. This lesson introduces the formal language of RL: bandits, Markov decision processes, policies, returns and value functions. Every RL paper you read will assume it.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The exploration-exploitation trade-off and multi-armed bandits.
- Epsilon-greedy, optimistic initialization and upper confidence bounds.
- Markov decision processes: states, actions, transitions and rewards.
- Returns, discounting and episodic versus continuing tasks.
- Policies and value functions.
- The Bellman equations and optimality.

### Key ideas

- **Bandits isolate exploration.** In a multi-armed bandit, you repeatedly pick one of k actions and get a random reward, with no state to worry about. To find the best arm you must try arms that currently look worse. Epsilon-greedy explores at random a fixed fraction of the time. Upper confidence bound (UCB) methods explore the arms you are most uncertain about. Regret, the total reward lost compared with always picking the best arm, measures how well a strategy balances the two.
- **An MDP formalizes the whole problem.** A Markov decision process has states, actions, a transition function P(s' | s, a), a reward function and a discount factor gamma. The Markov property says the next state depends only on the current state and action, not on the full history. When that is not true of what the agent observes, you have a partially observable MDP (POMDP), which is closer to what an LLM agent faces.
- **The goal is to maximize expected return.** The return is the sum of future rewards, each discounted by gamma per step. Discounting keeps infinite sums finite and expresses a preference for sooner rewards. Choosing the reward is a design decision, and badly chosen rewards get exploited (reward hacking).
- **A policy is a mapping from states to actions.** It can be deterministic or a probability distribution. The state-value function V(s) is the expected return from state s when following the policy. The action-value function Q(s, a) is the expected return after taking action a in s and then following the policy.
- **The Bellman equation is a recursion.** The value of a state equals the expected immediate reward plus the discounted value of the next state. The Bellman optimality equation replaces the expectation over the policy's actions with a max. Almost every RL algorithm is a way of solving or approximating these equations.
- **Optimal policies are greedy with respect to optimal values.** Once you know Q*, acting well is easy: pick the action with the highest Q* in each state. The hard part is learning Q* when the transitions are unknown, which is the subject of the next lesson.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read chapters 1 to 3 of Sutton and Barto's [Reinforcement Learning: An Introduction](http://incompleteideas.net/book/the-book-2nd.html) (second edition, free PDF). This is the standard RL textbook and the reference for the rest of this section.
   - Chapter 1 for the big picture, chapter 2 (Multi-armed Bandits) in full, and chapter 3 (Finite Markov Decision Processes) in full.
   - Do exercises 2.2, 2.4, 3.8 and 3.17 on paper.
1. Watch lectures 1 and 2 of [David Silver's Introduction to Reinforcement Learning](https://www.youtube.com/playlist?list=PLqYmG7hTraZDM-OYHWgPebj2MfCFzFObQ) (UCL and DeepMind). The slides are on [his teaching page](https://www.davidsilver.uk/teaching/).
   - Lecture 1 introduces the problem. Lecture 2 covers MDPs and the Bellman equations.
1. Read the [MDP chapter of the Berkeley CS188 textbook](https://inst.eecs.berkeley.edu/~cs188/textbook/mdp/) for a shorter, worked-example treatment.
1. Read [Part 1: Key Concepts in RL](https://spinningup.openai.com/en/latest/spinningup/rl_intro.html) from OpenAI's Spinning Up to see the same ideas in the notation deep RL papers use.
1. Practice: reproduce Figure 2.2 from Sutton and Barto. Implement the 10-armed testbed in NumPy, run epsilon-greedy with epsilon of 0, 0.01 and 0.1 for 1,000 steps averaged over 2,000 runs, and plot the average reward and the percentage of optimal actions. Add UCB as a fourth line.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The Multi-Armed Bandit Problem and Its Solutions](https://lilianweng.github.io/posts/2018-01-23-multi-armed-bandit/) by Lilian Weng covers epsilon-greedy, UCB and Thompson sampling with clear derivations.
- [Stanford CS234: Reinforcement Learning](https://web.stanford.edu/class/cs234/) posts its schedule, slides and assignments, a good model of what a graduate RL course covers.
