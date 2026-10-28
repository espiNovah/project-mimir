### Introduction

In this project you will run a controlled comparison: the same set of Blocksworld puzzles solved by your own BFS and A* search, by a classical PDDL planner, and by a language model, both on its own and inside a validator loop that feeds errors back to it. You will measure success rate, plan length, time and cost, then analyze how and why each method fails.

This is a small version of a real research question that papers such as PlanBench, LLM+P and the LLM-Modulo work have tried to answer. You will produce your own evidence instead of repeating someone else's claim. The validator-loop condition also teaches the most practical lesson of the section: when correctness matters, an agent's reliability comes from what checks its work.

### Before you start

- Create a new repo named `mimir-llm-vs-planner`. Set it up with `uv init` and add `unified-planning`, `up-fast-downward`, `anthropic`, `matplotlib` and `pytest` with `uv add`.
- [Unified Planning](https://unified-planning.readthedocs.io/en/latest/) reads PDDL, calls [Fast Downward](https://www.fast-downward.org/) through the `up-fast-downward` package, and includes a plan validator. If the Fast Downward wheel does not install on your machine, use [Pyperplan](https://github.com/aibasel/pyperplan) (`uv add pyperplan`), a pure-Python planner, instead.
- Use the standard 4-operator Blocksworld domain (`pick-up`, `put-down`, `stack`, `unstack`) you wrote in Search and Planning. Generate problem instances with the [PDDL generators](https://github.com/AI-Planning/pddl-generators) repo or write your own random generator. Fix the random seed so the instance set is reproducible.
- Set your `ANTHROPIC_API_KEY` environment variable. Use `claude-haiku-5-5` while developing and add `claude-sonnet-5-5` (or a model from another provider) for the final runs if your budget allows. Check current prices on the [Claude pricing page](https://platform.claude.com/docs/en/about-claude/pricing) and set a budget before you start, for example 10 US dollars. The [Batch API](https://platform.claude.com/docs/en/build-with-claude/batch-processing) is discounted and suits non-interactive runs like the single-shot condition (the validator loop needs ordinary calls, since each round depends on the last).
- Here is how to check an LLM's plan with Unified Planning. The validator tells you whether the plan is valid and, if not, which action could not be applied:

```python
from unified_planning.io import PDDLReader
from unified_planning.shortcuts import PlanValidator

reader = PDDLReader()
problem = reader.parse_problem("domain.pddl", "problems/bw-05-001.pddl")
plan = reader.parse_plan(problem, "plans/llm/bw-05-001.plan")  # one "(action args)" per line

with PlanValidator(problem_kind=problem.kind) as validator:
    result = validator.validate(problem, plan)

print(result.status)  # ValidationResultStatus.VALID or INVALID
print(result.reason, result.inapplicable_action)  # why it failed, if it did
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Build a benchmark of at least 60 Blocksworld instances: at least 15 each with 4, 6, 8 and 10 blocks. Store them as PDDL files in `problems/`.
1. Solve every instance with your own BFS and A* from Search and Planning (with a time limit per instance, such as 60 seconds) and with Fast Downward. Record for each instance and method: solved or not, plan length, number of states expanded (for your own searches) and wall-clock time.
1. Write an LLM planner that gives the model the domain and problem (as PDDL or as a clear natural-language description; pick one and justify it) and asks for a plan in a fixed format that your code parses. Run it on every instance with temperature and other settings fixed and saved in a config file.
1. Write an LLM-plus-validator planner. When the plan is invalid, send the validator's error back to the model (which action failed and why) and ask for a corrected plan, up to a fixed number of rounds such as 5. Record how many rounds each success needed.
1. Add an obfuscated condition in the style of PlanBench's Mystery Blocksworld: rename the predicates, actions and objects to meaningless words, keeping the structure identical, and rerun both LLM planners on at least the 4- and 6-block instances.
1. Validate every plan from every method with the same validator. Never count a plan as a success because the model said it was correct.
1. Track cost: log input and output tokens for every LLM call and compute the dollar cost per instance from the published prices. Stop if you reach your budget.
1. Produce a results table and at least two plots: success rate against number of blocks for every method, and cost or time per solved instance. Report plan length relative to the optimal plan (from A*) for solved instances.
1. Analyze failures. Read at least 15 failed LLM plans and sort them into categories you define, such as "violated a precondition," "goal not reached," "invalid format" or "loop." Report the count for each category, and show one example of each.
1. Push your project to GitHub with a README that explains what it does, how to rerun the whole benchmark, and what you learned. Write the README as a short research report: question, setup, results, failure analysis and limitations (for example, Blocksworld is one domain, and your instance sizes are small).

#### Extra credit

- Add an LLM+P condition: the model translates a natural-language description into a PDDL problem file, and Fast Downward solves it. Measure how often the translation, not the planner, is the point of failure.
- Compare a standard model with a reasoning model or extended thinking, and plot success against tokens spent.
- Add a second domain, such as Logistics or a grid navigation domain, and see whether the ranking of methods changes.
- Run each LLM condition three times and report confidence intervals for the success rates.

</div>

### Submitting your work

A strong submission treats this as an experiment, not a demo. All methods face the same instances and the same validator, settings are saved in config files, and the raw per-instance results are committed so anyone can regenerate the plots. The failure analysis is the most valuable part. Specific, counted categories with real examples tell a reader far more than a single success rate. Be careful with conclusions: "Haiku with a validator solved 92% of 8-block instances at 3 cents each" is a finding; "LLMs can plan" is not.
