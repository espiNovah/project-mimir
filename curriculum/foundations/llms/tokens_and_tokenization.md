### Introduction

You read text as letters and words. A language model doesn't. Before any text reaches the neural network, it's chopped into pieces called **tokens**, and each token is swapped for a number. The model only ever sees those numbers.

This sounds like a technical detail, but it shapes almost everything about working with LLMs. You're billed per token. Context windows are measured in tokens. Rate limits are in tokens per minute. And some famous model weaknesses, like miscounting the letters in a word, come straight from tokenization. This lesson shows you what tokens are and gets you comfortable reasoning about them.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What a token is and why models use them instead of letters or words.
- How tokenizers like byte-pair encoding build their vocabulary.
- Why the same text costs different amounts in different languages and formats.
- How tokens affect cost, context limits and model behavior.
- How to count tokens yourself with `tiktoken`, and why counts differ between providers.

### What a token is

A **token** is a chunk of text, often a whole common word, part of a longer word, a punctuation mark or a bit of whitespace. Here's how one real tokenizer splits a few strings (each token separated by `|`):

```text
The| cat| sat| on| the| mat|.                     -> 7 tokens
un|bel|ievably                                    -> 3 tokens
 strawberry                                       -> 1 token
Str|aw|berry                                      -> 3 tokens
def| add|(a|,| b|):\n|   | return| a| +| b        -> 11 tokens
```

A few things to notice:

- **Spaces are usually attached to the start of a word.** `" cat"` (with a leading space) is a different token from `"cat"`.
- **Common words are single tokens; rare words get split.** "unbelievably" becomes three pieces.
- **Capitalization changes things.** `" strawberry"` is one token, but `"Strawberry"` at the start of a sentence splits into three.

The full list of tokens a tokenizer knows is its **vocabulary**, typically somewhere between 50,000 and a few hundred thousand entries. Each token has an ID number, and those IDs are what the model actually receives.

As a rough rule of thumb for English prose, one token is about three-quarters of a word, or about four characters. Use it for quick estimates, never for billing.

### Why not letters or words?

Using individual letters would make every text extremely long (and models get slower and more expensive as input grows). Using whole words would need an impossibly large vocabulary and would leave the model helpless when it met a new word, a typo or a variable name like `get_user_by_id`.

Subword tokens are the compromise. The most common method, **byte-pair encoding (BPE)**, builds its vocabulary from data: start with individual bytes, find the pair of neighbors that appears most often in a huge pile of text, merge that pair into a new token, and repeat tens of thousands of times. Frequent words end up as single tokens, while anything unusual can still be spelled out from smaller pieces. Nothing is ever "unknown."

### Why tokens matter to you

**Cost.** Model APIs charge per million input tokens and per million output tokens, with output usually several times more expensive. Every word of your prompt, every document you include and every word of the answer has a price.

**Languages and formats aren't equal.** Tokenizers are built from training data that's mostly English, so English is usually the most efficient. The same sentence in French, Hindi, Japanese or Amharic often takes more tokens, sometimes several times more, which means it costs more and fills the context window faster. Code, JSON and unusual formatting also tokenize differently from prose. You'll measure this yourself in the Token & Temperature Lab project.

**Limits.** The **context window**, the total amount of text a model can consider at once, is measured in tokens. So are rate limits. You'll learn more about both in the Context Windows and Sampling lesson.

**Odd behavior.** Because the model sees `" strawberry"` as a single token rather than ten letters, questions like "how many r's are in strawberry?" are genuinely harder for it than they look. The same goes for reversing strings, counting characters and some arithmetic on long numbers. Modern models handle many of these better than older ones did, often by reasoning step by step, but the underlying cause is tokenization.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Every model family has its own tokenizer

OpenAI, Anthropic, Google, Meta and others each use their own tokenizer, and providers sometimes change tokenizers between model generations. The same text can produce noticeably different token counts on different models. Use a tool like `tiktoken` to build intuition, but when you need an exact count for a specific model, use that provider's own token counting tool. You'll use Anthropic's in the Tokens, Cost and Rate Limits lesson.

</div>

### Counting tokens with tiktoken

`tiktoken` is OpenAI's open-source tokenizer library. It works offline, needs no account and is a great way to experiment:

```bash
uv add tiktoken
```

```python
import tiktoken

enc = tiktoken.get_encoding("o200k_base")   # the tokenizer used by recent OpenAI models

text = "The cat sat on the mat."
ids = enc.encode(text)

print(len(ids), "tokens")                   # 7 tokens
print(ids)                                  # a list of integer token IDs
print([enc.decode([i]) for i in ids])       # ['The', ' cat', ' sat', ' on', ' the', ' mat', '.']
```

`encode` turns text into token IDs and `decode` turns IDs back into text. The first time you run it, `tiktoken` downloads the vocabulary file, so you need an internet connection once.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Play with [Tiktokenizer](https://tiktokenizer.vercel.app/), a free web tool that colors each token so you can see exactly how text is split.
   - Paste in a paragraph of English, then the same paragraph translated into another language you know (or use a translation tool), then a short Python function. Note the token counts for each.
   - Try a long number, a URL, a word with a typo, and the same word in ALL CAPS. Which surprised you?
1. Watch Andrej Karpathy's [Let's build the GPT Tokenizer](https://www.youtube.com/watch?v=zduSFxRajkE) for the full story of how BPE works and why tokenization causes so many odd behaviors.
   - Watch the first 20 minutes or so, which explain tokenization and BPE conceptually. The rest builds a tokenizer from scratch in code; it's excellent if you want to go deeper, but optional.
1. Read the Hugging Face LLM Course page on [Byte-Pair Encoding tokenization](https://huggingface.co/learn/llm-course/chapter6/5) for a worked, step-by-step example of how merges are learned.
1. Write a small script that uses `tiktoken` to count the tokens in a sentence you type in.
   - Print the token count, the words-to-tokens ratio and each token wrapped in brackets so you can see the boundaries.
   - Try at least three sentences in two languages and record the results in your learning journal. You'll extend this into a file-counting tool in the project at the end of this section.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What is a token?](#what-a-token-is)
- [Why do models use subword tokens instead of letters or whole words?](#why-not-letters-or-words)
- [How does byte-pair encoding build its vocabulary?](#why-not-letters-or-words)
- [Why can the same message cost different amounts in different languages or formats?](#why-tokens-matter-to-you)
- [Why won't a tiktoken count exactly match what another provider bills you for?](#counting-tokens-with-tiktoken)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- The [tiktoken repository](https://github.com/openai/tiktoken) explains the library's design and lists its encodings.
