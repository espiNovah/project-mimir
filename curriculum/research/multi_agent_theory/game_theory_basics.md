<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

In Multi-Agent Systems you built agents that cooperate because you designed them to share one goal. Many real systems are different: agents represent different people or companies with different interests, such as a buyer's agent and a seller's agent. Game theory is the mathematics of decisions when the outcome depends on what others choose. It gives you predictions to test LLM agents against, and it is the foundation of every multi-agent systems course at the graduate level.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Normal-form games, strategies and payoffs.
- Dominant strategies and iterated elimination of dominated strategies.
- Nash equilibrium in pure and mixed strategies.
- The prisoner's dilemma and why equilibria can be inefficient.
- Extensive-form games, backward induction and subgame perfection.
- Repeated games, tit-for-tat and the folk theorem.

### Key ideas

- **A game is players, strategies and payoffs.** In a normal-form game, each player picks a strategy at the same time, and a payoff table gives each player's reward for every combination. Players are assumed to be rational (they maximize their own expected payoff), and to know that the others are rational too.
- **Dominance is the strongest prediction.** A strategy is strictly dominated if another strategy does better no matter what the others do. Rational players never play dominated strategies, and removing them repeatedly sometimes leaves a single prediction.
- **A Nash equilibrium is a stable profile.** It is a choice of strategy for every player such that no player can gain by changing only their own strategy. Every finite game has at least one Nash equilibrium if players may randomize (a mixed strategy). In a mixed equilibrium, each player's randomization makes the others indifferent between their choices.
- **Equilibria can be bad for everyone.** In the prisoner's dilemma, defecting dominates cooperating for each player, so mutual defection is the only equilibrium, even though mutual cooperation pays both more. Many problems in multi-agent systems, from shared resources to price wars, have this structure.
- **Sequential games are solved backward.** When players move in turns, an extensive-form game tree captures who knows what and when. Backward induction solves it from the end. A subgame-perfect equilibrium rules out threats that a player would not actually carry out when the time came.
- **Repetition changes incentives.** If the prisoner's dilemma is repeated with no known last round, cooperation can be sustained, because defecting today invites punishment tomorrow. The folk theorem says many outcomes, including full cooperation, can be equilibria of repeated games when players are patient enough. With a known final round, backward induction predicts defection all the way back to the start, which human players (and LLMs) often do not follow.
- **Strategies like tit-for-tat do well in practice.** In Axelrod's tournaments, tit-for-tat (cooperate first, then copy the opponent's last move) beat more complicated strategies, because it is nice, retaliates, forgives and is easy to understand.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Play Nicky Case's interactive [The Evolution of Trust](https://ncase.me/trust/) for a 30-minute introduction to the repeated prisoner's dilemma and strategies like tit-for-tat.
1. Watch Yale's [ECON 159: Game Theory](https://oyc.yale.edu/economics/econ-159) by Ben Polak, a complete free undergraduate course with lecture notes and problem sets. The videos are also on [YouTube](https://www.youtube.com/playlist?list=PL6EF60E1027E1A10B).
   - Watch lectures 1 to 6 (dominance, best responses, Nash equilibrium), 9 and 10 (mixed strategies), 13 to 16 (backward induction) and 21 and 22 (repeated games).
   - Do the problem sets for those lectures before reading the solutions.
1. Read chapter 3 (Introduction to Noncooperative Game Theory: Games in Normal Form) and section 6.1 (repeated games) of [Multiagent Systems: Algorithmic, Game-Theoretic, and Logical Foundations](https://www.masfoundations.org/) by Shoham and Leyton-Brown, which the authors offer as a free PDF. It covers the same material with the formal definitions computer science papers use.
1. Read the [Prisoner's Dilemma entry](https://plato.stanford.edu/entries/prisoner-dilemma/) in the Stanford Encyclopedia of Philosophy for the variations (iterated, finitely repeated, many players) that appear in research papers.
   - Read sections 1 to 4 and the section on the iterated prisoner's dilemma.
1. Practice: write a Python function that finds all pure-strategy Nash equilibria of a two-player game given its payoff matrices, and another that computes the mixed equilibrium of any 2x2 game. Test them on the prisoner's dilemma, matching pennies, battle of the sexes and stag hunt. Then simulate a 200-round iterated prisoner's dilemma tournament among tit-for-tat, always-defect, always-cooperate and random.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The Game Theory entry](https://plato.stanford.edu/entries/game-theory/) in the Stanford Encyclopedia of Philosophy discusses what equilibrium concepts assume about rationality, useful when asking whether LLMs should be expected to play equilibria.
- [Tim Roughgarden's Algorithmic Game Theory lecture notes](https://timroughgarden.org/f13/f13.html) (Stanford CS364A) are free notes and videos on the computational side of game theory: the price of anarchy, mechanism design and how hard it is to compute equilibria.
