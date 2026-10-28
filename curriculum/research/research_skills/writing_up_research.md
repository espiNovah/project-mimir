<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Research that is not written up clearly has little effect. A paper, a thesis chapter or a workshop submission is how your work reaches other people, and in a master's program it is also how your work is graded. Good research writing is a learnable skill with clear conventions. This lesson covers how to structure a paper, how to make figures that carry the argument, how to write in LaTeX, and how to revise.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Writing the paper early, as a way of doing the research.
- The standard structure of an ML paper and what each section must do.
- Stating contributions precisely.
- Figures and tables that make the result obvious.
- Writing in LaTeX and Overleaf.
- Related work, limitations and honest framing.
- Revising, getting feedback and responding to reviews.

### Key ideas

- **Write to think.** Simon Peyton Jones's advice is to start writing before the research is finished. Drafting the paper shows you which claims lack evidence and which experiments you still need. A single, clear idea per paper is enough.
- **Each section has a job.** The abstract states the problem, the approach, the key result and why it matters. The introduction motivates the problem and lists specific, checkable contributions. The method section has enough detail to reimplement. Experiments state the setup, then the results, then what they mean. Limitations say plainly what the work does not show.
- **Contributions must be falsifiable.** "We propose X, which improves Y by Z on benchmark B" is a contribution. "We explore agent memory" is not. Every listed contribution should point to a section and a result that supports it.
- **Figures carry the argument.** Many readers look at Figure 1 and the main results table before reading anything else. Each figure should make one point, with labeled axes, units, error bars and a caption that states the takeaway. Tables should bold the best result only when the difference is meaningful.
- **LaTeX is the standard tool.** Conferences provide LaTeX templates, and Overleaf lets you write LaTeX in the browser for free. Learn the basics: sections, math, figures, tables, citations with BibTeX, and cross-references.
- **Related work positions, it does not list.** Group prior work by approach and say how yours differs from each group. Cite the papers you compare against, and describe them fairly.
- **Revision is most of writing.** Get feedback early from someone outside the project, cut anything that does not support the main claim, and check every number in the text against your results files. Reviews, even harsh ones, show you where readers get lost.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Watch Simon Peyton Jones's talk [How to Write a Great Research Paper](https://www.youtube.com/watch?v=VK51E3gHENc) (Microsoft Research). The slides and a summary are on [Microsoft Research's page for the talk](https://www.microsoft.com/en-us/research/academic-program/write-great-research-paper/).
   - Write down his seven suggestions and apply them in the practice item below.
1. Learn LaTeX with Overleaf's [Learn LaTeX in 30 minutes](https://www.overleaf.com/learn/latex/Learn_LaTeX_in_30_minutes) and its [guide to mathematical expressions](https://www.overleaf.com/learn/latex/Mathematical_expressions). Overleaf's free plan is enough for everything in this track.
1. Reread [Troubling Trends in Machine Learning Scholarship](https://arxiv.org/abs/1807.03341) from Reading Papers, this time as a checklist for your own writing.
1. Study the structure of two papers from The Agentic AI Reading List, such as ReAct and SWE-agent. For each, list the contributions from the introduction and find the figure or table that supports each one. Note how Figure 1 summarizes the paper.
1. Practice: write a 2-page workshop-style paper in LaTeX about one of your earlier Research Track projects (for example LLM vs Classical Planner or Negotiation Arena), using a conference template from Overleaf. Include an abstract, a contributions list, one main figure with error bars, a short related work section and a limitations paragraph. Ask someone to read it and tell you the main claim in one sentence. If they cannot, revise.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Matplotlib's documentation](https://matplotlib.org/stable/) covers the plot settings you need for publication-quality figures, such as vector output, font sizes and error bars.
- [arXiv's submission guide](https://info.arxiv.org/help/submit/index.html) explains how to post a preprint when you have something worth sharing.
