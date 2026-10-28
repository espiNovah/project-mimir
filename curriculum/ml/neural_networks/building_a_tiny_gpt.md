<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

In Transformers and Attention you learned what a transformer does. Now you'll build one. A tiny GPT, trained on a few megabytes of text on a free GPU, uses the same architecture as the frontier models you call through an API, just with far fewer layers, far less data and a vocabulary of characters instead of tokens. Building one is the single best way to stop thinking of language models as magic.

This lesson walks through attention and the transformer intuitively, then points you at Andrej Karpathy's from-scratch build, which is the standard way people learn this.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Language modeling as next-token prediction.
- Character-level tokenization and the bigram baseline.
- Attention and the transformer, intuitively.
- Queries, keys, values and causal masking.
- Multi-head attention, feed-forward layers, residual connections and layer norm.
- Training, validation loss and sampling from a trained model.
- How a tiny GPT relates to a production LLM.

### Key ideas

- **A language model predicts the next token.** Given the text so far, it outputs a probability distribution over the vocabulary (softmax over logits, from Matrices and Probability). Training minimizes cross-entropy: the average negative log probability of the true next token. Generation is repeated sampling.
- **Start with a bigram baseline.** A model that predicts the next character from only the current character is simple and already beats random. Your transformer has to beat its validation loss, the same baseline habit you built in Overfitting and Baselines.
- **Attention, intuitively: each token asks a question and gathers answers.** Every position produces a query ("what am I looking for?"), a key ("what do I contain?") and a value ("what will I share?"). Dot products between queries and keys (the similarity you studied in Vectors and Similarity) are softmaxed into weights, and each position takes a weighted average of values. That is how "it" learns to look back at "the cat."
- **Causal masking keeps the model honest.** During training, each position may only attend to earlier positions, so it can't peek at the answer it's supposed to predict.
- **A transformer block is attention plus a feed-forward layer, wrapped in residual connections and layer norm.** Attention moves information between positions; the feed-forward layer processes each position independently. Residual connections ("add the input back") and normalization keep deep stacks trainable. Multiple heads let the model attend to different things at once.
- **Scale is the main difference from production models.** Your model may have a few million parameters and a context of 256 characters. Frontier models use the same blocks with billions of parameters, subword tokenizers, trillions of training tokens, and then extra post-training stages that turn a text predictor into a helpful assistant.
- **Loss curves tell the story.** Validation loss falling means the model is generalizing. Samples go from random characters, to plausible words, to plausible style as loss drops.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Watch [3Blue1Brown's transformer chapters](https://www.3blue1brown.com/topics/neural-networks) for the best visual explanation of attention.
   - Watch "Transformers, the tech behind LLMs" and [the attention chapter](https://www.3blue1brown.com/lessons/attention). Rewatch the query/key/value section until you could explain it to a friend.
1. Build along with the Zero to Hero video [Let's build GPT: from scratch, in code, spelled out](https://www.youtube.com/watch?v=kCc8FmEb1nY), the core of this lesson.
   - Code every step yourself in a Colab or Kaggle notebook with a GPU. Get the bigram model working before moving on to self-attention.
   - If you have time, watch the earlier "makemore" videos from [Neural Networks: Zero to Hero](https://karpathy.ai/zero-to-hero.html) first; they make this one easier.
1. Read [The Illustrated Transformer by Jay Alammar](https://jalammar.github.io/illustrated-transformer/) as a written companion with diagrams of every step.
1. Watch [Karpathy's Deep Dive into LLMs like ChatGPT](https://www.youtube.com/watch?v=7xTGNNLPyMI) to connect your tiny model to how real assistants are built.
   - Focus on the pretraining, tokenization and post-training sections. Write down three differences between your tiny GPT and a production assistant.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [nanoGPT](https://github.com/karpathy/nanoGPT) is Karpathy's clean, minimal GPT training repository, useful for reading a tidy version of what you built.
- [nanochat](https://github.com/karpathy/nanochat) is a stretch goal: a full, small ChatGPT-style pipeline (tokenizer, pretraining, fine-tuning, chat UI) designed to be trained end to end on a modest budget.
