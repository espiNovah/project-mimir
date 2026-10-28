<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Your capstone is the project you will talk about in every interview, so the problem you choose matters more than the technology. A clever agent that nobody needs is a weak portfolio piece. A simple agent that saves a real person two hours a week is a strong one. This lesson is about finding that person and that problem: talking to people, watching how they actually work, and picking a workflow that an agent can genuinely improve.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why a real user beats an imagined one.
- Where to find people with problems worth solving.
- How to run a user interview without leading the witness.
- How to spot a workflow worth automating.
- Deciding whether the problem needs an agent, a workflow or no AI at all.
- Scoping a problem you can finish in about 100 hours.

### Key ideas

- **Start with a person, not a technology.** "I want to build a multi-agent RAG system" is a solution looking for a problem. "My friend who runs a small bakery spends Sunday nights answering supplier emails" is a problem. Good places to look: your current or past job, friends' jobs, a club or nonprofit you belong to, a small local business, or an open-source project you use.
- **Ask about the past, not the future.** People are bad at predicting what they would use and very good at describing what they did last week. Ask "Tell me about the last time you did this. What took longest? What did you do when it went wrong?" Avoid pitching your idea or asking "Would you use an app that...?"; people say yes to be polite.
- **Watch the work if you can.** Ask to sit with someone while they do the task, or have them share their screen. You will see steps nobody mentions in interviews, like copying data between three browser tabs.
- **Look for the right shape.** Good capstone problems are repetitive, text-heavy and time-consuming, have a clear definition of "done well," and can tolerate a human checking the result. Pain that happens weekly beats pain that happens yearly.
- **Pick the simplest thing that works.** Revisit Workflows vs Agents. Many real problems are best solved by a fixed workflow with one or two model calls. Use an agent only where the steps genuinely can't be known in advance. A smaller, reliable system is a better capstone than an ambitious, flaky one.
- **Scope ruthlessly.** You have roughly 100 hours. Choose one workflow for one kind of user. You can always expand later; you can't get back time spent on features nobody asked for.
- **Get a commitment.** Before you build, confirm that your user (and ideally two or three others like them) will try your prototype and give you feedback. You will need at least three real users for the capstone project.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Watch Y Combinator's [How to Talk to Users](https://www.youtube.com/watch?v=z1iF1c8w5Lg), a short, practical guide to user interviews from Startup School.
   - Write down the questions it suggests asking and the mistakes it warns against.
1. Read Paul Graham's [Do Things That Don't Scale](https://paulgraham.com/ds.html) for why serving a handful of users very well is the right start.
   - Focus on the parts about recruiting your first users by hand.
1. Reread [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents), this time asking of each pattern: "Which real workflow I've seen would fit this?"
1. Practice: interview at least three people about a task they do repeatedly.
   - Keep notes for each interview: the task, how often they do it, how long it takes, what goes wrong and what "done well" looks like.
   - Pick one problem, and write a short paragraph explaining why it is worth solving, why AI helps, and whether it needs an agent or a workflow.
   - Get at least three people to agree to try your prototype once it exists.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [A Field Guide to Rapidly Improving AI Products](https://hamel.dev/blog/posts/field-guide/) explains why involving domain experts early makes AI products better, which applies directly to your capstone user.
