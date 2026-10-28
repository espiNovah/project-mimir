### Introduction

You have read about the difference between workflows and agents. Now you will feel it. In this project you will hand-build the smallest agent loop you can, with nothing but the raw model API, and watch it think, act and observe one step at a time. Then you will step back and write a short decision memo that sorts five real tasks into "no LLM," "workflow" or "agent," with reasons.

The loop is deliberately tiny. The point is not to build something useful yet, but to see that an agent really is "a model using tools in a loop," and to practice the judgment call that comes before every agent project: does this task need one at all?

### Before you start

- Create a new GitHub repository named `mimir-workflow-or-agent` and set it up as a `uv` project (`uv init`, then `uv add anthropic`), just as you did in Project: Hello, uv.
- Make sure your API key is in the `ANTHROPIC_API_KEY` environment variable, as in Project: Terminal Chatbot. Never commit it.
- Use a cheap model such as `claude-haiku-5-5` for this project. Any provider with tool calling works the same way if you prefer another one.
- Pick one simple tool for your loop. Good choices: a calculator that evaluates basic arithmetic safely (parse the numbers and operator yourself; do not use Python's `eval`), a function that returns the current date and time, or a lookup in a small dictionary of facts you write yourself.
- You will need the list of five tasks you wrote in the Workflows vs Agents assignment.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Peek at the docs, not at solutions

You have not had the full tool-use lessons yet, and that is fine. The "Agents" section of Building Effective Agents and the first part of the Claude docs tutorial on building a tool-using agent show the shape of a tool call and a tool result. Try to write the loop yourself before looking at anyone's finished code.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

#### Part 1: The tiny loop

1. Write `loop.py`: a single-tool agent loop in 20 lines of code or fewer (blank lines and comments do not count), using the provider's SDK directly with no agent framework.
1. The loop must send the conversation to the model, check whether the model asked for the tool, run the tool, append the result to the conversation, and go around again.
1. It must have an explicit natural stop condition (the model replies without requesting a tool) and a hard `MAX_STEPS` cap, so it can never run forever. When the cap is hit, the program must say so instead of exiting silently.
1. Print every step in a readable form, labeled `THINK`, `ACT` and `OBSERVE`: the model's text, the tool name and arguments it requested, and the tool's result.
1. Run it on a task that needs at least two tool calls (for example, "What is 17% of 2,340, plus 15?") and save the full printed output as `sample_run.txt` in your repo.
1. Run it once with `MAX_STEPS` set to 1 on the same task and save that output as `capped_run.txt`, showing the cap working.

#### Part 2: The decision memo

1. Write `MEMO.md` classifying five real tasks (from your own life, job or a business you know) as **no LLM**, **workflow** or **agent**.
1. Include at least one task in each category.
1. For each task, give two or three sentences of reasoning: Is the path predictable? How many steps, and are they known in advance? What does a mistake cost? Could plain code do it?
1. For the task you labeled "agent," sketch the tools it would need and its stop conditions.

#### Part 3: What did it cost?

1. Using the token counts the API returns with each response (the `usage` field), add up the input and output tokens for your `sample_run.txt` run.
1. Using your provider's current pricing page, calculate the cost of that run in dollars. Show your math in the README.
1. Notice that input tokens grow on every step because the whole history is resent. In one or two sentences, estimate how the cost would change if the same task took 20 steps instead of 2.

1. Push your project to GitHub with a README that explains what it does, how to run it, and what you learned.

#### Extra credit

- Add a second tool and show, in a new sample run, the model choosing between them.
- Rewrite one of your "workflow" tasks from the memo as a real two-step prompt chain and compare its output and token use with running it through your loop.
- Make the loop stop on a cost budget (for example, "stop after $0.01") as well as a step cap.

</div>

### Submitting your work

A strong submission lets a reader understand the whole agent idea in two minutes. The README should link to `sample_run.txt` and show a short excerpt of it, so a reviewer can see the think, act, observe steps without running anything. It should state the line count of `loop.py`, point to `capped_run.txt` as proof the step cap works, and include the token and cost table with the math shown. The memo should read like advice to a manager: clear decisions, honest reasons, and at least one case where you decided an LLM was not needed at all.
