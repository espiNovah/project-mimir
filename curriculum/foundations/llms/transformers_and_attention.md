### Introduction

Almost every modern language model, from GPT and Claude to Gemini, Llama and the small open models you can run on a laptop, is built on the same basic design: the **transformer**, introduced by researchers at Google in a 2017 paper called "Attention Is All You Need." Its key idea, **attention**, lets every word in a passage look at every other word to figure out what it means in context.

You won't implement a transformer in this curriculum. But a high-level picture of how one turns your prompt into a next-token prediction will help you understand why prompts are structured the way they are, why long inputs cost more, and why models generate text one token at a time.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The journey from text to tokens to embeddings to a prediction.
- What embeddings are: meaning as a list of numbers.
- What attention does, using an everyday analogy.
- How transformer layers stack to build up understanding.
- Why models generate text one token at a time.
- Why attention makes long inputs more expensive.

### From text to prediction

Here's the whole pipeline in one picture. When you send "The capital of France is" to a model:

1. **Tokenize.** The text is split into tokens and turned into token IDs, as you saw in the last lesson.
1. **Embed.** Each token ID is looked up in a big table and replaced by an **embedding**: a long list of numbers (thousands of them) that represents that token. Information about each token's position is added too, since word order matters.
1. **Transform.** The embeddings flow through a stack of identical **transformer blocks**, often dozens of them. Each block lets the tokens exchange information (attention) and then processes each token individually (a small neural network, like the ones in the first lesson of this section).
1. **Predict.** At the end, the final vector for the last position is converted into a score for every token in the vocabulary. Those scores become probabilities: maybe `" Paris"` 92%, `" a"` 2%, `" the"` 1%, and so on.

One token is picked from those probabilities (how that pick happens is the next lesson's topic), added to the end of the text, and the whole process runs again to predict the token after that. This loop of "predict one token, append it, repeat" is called **autoregressive generation**. It's why you see answers stream in word by word, and why output tokens are slower and pricier than input tokens: the model has to run once per output token.

### Embeddings: meaning as numbers

An embedding is a point in a space with thousands of dimensions. You can't picture that, but you can picture the idea in two: words with similar meanings end up near each other. "Cat" sits near "dog," far from "carburetor." Directions in the space can even carry meaning; the classic example is that the direction from "man" to "woman" is roughly the same as the direction from "king" to "queen."

The model learns these embeddings during training, by the same guess-measure-adjust loop you saw before. Nobody decides that dimension 1,742 means "is an animal." You'll meet embeddings again in the Embeddings and Retrieval section, where you'll use them to search documents by meaning.

### Attention: tokens looking at each other

The trouble with a starting embedding is that it represents a token *on its own*. But meaning depends on context. Consider:

```text
The animal didn't cross the street because it was too tired.
The animal didn't cross the street because it was too wide.
```

In the first sentence, "it" means the animal; in the second, the street. A model has to use the surrounding words to work that out.

**Attention** is the mechanism that does this. For each token, the model asks: which other tokens in this passage are relevant to me, and how much? One helpful analogy is a library search:

- Each token produces a **query**: "here's what I'm looking for."
- Each token also produces a **key**: "here's what I contain."
- And a **value**: "here's the information I'll share if you pick me."

The model compares the query of "it" against the keys of every earlier token. "Animal" and "tired" match strongly in the first sentence, so their values get blended into the representation of "it." After attention, the vector for "it" doesn't just mean "a pronoun"; it means "a pronoun referring to a tired animal."

A transformer block runs many of these attention lookups side by side (**multi-head attention**), so different heads can track different kinds of relationships, such as grammar, who-did-what, or which bracket closes which. Stacking dozens of blocks lets the model build from simple patterns in early layers to abstract ones in later layers.

In models that generate text, attention only looks backward: each token can see the tokens before it but not after. That's what makes next-token prediction a fair test during training.

<div class="lesson-note" markdown="1">

#### Why long prompts cost more

In basic attention, every token compares itself with every other token, so doubling the length of your input roughly quadruples that part of the work. Providers use many clever tricks to make long inputs practical, and models now accept hundreds of thousands of tokens or more, but long inputs are still slower and more expensive. Later in the curriculum you'll learn to decide carefully what goes into a model's input, a skill called context engineering.

</div>

### What this means for you as a builder

You don't need the internals to build things, but a few practical consequences fall out of this picture:

- **The model only knows what's in its input and its weights.** Everything it uses to answer has to either have been learned in training or be in the tokens you send.
- **Every output token is a fresh prediction.** The model doesn't plan a whole answer and then type it out. That's why asking it to think through a problem before answering can help: the reasoning it writes becomes input for the tokens that follow.
- **Position and structure in the prompt matter.** Attention can find relevant information anywhere, but clear structure (headings, labels, XML tags) makes the relevant parts easier to find, which you'll use heavily in the Prompting section.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Return to 3Blue1Brown's [Neural Networks series](https://www.3blue1brown.com/topics/neural-networks) for the transformer chapters.
   - Watch [Transformers, the tech behind LLMs](https://www.3blue1brown.com/lessons/gpt) and [Attention in transformers, step-by-step](https://www.3blue1brown.com/lessons/attention). They're the clearest visual explanations of embeddings and attention available. Don't worry if some of the matrix details go past you; aim to understand what each step is for.
1. Read Jay Alammar's [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/), a famous illustrated walkthrough of the original architecture.
   - Read up to and including "Self-Attention in Detail." The rest covers the encoder-decoder design used for translation, which modern chat models simplify; skim it.
1. Explore the [Transformer Explainer](https://poloclub.github.io/transformer-explainer/) from Georgia Tech, an interactive visualization that runs a real (small) GPT-2 model in your browser.
   - Type your own sentence and follow it through the embedding, attention and output stages. Click into an attention head and see which earlier tokens it focuses on.
   - Look at the probability bar chart at the end. You'll come back here for the next lesson and the project.
1. In your learning journal, explain the pipeline from text to next-token prediction in five or six sentences of your own, as if to a friend who has never coded. If you can't, rewatch the sections that felt fuzzy.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- Jay Alammar's [The Illustrated GPT-2](https://jalammar.github.io/illustrated-gpt2/) focuses on the decoder-only design that modern chat models actually use.
- The 3Blue1Brown chapter on [how LLMs might store facts](https://www.3blue1brown.com/lessons/mlp) covers the other half of each transformer block, the part that isn't attention.
