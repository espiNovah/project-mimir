### Introduction

Every autonomous language agent you have built so far engages in planning of some kind: given a user prompt, it decomposes the objective, decides which tool to call next, evaluates tool observations, and adjusts its subsequent actions.

However, a fundamental debate divides artificial intelligence researchers: **Can an autoregressive large language model autonomously plan?**

In the classical sense established in [Search and Planning](#/lesson/research/planning/search_and_planning), planning requires exploring state spaces, guaranteeing that action preconditions are satisfied, verifying that delete effects do not invalidate downstream goals, and guaranteeing soundness. While LLMs excel at proposing plausible next steps, translating between human prose and formal code, and recognizing common solution templates, they struggle with long-horizon combinatorial constraints, often hallucinating invalid actions when problem instances deviate from training data.

This lesson examines:
1. The progression of prompting and search paradigms: Chain-of-Thought, ReAct, and Tree of Thoughts.
2. The empirical evidence from benchmarks like PlanBench and Mystery Blocksworld.
3. Neurosymbolic hybrid architectures: LLM+P and LLM-Modulo systems.
4. The economics and capabilities of test-time compute scaling in modern reasoning models.

### The evolution of reasoning paradigms

Over recent years, AI researchers developed increasingly structured techniques to steer autoregressive models toward deliberative reasoning:

![Evolution of LLM Planning and Reasoning Paradigms](assets/images/planning_paradigms_comparison.svg)

#### 1. Chain-of-Thought (CoT) prompting

Standard input-output prompting forces the transformer to predict the final answer immediately, using only a single forward pass of fixed compute. In contrast, **Chain-of-Thought** (Wei et al., 2022) prompts the model to generate intermediate reasoning tokens prior to emitting the final answer:

```text
Question: A farmer has 14 sheep. All but 6 die. How many are left?
Thought: The phrase "all but 6 die" means that 6 sheep survive.
Answer: 6
```

Generating intermediate tokens allows each subsequent token to attend back over prior reasoning steps, allocating dynamic test-time compute proportional to token length.

**Self-Consistency** (Wang et al., 2022) enhances CoT by sampling multiple distinct reasoning paths at non-zero temperature and taking a majority vote over the final answers, filtering out idiosyncratic arithmetic slips.

#### 2. ReAct: interleaving reasoning with actions

Pure Chain-of-Thought operates purely in internal memory, isolated from external ground truth. When an error occurs in step 2, step 3 builds upon that false premise, leading to unrecoverable compounding errors.

**ReAct** (Yao et al., 2022) interleaves reasoning traces ("Thoughts") with external environment interactions ("Actions" and "Observations"):

```text
Thought: I need to check the user's current account balance before processing the refund.
Action: fetch_balance(user_id="usr_482")
Observation: {"balance": 150.00, "currency": "USD"}
Thought: The account balance is $150.00, which is sufficient for the $40.00 refund.
Action: execute_refund(amount=40.00)
```

By grounding thought in real-world observations, ReAct prevents epistemic drift and enables the agent to recover from unexpected errors.

#### 3. Tree of Thoughts (ToT): search over reasoning steps

ReAct and CoT explore only a single linear path. If the model makes a poor decision early on, it cannot easily back up.

**Tree of Thoughts** (Yao et al., 2023) frames language generation as a formal state-space search:
- A "thought" is a coherent semantic unit (such as a single algebraic manipulation or a candidate code modification).
- At each state, the model proposes multiple alternative candidate thoughts.
- A heuristic evaluator (either the LLM itself prompted with a scoring rubric or an external validator) scores each candidate branch.
- Standard search algorithms (Breadth-First Search, Depth-First Search, or A*) traverse the tree, pruning unpromising branches and backtracking when dead ends are detected.

On complex combinatorial problems like the Game of 24, standard GPT-4 achieved a 7.3% success rate with standard CoT, while Tree of Thoughts with BFS achieved 74%.

### Can LLMs plan autonomously? The PlanBench reality check

Despite impressive demonstration videos, empirical studies lead by Subbarao Kambhampati and colleagues demonstrated that LLMs alone struggle with autonomous planning.

In **PlanBench** (Valmeekam et al., 2022, 2023), language models were evaluated on classical planning benchmarks including Blocksworld, Logistics, and Gripper:

1. **Standard Blocksworld:** When prompted with natural language descriptions of standard blocks (`A`, `B`, `C`), leading frontier models generated valid plans only 30% to 60% of the time on plans longer than 4 steps.
2. **Mystery Blocksworld:** To test whether models were truly planning or simply retrieving memorized patterns from internet tutorials, researchers obfuscated domain names:
   - "block" was renamed to "province".
   - "table" was renamed to "ocean".
   - "stack" was renamed to "subjugate".
   - "clear" was renamed to "unoccupied".

The underlying transition graph and logical preconditions remained mathematically identical. Yet under obfuscation, LLM plan accuracy plummeted to **near 0%**. The models routinely attempted to stack blocks that were already covered by another block, or picked up objects when the robot gripper was already holding something.

**Core research takeaway:** Large language models are exceptional **idea generators and intuitive pattern recognizers**, but poor **deterministic constraint satisfiers**.

### Hybrid architectures with classical verifiers

Recognizing these complementary strengths and weaknesses, researchers developed hybrid neurosymbolic systems that combine the natural language fluency of LLMs with the formal guarantees of classical planners.

#### LLM+P: translating to formal planners

Introduced by Liu et al. (2023), **LLM+P** delegates the actual planning to a verified domain-independent planner:

```text
Natural Language Task Description
           ↓ (LLM Prompting)
PDDL Problem Specification (.pddl)
           ↓ (Fed into Fast Downward planner)
Sound, Optimal Action Plan (Provably correct)
           ↓ (LLM Translation)
Natural Language Execution Plan
```

Because writing a PDDL problem definition is a static syntax translation task rather than a combinatorial search over exponential trees, the LLM excels. The classical planner (e.g., Fast Downward) then finds the optimal plan in milliseconds with 100% mathematical guarantees.

#### LLM-Modulo frameworks: external verifiers in the loop

Kambhampati et al. (2024) formalized the **LLM-Modulo framework**:
1. An LLM acts as an unconstrained candidate generator, proposing action sequences or design drafts.
2. An **external sound verifier** (such as the VAL plan validator, a compiler, a test suite, or a formal SAT/SMT solver like Z3) checks the candidate against domain rules.
3. If constraints are violated, the verifier returns exact, localized failure diagnostics (e.g., *"Action `stack(B, C)` failed because `clear(C)` was false at step 3"*).
4. The LLM consumes the diagnostic feedback and refines its proposal.

This mirrors how human software engineers work: the engineer (generator) drafts code, the compiler and test suite (verifiers) enforce soundness, and the engineer refines until tests pass.

### Test-time compute scaling and modern reasoning models

The release of modern reasoning models (such as OpenAI o1/o3 and DeepSeek-R1) marks the convergence of reinforcement learning and test-time search:

- Rather than requiring hand-crafted tree-search harnesses (like Tree of Thoughts), reasoning models are trained with reinforcement learning against verifiable rule-based rewards (unit tests and symbolic math).
- The model autonomously learns to emit internal reasoning tokens representing trial plans, checks for edge cases, self-corrections, and backtracking within its hidden or `<think>` scratchpad.
- **Test-time compute scaling laws:** Increasing the number of reasoning tokens spent at inference time consistently improves benchmark performance across competitive programming and mathematics.

However, reasoning models do not eliminate the value of classical planners:
- Running an LLM through 10,000 reasoning tokens costs significant money and seconds of latency.
- A classical A* planner or Fast Downward solves equivalent symbolic tasks in 2 milliseconds on a single CPU core with zero financial cost and mathematical guarantees against hallucinations.
- Production agent architectures leverage both: using reasoning LLMs for ambiguous real-world understanding, and offloading deterministic sub-problems to classical solvers.

### Python implementation: an LLM-modulo plan verifier loop

Here is a minimal demonstration of an LLM-Modulo loop for Blocksworld, using an explicit symbolic state simulator as the verifier:

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class WorldState:
    on: dict[str, str]           # block -> block or "table"
    clear: set[str]              # blocks with nothing on top
    holding: Optional[str] = None # block currently in hand

    def clone(self) -> "WorldState":
        return WorldState(
            on=dict(self.on),
            clear=set(self.clear),
            holding=self.holding
        )

class SymbolicBlocksworldVerifier:
    """A sound deterministic verifier that validates action sequences."""

    @staticmethod
    def execute_plan(initial_state: WorldState, plan: list[str]) -> tuple[bool, Optional[str], WorldState]:
        state = initial_state.clone()

        for step_idx, action_str in enumerate(plan):
            parts = action_str.strip().split()
            cmd = parts[0].lower()

            if cmd == "pick-up":
                # pick-up X (from table)
                x = parts[1]
                if state.holding is not None:
                    return False, f"Step {step_idx}: Hand is not empty, already holding {state.holding}", state
                if x not in state.clear or state.on.get(x) != "table":
                    return False, f"Step {step_idx}: Cannot pick up {x}; not clear or not on table", state
                state.clear.remove(x)
                del state.on[x]
                state.holding = x

            elif cmd == "stack":
                # stack X Y
                x, y = parts[1], parts[2]
                if state.holding != x:
                    return False, f"Step {step_idx}: Hand is not holding {x}", state
                if y not in state.clear:
                    return False, f"Step {step_idx}: Target {y} is not clear", state
                state.holding = None
                state.on[x] = y
                state.clear.remove(y)
                state.clear.add(x)

            else:
                return False, f"Step {step_idx}: Unknown action '{action_str}'", state

        return True, None, state

# Demonstration:
if __name__ == "__main__":
    init = WorldState(on={"A": "table", "B": "table"}, clear={"A", "B"}, holding=None)
    
    # An invalid plan that hallucinates picking up B while holding A
    flawed_plan = ["pick-up A", "pick-up B", "stack A B"]
    valid, err, _ = SymbolicBlocksworldVerifier.execute_plan(init, flawed_plan)
    print("Flawed Plan Valid?", valid, "| Diagnostic:", err)

    # A valid plan
    correct_plan = ["pick-up A", "stack A B"]
    valid, err, final_state = SymbolicBlocksworldVerifier.execute_plan(init, correct_plan)
    print("Correct Plan Valid?", valid, "| Final on relation:", final_state.on)
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) (Yao et al., 2022).
   - Review sections 1 to 3. Compare the ReAct loop against the agent loop you built in previous sections.
2. Read [Tree of Thoughts: Deliberate Problem Solving with Large Language Models](https://arxiv.org/abs/2305.10601) (Yao et al., 2023).
   - Analyze how candidate thoughts are evaluated and how search algorithms (BFS/DFS) manage memory and backtracking.
3. Read [LLM+P: Empowering Large Language Models with Optimal Planning Proficiency](https://arxiv.org/abs/2304.11477) (Liu et al., 2023).
   - Study how the model is prompted with in-context examples of PDDL problem definitions.
4. Read [LLMs Can't Plan, But Can Help Planning in LLM-Modulo Frameworks](https://arxiv.org/abs/2402.01817) by Subbarao Kambhampati and colleagues.
   - Note the distinction between generative approximate heuristics and sound model-based verifiers.
5. Review the [PlanBench](https://arxiv.org/abs/2206.10498) benchmark results.
   - Pay close attention to the Mystery Blocksworld experiments and the impact of symbol obfuscation on plan validity.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Chain-of-Thought Prompting Elicits Reasoning in Large Language Models](https://arxiv.org/abs/2201.11903): The foundational paper establishing test-time token scaling.
- [Self-Consistency Improves Chain of Thought Reasoning in Language Models](https://arxiv.org/abs/2203.11171): Wang et al.'s majority-voting sampling method.
- [On the Planning Abilities of Large Language Models: A Critical Investigation](https://arxiv.org/abs/2305.15771): Rigorous empirical analysis of LLM plan failure modes.
- [LLMs-Planning Benchmark Repository](https://github.com/karthikv792/LLMs-Planning): Open-source problem generators and evaluation scripts for PlanBench.

### Knowledge check

Use these questions to verify your understanding of LLM planning and reasoning:

1. [How does Chain-of-Thought prompting enable an autoregressive model to allocate dynamic compute to complex problems?](#the-evolution-of-reasoning-paradigms)
2. [What is the core difference between the ReAct paradigm and Tree of Thoughts in terms of search trajectories?](#the-evolution-of-reasoning-paradigms)
3. [What happened when PlanBench evaluated LLMs on "Mystery Blocksworld" with obfuscated terms, and what does this reveal about LLM planning?](#can-llms-plan-autonomously-the-planbench-reality-check)
4. [How does the LLM+P framework decouple the natural language interface from combinatorial plan generation?](#hybrid-architectures-with-classical-verifiers)
5. [In an LLM-Modulo architecture, where does the guarantee of plan correctness come from?](#hybrid-architectures-with-classical-verifiers)
