### Introduction

Ask a model for a quote from a book, a citation for a claim or the release date of a library, and sometimes it will hand you something that sounds perfect and is completely made up. This is called a **hallucination**: a confident, fluent, false output.

Hallucinations are the single biggest reason AI features fail in the real world, and they don't come with a warning label. The wrong answer is written in exactly the same assured tone as the right one. You can't make them disappear entirely, but once you understand where they come from you can design systems that make them rarer, easier to catch and less costly when they happen. That design mindset runs through the rest of this curriculum.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What counts as a hallucination, with common examples.
- Why next-token prediction produces plausible but false text.
- How training and evaluation can reward guessing over admitting uncertainty.
- Which kinds of questions are most likely to produce hallucinations.
- Design patterns that reduce hallucinations and limit their damage.

### What hallucinations look like

Some of the most common forms you'll run into:

- **Invented sources.** Paper titles, authors, URLs or legal cases that don't exist, complete with plausible formatting.
- **Invented details about real things.** A real person's wrong birth year, a real company's nonexistent product, a quote that's close to something someone said but not quite.
- **Invented code.** A function or parameter that a library doesn't have, or that existed in an old version but was renamed. When you write code with AI tools, this one will bite you weekly.
- **Unfaithful summaries.** A summary of a document you provided that includes a claim the document never made.
- **Stale facts.** Information that was true before the model's knowledge cutoff and isn't anymore. Strictly, this is outdated knowledge rather than invention, but it looks the same to a user.

### Where they come from

Go back to the core idea from Neural Networks, Intuitively: a language model is trained to produce *plausible next tokens*. During pretraining, it learns what text tends to look like, not which statements are true. For a very common fact ("Paris is the capital of France"), the most plausible continuation and the true one are the same, because the fact appeared thousands of times in training data. For a rare fact, such as the birthday of a minor academic or the third paper by a particular author, the model may have seen it once or never. But it has seen millions of birthdays and paper titles, so it knows exactly what a plausible one looks like, and it produces one.

In other words, the model's fluency and its knowledge are separate things, and fluency is much stronger. It can always produce something that *sounds* right.

Training incentives make this worse. OpenAI researchers argued in a 2025 paper, summarized in [Why language models hallucinate](https://openai.com/index/why-language-models-hallucinate/), that much of the problem comes from how models are graded. Most benchmarks score an answer as simply right or wrong, with "I don't know" counting as wrong. Think of a multiple-choice exam with no penalty for wrong answers: a student who always guesses will outscore a student who leaves uncertain questions blank. Train and evaluate a model that way, and you teach it to guess confidently. Their suggested fix is to stop rewarding confident guesses over honest uncertainty, and model developers have been working to make models more willing to say they don't know.

<div class="lesson-note" markdown="1">

#### The risky zone

Hallucinations are most likely when a question is about something **specific and rare**: exact numbers, dates, names, quotes, citations, niche topics, recent events after the knowledge cutoff, or the details of a less popular library. Be most suspicious exactly when the answer would be hardest for you to check.

</div>

### Designing around hallucinations

You can't prompt hallucinations away completely, but you can build systems that work despite them. These are patterns you'll implement for real later in the curriculum:

- **Give the model the facts instead of relying on its memory.** If a question can be answered from a document, put the document in the context window and tell the model to answer only from it. This is the idea behind retrieval-augmented generation (RAG), covered in the RAG section, and it's the most effective fix there is.
- **Give it permission not to know.** Explicitly say that "I don't know" or "the document doesn't say" is an acceptable answer. Models follow this instruction surprisingly well.
- **Ask for evidence.** Have the model quote the passage that supports each claim, then check in code that the quote really appears in the source. A model that can't find a supporting quote should withdraw the claim.
- **Let it look things up.** Give an agent tools to search the web, read documentation or run code, so it can check facts instead of recalling them. You'll build this in the Tool Use section.
- **Verify in code wherever you can.** If a model writes code, run the tests. If it returns a URL, fetch it. If it returns JSON, validate it. Anything checkable should be checked automatically.
- **Match the stakes.** Add human review where a wrong answer would be expensive: medical, legal, financial or anything that takes irreversible action.
- **Measure it.** Build a test set of questions with known answers, including some the model *shouldn't* be able to answer, and track how often it makes things up. That's an eval, and you'll learn to build them in the Measuring Quality section.

Here's a taste of the "permission not to know" plus "answer from the source" pattern, as a prompt you could send to any model:

```text
Answer the question using only the article below.
If the article does not contain the answer, reply exactly: "The article doesn't say."
Quote the sentence from the article that supports your answer.

<article>
...article text here...
</article>

Question: In what year was the bridge completed?
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read OpenAI's [Why language models hallucinate](https://openai.com/index/why-language-models-hallucinate/), a short, readable summary of their 2025 research on the causes of hallucination.
   - Focus on the exam analogy and the argument about how evaluation rewards guessing. You don't need to read the linked research paper.
1. Watch the "hallucinations, tool use, knowledge/working memory" chapter of Andrej Karpathy's [Deep Dive into LLMs like ChatGPT](https://www.youtube.com/watch?v=7xTGNNLPyMI) (1:20:32 to 1:41:46).
   - It explains, with real examples, why models make things up and how training them to say "I don't know" and to use tools helps.
1. Read Anthropic's guide to [reducing hallucinations](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations).
   - Read the basic strategies carefully. Skim the advanced techniques; you'll use several of them in the RAG section.
1. Go hallucination hunting with any free chat app. You'll reuse your findings in the Token & Temperature Lab project.
   - Ask for things in the risky zone: three academic papers on a niche topic with authors and years; a quote from a minor historical figure; the parameters of a function in a small, less popular Python library; recent news.
   - Check every answer against a real source. Keep a log of each prompt, the answer, what was actually true, and how you verified it.
   - Try the "permission not to know" pattern on the same questions. Did it change anything?

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What is a hallucination, and what are some common forms it takes?](#what-hallucinations-look-like)
- [Why is a model's fluency not the same as its knowledge?](#where-they-come-from)
- [How can the way models are graded encourage confident guessing?](#where-they-come-from)
- [Which kinds of questions are most likely to produce hallucinations?](#where-they-come-from)
- [Why is giving the model the source document the most effective fix?](#designing-around-hallucinations)
- [How can you check in code that a model's claim is supported by its source?](#designing-around-hallucinations)
