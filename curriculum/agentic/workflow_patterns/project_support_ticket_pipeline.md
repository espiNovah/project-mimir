### Introduction

Customer support is one of the most common places companies put LLMs to work, and one of the best places to learn workflow patterns, because the job naturally breaks into steps: figure out what the customer wants, look up the relevant policy, draft a reply and check it before it goes out. In this project you will build a support ticket pipeline using the three kinds of patterns from this section, and then do what professionals actually do: measure whether all that structure beats one well-written prompt.

You will build a router, a prompt chain with a code gate, and an evaluator-optimizer loop, run all of them on the same 20 tickets, and report accuracy, cost and latency side by side.

### Before you start

- Create a new GitHub repository named `mimir-support-pipeline` and set it up as a `uv` project with the `anthropic` package.
- Use the [cheap model](#/models) for routing and drafting. You may use the [capable model](#/models) for the evaluator if you want a stronger judge; record which model each step uses.
- Invent a small fictional company (for example, a meal-kit delivery service). Write a `policies.md` file with 8 to 12 short policies, each with an ID like `POL-REFUND-01` or `POL-SHIP-03`. Cover at least four categories, such as billing, shipping, account and technical issues.
- Write 20 sample tickets in `tickets.jsonl`. For each one, record the correct category and the policy ID or IDs a good reply should cite. Include a few tricky ones: a ticket that mixes two issues, an angry one, and one that fits no category.
- Reuse what you learned in the Evals section: these 20 labeled tickets are your eval set.

### Assignment

<div class="lesson-content__panel" markdown="1">

#### Step 1: The baseline

1. Write a single-prompt baseline: one model call that receives the ticket and the full `policies.md` and returns a category and a reply.
1. Run it on all 20 tickets and record, for each ticket, the category it chose, the reply, the policy IDs cited, the tokens used and the time taken.

#### Step 2: Routing

1. Write a classifier step that returns one category from a fixed list (plus `other`) as structured output.
1. Write a separate handler for each category, with a prompt that includes only the policies for that category. Tickets classified as `other` should get a polite handoff reply that says a human will follow up.
1. Report the classifier's accuracy against your labels.

#### Step 3: Prompt chain with a gate

1. Inside each handler, chain at least two steps: for example, first extract the customer's actual request and the relevant policy IDs, then draft the reply.
1. Add a programmatic gate between or after the steps: plain code that checks the draft cites at least one valid policy ID that exists in `policies.md`. If the check fails, retry the drafting step once with a note about what was missing; if it fails again, mark the ticket for human review.
1. Log how often the gate caught a problem.

#### Step 4: Evaluator-optimizer

1. Add an evaluator that scores each draft against a short rubric (for example: answers the actual question, follows the cited policy, polite tone, under 150 words) and returns structured feedback.
1. If the draft fails, send the feedback back to the drafting step and revise. Cap the loop at 3 iterations, and return the best-scoring draft if none pass.
1. Record how many iterations each ticket needed.

#### Step 5: Measure

1. Run the full pipeline on all 20 tickets. Score both the baseline and the pipeline on: category accuracy, whether the correct policy was cited, and rubric pass rate.
1. Produce a comparison table in your README with these columns at minimum: approach, category accuracy, correct-policy rate, rubric pass rate, average tokens per ticket, average cost per ticket and average latency per ticket. Include at least the baseline, the router plus chain without the evaluator, and the full pipeline.
1. Write a short conclusion: was the extra complexity worth it? Which pattern added the most value, and which added cost without much gain?
1. Push your project to GitHub with a README that explains what it does, how to run it, and what you learned.

#### Extra credit

- Run the three handlers' independent steps or the 20 tickets concurrently and report the change in total wall-clock time.
- Add a voting step to the classifier (three cheap calls, majority wins) and measure whether accuracy improves enough to justify the cost.
- Route hard tickets to a larger model and easy ones to a smaller model, and show the effect on cost.
- Write `pytest` tests for the gate and the iteration cap that do not call the model.

</div>

### Submitting your work

The comparison table is the heart of a strong submission. A reviewer should be able to see in one glance how each approach performed, what it cost and how long it took, with numbers you actually measured. Commit the raw results (for example, `results/baseline.jsonl` and `results/pipeline.jsonl`) so anyone can check your math. A clear diagram of the pipeline helps, and so does an honest conclusion: it is perfectly fine, and often realistic, to find that the baseline was nearly as good. Saying so with evidence is exactly the judgment employers want to see.
