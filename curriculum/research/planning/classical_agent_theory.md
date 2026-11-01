### Introduction

The concept of an "agent" did not originate with large language models, prompt engineering, or autonomous coding tools. Since the late 1980s, computer scientists, philosophers, and cognitive theorists have formally studied what it means for an computational entity to perceive an environment, reason about its beliefs, choose actions, and pursue long-term objectives.

Many failure modes observed in contemporary LLM agents—such as losing track of goals midway through a workflow, endlessly repeating failed tool calls, or thrashing between competing subtasks—were analyzed decades ago in classical agent theory.

This lesson explores the foundational principles of agent architectures:
1. **The mathematical definition of an agent and rationality:** How agents map percept histories to actions under the PEAS framework.
2. **The environment taxonomy:** The dimensions that dictate architectural constraints.
3. **The deliberative vs. reactive debate:** Why pure symbolic planning was too brittle, why pure reactive systems lacked foresight, and how hybrid systems bridged the gap.
4. **The Belief-Desire-Intention (BDI) model:** How commitment, practical reasoning, and reconsideration strategies govern intelligent behavior.
5. **The modern synthesis:** How classical cognitive architectures map directly onto contemporary language agents via frameworks like CoALA.

### The formal definition of an agent and rationality

Mathematically, an **agent** is anything that can perceive its environment through sensors and act upon that environment through actuators:

```text
f: P* → A
```

where `P*` represents the sequence of all percepts received by the agent up to the present moment (its percept history), and `A` is the set of possible actions.

An agent is evaluated by a **performance measure**: an external, objective criterion that defines what states of the environment are desirable.

#### Rationality vs. omniscience

Russell and Norvig define a **rational agent** as:

> *"For each possible percept sequence, a rational agent should select an action that is expected to maximize its performance measure, given the evidence provided by the percept sequence and whatever built-in knowledge the agent has."*

Crucially, **rationality is not omniscience**:
- An omniscient agent knows the actual outcome of its actions and acts with perfect foresight (impossible in real-world stochastic physics).
- A rational agent makes the optimal expected decision based on the information it currently possesses, actively balancing exploitation with information gathering (exploration).

#### The PEAS framework

To design any agent rigorously, classical AI defines the **PEAS specification**:
1. **Performance Measure:** The quantitative metric being optimized (e.g., test pass rate, latency, execution cost).
2. **Environment:** The external world with which the agent interacts (e.g., a git repository, bash shell, web browser).
3. **Actuators:** The mechanisms through which the agent causes change (e.g., terminal commands, file writes, API requests).
4. **Sensors:** The mechanisms through which the agent receives percepts (e.g., stdout, exit codes, DOM trees).

### Properties of environments

The structure of the environment dictates which agent architecture is required:

- **Fully Observable vs. Partially Observable:** Does the agent's sensor suite provide complete access to the state of the world at each point in time? In a partially observable world (like software development or web browsing), the agent must maintain internal state (memory) to track unseen information.
- **Deterministic vs. Stochastic:** Is the next state of the world completely determined by the current state and the agent's action? If unexpected events or noise occur, the agent cannot execute open-loop plans; it must continuously verify outcomes.
- **Episodic vs. Sequential:** Does the current decision affect future decisions? In episodic tasks (like classification), each turn is independent. In sequential tasks (like writing code), early choices constrain all future options.
- **Static vs. Dynamic:** Can the environment change while the agent is deliberating? A chess game is static during a player's turn; autonomous driving is dynamic.
- **Discrete vs. Continuous:** Are states, time, percepts, and actions discrete (finite steps) or continuous (real numbers)?
- **Single-Agent vs. Multi-Agent:** Does the environment contain other autonomous entities whose actions affect the outcome (cooperative or competitive)?

| Agent Application | Observability | Determinism | Sequential? | Static? | Discrete? | Agents |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Chess** | Fully | Deterministic | Sequential | Semi (clock) | Discrete | Multi (competitive) |
| **Medical Diagnosis** | Partially | Stochastic | Sequential | Dynamic | Continuous | Single |
| **Coding Agent (SWE-bench)** | Partially | Mostly Deterministic | Sequential | Static | Discrete | Single |

### The ladder of agent architectures

Classical AI categorizes agents into five ascending levels of sophistication:

1. **Simple Reflex Agents:** Select actions based solely on the current percept, ignoring percept history: `Condition → Action` rules. They fail immediately in partially observable environments.
2. **Model-Based Reflex Agents:** Maintain an internal state reflecting the history of the world and unobserved variables: `State' = UpdateState(State, Action, Percept)`.
3. **Goal-Based Agents:** Combine internal state with explicit goal descriptions. They can plan forward: "Will executing action `a` bring the world closer to the goal?"
4. **Utility-Based Agents:** When goals conflict or can be reached in multiple ways, a real-valued utility function evaluates trade-offs between speed, cost, safety, and reliability.
5. **Learning Agents:** Decouple performance execution from learning. A **critic** evaluates agent performance against an external standard, a **learning element** updates policies, and a **learning goal generator** proposes exploratory actions.

### The architectural debate: deliberative vs. reactive

In the late 1980s, AI experienced a fundamental schism between two competing philosophies:

#### The classical deliberative paradigm (Sense-Plan-Act)

Pioneered by early symbolic systems (such as the Shakey robot at Stanford), deliberative agents maintained an explicit, logical world model. Upon receiving a percept, the agent updated its logical knowledge base, invoked a theorem prover or STRIPS planner to synthesize a complete sequence of actions to the goal, and then began execution.

**The failure mode:** Deliberation was slow and fragile. If a brick moved while the planner was searching, the synthesized 50-step plan became invalid before the first step was executed.

#### Reactive architectures: Brooks's subsumption architecture

In 1986, Rodney Brooks published *"Achieving Artificial Intelligence Through Building Robots"* and *"Elephants Don't Play Chess"*, arguing that explicit symbolic world representations and centralized planners were unnecessary for intelligence.

Brooks proposed the **Subsumption Architecture**:
- Intelligence is decomposed into vertical, autonomous **behavior layers** running asynchronously in parallel (e.g., Level 0: Avoid Obstacles; Level 1: Wander; Level 2: Explore).
- Higher layers can inhibit or subsume the inputs and outputs of lower layers, but there is no centralized world model or planning engine.

**The limitation:** Purely reactive agents excel at fast motor control and obstacle avoidance, but cannot solve problems requiring long-horizon reasoning, counterfactual planning, or deferred commitment.

#### Layered hybrid architectures

Modern autonomous systems adopted **hybrid architectures** (e.g., TouringMachines, InterRRaP):
- A fast, reactive bottom layer handles real-time safety and immediate tool feedback.
- A deliberative middle layer handles goal decomposition and plan tracking.
- A social/meta-cognitive top layer handles multi-agent communication and self-reflection.

### The Belief-Desire-Intention (BDI) architecture

Developed by Michael Bratman (1987) as a philosophical theory of practical human reasoning, and implemented computationally by Rao and Georgeff (1995) in the Procedural Reasoning System (PRS), **BDI** is the most widely adopted architecture for goal-directed autonomous agents.

![Belief-Desire-Intention (BDI) Practical Reasoning Architecture](assets/images/bdi_agent_architecture.svg)

#### Core mental attitudes

1. **Beliefs (`B`):** What the agent knows or believes to be true about the environment (including confidence levels, variable assignments, and cached files). When new percepts arrive, a `BeliefRevision(B, percept)` function updates internal knowledge.
2. **Desires (`D`):** The potential motivational states of the agent—all states of affairs that the agent would like to achieve. Desires may be mutually inconsistent or impossible to achieve simultaneously.
3. **Intentions (`I`):** The subset of desires to which the agent has **actively committed**, paired with an active plan chosen from a pre-compiled plan library or generated by a planner.

#### The role of commitment and reconsideration

A key insight of BDI theory is that **intentions drive means-ends reasoning and constrain future deliberation**:
- Once an agent commits to an intention `i`, it does not re-deliberate about what goals to pursue from scratch on every tick. It focuses exclusively on executing the sub-steps of `i`.
- **The reconsideration dilemma:**
  - An agent that **never reconsiders** (blind commitment) will continue executing a plan even after its goal has become impossible or has already been achieved.
  - An agent that **reconsiders on every single step** (cautious agent) spends all its computational budget re-evaluating priorities and never makes progress.

Optimal commitment strategies balance bold execution of established plans with targeted triggers that force reconsideration when environmental anomalies occur.

### Modern language agents through the classical lens: CoALA

In 2023, Sumers et al. introduced **CoALA (Cognitive Architectures for Language Agents)**, demonstrating that modern LLM agent frameworks (ReAct, AutoGPT, Toolformer, SWE-agent) are concrete implementations of classical cognitive architectures:

```text
Classical Agent Concept      LLM Agent Equivalent (CoALA)
------------------------------------------------------------------------------------
Sensors                      API inputs, tool return values, shell stdout/stderr
Actuators                    JSON tool calls, bash execution, python REPL execution
Working Memory / Beliefs     Current context window (system prompt + message history)
Episodic Memory              Vector database of past task transcripts / experiences
Semantic Memory              Pretrained transformer weights + RAG knowledge bases
Procedural Memory            Prompt templates, few-shot examples, tool definitions
Deliberation / Planning      Chain-of-thought, Tree of Thoughts, ReAct scratchpad
Intentions                   Generated checklist, TODO.md, open issues / PR branch
```

Viewing modern agents through classical theory provides immediate design prescriptions:
- When an LLM agent fails, diagnose whether the failure stems from **belief revision** (hallucinated state), **deliberation** (flawed plan generation), or **intention commitment** (abandoning goals prematurely).

### Python implementation: a minimal BDI agent loop

Here is an explicit implementation of a BDI agent execution loop:

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Plan:
    goal: str
    actions: list[str]

    def is_finished(self) -> bool:
        return len(self.actions) == 0

    def pop_action(self) -> str:
        return self.actions.pop(0)

class BDIAgent:
    def __init__(self, plan_library: dict[str, list[str]]):
        self.beliefs: dict[str, bool] = {}
        self.desires: set[str] = set()
        self.intentions: list[Plan] = []
        self.plan_library = plan_library

    def update_beliefs(self, percepts: dict[str, bool]):
        """Belief revision function."""
        self.beliefs.update(percepts)

    def generate_options(self) -> set[str]:
        """Generates candidate desires based on current beliefs."""
        candidate_goals = set()
        if not self.beliefs.get("data_downloaded", False):
            candidate_goals.add("download_data")
        if self.beliefs.get("data_downloaded", False) and not self.beliefs.get("model_trained", False):
            candidate_goals.add("train_model")
        return candidate_goals

    def filter_intentions(self):
        """Deliberation: selects desires to commit to and instantiates plans."""
        for desire in self.desires:
            # If not already committed to this goal
            if not any(plan.goal == desire for plan in self.intentions):
                if desire in self.plan_library:
                    new_plan = Plan(goal=desire, actions=list(self.plan_library[desire]))
                    self.intentions.append(new_plan)

    def should_reconsider(self) -> bool:
        """Reconsideration strategy: check if active plan is invalidated or done."""
        if not self.intentions:
            return True
        current_plan = self.intentions[0]
        # Drop intention if goal is already satisfied
        if self.beliefs.get(current_plan.goal, False):
            return True
        return False

    def step(self, percepts: dict[str, bool]) -> Optional[str]:
        """One cycle of the BDI practical reasoning loop."""
        # 1. Update beliefs from sensors
        self.update_beliefs(percepts)

        # 2. Check if we must reconsider intentions
        if self.should_reconsider():
            self.desires = self.generate_options()
            # Clean up finished plans
            self.intentions = [p for p in self.intentions if not self.beliefs.get(p.goal, False) and not p.is_finished()]
            self.filter_intentions()

        # 3. Execute next action from current intention
        if self.intentions:
            active_plan = self.intentions[0]
            if not active_plan.is_finished():
                return active_plan.pop_action()
        return None
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [Agents chapter of the Berkeley CS188 textbook](https://inst.eecs.berkeley.edu/~cs188/textbook/search/agents.html):
   - Review the formal definition of rational agents, environment properties, and the PEAS framework.
2. Read [BDI Agents: From Theory to Practice](https://cdn.aaai.org/ICMAS/1995/ICMAS95-042.pdf) by Anand Rao and Michael Georgeff (1995).
   - Read sections 1 to 3 for the architectural motivation and the abstract BDI interpreter loop.
3. Read [Cognitive Architectures for Language Agents (CoALA)](https://arxiv.org/abs/2309.02427) (Sumers et al., 2023).
   - Study Section 3 and Figure 2, which detail the mapping of working, episodic, semantic, and procedural memory to LLMs.
4. Review the lecture slides for Michael Wooldridge's *An Introduction to MultiAgent Systems*:
   - Read [Lectures 2 to 5](https://www.cs.ox.ac.uk/people/michael.wooldridge/pubs/imas/distrib/pdf-index.html) covering reactive, deliberative, and hybrid BDI agents.
5. Practice: Take an autonomous agent you built earlier (such as an Agent Loop or Coding Workflow). Write a 1-page architectural critique specifying its PEAS description, classifying its environment along each dimension, and identifying an instance where premature commitment or lack of intention reconsideration caused an execution failure.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The BDI Software Model](https://en.wikipedia.org/wiki/Belief%E2%80%93desire%E2%80%93intention_software_model): Concise reference on BDI logic and practical systems.
- [Jason Agent Programming Platform](https://jason-lang.github.io/): Open-source Java-based interpreter for AgentSpeak, used widely in multi-agent research.
- [Building Language Agents with CoALA](https://github.com/ysymyx/CoALA): Reference code repository and survey of modern language agent architectures.

### Knowledge check

Use these questions to verify your understanding of classical agent theory:

1. [What is the fundamental difference between a rational agent and an omniscient agent under the Russell & Norvig definition?](#the-formal-definition-of-an-agent-and-rationality)
2. [What are the six core dimensions used to classify agent environments, and how does a coding agent score on each?](#properties-of-environments)
3. [Why did Rodney Brooks's Subsumption Architecture reject centralized symbolic planning, and what was its primary limitation?](#the-architectural-debate-deliberative-vs-reactive)
4. [In the Belief-Desire-Intention (BDI) model, why is commitment to an intention essential for efficient practical reasoning?](#the-belief-desire-intention-bdi-architecture)
5. [How does the CoALA framework map classical cognitive concepts (such as working memory and procedural memory) onto modern LLM systems?](#modern-language-agents-through-the-classical-lens-coala)
