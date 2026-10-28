<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Hundreds of AI papers appear on arXiv every day. A researcher cannot read them all, and does not try to. Instead, they filter quickly, read a few papers deeply, and read critically, knowing that a polished paper can still have weak evidence. This lesson teaches a reading method, the tools researchers use to find and track papers, and the habits that keep you current without drowning.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The anatomy of a machine learning paper.
- The three-pass reading method.
- Reading critically: claims, evidence and missing baselines.
- Finding papers with arXiv, Hugging Face Papers and Semantic Scholar.
- Following citations backward and forward.
- Building a sustainable reading habit and note system.

### Key ideas

- **Papers follow a predictable structure.** Abstract, introduction (the problem and the claimed contributions), related work, method, experiments, discussion and limitations. The contributions list at the end of the introduction tells you what the authors think matters most, and the experiments are where you check whether it holds.
- **Read in three passes.** In S. Keshav's method, the first pass (5 to 10 minutes) reads the title, abstract, introduction, headings and conclusion to decide whether to continue. The second pass (about an hour) reads the paper carefully, looking at figures and tables, but skips proofs. The third pass re-creates the work in your head, or in code, and is how you find hidden assumptions. Most papers only deserve the first pass.
- **Read every claim as a hypothesis.** For each claim ask: what evidence supports it, compared with what baseline, over how many runs, and with what error bars? Watch for warning signs: comparisons against weak or untuned baselines, results on a single seed, cherry-picked examples, and vague words like "significantly" with no test behind them.
- **arXiv is where research appears first.** Most AI papers are posted to arXiv before, or instead of, peer review. The listing pages for cs.AI (artificial intelligence), cs.CL (computation and language) and cs.MA (multiagent systems) show the newest work. A preprint has not necessarily been reviewed, so judge the evidence yourself.
- **Use curators and graphs to filter.** Hugging Face Papers shows daily papers selected by the community, with links to code and models. (Papers with Code, long the standard place to find code for a paper, was shut down in 2025, and its address now redirects to Hugging Face.) Semantic Scholar shows who cites a paper and summarizes its influence. Following references backward and citations forward is the fastest way to map a new topic.
- **Keep notes you can search.** For each paper you read past the first pass, write a few lines: the problem, the method in one sentence, the key result, what you doubt, and how it relates to papers you know. A year of these notes becomes the related-work section of your thesis.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read S. Keshav's [How to Read a Paper](http://ccr.sigcomm.org/online/files/p83-keshavA.pdf), a two-page classic that introduces the three-pass method.
1. Read [Troubling Trends in Machine Learning Scholarship](https://arxiv.org/abs/1807.03341) by Zachary Lipton and Jacob Steinhardt, which names four common problems in ML papers: failing to separate explanation from speculation, failing to identify the source of gains, "mathiness," and misuse of language.
   - Read it in full. For each trend, write down one question you will now ask when reading a paper.
1. Set up your paper sources:
   - Bookmark the arXiv listings for [cs.AI](https://arxiv.org/list/cs.AI/recent), [cs.CL](https://arxiv.org/list/cs.CL/recent) and [cs.MA](https://arxiv.org/list/cs.MA/recent), and skim one day's titles in each.
   - Browse [Hugging Face Papers](https://huggingface.co/papers) for a week. Note which papers link to code.
   - Look up the [ReAct paper](https://arxiv.org/abs/2210.03629) on [Semantic Scholar](https://www.semanticscholar.org/) and find three highly cited papers that cite it.
1. Practice the three passes: choose one paper from The Agentic AI Reading List. Do a first pass and write five sentences (category, context, correctness, contributions, clarity, the "five Cs" from Keshav's paper). Do a second pass and write a one-page summary that includes one claim you think is weakly supported and why.
1. Start a reading log (a Markdown file in a GitHub repo is enough) using the note format from the key ideas. Add every paper you read during this track.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [OpenReview](https://openreview.net/) hosts the public reviews for major conferences such as ICLR and NeurIPS. Reading reviews of papers you know is one of the best ways to learn what reviewers look for.
- [alphaXiv](https://www.alphaxiv.org/) lets you read arXiv papers with public line-by-line discussion threads.
- [Connected Papers](https://www.connectedpapers.com/) draws a graph of papers related to one you choose, useful when starting a literature review.
