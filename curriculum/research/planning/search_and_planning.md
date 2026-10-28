<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Long before language models, AI researchers built agents that planned: given a starting state, a goal and a set of actions, find a sequence of actions that reaches the goal. The algorithms they developed are still the baseline that LLM planning papers compare against, and they come with guarantees LLMs lack, such as always finding a plan if one exists or always finding the shortest one. This lesson covers state-space search, heuristics, A* and classical planning with STRIPS and PDDL.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Formulating a problem as a search over states.
- Uninformed search: breadth-first, depth-first and uniform-cost search.
- Heuristics, admissibility and consistency.
- A* search and why it is optimal.
- Classical planning and the STRIPS representation.
- Writing domains and problems in PDDL.
- How domain-independent planners compute their own heuristics.

### Key ideas

- **A search problem has five parts.** A start state, the actions available in each state, a transition model (the result of an action), a goal test and a cost for each step. Once a problem is written this way, generic algorithms can solve it without knowing anything else about the domain.
- **Uninformed search trades memory against guarantees.** Breadth-first search finds the shortest plan in steps but stores the whole frontier. Depth-first search uses little memory but can wander forever. Uniform-cost search expands the cheapest path first and is optimal when steps have different costs. Iterative deepening combines the memory of depth-first with the completeness of breadth-first.
- **Heuristics add domain knowledge.** A heuristic h(n) estimates the remaining cost from a state to the goal. It is *admissible* if it never overestimates, and *consistent* if it obeys a triangle inequality between neighboring states. Good heuristics shrink the search enormously.
- **A* orders the frontier by g plus h.** g(n) is the cost so far and h(n) is the estimated cost to go. With an admissible heuristic (consistent, for graph search), A* is optimal: the first time it pops the goal, that plan is the cheapest. Greedy best-first search uses only h and is fast but not optimal.
- **Classical planning describes the world with facts.** In STRIPS, a state is a set of true facts such as `on(a, b)` or `clear(c)`. Each action has preconditions that must hold, and effects that add and delete facts. Blocksworld, stacking blocks with one robot hand, is the field's standard example.
- **PDDL is the shared language.** The Planning Domain Definition Language splits a task into a domain file (predicates and action schemas) and a problem file (objects, initial state and goal). Any PDDL planner can solve any PDDL task, which is what makes it useful as a tool for an LLM.
- **Planners derive heuristics automatically.** Systems such as Fast Downward relax the problem, for example by ignoring delete effects, and use the relaxed solution's cost as a heuristic. That is why one planner works across very different domains.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the search notes from the [Berkeley CS188 textbook](https://inst.eecs.berkeley.edu/~cs188/textbook/), the free online notes for UC Berkeley's intro AI course.
   - Read [State Spaces and Search Problems](https://inst.eecs.berkeley.edu/~cs188/textbook/search/state.html), [Uninformed Search](https://inst.eecs.berkeley.edu/~cs188/textbook/search/uninformed.html) and [Informed Search](https://inst.eecs.berkeley.edu/~cs188/textbook/search/informed.html).
1. Read Red Blob Games' [Introduction to the A* Algorithm](https://www.redblobgames.com/pathfinding/a-star/introduction.html) and use its interactive diagrams to compare breadth-first search, Dijkstra's algorithm, greedy best-first search and A* on the same map.
1. Read [planning.wiki's guide to PDDL](https://planning.wiki/guide/whatis/pddl) and its [domain reference](https://planning.wiki/ref/pddl/domain) to learn the syntax of domain and problem files.
1. Try a real planner. Follow the [Unified Planning installation guide](https://unified-planning.readthedocs.io/en/latest/getting_started/installation.html) and its [PDDL usage example](https://unified-planning.readthedocs.io/en/latest/notebooks/io/01-pddl-usage-example.html). Unified Planning is a Python library that reads PDDL and calls planners such as [Fast Downward](https://www.fast-downward.org/).
   - In a new project, run `uv add unified-planning up-fast-downward`, write a Blocksworld domain and a 4-block problem, and print the plan.
1. Practice: implement BFS and A* for Blocksworld in plain Python, representing each state as a frozenset of facts. Use "number of blocks not in their goal position" as the heuristic. Solve the same 4-block problem and compare the number of states each algorithm expands with Fast Downward's plan length.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The AIMA website](https://aima.cs.berkeley.edu/) is the home of *Artificial Intelligence: A Modern Approach* by Russell and Norvig, the standard AI textbook. The book itself is not free, but the site and the [official aima-python code repository](https://github.com/aimacode/aima-python) are, and the repo includes runnable notebooks for search and planning.
- [Pyperplan](https://github.com/aibasel/pyperplan) is a small classical planner written in pure Python, good for reading how a planner is built.
- [PDDL generators](https://github.com/AI-Planning/pddl-generators) creates random problem instances for Blocksworld and many other domains, which you will need in the project.
