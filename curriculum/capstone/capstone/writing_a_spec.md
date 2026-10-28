<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Before you write code for your capstone, you will write a spec: a short design document that says what you are building, for whom, how it will work and how you will know it succeeded. Writing it forces you to make decisions while they are still cheap to change. It also gives you something to measure against at the end, which is what turns "I built an agent" into "I built an agent that cut my user's task from 40 minutes to 10, measured over 30 runs."

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What a design doc is and why engineering teams write them.
- The sections of a one-page spec for an AI system.
- How to write measurable success criteria.
- Turning success criteria into an eval plan.
- Listing risks, non-goals and where humans stay in the loop.
- Getting feedback on a spec before you build.

### Key ideas

- **A spec is a thinking tool, not paperwork.** Teams at companies like Google write design docs to catch bad ideas before they cost weeks. Yours should fit on one or two pages. If you can't explain the system that briefly, it is too big for a capstone.
- **Use a standard shape.** Problem (who has it, how often, what it costs them today), goals and non-goals, the proposed design (a diagram and the main steps, and whether each step is a workflow or agent), data and tools needed, evaluation plan, risks and mitigations, and milestones.
- **Success criteria must be measurable.** "Helpful answers" can't be checked. "At least 85% of drafted replies accepted with minor or no edits by the user, over 30 real emails" can. Include at least one quality metric, one cost or latency budget (for example "under $0.05 and 20 seconds per task") and one user outcome such as time saved.
- **Know your baseline.** Measure how the task is done today, by hand or with existing tools. Without a baseline you can't show improvement.
- **The eval plan comes from the criteria.** For each success criterion, say how you'll test it: which cases, which code checks or judges, and what score counts as passing. Plan to seed the eval set from your interview notes and real examples from your user.
- **Name the risky actions.** List every action your system can take that would be hard to undo or embarrassing if wrong (sending messages, changing records, spending money), and say where a human must approve. Note the security risks from your Security Review lesson that apply.
- **Non-goals protect your schedule.** Writing "will not support multiple users' calendars" or "no mobile app" keeps scope creep out.
- **Share it before building.** Show the spec to your user and, if you can, to another engineer. Ask your user directly: "If it did this, would it actually help you?"

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read Malte Ubl's [Design Docs at Google](https://www.industrialempathy.com/posts/design-docs-at-google/) to understand why design docs exist and what goes in them.
   - Focus on the sections describing the anatomy of a design doc and when a doc is not worth writing.
1. Study Eugene Yan's [ml-design-docs template](https://github.com/eugeneyan/ml-design-docs), a free template for machine learning and AI system designs.
   - Read the README and the template. You will adapt it into a shorter spec for your capstone.
1. Reread the parts of the [LLM Evals FAQ](https://hamel.dev/blog/posts/evals-faq/) about choosing metrics and how many examples you need, so your eval plan is realistic.
1. Practice: write the spec for your capstone using the problem you picked in the previous lesson.
   - Include problem, goals and non-goals, design diagram, success criteria with numbers, baseline, eval plan, risky actions requiring approval, risks and milestones.
   - Commit it to your capstone repo as `SPEC.md`, then share it with your user and record their feedback at the bottom.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Building A Generative AI Platform](https://huyenchip.com/2024/07/25/genai-platform.html) by Chip Huyen is a useful map of components to consider when drawing your design diagram.
