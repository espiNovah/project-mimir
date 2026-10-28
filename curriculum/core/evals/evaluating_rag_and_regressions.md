<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

A RAG system can fail in two places: it can retrieve the wrong passages, or it can answer badly from the right ones. If you only score the final answer, you cannot tell which part to fix. This lesson shows how to evaluate retrieval and generation separately, how evaluation tools like Ragas and promptfoo package common metrics, and how to run evals automatically so a prompt change that breaks something is caught before users see it. That last idea, testing prompts like code, is called *regression testing*.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- How to evaluate retrieval and generation separately.
- Retrieval metrics: hit rate, recall at k and MRR.
- Answer metrics: faithfulness, relevance and correctness.
- What evaluation frameworks offer and when to use them.
- What a regression is and how to catch one.
- How to compare two versions of a system fairly.

### Key ideas

- **Evaluate the pipeline in stages.** For each test question, record which chunks should be retrieved. Score retrieval on its own first; if the right passage never reaches the prompt, no prompt change will fix the answer.
- **Retrieval metrics are simple code.** *Hit rate at k* asks whether any correct chunk is in the top k. *Recall at k* asks what share of all correct chunks were found. *MRR* rewards finding the correct chunk near the top. None of them need a model.
- **Answer metrics need care.** *Faithfulness* checks that every claim is supported by the retrieved context. *Answer relevance* checks that the answer addresses the question. *Correctness* compares the answer to a reference answer you wrote. Faithfulness and correctness are different: an answer can be faithful to the wrong passage.
- **Test the refusals too.** Out-of-scope and trick questions (with false premises, or about things not in the docs) check that the system says "I don't know" instead of inventing an answer. Track the refusal rate on these separately from accuracy on answerable questions.
- **Frameworks package the boilerplate.** Ragas offers ready-made RAG metrics, many of them LLM-judged; promptfoo runs prompts and models against test cases defined in a config file, with code and model-graded assertions, and can run in CI (continuous integration, which runs checks automatically on every push). Both are free and open source and work with many providers. Treat their judged metrics like any judge: spot-check them against your own labels.
- **A regression is something that used to work and now does not.** Changing a prompt, model, chunk size or retriever can fix one failure and quietly cause three others. Rerun the full eval after every change and compare per-question results, not just the average.
- **Compare fairly.** Change one thing at a time, use the same dataset and the same judge, and run more than once when scores are close, because outputs vary. A one-point change on 50 questions may be noise.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [Ragas documentation](https://docs.ragas.io/), starting from the home page and the [list of available metrics](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/).
   - Read the descriptions of context precision, context recall, faithfulness and response relevancy. Note which ones use an LLM.
1. Read [promptfoo's introduction](https://www.promptfoo.dev/docs/intro/) and follow its [getting started guide](https://www.promptfoo.dev/docs/getting-started/).
   - Set up a config with two prompt variants and a few test cases, and run `promptfoo eval` and `promptfoo view`.
   - promptfoo was acquired by OpenAI in March 2026. It remains open source and works with many model providers, including Claude.
1. Read [promptfoo's assertions and metrics reference](https://www.promptfoo.dev/docs/configuration/expected-outputs/) to see which checks are code-based and which are model-graded.
1. Revisit the evaluation sections of the [Hamel and Shreya evals FAQ](https://hamel.dev/blog/posts/evals-faq/) that cover RAG and retrieval.
1. Practice: write 20 test questions for your Chat With Your Docs system, each with the expected source chunk and a short reference answer. Compute hit rate at 5 with plain Python. Then change one retrieval setting (such as chunk size or the number of reranked results), rerun, and list which individual questions got better and which got worse.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [promptfoo's GitHub Action guide](https://www.promptfoo.dev/docs/integrations/github-action/) shows how to run evals automatically on every pull request. You will set this up properly in the Production path.
