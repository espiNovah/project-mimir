<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Real documents are long: manuals, policies, books, wikis. You cannot embed a 200-page PDF as one vector and expect to find the right paragraph. Instead you split documents into smaller pieces called *chunks*, embed each one, and store them in a database built for fast similarity search. This lesson covers both halves of that ingestion pipeline: how to chunk well, and where to put the vectors.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The steps of an ingestion pipeline: load, clean, chunk, embed, store.
- Why chunk size matters and how to choose it.
- Common chunking strategies: fixed-size, recursive and structure-aware.
- Why metadata belongs with every chunk.
- What a vector database does and how approximate search works.
- How to choose between Chroma, pgvector and hosted services.

### Key ideas

- **Ingestion is a pipeline.** Load documents (PDF, HTML, Markdown), clean out noise such as navigation menus and page numbers, split into chunks, embed each chunk, and store the vector with its text and metadata. Run it once up front and again whenever documents change.
- **Chunk size is a trade-off.** Small chunks are precise but lose surrounding context; large chunks keep context but blur several topics into one vector and use more of the prompt. A few hundred tokens per chunk is a common starting point, but measure on your own data.
- **Respect the document's structure.** Splitting every 500 characters can cut sentences and tables in half. *Recursive* splitting tries paragraph breaks first, then sentences, then words. *Structure-aware* splitting follows headings in Markdown or HTML. A small overlap between neighboring chunks reduces the chance of cutting an idea in two.
- **Metadata makes chunks useful.** Store the source file, title, section heading, page number and position with each chunk. You need it to cite sources, filter searches (only this product's manual), and show users where an answer came from.
- **Contextual chunks retrieve better.** A chunk such as "Revenue grew 3% over the previous quarter" is ambiguous on its own. Prepending a short description of where it came from (which company, which report) before embedding, a technique Anthropic calls *contextual retrieval*, markedly reduces failed retrievals.
- **Vector databases search quickly at scale.** Comparing a query against every vector works for thousands of chunks. For millions, vector databases use *approximate nearest neighbor* (ANN) indexes such as HNSW that trade a little accuracy for a lot of speed.
- **Pick the simplest store that fits.** Chroma runs locally inside your Python process and is great for learning. pgvector adds vector columns to PostgreSQL, so vectors live next to the rest of your data and you can combine similarity with normal SQL filters. Hosted services handle scale for you, usually at a cost.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Pinecone's chunking strategies guide](https://www.pinecone.io/learn/chunking-strategies/).
   - Read the whole article. It compares fixed-size, recursive, document-structure and semantic chunking, and how to pick a size.
1. Read [Introducing Contextual Retrieval](https://www.anthropic.com/research/contextual-retrieval) by Anthropic.
   - Read up to and including the section on contextual embeddings. You will come back for the BM25 and reranking parts in the next lesson.
1. Follow the [Chroma getting started guide](https://docs.trychroma.com/docs/overview/getting-started).
   - Create a collection, add documents with metadata, and run queries with a metadata filter.
1. Read the README of [pgvector](https://github.com/pgvector/pgvector) to see how vectors work inside PostgreSQL.
   - Read the "Getting Started," "Querying" and "Indexing" sections. Note the distance operators and the difference between HNSW and IVFFlat indexes.
1. Practice: write an ingestion script for a folder of 5 to 10 Markdown or text documents. Chunk them two ways (fixed-size and heading-aware), store both versions in Chroma with source and heading metadata, and run the same ten questions against each. Write down which chunking returned the right passage more often.

</div>
