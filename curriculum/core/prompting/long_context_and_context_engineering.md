### Introduction

Modern models can read hundreds of thousands of tokens at once. That does not mean you should stuff everything in. What you put in the context window, and where you put it, has a large effect on quality, cost and speed. This shift in thinking, from crafting the perfect sentence to curating the right information, is called *context engineering*. It is the skill that separates toy demos from systems that work, and it underpins RAG, memory and agents later in the curriculum.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What context engineering is and how it extends prompt engineering.
- How to get text out of a PDF so you can put it in a prompt.
- How to structure long documents inside a prompt, and where to put the question.
- Why more context can make answers worse.
- How prompt caching makes reused context cheaper and faster.
- How to think of context as a limited budget.

### What context engineering is

In the last two lessons you focused on the *instructions*: how to word a task, add examples and structure the prompt. But the instructions are only part of what the model sees. On a real call, the **context** is everything sent to the model: the system prompt, the conversation history, any documents you pasted or retrieved, tool definitions and tool results. All of it competes for the same context window, which you met in Context Windows and Sampling.

**Context engineering** is the job of deciding which tokens earn a place in the context on each call. Prompt engineering asks "how should I phrase this?" Context engineering asks "what does the model need to see to do this well, and what should I leave out?" In a simple app the answer is easy. In a document Q&A system it means choosing which pages to include. In an agent that runs for an hour, it means deciding which old tool results to drop. You will come back to this idea in the RAG section and again in Context Engineering for Agents.

### Getting text out of a PDF

Much of the long material you'll want to work with arrives as PDFs: reports, manuals, papers. A model API can accept some PDFs directly (you'll see that in Images, PDFs and Audio), but often you want the plain text so you can trim it, count its tokens and wrap it in tags yourself. For a simple, text-based PDF, the `pypdf` library does this in a few lines:

```python
# pdf_to_text.py  (run with: uv add pypdf, then uv run pdf_to_text.py report.pdf)
import sys
from pathlib import Path

from pypdf import PdfReader

pdf_path = Path(sys.argv[1])
reader = PdfReader(pdf_path)

pages = []
for number, page in enumerate(reader.pages, start=1):
    text = page.extract_text() or ""  # empty for scanned (image-only) pages
    pages.append(f"[page {number}]\n{text}")

out_path = pdf_path.with_suffix(".txt")
out_path.write_text("\n\n".join(pages), encoding="utf-8")
print(f"{len(reader.pages)} pages, {sum(len(p) for p in pages):,} characters -> {out_path}")
```

Keeping a `[page N]` marker on each page is a small but useful habit: when the model quotes the document, you can see where the quote came from. Expect the output to be imperfect. Tables come out as jumbled text, headers and footers repeat on every page, and a scanned PDF gives you nothing at all because its pages are pictures. That's fine for this lesson. Doing this properly (tables, layout, scanned pages) is the subject of Document Parsing in the RAG section.

### Structuring long documents

Once you have the text, how you lay it out in the prompt matters. Three habits work well across providers:

**Put long documents first and the question last.** For long inputs, place the documents near the top of the prompt and your instructions and question at the end. Anthropic reports that putting the query at the end can noticeably improve answer quality on long, multi-document inputs. A useful way to picture it: the model reads the material, then is asked the question while the question is the freshest thing in view.

**Wrap each document in tags with metadata.** When there are several documents, label them so the model can tell them apart and refer to them:

```text
<documents>
  <document index="1">
    <source>annual_report_2025.pdf</source>
    <content>
    [page 1]
    ...
    </content>
  </document>
  <document index="2">
    <source>board_minutes_march.pdf</source>
    <content>...</content>
  </document>
</documents>

Using only the documents above, answer the question below. First copy the
sentences that are relevant to the question into <quotes> tags, citing the
source of each. Then answer inside <answer> tags. If the documents do not
contain the answer, say so.

<question>What was the revenue growth in 2025, and what explanation was given?</question>
```

**Ask the model to quote before it answers.** That instruction in the example above is deliberate. Pulling the relevant quotes out first makes the model locate the evidence before reasoning about it, which cuts through the noise of a long document. It also makes the answer easy for *you* to check: if the quotes don't support the answer, something is wrong. This is the same "reason before answering" idea from the last lesson, aimed at long inputs.

### More context can make answers worse

It is tempting to think that more information can only help. It can't. Models use their context unevenly. A well-known study, "Lost in the Middle," found that models were best at using information near the start or end of a long input and noticeably worse at using facts buried in the middle. Later work by Chroma, called "Context Rot," found that performance tends to drop as inputs get longer, even on simple tasks and even when the needed fact is clearly present.

So think of attention as a **budget**, not a bucket. Every irrelevant paragraph you include costs money and time, and also dilutes the model's attention to the paragraphs that matter. The goal is the smallest set of high-signal tokens that gets the job done. In practice:

- Trim boilerplate: navigation menus, legal footers, repeated headers.
- Remove duplicates.
- Summarize old conversation turns instead of resending them word for word.
- Include only the relevant sections of a long document, not the whole thing.

That last point is what **retrieval** does automatically: instead of sending a 300-page manual, you search it and send the five most relevant passages. That is RAG, the subject of a whole section later in this path. Summarizing old history, called **compaction**, appears in the Memory section of the Agentic path. Both are context engineering tools.

### Prompt caching

Many apps send the same large chunk of context over and over: a long system prompt, a reference manual, a set of examples. Processing those tokens again on every call is wasteful. **Prompt caching** lets the provider keep the processed start of a prompt (the *prefix*) for a few minutes, so the next call that begins with exactly the same prefix reads it from the cache. Cached reads are much cheaper than fresh input tokens and come back faster.

On Claude you mark where the stable part ends with a `cache_control` marker, as in the code below. That marker, and the separate prices for cache writes and reads, are Claude features: OpenAI and many other providers cache long prefixes automatically with no marker, and a local model has no per-token bill to save (see [On other providers](#on-other-providers)). Caching is a **prefix match**: it only works if the beginning of the prompt is byte-for-byte identical. Change one character near the top and everything after it must be processed fresh. So put stable content first (system prompt, reference documents) and changing content last (the user's question). That's the same order the long-context advice recommends, which is convenient.

```python
# cached_qa.py  (run with: uv run cached_qa.py report.txt)
import os
import sys

import anthropic

MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
client = anthropic.Anthropic()
document = open(sys.argv[1], encoding="utf-8").read()

questions = ["What is this document about?", "List three numbers it mentions."]
for question in questions:
    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system="You answer questions using only the document the user provides.",
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"<document>\n{document}\n</document>",
                    "cache_control": {"type": "ephemeral"},  # cache everything up to here
                },
                {"type": "text", "text": f"<question>{question}</question>"},
            ],
        }],
    )
    u = response.usage
    print(f"{question!r}: input={u.input_tokens} "
          f"cache_write={u.cache_creation_input_tokens} cache_read={u.cache_read_input_tokens}")
```

On the first question you should see a cache *write*; on the second, a cache *read* of roughly the document's size. If `cache_read_input_tokens` stays at zero, either the document is shorter than the model's minimum cacheable length (from a few hundred to a few thousand tokens, depending on the model) or something in the prefix changed between calls. You will use caching seriously in the Cost and Latency section of the Production path.

### Know your limits

Every model has a maximum context size and a separate maximum output size, and thinking tokens count toward the window too. Check the numbers for the model you use on [Current Models](#/models), and measure rather than guess: the `usage` field on every response tells you exactly how many input tokens a document cost. A rough rule for English is about four characters per token, so a 50-page report might be 25,000 to 40,000 tokens. That fits easily in a modern window, but at scale, sending it on every question adds up. Before you send something big, ask whether the model needs all of it.

### On other providers

Almost everything here is provider-neutral. Context as a budget, documents first and the question last, tagged documents with metadata, quote-then-answer, trimming and the "Lost in the Middle" effect apply to every model, and small open models usually suffer from long inputs *more* than hosted ones. The `pypdf` step is plain Python. Two things differ. First, **caching**: OpenAI caches long prompt prefixes automatically, with no `cache_control` marker, and reports the cached part as `usage.prompt_tokens_details.cached_tokens` *inside* its `prompt_tokens` total, while Claude reports cache reads and writes separately from `input_tokens`; minimum lengths, lifetimes and discounts differ too, so read OpenAI's [prompt caching guide](https://developers.openai.com/api/docs/guides/prompt-caching) before comparing bills. The prefix rule is the same everywhere: stable content first. Second, **window size**: hosted models now take hundreds of thousands of tokens, but Ollama sets a local model's context from your machine's memory, as small as 4,000 tokens on a typical laptop, and a longer prompt can be cut short without an error, so raise it as its [context length page](https://docs.ollama.com/context-length) explains before you paste in a 30-page report. Here is the cache check from `cached_qa.py` on OpenAI:

```python
# cached_qa_openai.py  (uv add openai; set OPENAI_API_KEY and OPENAI_MODEL)
import os
import sys

from openai import OpenAI

client = OpenAI()
document = open(sys.argv[1], encoding="utf-8").read()
for question in ["What is this document about?", "List three numbers it mentions."]:
    response = client.chat.completions.create(
        model=os.environ["OPENAI_MODEL"],  # a current ID from OpenAI's models page
        messages=[{"role": "system", "content": "Answer using only the document."},
                  {"role": "user", "content": f"<document>\n{document}\n</document>\n<question>{question}</question>"}],
    )  # no marker: a long shared prefix is cached automatically
    print(question, response.usage.prompt_tokens, response.usage.prompt_tokens_details.cached_tokens)
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Effective context engineering for AI agents](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents) by Anthropic. It is the clearest statement of why context is a budget.
   - Read the whole post. Do not worry if the agent-specific parts feel abstract; you will return to them in the Memory section.
1. Read the long-context section of [Anthropic's prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices).
   - Note the advice on document placement, XML structure and quoting.
1. Read [Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows) in the Claude docs to understand how input, output and thinking tokens share the window.
1. Skim [Context Rot](https://research.trychroma.com/context-rot) by Chroma research.
   - Read the introduction and look at the charts. The takeaway: performance drops as input length grows, even on simple tasks.
1. Skim the [pypdf text extraction guide](https://pypdf.readthedocs.io/en/stable/user/extract-text.html) so you know what `extract_text` can and can't do.
1. Practice: find a text-based PDF of 30+ pages (an annual report or a government report works well) and convert it with `pdf_to_text.py`. Write five questions whose answers you can check yourself. Ask each question twice: once with the question *before* the document, once *after*, with the document wrapped in tags and the quote-first instruction. Record in a table whether each answer was correct and the `usage.input_tokens` for each call. Then run `cached_qa.py` on the same text and note the cache numbers.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [How does context engineering differ from prompt engineering?](#what-context-engineering-is)
- [How do you extract text from a PDF, and when will that not work?](#getting-text-out-of-a-pdf)
- [Where should the question go relative to a long document, and why ask for quotes first?](#structuring-long-documents)
- [Why can adding more context make answers worse?](#more-context-can-make-answers-worse)
- [Why must stable content come first for prompt caching to work?](#prompt-caching)
- [How can you find out how many tokens a long document costs?](#know-your-limits)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172) is the research paper behind the "middle of the context is weakest" finding.
- [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) in the Claude docs explains how to mark cacheable prefixes, minimum lengths and pricing. You will use it seriously in the Cost and Latency section.
- [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting) shows how to count a prompt's tokens before you send it.
