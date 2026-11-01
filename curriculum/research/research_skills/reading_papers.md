> [!TIP]
> **Prerequisite track:** This lesson is part of the Research Track and assumes you have completed [ML Foundations](#/path/ml).

### Introduction

Between 200 and 500 new artificial intelligence preprints are posted to arXiv every single day. No researcher can read them all, and attempting to do so leads to information overload, superficial skimming, and intellectual exhaustion.

Senior researchers do not read every paper from beginning to end. Instead, they employ systematic filtering funnels:
1. They triage papers rapidly, investing minutes to decide whether a paper warrants hours.
2. They read critically, distinguishing between substantiated empirical findings and marketing rhetoric.
3. They track citation networks and community reviews to separate foundational breakthroughs from ephemeral noise.

This lesson teaches S. Keshav's classic three-pass reading method, dissects the standard anatomy of an AI research paper, surveys the common methodological pitfalls identified by Lipton & Steinhardt, and provides a structured framework for building an enduring personal research knowledge base.

### The anatomy of a machine learning paper

Peer-reviewed machine learning papers adhere to a predictable rhetorical structure:

```text
Section                   Core Scholarly Purpose
-----------------------------------------------------------------------------------------------------
Abstract                  Self-contained 200-word summary: context, problem, core idea, key metric result.
Introduction              Motivation, why existing solutions fail, and the explicit list of claimed contributions.
Related Work              Situates the paper in the academic landscape; delineates how this work differs from prior art.
Method                    Formal mathematical problem formulation, architectural diagrams, algorithms.
Experiments & Results     Empirical testbeds, baseline comparisons, headline numbers, ablations, error analysis.
Limitations & Discussion  Where the method fails, unaddressed edge cases, safety implications, future research.
```

When evaluating a paper, the most critical paragraph is the **contributions list** at the end of the Introduction (typically phrased as: *"In summary, our key contributions are threefold..."*). This is the contract the authors establish with the reader. Every experiment in the paper exists solely to prove or disprove those claimed contributions.

### The three-pass reading method

In his influential guide *How to Read a Paper* (2007), Prof. S. Keshav formalized a three-pass approach to academic reading:

![S. Keshav's Three-Pass Method for Reading Research Papers](assets/images/three_pass_reading_workflow.svg)

#### Pass 1: The bird's-eye view (5 to 10 minutes)

The goal of the first pass is triage: to understand the broad scope and decide whether to invest further time.
1. Read the title, abstract, and introduction carefully.
2. Read the section and sub-section headings to understand the logical flow.
3. Glance over the figures, diagrams, and table captions.
4. Read the conclusion.
5. Scan the references, mentally noting any familiar authors or landmark papers.

At the end of Pass 1, you must be able to answer **Keshav's 5 Cs**:
- **Category:** What type of paper is this? (An empirical benchmark? A new algorithm? A theoretical proof? A systems paper?)
- **Context:** Which existing papers does this work build upon or contradict?
- **Correctness:** Do the assumptions appear plausible on the surface?
- **Contributions:** What are the paper's main claimed advances?
- **Clarity:** Is the manuscript well-written and structured?

*Rule of thumb:* Approximately 90% of papers you encounter should stop after Pass 1.

#### Pass 2: Grasping the content (~1 hour)

In the second pass, read the paper thoroughly:
- Follow the argument from start to finish, but skip detailed proofs, obscure hyperparameter tables, or complex mathematical derivations.
- Scrutinize the figures and graphs: look closely at the axis scales (linear vs. logarithmic), error bars, and labels. Did the authors truncate the y-axis to exaggerate a tiny 0.5% gain?
- Mark unread references and unfamiliar terminology for follow-up reading.

At the end of Pass 2, you should be able to explain the core idea of the paper to a colleague from memory. Approximately 9% of papers warrant Pass 2.

#### Pass 3: Deep mastery and virtual recreation (3 to 5 hours)

The third pass is the key to becoming a true domain expert. The goal is to **virtually recreate the paper in your mind or in code**:
- Assume you are the author. Starting from the problem statement, derive the formulas yourself before reading the authors' steps.
- Re-implement the core algorithm in Python from scratch.
- Identify the unstated assumptions: what happens when data is out-of-distribution? What happens if the batch size is halved? Where does the method fail?

Only the top 1% of papers—the seminal foundations of your specific thesis or production system—warrant Pass 3.

### Critical reading: auditing claims against evidence

A published paper is not infallible truth; it is an argument submitted to the scientific community. When reading, treat every claim as a hypothesis that the experimental section must prove.

#### Lipton and Steinhardt's troubling trends (2018)

In *"Troubling Trends in Machine Learning Scholarship"*, Zachary Lipton and Jacob Steinhardt identified four prevalent failure modes in AI research:

1. **Failure to Isolate the Source of Gains:** An author introduces a complex new architecture with five novel components and reports higher accuracy. Did the new mathematical idea produce the gain, or was it simply better hyperparameter tuning, a different learning rate schedule, or an unmentioned data augmentation trick? Look for **controlled ablation studies** that remove each component one by one.
2. **"Mathiness":** The use of excessive, dense formal mathematical notation that does not derive formal proofs or clarify intuition, but instead serves to intimidate reviewers and disguise empirical heuristics as fundamental theory.
3. **Conflating Explanation with Speculation:** Stating speculative intuitions as empirical facts (e.g., claiming a network *"learned semantic disentanglement"* without conducting probing experiments to verify it).
4. **Misuse of Language:** Using evocative anthropomorphic terms (e.g., claiming an agent *"understands"*, *"believes"*, or *"plans"*) to overstate capabilities beyond what the mathematical objective justifies.

#### Common experimental red flags

When auditing the experiments section, watch for these warning signs:
- **Weak or Untuned Baselines:** Did the authors compare their carefully tuned model against an off-the-shelf baseline running default hyperparameters?
- **Missing Variance and Seeds:** Are results reported as a single point estimate (e.g., *"Our model scored 82.4%"*) without standard deviations across multiple random seeds?
- **Cherry-Picked Qualitative Outputs:** Does the paper showcase three brilliant dialogue transcripts without providing automated statistical evaluations across hundreds of unseen test cases?
- **Dataset Contamination:** Did the evaluation dataset leak into the pretraining web crawl or SFT mixture?

### Literature discovery and tracking tools

Building a sustainable research habit requires mastering modern discovery tools:

- **arXiv Listing Categories:**
  - `cs.AI` (Artificial Intelligence)
  - `cs.LG` (Machine Learning)
  - `cs.CL` (Computation and Language)
  - `cs.MA` (Multiagent Systems)
- **Hugging Face Papers:** The modern community curation hub (replacing Papers with Code), featuring daily upvoted preprints linked directly to open-weight models, datasets, and code repositories.
- **Semantic Scholar & Connected Papers:** Tools for exploring citation topology:
  - *Backward Search:* Who did this paper cite? (Foundational roots).
  - *Forward Search:* Who cited this paper since publication? (Modern descendants and critiques).
- **OpenReview:** Public repository of reviewer discussions, rebuttals, and author revisions for top conferences (ICLR, NeurIPS). Reading negative reviews of popular papers is the fastest way to learn how elite researchers spot methodological flaws.

### A researcher's reading log template

Maintain a personal markdown research log (e.g., in a git repository or Obsidian vault) with a dedicated entry for every paper read past Pass 1:

```markdown
# [Paper Title]
**Authors:** [Author list] | **Year:** [Year] | **Link:** [arXiv URL]

### 1. Problem & Core Idea
- What exact problem does this paper address?
- What is the key hypothesis / insight in 1-2 sentences?

### 2. Method
- How is the system constructed? (Architecture, loss function, algorithm).

### 3. Key Evidence & Results
- What benchmarks were evaluated?
- What was the quantitative headline result compared to the primary baseline?
- Did the ablations conclusively validate the claimed source of improvement?

### 4. Doubts & Critique
- What was missing? (Untuned baselines, missing seeds, suspicious metrics).
- Where will this method fail in production?

### 5. Connection to My Work
- How does this inform what I am building?
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read S. Keshav's classic [How to Read a Paper](http://ccr.sigcomm.org/online/files/p83-keshavA.pdf) (2 pages).
2. Read [Troubling Trends in Machine Learning Scholarship](https://arxiv.org/abs/1807.03341) by Zachary Lipton and Jacob Steinhardt.
   - For each of the four troubling trends, formulate one explicit audit question to ask when reviewing future papers.
3. Set up your discovery workflow:
   - Browse the recent preprints on [arXiv cs.AI](https://arxiv.org/list/cs.AI/recent) and [cs.CL](https://arxiv.org/list/cs.CL/recent).
   - Explore [Hugging Face Papers](https://huggingface.co/papers) and examine the top-ranked paper of the week along with its linked repository.
   - Look up [ReAct](https://arxiv.org/abs/2210.03629) on [Semantic Scholar](https://www.semanticscholar.org/) and identify three subsequent papers that extended its paradigm.
4. Practice Keshav's method: Select one landmark paper from [The Agentic AI Reading List](#/lesson/research/research_skills/agentic_ai_reading_list).
   - Conduct Pass 1 and answer Keshav's 5 Cs.
   - Conduct Pass 2 and write a structured 1-page reading log following the template above, highlighting at least one questionable assumption or missing ablation.
5. Search [OpenReview](https://openreview.net/) for an accepted paper at a recent ICLR conference, read the official reviewer critiques and author rebuttals, and summarize the primary weaknesses identified during peer review.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [OpenReview](https://openreview.net/): Transparent academic peer review portal for leading AI venues.
- [Connected Papers](https://www.connectedpapers.com/): Visual graph visualization of academic citation networks.
- [alphaXiv](https://www.alphaxiv.org/): Interactive arXiv interface featuring open, line-by-line scholarly commentary.

### Knowledge check

Use these questions to verify your understanding of reading research papers:

1. [What is the explicit role of the contributions list in an AI paper's introduction, and how should it guide your reading?](#the-anatomy-of-a-machine-learning-paper)
2. [What are Keshav's 5 Cs answered during Pass 1, and what percentage of papers should stop after this pass?](#the-three-pass-reading-method)
3. [What is "mathiness" in machine learning literature, and why did Lipton and Steinhardt identify it as a troubling trend?](#critical-reading-auditing-claims-against-evidence)
4. [Why are ablation studies indispensable for validating the empirical claims of a new machine learning method?](#critical-reading-auditing-claims-against-evidence)
5. [What is the difference between backward citation search and forward citation search when mapping an unfamiliar research area?](#literature-discovery-and-tracking-tools)
