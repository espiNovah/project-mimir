<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Put many LLM agents in a shared environment and behavior appears that nobody programmed: agents organize a party, spread information, cooperate, or collude. A growing body of research uses these setups to simulate social behavior, to test how LLMs act strategically, and to improve answers through debate. This lesson surveys that work and, just as important, the methodological problems that make many of its findings fragile.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Generative agents: memory, reflection and planning in a simulated town.
- Role-playing agent societies and communicative agents.
- LLMs playing classic games: what they do compared with equilibrium predictions.
- Multi-agent debate as a way to improve reasoning.
- Emergent risks: collusion, deception and correlated failures.
- How to design multi-agent simulation studies that hold up.

### Key ideas

- **Generative agents combine memory, reflection and planning.** In the Generative Agents paper, 25 LLM-driven characters in a sandbox town stored observations in a memory stream, retrieved them by recency, importance and relevance, periodically wrote higher-level reflections, and made daily plans. Starting from one agent's intention to host a party, invitations spread and other agents showed up. Ablations showed each component mattered for believability.
- **Role-play creates agent societies cheaply.** Frameworks such as CAMEL assign agents roles (for example, a user and an assistant) and let them converse to complete tasks. This is useful for generating data and studying cooperation, but conversations can loop, drift off task or flip roles.
- **LLMs are not textbook rational players.** In repeated games studies, models often cooperate more than game theory predicts in the one-shot prisoner's dilemma, can be unforgiving after a single defection, and coordinate poorly in games that require taking turns. Benchmarks such as GTBench find that strategic reasoning varies widely across game types and models. Results can change with prompt wording, the names of the actions and the model version.
- **Debate can help, under conditions.** Having several model instances propose answers, critique each other and revise improves accuracy on some reasoning and factuality tasks. Gains depend on diversity between agents. Copies of the same model often agree on the same wrong answer.
- **New risks come from interaction.** Agents can learn to collude, for example tacitly raising prices in a simulated market, and can be manipulated by messages from other agents (a multi-agent form of prompt injection). Because agents often share one underlying model, their errors are correlated, so a group of agents is less independent than it looks.
- **Simulation studies need careful controls.** Strong claims need fixed-strategy baselines, many runs with different seeds, varied prompt framings, and checks that the model has not simply memorized the game from its training data. Treat a single impressive transcript as an anecdote, not evidence.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Generative Agents: Interactive Simulacra of Human Behavior](https://arxiv.org/abs/2304.03442) by Park and colleagues.
   - Read sections 1 to 5 and the evaluation. Draw the agent architecture from memory, then compare it with the memory system you built in The Agent That Remembers.
   - Optional: browse the [Generative Agents code](https://github.com/joonspk-research/generative_agents).
1. Read [Playing repeated games with Large Language Models](https://arxiv.org/abs/2305.16867) by Akata and colleagues, which pits LLMs against each other and fixed strategies in repeated 2x2 games.
   - Read the whole paper. Note the payoff matrices, the number of rounds, how behavior is measured, and the "prompting the model to predict the other player" intervention.
1. Read [GTBench: Uncovering the Strategic Reasoning Limitations of LLMs via Game-Theoretic Evaluations](https://arxiv.org/abs/2402.12348).
   - Read the introduction, the taxonomy of games and the main findings. Note which kinds of games are hardest for models.
1. Read [Improving Factuality and Reasoning in Language Models through Multiagent Debate](https://arxiv.org/abs/2305.14325).
   - Read the method and results, and look for evidence of how much improvement depends on the number of agents and rounds.
1. Practice: write a one-page critique of one of the papers above as if you were a reviewer. Cover the claims, the evidence for each, missing baselines or controls, and one follow-up experiment that would most strengthen or weaken the main conclusion. Use the method from Reading Papers.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [CAMEL: Communicative Agents for "Mind" Exploration of Large Language Model Society](https://arxiv.org/abs/2303.17760) introduced role-playing agent societies and analyzes how their conversations fail.
- [Large Language Model based Multi-Agents: A Survey of Progress and Challenges](https://arxiv.org/abs/2402.01680) maps the field, including simulation, problem-solving and evaluation work.
- [Theory of Mind for Multi-Agent Collaboration via Large Language Models](https://arxiv.org/abs/2310.10701) tests whether LLM agents model each other's beliefs during a cooperative game.
