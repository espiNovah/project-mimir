> [!TIP]
> **Prerequisite track:** This lesson is part of the Research Track and assumes you have completed [ML Foundations](#/path/ml).

### Introduction

In previous modules on multi-agent systems, you designed agents that cooperated smoothly because you controlled every participant and gave them a shared objective function.

In real-world deployment, however, autonomous agents represent different individuals, organizations, or competing software platforms:
- A buyer's shopping agent negotiates against a seller's pricing bot.
- High-frequency trading bots compete for arbitrage liquidity in financial order books.
- LLM coding assistants bid for limited execution compute on a shared GPU cluster.

When multiple autonomous agents interact, an agent cannot simply choose an action in isolation: its payoff depends fundamentally on the actions chosen by other agents, who are simultaneously anticipating what it will do.

**Game theory** is the formal mathematical study of strategic interaction between rational decision-makers. It provides the equilibrium concepts, optimality criteria, and predictive frameworks necessary to analyze, benchmark, and govern multi-agent AI ecosystems.

### Normal-form games and strategic dominance

A finite **normal-form game** (or strategic-form game) is defined by three components:
1. A finite set of **players** `N = {1, 2, ..., n}`.
2. For each player `i ∈ N`, a non-empty finite set of pure **actions/strategies** `S_i`. The set of all strategy profiles is the Cartesian product `S = S_1 × S_2 × ... × S_n`.
3. For each player `i ∈ N`, a **payoff function** `u_i: S → R` assigning a real-valued utility to each strategy profile `s = (s_1, s_2, ..., s_n)`.

We often write `s = (s_i, s_{-i})`, where `s_i` is player `i`'s chosen strategy and `s_{-i}` represents the vector of strategies chosen by all other players.

#### Strict and weak dominance

Rationality implies that players seek to maximize their expected payoff:

- A strategy `s_i ∈ S_i` is **strictly dominated** by `s_i'` if for all possible strategies of the opponents `s_{-i} ∈ S_{-i}`:
  ```text
  u_i(s_i', s_{-i}) > u_i(s_i, s_{-i})
  ```
- A strategy `s_i ∈ S_i` is **weakly dominated** by `s_i'` if `u_i(s_i', s_{-i}) >= u_i(s_i, s_{-i})` for all `s_{-i}`, with strict inequality for at least one `s_{-i}`.

**Iterated Elimination of Strictly Dominated Strategies (IESDS):** A rational player will never play a strictly dominated strategy. If all players know that all players are rational (common knowledge of rationality), we can iteratively eliminate dominated strategies. If this process shrinks the game down to a unique profile, the game is **strictly dominance-solvable**.

### Nash equilibrium: pure and mixed strategies

While dominance elimination is powerful, most games cannot be solved by dominance alone. We need a general equilibrium concept.

#### Best response and pure strategy Nash equilibrium

Player `i`'s **best response** to opponent strategies `s_{-i}` is the set of actions that maximize `u_i`:

```text
BR_i(s_{-i}) = argmax_{s_i ∈ S_i} u_i(s_i, s_{-i})
```

A strategy profile `s* = (s_1*, s_2*, ..., s_n*)` is a **Pure Strategy Nash Equilibrium (PSNE)** if every player's strategy is a best response to the strategies of all other players:

```text
u_i(s_i*, s_{-i}*) >= u_i(s_i, s_{-i}*)   for all s_i ∈ S_i  and all i ∈ N
```

In a Nash equilibrium, **no player has a unilateral incentive to deviate**. The system is in strategic balance.

#### Mixed strategies and the indifference principle

In games like Matching Pennies or Rock-Paper-Scissors, no pure strategy equilibrium exists. Players must randomize their choices.

A **mixed strategy** `σ_i ∈ Δ(S_i)` is a probability distribution over player `i`'s pure actions, where `Σ_{a ∈ S_i} σ_i(a) = 1` and `σ_i(a) >= 0`.

**Nash's Existence Theorem (John Nash, 1950):** *Every finite game has at least one Nash equilibrium in mixed strategies.*

In any mixed-strategy equilibrium where player `i` randomizes across multiple actions with non-zero probability:
```text
E[u_i(a_1, σ_{-i})] = E[u_i(a_2, σ_{-i})] = ... = E[u_i(σ_i, σ_{-i})]
```
This is the **Indifference Principle**: player `j` chooses their randomization probabilities specifically to make player `i` completely indifferent between their candidate pure actions.

### Canonical 2x2 normal-form games

Studying 2-player, 2-action games reveals fundamental strategic archetypes:

![Canonical 2x2 Normal-Form Games and Strategic Equilibria](assets/images/game_theory_canonical_games.svg)

#### 1. The Prisoner's Dilemma: individual vs. collective rationality

Two suspects are arrested. Each can independently choose to **Cooperate (C)** with their partner (remain silent) or **Defect (D)** (confess and betray).
- Payoffs `(u_1, u_2)`: `(C, C) = (3, 3)`, `(D, C) = (5, 0)`, `(C, D) = (0, 5)`, `(D, D) = (1, 1)`.
- For Player 1: If Player 2 plays C, defecting gives `5 > 3`. If Player 2 plays D, defecting gives `1 > 0`.
- **Defection is a strictly dominant strategy** for both players.
- The unique Nash equilibrium is `(D, D)` yielding payoff `(1, 1)`, even though mutual cooperation `(C, C)` yields `(3, 3)`.
- The equilibrium is **Pareto sub-optimal**: an outcome exists where both players are strictly better off, but self-interested rationality prevents them from reaching it.

#### 2. The Stag Hunt: trust and coordination

Two hunters can choose to hunt a **Stag (S)** (which requires mutual cooperation to succeed) or a **Hare (H)** (which can be caught alone without help).
- Payoffs: `(S, S) = (4, 4)`, `(S, H) = (0, 3)`, `(H, S) = (3, 0)`, `(H, H) = (3, 3)`.
- There are **two pure Nash equilibria**: `(S, S)` and `(H, H)`.
- `(S, S)` is **payoff-dominant**: both hunters receive the maximum possible utility.
- `(H, H)` is **risk-dominant**: hunting a hare guarantees a payoff of 3 regardless of what the other hunter does. If Player 1 is uncertain whether Player 2 can be trusted, hunting a hare minimizes downside risk.

#### 3. Battle of the Sexes (Bach or Stravinsky)

Two agents want to attend an event together. Player 1 prefers Opera (O); Player 2 prefers Ballet (B). Both prefer attending an event together over attending alone.
- Payoffs: `(O, O) = (3, 2)`, `(B, B) = (2, 3)`, `(O, B) = (0, 0)`, `(B, O) = (0, 0)`.
- Two pure equilibria `(O, O)` and `(B, B)` plus one mixed equilibrium. This represents asymmetric coordination with conflicting interests.

### Extensive-form games and backward induction

When agents act sequentially over time with observable turns, games are represented in **extensive form** using a game tree:
- Nodes represent decision points for specific players.
- Edges represent available actions.
- Leaf nodes contain terminal payoffs.

#### Backward induction and subgame perfection

In finite games of perfect information (such as Chess, Tic-Tac-Toe, or sequential price setting), games are solved from terminal leaves back to the root using **backward induction** (Zermelo's Theorem, 1913):
1. Start at the penultimate nodes (where the final player acts).
2. The final player chooses the action maximizing their payoff.
3. Replace the node with the resulting payoff vector.
4. Step backward one ply and repeat until the root is reached.

Backward induction identifies a **Subgame-Perfect Nash Equilibrium (SPNE)**: an equilibrium that constitutes a valid Nash equilibrium in every subgame of the original game tree, ruling out **non-credible threats** (threats that a rational agent would never execute if called upon to act).

### Repeated games and the Folk Theorem

What happens when an interaction like the Prisoner's Dilemma is played repeatedly between the same agents?

#### Finitely repeated games

If the game is repeated for a known, fixed number of rounds `T` (e.g. 100 rounds), backward induction causes cooperation to unravel:
- In round `T`, there is no future. Both players defect.
- Knowing round `T` will feature mutual defection, round `T-1` becomes the effective final round. Both players defect.
- By induction, defection unravels all the way back to round 1!

#### Infinitely repeated games and discount factors

When games are repeated indefinitely with continuation probability or discount factor `δ ∈ (0, 1)`, the shadow of the future enables robust cooperation.

A player compares the one-time temptation to cheat against the long-term cost of punishment:
- Cooperating forever yields discounted return: `3 + 3δ + 3δ^2 + ... = 3 / (1 - δ)`.
- Cheating yields immediate defect payoff 5, followed by permanent punishment (payoff 1 forever under a **Grim Trigger** strategy): `5 + 1δ + 1δ^2 + ... = 5 + δ / (1 - δ)`.

Cooperation is stable whenever:
```text
3 / (1 - δ) >= 5 + δ / (1 - δ)
3 >= 5(1 - δ) + δ
2δ >= 2  ==>  δ >= 0.5
```
If agents value future payoffs at `δ >= 0.5`, mutual cooperation is a subgame-perfect Nash equilibrium.

#### Axelrod's tournaments: Tit-for-Tat

In Robert Axelrod's famous computer tournaments (1980), programs competed in iterated prisoner's dilemma matches. Anatol Rapoport's **Tit-for-Tat** strategy won repeatedly:
1. **Nice:** Cooperate on round 1.
2. **Retaliatory:** If the opponent defects, defect on the very next round.
3. **Forgiving:** If the opponent returns to cooperation, immediately resume cooperation.
4. **Clear:** The strategy is transparent and easily anticipated by opponents.

#### The Folk Theorem

The **Folk Theorem** for repeated games states that any feasible payoff profile that gives each player strictly more than their min-max reservation utility can be sustained as a subgame-perfect equilibrium, provided players are sufficiently patient (`δ` close to 1).

### Python implementation: finding pure and mixed Nash equilibria

Here is a Python utility to compute pure strategy Nash equilibria and solve 2x2 mixed strategy equilibria:

```python
import numpy as np

def find_pure_nash_equilibria(u1: np.ndarray, u2: np.ndarray) -> list[tuple[int, int]]:
    """
    Finds all Pure Strategy Nash Equilibria for a 2-player normal-form game.
    u1, u2 are payoff matrices of shape (m, n).
    """
    m, n = u1.shape
    equilibria = []

    # Best responses for Player 1 (maximize over rows for each column j)
    p1_best_responses = np.zeros((m, n), dtype=bool)
    for j in range(n):
        max_val = np.max(u1[:, j])
        p1_best_responses[u1[:, j] == max_val, j] = True

    # Best responses for Player 2 (maximize over columns for each row i)
    p2_best_responses = np.zeros((m, n), dtype=bool)
    for i in range(m):
        max_val = np.max(u2[i, :])
        p2_best_responses[i, u2[i, :] == max_val] = True

    # Mutual best responses
    for i in range(m):
        for j in range(n):
            if p1_best_responses[i, j] and p2_best_responses[i, j]:
                equilibria.append((i, j))

    return equilibria

def solve_2x2_mixed_nash(u1: np.ndarray, u2: np.ndarray) -> tuple[float, float]:
    """
    Solves for the unique interior mixed-strategy Nash equilibrium in a 2x2 game.
    Returns: (p, q), where Player 1 plays Row 0 with prob p, and Player 2 plays Col 0 with prob q.
    """
    # Player 2 makes Player 1 indifferent between Row 0 and Row 1:
    # q * u1[0,0] + (1-q) * u1[0,1] = q * u1[1,0] + (1-q) * u1[1,1]
    denom_p1 = (u1[0, 0] - u1[0, 1]) - (u1[1, 0] - u1[1, 1])
    if denom_p1 == 0:
        q = np.nan
    else:
        q = (u1[1, 1] - u1[0, 1]) / denom_p1

    # Player 1 makes Player 2 indifferent between Col 0 and Col 1:
    # p * u2[0,0] + (1-p) * u2[1,0] = p * u2[0,1] + (1-p) * u2[1,1]
    denom_p2 = (u2[0, 0] - u2[1, 0]) - (u2[0, 1] - u2[1, 1])
    if denom_p2 == 0:
        p = np.nan
    else:
        p = (u2[1, 1] - u2[1, 0]) / denom_p2

    return float(p), float(q)

# Example demonstration on Prisoner's Dilemma
if __name__ == "__main__":
    u1_pd = np.array([[3, 0], [5, 1]])
    u2_pd = np.array([[3, 5], [0, 1]])
    psne = find_pure_nash_equilibria(u1_pd, u2_pd)
    print("Prisoner's Dilemma PSNE indices (row, col):", psne) # [(1, 1)] -> (Defect, Defect)
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Play Nicky Case's interactive game [The Evolution of Trust](https://ncase.me/trust/) to explore Axelrod's tournaments, error tolerance, and the emergence of cooperative norms.
2. Watch lectures 1 to 6 and 13 to 16 of Yale's [ECON 159: Game Theory](https://oyc.yale.edu/economics/econ-159) with Ben Polak (available on [YouTube](https://www.youtube.com/playlist?list=PL6EF60E1027E1A10B)).
   - Focus on best response correspondence, mixed strategy calculations, and backward induction.
3. Read Chapter 3 (Normal Form Games) and Section 6.1 (Repeated Games) of [Multiagent Systems: Algorithmic, Game-Theoretic, and Logical Foundations](https://www.masfoundations.org/) by Shoham and Leyton-Brown.
4. Read the [Prisoner's Dilemma entry](https://plato.stanford.edu/entries/prisoner-dilemma/) in the Stanford Encyclopedia of Philosophy.
5. Practice: Implement a 200-round iterated tournament between four automated agents (Always-Cooperate, Always-Defect, Tit-for-Tat, and Tit-for-Two-Tats) in Python. Add 5% random communication noise (accidental defection) and analyze why standard Tit-for-Tat degrades into mutual recrimination while Tit-for-Two-Tats maintains resilience.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Game Theory Entry in Stanford Encyclopedia of Philosophy](https://plato.stanford.edu/entries/game-theory/): Epistemic assumptions behind rationality and equilibrium concepts.
- [Tim Roughgarden's Algorithmic Game Theory Lecture Notes](https://timroughgarden.org/f13/f13.html): Stanford CS364A notes on price of anarchy and computational game theory.
- [Axelrod Python Library](https://axelrod.readthedocs.io/en/stable/): Open-source research library containing hundreds of tournament strategies for the iterated prisoner's dilemma.

### Knowledge check

Use these questions to verify your understanding of game theory basics:

1. [Under what condition is an action strictly dominated, and why can strictly dominated strategies be safely eliminated?](#normal-form-games-and-strategic-dominance)
2. [What is the formal definition of a Nash equilibrium, and what does the Indifference Principle state regarding mixed strategies?](#nash-equilibrium-pure-and-mixed-strategies)
3. [Why is the unique Nash equilibrium of the Prisoner's Dilemma Pareto sub-optimal?](#canonical-2x2-normal-form-games)
4. [How does backward induction identify subgame-perfect Nash equilibria, and how does it rule out non-credible threats?](#extensive-form-games-and-backward-induction)
5. [How does the shadow of the future in infinitely repeated games enable cooperation under the Folk Theorem?](#repeated-games-and-the-folk-theorem)
