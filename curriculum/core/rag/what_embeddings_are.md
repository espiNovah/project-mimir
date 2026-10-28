<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Language models only know what was in their training data and what you put in the context window. To answer questions about your own documents, you need a way to find the right passages quickly, even when the question uses different words from the document. Embeddings make that possible. They turn text into lists of numbers so that texts with similar meanings end up close together. This lesson explains what embeddings are and how to use them for semantic search, the first building block of retrieval-augmented generation (RAG).

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What an embedding is.
- How similarity between embeddings is measured.
- What semantic search is and how it differs from keyword search.
- What retrieval-augmented generation is.
- How to create embeddings locally or with an API.
- How to choose an embedding model.

### Key ideas

- **An embedding is a list of numbers that represents meaning.** An embedding model reads a piece of text and outputs a vector, often a few hundred to a few thousand numbers long. The individual numbers do not mean anything you can read, but their positions relative to other vectors do: "How do I reset my password?" and "I forgot my login" land close together.
- **Closeness is measured with cosine similarity.** Cosine similarity compares the direction of two vectors and gives a score from -1 to 1, where higher means more similar. Many models output normalized vectors, in which case the dot product gives the same ranking. You will see the math in the ML Foundations path, but you do not need it to use embeddings.
- **Semantic search finds meaning, not words.** Embed every passage once, embed the query at search time, and return the passages with the highest similarity. This finds relevant passages even with no shared words, but can miss exact matches such as product codes or names, which is why the next lessons add keyword search.
- **RAG is retrieve, then generate.** Retrieval-augmented generation finds the most relevant passages for a question and puts them in the prompt, so the model answers from your documents instead of from memory. It is the most common way to give a model knowledge it was not trained on.
- **Query and documents must use the same model.** Vectors from different embedding models are not comparable. If you change models, re-embed everything.
- **You can run embeddings locally or through an API.** Sentence Transformers runs good open models on your laptop for free. Hosted embedding APIs from several providers are an alternative; some model providers, including Anthropic, point to partner embedding services rather than offering their own.
- **Choose models with benchmarks, then test on your data.** Leaderboards such as MTEB compare embedding models across tasks, but the only result that matters is retrieval quality on your own documents and questions. Also consider vector size, speed, cost and supported languages.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Embeddings: what they are and why they matter](https://simonwillison.net/2023/Oct/23/embeddings/) by Simon Willison.
   - Read the whole post. It is the clearest plain-language introduction available, with practical examples of related-content search.
1. Work through the [Sentence Transformers quickstart](https://sbert.net/docs/quickstart.html).
   - Install it with `uv add sentence-transformers`, run the embedding and similarity examples, and try a few sentences of your own.
1. Read the [Claude docs page on embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings) to see how a model provider thinks about choosing an embedding model.
   - Focus on the criteria for picking a model. You do not need to sign up for any service.
1. Practice: embed 30 short sentences on three or four different topics with a Sentence Transformers model. Write a function `search(query, k=3)` that returns the most similar sentences with their scores. Try queries that share no words with the right answer, and one that depends on an exact name or number, and note where semantic search does well and where it fails.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard) compares embedding models on many retrieval and similarity tasks.
- [The Sentence Transformers documentation](https://sbert.net/) lists pretrained models and explains training your own.
