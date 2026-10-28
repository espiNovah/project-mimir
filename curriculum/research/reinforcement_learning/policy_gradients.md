<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Value-based methods learn how good each action is, then act greedily. Policy gradient methods skip that step and adjust the policy's parameters directly to make high-return behavior more likely. That makes them a natural fit for large or continuous action spaces, and for language models, whose policy is a distribution over tokens. This lesson derives the policy gradient, then builds up to actor-critic methods and PPO, the algorithm that trained the first RLHF chatbots.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Parameterized stochastic policies.
- The policy gradient theorem and the log-derivative trick.
- REINFORCE and why it has high variance.
- Baselines and advantage functions.
- Actor-critic methods and generalized advantage estimation.
- Trust regions and PPO's clipped objective.

### Key ideas

- **Optimize the policy directly.** Write the policy as a distribution pi(a | s; theta), for example a softmax over action scores from a small network. The objective J(theta) is the expected return. You want its gradient so you can do gradient ascent.
- **The log-derivative trick makes the gradient computable.** Because the gradient of p equals p times the gradient of log p, the gradient of expected return becomes an expectation of (gradient of log pi(a | s)) times the return. You can estimate it by sampling episodes, with no need to differentiate through the environment.
- **REINFORCE is the simplest version.** Run an episode, then for each step, push up the log-probability of the action taken, in proportion to the return that followed. It is unbiased but very noisy, so it needs many episodes.
- **Baselines cut variance without adding bias.** Subtracting any function of the state, b(s), from the return leaves the expected gradient unchanged, because the expected gradient of log pi is zero. A good baseline is an estimate of V(s). The return minus the baseline estimates the *advantage*: how much better the action was than average.
- **Actor-critic methods learn both.** The actor is the policy; the critic is a learned value function that supplies the baseline and can replace full returns with bootstrapped estimates. Generalized advantage estimation (GAE) blends one-step and multi-step advantage estimates with a parameter lambda to trade bias against variance.
- **Big policy updates are dangerous.** One bad gradient step can collapse a policy, and the data it then collects is worse. Trust-region methods limit how far each update moves the policy. PPO does this cheaply by clipping the ratio between the new and old action probabilities, so the objective stops rewarding changes beyond a small range.
- **Implementation details matter.** PPO's published results depend on choices such as advantage normalization, learning rate annealing and value-loss clipping. Small differences in these explain many failed reproductions.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read chapter 13 (Policy Gradient Methods) of [Sutton and Barto](http://incompleteideas.net/book/the-book-2nd.html).
   - Sections 13.1 to 13.5 cover the policy gradient theorem, REINFORCE, baselines and actor-critic. Work through the proof of the policy gradient theorem in section 13.2 line by line.
1. Read [Part 3: Intro to Policy Optimization](https://spinningup.openai.com/en/latest/spinningup/rl_intro3.html) from OpenAI's Spinning Up. It derives the policy gradient in deep RL notation and includes a minimal PyTorch implementation.
   - Read the derivation, then the "Implementing the Simplest Policy Gradient" section, and run the code.
1. Watch lecture 7 (Policy Gradient Methods) of [David Silver's RL course](https://www.youtube.com/playlist?list=PLqYmG7hTraZDM-OYHWgPebj2MfCFzFObQ).
1. Do units 4 and 8 of the [Hugging Face Deep RL Course](https://huggingface.co/learn/deep-rl-course/unit0/introduction). Unit 4 implements REINFORCE in PyTorch. Unit 8 covers PPO.
1. Read the [PPO paper](https://arxiv.org/abs/1707.06347), then [The 37 Implementation Details of Proximal Policy Optimization](https://iclr-blog-track.github.io/2022/03/25/ppo-implementation-details/). List the five details you think matter most and why.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Policy Gradient Algorithms](https://lilianweng.github.io/posts/2018-04-08-policy-gradient/) by Lilian Weng surveys the main policy gradient methods with consistent notation.
- [High-Dimensional Continuous Control Using Generalized Advantage Estimation](https://arxiv.org/abs/1506.02438) is the original GAE paper.
- [Deep Reinforcement Learning that Matters](https://arxiv.org/abs/1709.06560) shows how much seeds, hyperparameters and code bases change deep RL results.
