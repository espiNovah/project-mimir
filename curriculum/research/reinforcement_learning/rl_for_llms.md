<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

A pretrained language model predicts text. It does not yet follow instructions, refuse harmful requests or reason carefully through a math problem. Those behaviors are added in post-training, and much of post-training is reinforcement learning. This lesson connects the policy gradient methods you just learned to the three ideas that shaped modern models: RL from human feedback (RLHF), direct preference optimization (DPO), and RL from verifiable rewards, the recipe behind reasoning models.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- How an LLM can be treated as a policy.
- The RLHF pipeline: supervised fine-tuning, reward modeling and PPO.
- The KL penalty and why it keeps the model close to its starting point.
- Direct preference optimization and why it needs no reward model.
- RL from verifiable rewards and GRPO.
- Reward hacking and over-optimization.
- Tools for running these methods at small scale.

### Key ideas

- **An LLM is a policy over tokens.** The state is the prompt plus the tokens generated so far, each action is the next token, and the episode ends when the response is complete. Usually the reward arrives only once, at the end. Everything from Policy Gradients applies, at a very large scale.
- **RLHF has three stages.** First, supervised fine-tuning (SFT) on example responses. Second, train a reward model on human comparisons ("response A is better than B"), usually with a Bradley-Terry loss that turns pairwise preferences into a scalar score. Third, optimize the SFT model against the reward model with PPO. InstructGPT showed that a small model trained this way was preferred to a much larger model without it.
- **The KL penalty is a leash.** The RL objective subtracts a penalty proportional to the KL divergence between the new policy and the SFT model. Without it, the policy drifts toward odd text that scores well with the reward model but is not actually better.
- **DPO removes the reward model and the RL loop.** The DPO paper shows that the KL-constrained RLHF objective has a closed-form optimal policy. Rearranging gives a simple classification-style loss on preference pairs that you can minimize directly. It is cheaper and more stable than PPO, and it is now a standard baseline.
- **Verifiable rewards skip human labels.** For math, code and other tasks with checkable answers, the reward can be a program: does the answer match, do the tests pass? DeepSeek-R1 used this with GRPO (group relative policy optimization), which samples several answers per prompt and uses each answer's reward relative to the group average as its advantage, so no critic network is needed. Long chains of reasoning emerged from this training.
- **Every reward can be gamed.** Reward models have blind spots, and policies find them: longer answers, flattery, confident wrong answers. Verifiable rewards can be hacked too, for example by code that special-cases the tests. Over-optimization, where true quality falls while the proxy reward keeps rising, is a central open problem.
- **Agents are the next frontier.** Training agents with RL means multi-turn episodes with tool calls and sparse rewards, which brings back the credit-assignment and exploration problems from classic RL.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Training language models to follow instructions with human feedback](https://arxiv.org/abs/2203.02155) (InstructGPT).
   - Read sections 1 to 3 and Figure 2 closely. Note the three stages, the reward model loss and the PPO objective with its KL term.
1. Read [Direct Preference Optimization: Your Language Model is Secretly a Reward Model](https://arxiv.org/abs/2305.18290).
   - Read sections 1 to 4. Work through the derivation in section 4 with pen and paper, using what you learned about KL divergence in Probability and Statistics.
1. Read [DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning](https://arxiv.org/abs/2501.12948).
   - Read the sections on DeepSeek-R1-Zero, the GRPO objective, the rule-based rewards and the "aha moment." Note what they say about why they avoided neural reward models.
1. Use Nathan Lambert's free [RLHF book](https://rlhfbook.com/) as your reference text for this whole topic.
   - Read the chapters on reward modeling, policy gradient algorithms, direct alignment algorithms and reasoning training. Each chapter cites the key papers, so use it to find follow-up reading.
1. Read the [Hugging Face TRL documentation](https://huggingface.co/docs/trl/index), the most widely used open-source library for these methods.
   - Read the [DPO Trainer](https://huggingface.co/docs/trl/dpo_trainer) and [GRPO Trainer](https://huggingface.co/docs/trl/grpo_trainer) pages. Optional: on a free Colab or Kaggle GPU, run the DPO quickstart on a small model, using what you learned in LoRA Fine-Tuning to keep memory low.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Illustrating Reinforcement Learning from Human Feedback](https://huggingface.co/blog/rlhf) on the Hugging Face blog is a short visual overview of the RLHF pipeline.
- [Constitutional AI: Harmlessness from AI Feedback](https://arxiv.org/abs/2212.08073) replaces most human preference labels with AI feedback guided by written principles (RLAIF).
- [DeepSeekMath](https://arxiv.org/abs/2402.03300) is the paper that introduced GRPO, with a clearer derivation than the R1 paper.
- [Let's Verify Step by Step](https://arxiv.org/abs/2305.20050) compares rewarding final answers with rewarding each reasoning step (process supervision).
- [Open R1](https://github.com/huggingface/open-r1) is Hugging Face's open reproduction of the DeepSeek-R1 pipeline.
