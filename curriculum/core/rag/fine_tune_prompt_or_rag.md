<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

"Should we fine-tune a model on our data?" is one of the most common questions an AI engineer gets, and the most common right answer is "not yet." Fine-tuning changes a model's weights; prompting and retrieval change what the model sees. Each solves different problems, at very different costs. Choosing badly wastes weeks.

This lesson gives you a decision framework you can defend in a design review or an interview, built on the evaluation habits you've practiced since Why Evals Matter.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What prompting, retrieval (RAG) and fine-tuning each change.
- Knowledge problems versus behavior problems.
- The usual order to try things in.
- When fine-tuning genuinely wins: format, style, narrow tasks, cost and latency.
- The hidden costs of fine-tuning: data, evaluation, maintenance.
- Using an eval set to make the decision with numbers.

### Key ideas

- **Prompting changes instructions, RAG changes knowledge, fine-tuning changes behavior.** If the model lacks facts (your product docs, last week's tickets), retrieval is almost always the answer, because fine-tuning is a poor and expensive way to add facts and those facts go stale. If the model knows enough but behaves wrongly (wrong format, wrong tone, inconsistent labels), better prompting, then fine-tuning, are the levers.
- **Try them in order of cost.** Start with a clear prompt and a few examples. Add retrieval if knowledge is missing. Consider fine-tuning only when you have an eval showing prompting has plateaued, and enough good labeled examples (often hundreds to thousands) to train on.
- **Fine-tuning shines on narrow, high-volume tasks.** Classification, extraction into a fixed schema, or matching a house style are good fits. A fine-tuned small model can match a much larger prompted model on such a task while being far cheaper and faster, and it can run on your own hardware.
- **Fine-tuning has hidden costs.** You need clean training data, a held-out test set, GPU time, a way to serve the model, and a plan to retrain when the task or base model changes. A prompt change ships in minutes; a retrain does not.
- **The techniques combine.** Many production systems use a fine-tuned model inside a RAG pipeline, or a frontier model for hard cases and a small fine-tuned model for the bulk.
- **Decide with an eval, not a hunch.** Compare options on the same held-out test set with the metrics that matter: quality, cost per 1,000 calls and latency. Don't forget the classic baseline: sometimes a TF-IDF classifier from Beat the Baseline is good enough.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the fine-tuning section of [Eugene Yan's Patterns for Building LLM-based Systems and Products](https://eugeneyan.com/writing/llm-patterns/), a widely cited practitioner guide.
   - Read the sections on fine-tuning and retrieval-augmented generation, and note his reasons for and against fine-tuning.
1. Read the opening page of the [fine-tuning chapter of the Hugging Face LLM Course](https://huggingface.co/learn/llm-course/chapter11/1) for the open-model view on when and why to fine-tune.
1. Read [What We've Learned From A Year of Building with LLMs](https://applied-llms.org/), written by a group of experienced practitioners.
   - Read the tactical and operational sections on prompting versus RAG versus fine-tuning, and on starting with evals.
1. For each of these scenarios, write one paragraph choosing prompting, RAG, fine-tuning or a classic model, and say what evidence would change your mind: an assistant that answers questions about a company's 500-page HR handbook; a system that routes two million support messages a month to one of 77 intents; a tool that rewrites marketing copy in a very specific brand voice; a chatbot that must always reply in valid JSON.

</div>
