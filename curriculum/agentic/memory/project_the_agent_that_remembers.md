### Introduction

The agent you built in Project: Agent Loop From Scratch forgets everything when it exits, and it falls over once a task outgrows its context window. In this project you will fix both. You will extend that same agent so it can finish a task too big for a single context window by working across several sessions, keeping a progress file it reads at the start and updates at the end, managing its context as it goes, and remembering facts about its user from one run to the next.

Then you will prove it helped. You will run the same long task with and without your memory features and report the difference in tokens used and whether the task actually got finished.

### Before you start

- Keep working in your `mimir-agent-loop` repository on a new branch, or fork it into a new repository named `mimir-agent-that-remembers`. Either way, the original loop, tools and traces should still work.
- Choose one long task that genuinely does not fit in one context window with your current agent. Good options:
  - Summarize every file in a folder of 40 or more long documents (for example, public-domain book chapters from Project Gutenberg, or a set of long articles) into a single structured report.
  - Research and write a 10-section report where each section needs several web searches.
  - Build a small command-line app with 8 to 10 features, if your agent has safe file and code tools.
- Write down a clear definition of "done" for the task that code can check, such as "the report has all 40 entries, each with a title and a summary under 100 words." You will need it to measure completion.
- Reread Effective harnesses for long-running agents before you start.

### Assignment

<div class="lesson-content__panel" markdown="1">

#### Step 1: Measure the baseline

1. Run the long task with your original agent (no memory features) at least once. Record total input and output tokens, number of steps, cost, why the run ended and how much of the task was completed according to your definition of done. Save the trace.

#### Step 2: Sessions and progress files

1. Add an initializer session that breaks the task into a checklist file (for example, `state/tasks.json`, with an `id`, a description and a `done` field for each item) and creates a `state/PROGRESS.md` file.
1. Every later session must read the progress file and task list at the start, work on a small number of unfinished items, verify each one with a code check before marking it done, and update the progress file at the end with what was finished, what is next and any problems.
1. Write a small runner that starts sessions one after another until the task list is complete or a session budget (for example, 10 sessions) is reached. Each session must start with a fresh conversation; only the files carry over.

#### Step 3: Context management

1. Within each session, track input tokens on every turn. When they cross a threshold you choose and justify, either compact the conversation (summarize older turns and keep the most recent ones) or clear old tool results. You may use your provider's built-in compaction or context editing, or write your own.
1. Log every time compaction or clearing happens, and how many tokens it saved.

#### Step 4: Long-term user memory

1. Add a way for the agent to save facts about the user (for example, preferred output format, name, topics they care about) to a separate file such as `memory/user.json`, through `remember` and `recall` tools or a similar design.
1. Show that a fact learned in one run is loaded and applied in a completely new run.
1. Keep memory writes inside the memory folder only, refuse paths outside it, and test that refusal.

#### Step 5: Report

1. Run the same long task with the full memory-enabled agent. Record the same measures as in Step 1, plus the number of sessions and the number of compactions.
1. Write a before and after table in your README: total tokens, peak tokens in a single request, cost, sessions, steps and percent of the task completed.
1. Explain what made the difference, and describe at least one problem you hit (for example, a summary that dropped an important detail, or the agent marking something done that was not) and how you fixed it.
1. Push your project to GitHub with a README that explains what it does, how to run it, and what you learned.

#### Extra credit

- Use Git inside the agent's workspace: commit after every verified item, and show the agent recovering from a deliberately broken state by reading the log and rolling back.
- Compare two context strategies (for example, compaction versus clearing tool results) on the same task and report which one finished with fewer tokens.
- Add a memory review step that removes stale or conflicting user facts, and show it working.
- Run sessions with a subagent that does the heavy reading and returns only a short summary, and measure the effect on the main agent's context.

</div>

### Submitting your work

The before and after table is the centerpiece. A reviewer should see clearly that the baseline ran out of room or stopped early, and that your version finished, with the token and cost numbers to back it up. Commit the state files from a finished run (`tasks.json`, `PROGRESS.md` and the user memory file) so readers can see what the agent wrote for itself, and link to traces that show a session starting by reading its notes and a compaction happening mid-session. A short diagram of the session cycle (read notes, work, verify, update notes, commit) makes the design easy to grasp at a glance.
