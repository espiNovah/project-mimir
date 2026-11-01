### Introduction

Research that is not communicated clearly has little impact. A technical breakthrough, a state-of-the-art benchmark result, or a novel theoretical insight will be overlooked or rejected by reviewers if the manuscript fails to convey why the problem matters, how the method functions, and where the evidence lies.

In academia, clear writing determines whether your paper is accepted to top-tier conferences (NeurIPS, ICML, ICLR, ACL). In research engineering and industry labs, it determines whether your architecture proposal is funded, built, and cited.

Good research writing is not an innate gift; it is a systematic craft with rigorous structural conventions.

This lesson explores:
1. Simon Peyton Jones's "Write to Think" methodology: drafting early as an experimental tool.
2. The rhetorical hourglass architecture of machine learning papers.
3. Formulating bulletproof, falsifiable contributions lists.
4. Visual storytelling and the paramount role of Figure 1.
5. Authoring with LaTeX and BibTeX.
6. The ethics of limitations and the craft of author rebuttals during peer review.

### Simon Peyton Jones on writing to think

Most junior researchers believe in a linear sequential process:
```text
Idea → Do Research → Collect Results → Write Paper
```
Computer scientist Simon Peyton Jones (Microsoft Research / Cambridge) famously argued that this sequence is backwards. The true scientific workflow is:
```text
Idea → Write Draft → Uncover Flaws & Gaps → Do Experiments → Refine Paper
```

![The Scientific Paper Hourglass: Rhetorical Architecture and Flow](assets/images/paper_structure_funnel.svg)

#### Why early drafting transforms research quality

- **Writing uncovers missing experiments:** When you force yourself to write the Experiments section before running all your jobs, you immediately realize which baselines are missing, which ablations are mandatory, and which metrics are ambiguous.
- **One sharp idea is enough:** Papers that try to present three disjoint ideas confuse reviewers. A great paper possesses **one single, clear, defensible contribution** and defends it thoroughly.
- **Do not hoard the idea:** Explain your core idea on page 1. Do not withhold the punchline until page 6 like a mystery novel; academic readers scan impatiently and decide whether to reject within five minutes.

### The rhetorical hourglass structure

A scientific paper functions as an **hourglass**: it opens with broad contextual motivation, narrows to hyper-specific technical precision in the Method and Experiments, and broadens back out to field-wide implications in the Discussion:

#### 1. Title and abstract: the 4-sentence formula

The abstract must be a self-contained miniature paper (roughly 150–200 words) answering four questions:
1. **Context:** What is the state of the world, and why does this problem matter?
2. **Problem/Gap:** What is the critical failure mode or limitation of existing approaches?
3. **Core Insight:** What is our proposed method, and what is the key intuition behind it?
4. **Headline Result:** What quantitative result did our method achieve on the target benchmark?

#### 2. The introduction and the contributions list

The introduction must establish the narrative stakes. It culminates in the most critical paragraph in the manuscript: the **explicit contributions list**.

Each contribution bullet point must be **specific, factual, and falsifiable**:
- *Weak:* "We explore agentic memory architectures." (Vague, non-falsifiable).
- *Weak:* "We show that our agent is better." (Better than what? By how much?).
- *Strong:* "We introduce a hierarchical memory stream combining recency, importance, and dense retrieval, reducing retrieval latency by 42% while matching full-context pass@1 on SWE-bench Lite (Section 4.2)."

#### 3. Related work: positioning, not listing

Do not write Related Work as an alphabetical bibliography summarizing papers in isolation (*"Smith et al. did X. Jones et al. did Y."*).

Instead, **group prior work by paradigm and contrast directly**:
- *"While prior retrieval architectures (e.g., Lewis et al., 2020) rely on static BM25 or bi-encoder embeddings, they fail to account for temporal decay in interactive agent sessions. In contrast, our approach introduces an exponential recency discounting factor..."*

#### 4. Method: reproducible formalization

The method section must provide sufficient mathematical and algorithmic detail for an independent researcher to re-implement your system without looking at your source code.
- Define notation in a dedicated table or paragraph before using it.
- Include a high-level architectural diagram or formal pseudocode block.

#### 5. Experiments: headline tables and ablations

Structure the empirical evaluation logically:
1. **Experimental Setup:** Datasets, evaluation metrics, model checkpoints, and compute environment.
2. **Main Comparative Results:** A clean summary table comparing your method against all competitive baselines. Bold the best result only when the margin is statistically significant.
3. **Ablation Studies:** Systematically disable components one by one to validate the causal source of improvement.
4. **Error Analysis:** Analyze where and why your method failed; qualitative extracts of failure modes demonstrate scientific honesty and guide future research.

#### 6. Limitations and broader impacts

Reviewers will actively look for where your method breaks down. If you hide its limitations, reviewers will uncover them and suspect dishonesty. If you state them plainly in a dedicated Limitations section, you build credibility:
- State compute constraints, domain boundaries, sensitivity to hyperparameters, and potential failure modes openly.

### Visual storytelling: the primacy of Figure 1

Many reviewers skim Figure 1 and the main results table before reading a single sentence of prose:

- **The Self-Contained Figure 1 Rule:** Figure 1 should convey the entire thesis of the paper: the problem, your proposed architecture, and a mini-plot showing the headline result.
- **Informative Captions:** Never write a generic caption like *"Figure 1: Overview of our system."* Write a complete narrative caption:
  > *"Figure 1: Architecture of AgentX. Left: Incoming user tickets are decomposed by the planner into sub-goals. Center: Ephemeral tools execute in isolated sandboxes. Right: On SWE-bench Lite, AgentX achieves 34.2% pass@1, outperforming baseline ReAct by +8.4% while using 30% fewer tokens."*
- **Vector Graphics Only:** Always export figures as vector PDF or SVG. Rasterized PNG or JPEG screenshots with blurry fonts will instantly alienate reviewers.

### Authoring in LaTeX and Overleaf

LaTeX is the universal typesetting standard for academic computer science. Top venues (NeurIPS, ICML, ICLR, CVPR, ACL) provide official LaTeX document classes (`.sty` and `.cls` files).

#### Minimal conference workshop template structure

```latex
\documentclass{article}
\usepackage{neurips_2024}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{hyperref}

\title{AgentX: Verifiable Planning via Neurosymbolic Feedback}
\author{Alex Rivera \quad Jordan Vance \\ Department of Computer Science \\ University of Mímir}

\begin{document}
\maketitle

\begin{abstract}
Autonomous language agents frequently hallucinate action preconditions in combinatorial tasks. 
We propose AgentX, an LLM-Modulo architecture that pairs autoregressive plan proposals with 
a sound classical PDDL verifier. On 100 Blocksworld instances, AgentX eliminates precondition 
violations entirely, raising task completion from 41.0\% to 92.0\% with zero increase in parameter scale.
\end{abstract}

\section{Introduction}
Autoregressive language models excel at natural language translation but struggle with formal 
combinatorial search~\cite{valmeekam2023planning}. In this paper, we demonstrate that pairing 
an LLM with a sound symbolic verifier resolves this limitation.

Our key contributions are:
\begin{itemize}
    \item We formalize the LLM-Modulo verification loop for interactive agent environments (Section~\ref{sec:method}).
    \item We evaluate AgentX on 60 Blocksworld instances, achieving a 92.0\% pass rate against a 41.0\% baseline (Section~\ref{sec:experiments}).
    \item We release our benchmark harness and verification logs under an open license.
\end{itemize}

\section{Method}\label{sec:method}
Let $\mathcal{S}$ denote the state space and $\mathcal{A}$ denote available actions. 
The agent optimizes expected return while satisfying formal constraints:
\begin{equation}
    \max_{\theta} \mathbb{E}_{\tau \sim \pi_\theta} \left[ R(\tau) \right] \quad \text{s.t.} \quad \mathcal{V}(\tau) = 1
\end{equation}

\bibliography{references}
\bibliographystyle{plainnat}
\end{document}
```

### Navigating peer review and writing rebuttals

At conferences like ICLR or NeurIPS, papers undergo double-blind peer review followed by an **author rebuttal period**.

#### How to write an effective rebuttal

1. **Be Dispassionate and Courteous:** Reviewers may misunderstand your work or issue unfair critiques. Never argue aggressively or express offense. Begin by thanking the reviewer for their constructive engagement.
2. **Address Every Concern Directly:** Organize your response point-by-point, quoting each specific reviewer question.
3. **Bring New Data, Not Adjectives:** If a reviewer asks *"How does this perform on larger models?"*, do not merely argue that it probably works. Run the experiment on the larger model, report the exact numbers in the rebuttal, and state that the results have been incorporated into the revised manuscript.
4. **Distinguish Clarifications from Real Weaknesses:** If a reviewer was confused, acknowledge that the original prose was ambiguous and specify exactly how the text in Section 3 has been revised to eliminate ambiguity.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Watch Simon Peyton Jones's classic lecture [How to Write a Great Research Paper](https://www.youtube.com/watch?v=VK51E3gHENc) (Microsoft Research).
   - Review his slides and summary on the official [Microsoft Research talk page](https://www.microsoft.com/en-us/research/academic-program/write-great-research-paper/).
   - Summarize his seven key recommendations in your notes.
2. Complete Overleaf's [Learn LaTeX in 30 minutes](https://www.overleaf.com/learn/latex/Learn_LaTeX_in_30_minutes) and review the [Mathematical expressions guide](https://www.overleaf.com/learn/latex/Mathematical_expressions).
3. Review [Troubling Trends in Machine Learning Scholarship](https://arxiv.org/abs/1807.03341) (Lipton & Steinhardt) and check that your own writing avoids "mathiness" and anthropomorphic speculation.
4. Inspect the introductions and Figure 1 designs of two seminal papers from [The Agentic AI Reading List](#/lesson/research/research_skills/agentic_ai_reading_list) (e.g., ReAct and SWE-agent).
   - Trace how Figure 1 visualizes the core contribution, and locate the exact table supporting each bullet in the contributions list.
5. Practice: Take the experimental results from one of your prior projects (such as [LLM vs Classical Planner](#/lesson/research/planning/project_llm_vs_classical_planner) or [Negotiation Arena](#/lesson/research/multi_agent_theory/project_negotiation_arena)). Draft a 2-page workshop-style conference paper in Overleaf containing:
   - A 4-sentence abstract.
   - An introduction with an explicit 3-bullet contributions list.
   - A publication-ready vector plot with error bars and a self-contained caption.
   - A candid Limitations section.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Matplotlib Publication Settings Guide](https://matplotlib.org/stable/): Recommended dpi, font size, and vector output settings for academic figures.
- [arXiv Submission Documentation](https://info.arxiv.org/help/submit/index.html): Official formatting, TeX engine, and license guidelines for posting preprints.
- [George Whitesides' Group: Writing a Paper](https://onlinelibrary.wiley.com/doi/10.1002/adma.200400767): Classic essay on paper outlining from Harvard chemistry professor George Whitesides.

### Knowledge check

Use these questions to verify your understanding of writing up research:

1. [Why does Simon Peyton Jones advocate drafting the research paper before completing the experiments?](#simon-peyton-jones-on-writing-to-think)
2. [What are the four components of the 4-sentence abstract formula?](#the-rhetorical-hourglass-structure)
3. [What criteria distinguish a strong, falsifiable contributions list from a weak summary?](#the-rhetorical-hourglass-structure)
4. [What is the "Self-Contained Figure 1 Rule," and why is it critical for skimming reviewers?](#visual-storytelling-the-primacy-of-figure-1)
5. [What is the most effective rhetorical strategy when responding to critical reviewer feedback during a conference rebuttal?](#navigating-peer-review-and-writing-rebuttals)
