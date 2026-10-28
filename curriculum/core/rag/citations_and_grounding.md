<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Retrieving the right passages is only half the job. The model still has to answer from those passages, show where each claim came from, and admit when the documents do not contain the answer. An answer that sounds confident but cannot be traced to a source is worse than no answer, because users cannot tell when to trust it. This lesson covers *grounding* (keeping answers tied to sources) and *citations* (showing the sources), the features that make a RAG system trustworthy.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What grounding means and why retrieval alone does not guarantee it.
- How to format retrieved passages so the model can cite them.
- How to prompt for answers that use only the provided sources.
- How native citation features return verifiable quotes.
- How to make the model say "I don't know."
- How to check citations with code.

### Key ideas

- **Retrieval does not stop hallucination by itself.** A model given passages can still blend them with its training knowledge, misread them, or fill gaps with plausible guesses (see the Why Models Hallucinate lesson). Grounding is something you design for and check, not something you get for free.
- **Label every passage so it can be cited.** Put each retrieved chunk in tags with an ID and its source, for example `<source id="3" title="Refund policy">…</source>`. Ask the model to cite the IDs that support each claim. Your interface can then link each citation to the original passage.
- **Instruct the model to stay inside the sources.** Say explicitly that answers must rely only on the provided documents, that every factual claim needs a citation, and what to say when the documents do not cover the question. Asking the model to extract relevant quotes first and answer from them, as in the long-context lesson, makes this more reliable.
- **Native citations return exact spans.** Claude's citations feature lets you pass documents and get back answers whose claims are linked to the exact quoted text in your documents. Because the quotes come straight from the source, they are guaranteed to exist in it. Other providers offer similar features; when one is not available, prompt for quotes and verify them yourself.
- **"I don't know" is a feature.** Give the model explicit permission and a specific phrase to use when sources are insufficient, and test it with questions your documents cannot answer. You can also refuse before calling the model when the best retrieval score is below a threshold you tuned.
- **Verify citations with code.** Check that every cited ID was actually retrieved and that any quoted text appears in the source (after normalizing whitespace). Flag or drop answers that fail. These checks are cheap and catch a surprising number of problems.
- **Faithfulness is measurable.** Whether an answer is supported by its sources, called *faithfulness*, is one of the core metrics you will compute in the Evals section.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Citations](https://platform.claude.com/docs/en/build-with-claude/citations) in the Claude docs.
   - Read how to enable citations on documents, the shape of the citation objects in the response, and the notes on chunking documents for citations. Run the first example yourself.
1. Read the sections on long documents and on reducing hallucinations in [Anthropic's prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices).
   - Note the advice to ground answers in quotes and to let the model say it does not know.
1. Complete chapter 8 ("Avoiding Hallucinations") of [Anthropic's interactive prompt engineering tutorial](https://github.com/anthropics/prompt-eng-interactive-tutorial).
   - As before, use a current model ID and follow current docs where they differ.
1. Practice: connect your hybrid retrieval from the last lesson to a model. Write a prompt that requires a citation for every claim and a fixed phrase when the answer is not in the sources. Test it with ten answerable questions and five unanswerable ones. Write a function that checks every cited ID was retrieved, and count how often the model correctly refused the unanswerable questions.

</div>
