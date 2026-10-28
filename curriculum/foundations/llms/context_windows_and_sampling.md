### Introduction

In the last lesson you saw that a model produces a probability for every possible next token. Two practical questions follow, and you'll deal with both in every app you build. First: how much text can the model take into account when making that prediction? That's the **context window**. Second: given the probabilities, how does it actually pick a token? That's **sampling**, and the dials that control it, like **temperature**, explain why the same prompt can give you different answers each time.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What the context window is and what counts toward it.
- Why models have no memory between requests.
- Why more context isn't always better.
- How a model turns probabilities into a chosen token.
- What temperature, top-p and top-k do.
- Why model output is non-deterministic, and how to design for that.

### The context window

The **context window** is everything the model can "see" while generating a response: your instructions, the conversation so far, any documents you've included, tool definitions and the response it's writing. It's measured in tokens. Think of it as the model's working memory, separate from the knowledge baked into its weights during training.

Context windows have grown enormously, from around 4,000 tokens in early ChatGPT to hundreds of thousands or a million tokens in current frontier models. A million tokens is roughly a few thousand pages of text. Each model's documentation lists its limit.

Three facts about context windows will save you a lot of confusion:

- **Input and output share the space.** If a model has a 200,000-token window and your prompt uses 190,000, there are only 10,000 left for the answer. Separately, you set a **max tokens** limit on each request to cap how long the response may be.
- **Models don't remember anything between requests.** Like the HTTP servers in How the Web Works, model APIs are stateless. A chat app "remembers" your conversation because it sends the *entire* history again with every new message. That means each turn of a long conversation costs more than the last, a fact you'll see in real numbers when you build the Terminal Chatbot.
- **More isn't automatically better.** As the amount of text in the window grows, models get worse at finding and using any particular piece of it. This is sometimes called **context rot**. A focused prompt with only the relevant information often beats a huge one containing everything. Choosing what to include is a skill, context engineering, that you'll study in the AI Engineering Core path.

<div class="lesson-note" markdown="1">

#### Context versus training knowledge

If you need a model to use information it wasn't trained on, such as your company's documents, today's news or the user's files, you have to put that information into the context window. There's no other way in short of retraining. Most of the techniques later in this curriculum, from retrieval to tool use to memory, are really strategies for getting the right information into the context window at the right time.

</div>

### From probabilities to a token

At each step, the model outputs a score for every token in its vocabulary, and those scores are converted into probabilities that add up to 100%. Say the text so far is "My favorite fruit is" and the top probabilities are:

```text
 mango    40%
 apple    25%
 banana   15%
 the       8%
 kiwi      5%
 ... (tens of thousands of others sharing the last 7%)
```

The model now has to choose one. There are two basic approaches:

- **Greedy decoding:** always pick the most likely token (" mango"). Predictable, but it tends toward bland, repetitive text and can get stuck in loops.
- **Sampling:** pick randomly, weighted by the probabilities. " mango" 40% of the time, " apple" 25% of the time, and so on. This produces more varied, natural text, and it's what chat models do by default.

Sampling is why asking the same question twice can give two different answers, even with nothing else changed.

### Temperature, top-p and top-k

**Temperature** reshapes the probabilities before sampling:

- **Low temperature** (near 0) sharpens them: the favorite becomes even more likely, approaching greedy decoding. Good for factual answers, extraction and code.
- **Temperature 1** leaves the model's probabilities as they are.
- **High temperature** (above 1) flattens them, giving unlikely tokens more of a chance. More surprising, more creative, and past a point, incoherent.

You can see the effect with a few lines of Python, no model required. This takes raw scores (called **logits**) for five candidate tokens, applies a temperature and shows the resulting probabilities:

```python
import math
import random

tokens = [" mango", " apple", " banana", " the", " kiwi"]
logits = [3.0, 2.5, 2.0, 1.3, 0.8]       # raw model scores; higher means more likely


def probabilities(logits: list[float], temperature: float) -> list[float]:
    scaled = [score / temperature for score in logits]
    exps = [math.exp(s) for s in scaled]
    total = sum(exps)
    return [e / total for e in exps]


for temperature in [0.2, 1.0, 2.0]:
    probs = probabilities(logits, temperature)
    picks = random.choices(tokens, weights=probs, k=10)
    shown = ", ".join(f"{t.strip()} {p:.0%}" for t, p in zip(tokens, probs))
    print(f"T={temperature}: {shown}")
    print(f"        10 samples: {[p.strip() for p in picks]}")
```

Run it a few times. At `T=0.2`, nearly every sample is "mango." At `T=2.0`, you'll see all five.

Two other common settings cut off the long tail of unlikely tokens before sampling:

- **Top-k** keeps only the `k` most likely tokens (say, the top 40).
- **Top-p** (also called nucleus sampling) keeps the smallest set of top tokens whose probabilities add up to `p` (say, 0.9) and discards the rest.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Not every model lets you change these

Sampling settings are an area where providers differ and change over time. Some APIs accept `temperature`, `top_p` and `top_k`. Others, including several of the newest reasoning-focused models, fix them at their defaults and reject other values, expecting you to steer the output with instructions instead. Always check the current documentation for the specific model you're using.

</div>

### Designing for non-determinism

Even at temperature 0, most hosted models aren't perfectly repeatable: tiny differences in how the hardware does the math can change which token wins a close race, and one different token early on can send the rest of the answer down another path. Treat model output as **non-deterministic**. That has practical consequences you'll build on throughout the curriculum:

- Never assume a prompt that worked once will work every time. Test it many times; this is the core idea behind evals.
- When you need a fixed format, ask for structured output and validate it in code rather than hoping.
- When a result matters, save it. Don't plan on reproducing it later by rerunning the same prompt.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read Anthropic's documentation on [context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows).
   - Read "How the context window works" and the table of context window sizes. Skim the sections on extended thinking and tool use; they'll make more sense after the Reasoning Models lesson and the Tool Use section.
1. Return to the [Transformer Explainer](https://poloclub.github.io/transformer-explainer/) and experiment with its temperature slider.
   - Enter a short prompt, then generate the next token several times each at a low, medium and high temperature. Watch how the probability chart changes shape.
   - If your version of the tool shows top-k or top-p controls, try those too and note what changes.
1. Watch the section of Andrej Karpathy's [Deep Dive into LLMs like ChatGPT](https://www.youtube.com/watch?v=7xTGNNLPyMI) on inference.
   - Watch the "inference" chapter (26:01 to 31:09). It shows sampling happening one token at a time. If you have time, continue through "GPT-2: training and inference" (to 42:52).
1. Run the temperature script from this lesson.
   - Add top-k: before sampling, keep only the two highest-scoring tokens and renormalize their probabilities. How does that change the samples at `T=2.0`?
   - In your learning journal, describe a feature you might build where you'd want very low randomness, and one where you'd want more.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What counts toward the context window?](#the-context-window)
- [Why doesn't a model remember your previous requests?](#the-context-window)
- [Why can adding more context make answers worse?](#the-context-window)
- [How does a model turn a list of probabilities into one chosen token?](#from-probabilities-to-a-token)
- [What do temperature and top-p each change about the output?](#temperature-top-p-and-top-k)
- [How should you design an app knowing the same prompt can give different answers?](#designing-for-non-determinism)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- Anthropic's [Effective context engineering for AI agents](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents) explains why context is a finite resource and how agent builders manage it. It's assigned later in the curriculum, but the first sections are readable now.
- The [Claude glossary](https://platform.claude.com/docs/en/about-claude/glossary) has short definitions of context window, temperature, tokens and other terms from this section.
