> [!TIP]
> **Prerequisite track:** This lesson is part of the Research Track and assumes you have completed [ML Foundations](#/path/ml).

### Introduction

Before large neural networks and autoregressive transformers dominated artificial intelligence, autonomous systems tackled complex objectives through **deliberative planning**: given an explicit representation of the current world state, a set of available actions with defined preconditions and effects, and a goal condition, discover a valid sequence of actions that transforms the start state into the goal.

While contemporary language models generate text fluently, they frequently produce invalid plans, suffer from combinatorial hallucinations, or lose coherence over long horizons. In contrast, classical planning algorithms provide formal guarantees:
- **Completeness:** If a valid plan exists, the algorithm is guaranteed to find it.
- **Optimality:** With appropriate heuristics, the algorithm is guaranteed to find the shortest or lowest-cost plan.

This lesson explores state-space search algorithms (from BFS and Dijkstra to A*), introduces Monte Carlo Tree Search (MCTS), and covers symbolic classical planning using STRIPS and PDDL (Planning Domain Definition Language). Understanding these algorithms gives you the analytical tools to benchmark, evaluate, and hybridize modern LLM reasoning architectures.

### The search problem formulation

A classical deterministic search problem is defined by five components:

1. **State space `S`:** The set of all possible configurations of the world.
2. **Initial state `s_0 ∈ S`:** The state where the agent begins.
3. **Action function `Actions(s)`:** The set of legal actions executable from state `s`.
4. **Transition model `Result(s, a) → s'`:** A deterministic function returning the state that results from taking action `a` in state `s`.
5. **Goal test `IsGoal(s)`:** A boolean function determining whether state `s` satisfies the agent's objective.
6. **Path cost `c(s, a, s')`:** The non-negative step cost of executing action `a` to transition from `s` to `s'`.

A **solution** is a sequence of actions `(a_0, a_1, ..., a_{k-1})` leading from `s_0` to any state `s_k` where `IsGoal(s_k)` is true. An **optimal solution** is a solution with the lowest cumulative path cost `Σ c(s_t, a_t, s_{t+1})`.

### Uninformed search strategies

Uninformed (or blind) search algorithms explore the state space using only the problem definition, without domain-specific knowledge estimating the distance to the goal.

```text
Algorithm                   Frontier Data Structure   Complete?   Optimal?          Time Complexity   Space Complexity
----------------------------------------------------------------------------------------------------------------------
Breadth-First Search (BFS)  FIFO Queue                Yes         Yes (if costs 1)  O(b^d)            O(b^d)
Depth-First Search (DFS)    LIFO Stack                No (graphs) No                O(b^m)            O(b · m)
Uniform-Cost Search (UCS)   Priority Queue (on g(n))  Yes         Yes (any c >= ε)  O(b^{1 + C*/ε})   O(b^{1 + C*/ε})
Iterative Deepening (IDS)   Repeated DFS at depth d   Yes         Yes (if costs 1)  O(b^d)            O(b · d)
```

where:
- `b` is the branching factor (maximum actions per state).
- `d` is the depth of the shallowest goal state.
- `m` is the maximum depth of the state space.
- `g(n)` is the path cost from the start node to node `n`.
- `C*` is the cost of the optimal solution.

#### The tradeoff: memory vs. optimality

- **Breadth-First Search** guarantees finding the shallowest solution, but storing every state on the frontier requires `O(b^d)` memory. For `b = 10` and `d = 8`, the frontier contains 100 million nodes, quickly exhausting RAM.
- **Depth-First Search** requires only linear memory `O(b · m)` along the active branch, but risks getting trapped in infinite loops or returning excessively long paths.
- **Iterative Deepening Search (IDS)** achieves the best of both worlds: it runs depth-limited DFS with limits `1, 2, 3, ...`, achieving the minimal memory of DFS with the completeness and optimality of BFS.

### Informed search and heuristic theory

Informed search leverages a **heuristic function** `h(n)`: an estimate of the cheapest path cost from node `n` to a goal state.

#### Admissibility

A heuristic is **admissible** if it never overestimates the true cost to reach the nearest goal:

```text
0 <= h(n) <= h*(n)  for all n
```

where `h*(n)` is the true optimal cost from `n` to the goal, and `h(goal) = 0`. An admissible heuristic is optimistic: it assumes the goal is closer or easier to reach than it actually is.

#### Consistency (monotonicity)

For graph search (where visited states are recorded in a closed set to avoid redundant expansion), admissibility is not enough to guarantee optimality without reopening closed nodes. We require **consistency**:

```text
h(n) <= c(n, a, n') + h(n')
```

Consistency states that the estimated cost from `n` cannot exceed the actual step cost to neighbor `n'` plus the estimated cost from `n'`. Consistency satisfies the triangle inequality and mathematically implies admissibility.

### A* search and proof of optimality

**A* search** evaluates frontier nodes using the evaluation function:

```text
f(n) = g(n) + h(n)
```

- `g(n)`: The exact, known cost incurred so far from `s_0` to `n`.
- `h(n)`: The estimated cost remaining from `n` to the goal.
- `f(n)`: The estimated total cost of the cheapest path passing through `n`.

#### Optimality of A*

When `h(n)` is consistent, the sequence of nodes expanded by A* has non-decreasing `f`-values:

```text
f(n') = g(n') + h(n') = g(n) + c(n, a, n') + h(n') >= g(n) + h(n) = f(n)
```

**Theorem:** *The first time A* expands a goal node `G`, that node represents an optimal path.*

**Proof:**
Suppose A* selected a sub-optimal goal `G_2` with cost `g(G_2) > C*`.
Because the optimal goal `G*` has not yet been expanded, there must exist an unexpanded node `n` on the frontier that lies on the true optimal path to `G*`.
By definition of admissibility:
```text
f(n) = g(n) + h(n) <= g(n) + h*(n) = C*
```
Because `G_2` is a goal node, `h(G_2) = 0`, so `f(G_2) = g(G_2) > C*`.
Therefore:
```text
f(n) <= C* < f(G_2)
```
Since A* expands the node with the lowest `f`-value from the priority queue, it must expand `n` before `G_2`. By induction, every node along the optimal path will be expanded before `G_2` can ever be selected. Thus, A* cannot terminate with a sub-optimal goal.

### Monte Carlo tree search (MCTS)

In massive state spaces where evaluating every branch is intractable and analytical heuristics are difficult to construct (e.g., Go, Chess, or multi-step programmatic reasoning), **Monte Carlo Tree Search (MCTS)** builds an asymmetric search tree directed by random sampling.

![Monte Carlo Tree Search: The Four Core Phases](assets/images/mcts_phases.svg)

MCTS iterates through four phases on each simulation cycle:

1. **Selection:** Starting at the root state, recursively select child nodes using a bandit algorithm such as **UCB1** (Upper Confidence Bound applied to Trees):
   ```text
   UCT(s, a) = Q(s, a) / N(s, a) + c * sqrt( ln(N(s)) / N(s, a) )
   ```
   The first term exploits actions known to yield high returns; the second term explores actions with low visit counts `N(s, a)`.
2. **Expansion:** Upon reaching a leaf node where legal actions remain unexpanded, instantiate one or more child nodes.
3. **Simulation (Rollout):** From the new node, simulate the environment forward using a fast rollout policy (or heuristic/value network evaluation) until a terminal state or horizon is reached, returning reward `R`.
4. **Backpropagation:** Propagate reward `R` back up the trajectory to the root, incrementing visit counts `N(s) ← N(s) + 1` and updating value estimates `Q(s, a) ← Q(s, a) + (R - Q(s, a)) / N(s, a)`.

MCTS formed the foundation of AlphaGo, AlphaZero, and modern test-time compute scaling for reasoning language models.

### Classical planning: STRIPS and PDDL

In classical planning, world states and actions are represented symbolically using first-order logic predicates.

#### STRIPS representation

Introduced by Fikes and Nilsson (1971), a **STRIPS** action `a` consists of:
- **Preconditions (`Pre(a)`):** Literals that must be true in state `s` for `a` to be executable.
- **Add List (`Add(a)`):** Literals that become true after executing `a`.
- **Delete List (`Del(a)`):** Literals that cease to be true after executing `a`.

The successor state is defined by set operations:

```text
Result(s, a) = ( s \ Del(a) ) ∪ Add(a)
```

#### The Blocksworld example in PDDL

The **Planning Domain Definition Language (PDDL)** standardizes STRIPS across modern research. A planning task is split into two files:
1. **Domain file:** Defines predicates and parameterized action schemas.
2. **Problem file:** Defines concrete objects, the initial state, and the goal specification.

Here is a classic Blocksworld domain schema:

```lisp
(define (domain blocksworld)
  (:requirements :strips)
  (:predicates
    (on ?x ?y)
    (ontable ?x)
    (clear ?x)
    (holding ?x)
    (handempty))

  (:action pick-up
    :parameters (?x)
    :precondition (and (clear ?x) (ontable ?x) (handempty))
    :effect (and (not (ontable ?x))
                 (not (clear ?x))
                 (not (handempty))
                 (holding ?x)))

  (:action stack
    :parameters (?x ?y)
    :precondition (and (holding ?x) (clear ?y))
    :effect (and (not (holding ?x))
                 (not (clear ?y))
                 (clear ?x)
                 (handempty)
                 (on ?x ?y))))
```

#### Domain-independent heuristics: delete relaxation

How do modern planners like **Fast Downward** find solutions across thousands of arbitrary domains without hand-crafted heuristics?

They automatically extract heuristics by **relaxing the problem**:
- In the **delete relaxation** (`h^+`), the planner deletes the delete-list of every action: actions can only add facts, never destroy them.
- In this relaxed monotone world, achieving goals is vastly easier and can be computed in polynomial time.
- The cost of the optimal relaxed plan provides an admissible, domain-independent heuristic for the real planning task.

### Python implementation: A* search

Here is a clean, dependency-free implementation of A* graph search:

```python
import heapq
from typing import Callable, Generic, Optional, TypeVar

State = TypeVar("State")

class PriorityQueue(Generic[State]):
    def __init__(self):
        self._heap = []
        self._count = 0

    def push(self, item: State, priority: float):
        heapq.heappush(self._heap, (priority, self._count, item))
        self._count += 1

    def pop(self) -> State:
        return heapq.heappop(self._heap)[2]

    def __len__(self) -> int:
        return len(self._heap)

def a_star_search(
    start_state: State,
    is_goal: Callable[[State], bool],
    get_successors: Callable[[State], list[tuple[State, str, float]]],
    heuristic: Callable[[State], float],
) -> Optional[tuple[list[str], float]]:
    """
    Runs A* graph search.
    Returns: (list_of_actions, total_cost) or None if no path exists.
    """
    frontier = PriorityQueue[State]()
    frontier.push(start_state, heuristic(start_state))

    came_from: dict[State, tuple[Optional[State], Optional[str]]] = {start_state: (None, None)}
    cost_so_far: dict[State, float] = {start_state: 0.0}

    while len(frontier) > 0:
        current = frontier.pop()

        if is_goal(current):
            # Reconstruct path
            actions = []
            curr = current
            while came_from[curr][0] is not None:
                prev_state, action = came_from[curr]
                actions.append(action)
                curr = prev_state
            actions.reverse()
            return actions, cost_so_far[current]

        current_cost = cost_so_far[current]

        for next_state, action, step_cost in get_successors(current):
            new_cost = current_cost + step_cost
            if next_state not in cost_so_far or new_cost < cost_so_far[next_state]:
                cost_so_far[next_state] = new_cost
                priority = new_cost + heuristic(next_state)
                frontier.push(next_state, priority)
                came_from[next_state] = (current, action)

    return None
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the search chapters from the [Berkeley CS188 textbook](https://inst.eecs.berkeley.edu/~cs188/textbook/):
   - [State Spaces and Search Problems](https://inst.eecs.berkeley.edu/~cs188/textbook/search/state.html)
   - [Uninformed Search](https://inst.eecs.berkeley.edu/~cs188/textbook/search/uninformed.html)
   - [Informed Search](https://inst.eecs.berkeley.edu/~cs188/textbook/search/informed.html)
2. Explore Red Blob Games' interactive [Introduction to the A* Algorithm](https://www.redblobgames.com/pathfinding/a-star/introduction.html).
   - Observe how BFS, Dijkstra, Greedy Best-First, and A* explore different frontier shapes on grid obstacles.
3. Read [planning.wiki's guide to PDDL](https://planning.wiki/guide/whatis/pddl) and the [domain specification reference](https://planning.wiki/ref/pddl/domain).
4. Install Unified Planning and run Fast Downward on a local Blocksworld problem:
   - Run `uv add unified-planning up-fast-downward`.
   - Formulate a 4-block stack inversion problem and inspect the generated action plan.
5. Implement A* for Blocksworld in Python using `frozenset` state representations, compare expansions against BFS, and verify that an admissible heuristic strictly dominates unguided search.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [AIMA Code Repository (aima-python)](https://github.com/aimacode/aima-python): Official Python implementations of Russell & Norvig's search and planning algorithms.
- [Fast Downward Planning System](https://www.fast-downward.org/): The leading domain-independent classical planning engine.
- [Pyperplan](https://github.com/aibasel/pyperplan): Lightweight, pure-Python classical planner written for educational study.

### Knowledge check

Use these questions to verify your understanding of search and planning:

1. [What are the five core mathematical components required to formulate a formal state-space search problem?](#the-search-problem-formulation)
2. [What condition must a heuristic satisfy to be admissible, and what additional condition is required for consistency?](#informed-search-and-heuristic-theory)
3. [Why is A* search guaranteed to return an optimal path the very first time it expands a goal state?](#a-search-and-proof-of-optimality)
4. [What are the four phases of Monte Carlo Tree Search (MCTS), and how does the UCT formula balance exploration and exploitation?](#monte-carlo-tree-search-mcts)
5. [In STRIPS and PDDL planning, what is the delete relaxation heuristic, and why can it be computed efficiently?](#classical-planning-strips-and-pddl)
