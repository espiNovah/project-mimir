### Introduction

You can build excellent AI applications without ever training a model yourself. But you can't build them well while treating the model as magic. When a model confidently invents a fact, ignores an instruction buried in a long prompt, or does brilliantly on one task and badly on a similar one, you need a mental model of what's going on inside to reason about why.

This section builds that mental model, with no math required. We start with the foundation: what a neural network is and what it means for one to "learn."

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What a model is: a function with adjustable settings.
- What parameters (weights) are and why there are billions of them.
- How training works: guess, measure the error, adjust, repeat.
- What gradient descent means, without the math.
- How a language model is trained to predict the next word.
- The stages that turn a raw next-word predictor into a helpful assistant.

### A model is a function with knobs

You've written plenty of functions by now. A function takes an input and returns an output. A neural network is also a function, with one twist: instead of you writing the rules inside, it has millions or billions of adjustable numbers, called **parameters** or **weights**, and the rules emerge from how those numbers are set.

Picture a giant mixing desk in a recording studio with billions of knobs. Sound (the input) goes in one side, flows through the knobs, and music (the output) comes out the other. With the knobs set randomly, you get noise. With them set just right, you get a symphony. Training is the process of finding good knob settings.

Inside, the network is organized into **layers**. Each layer takes a list of numbers, mixes them together using its weights, applies a simple non-linear squish (so the network can represent curves rather than only straight lines), and passes a new list of numbers on to the next layer. Stack enough layers and the network can represent astonishingly complicated relationships, such as "these pixels form the digit 7" or "after these words, the next word is probably 'Paris'."

Everything a neural network handles has to be numbers. Images become grids of pixel brightness. Text becomes lists of numbers too; how that works is the subject of the next lesson.

### Learning is guess, measure, adjust

Nobody sets those billions of knobs by hand. Instead, the network learns from examples:

1. **Guess.** Feed in an example, such as a picture of a handwritten 7, and see what the network outputs. At first, with random weights, it's nonsense.
1. **Measure.** Compare the output to the right answer and compute a single number for how wrong it was. This number is called the **loss**. Big loss, bad guess.
1. **Adjust.** Nudge every weight a tiny amount in whichever direction would have made the loss a little smaller.
1. **Repeat** millions of times, over millions of examples.

The clever part is step 3. An algorithm called **backpropagation** works out, for every single weight, which direction to nudge it. Repeatedly stepping "downhill" toward lower loss is called **gradient descent**. The usual picture is a hiker in thick fog trying to reach the bottom of a valley: they can't see the destination, but they can feel which way the ground slopes under their feet, so they keep taking small steps downhill.

Here's a toy version you can run. It "learns" a single knob, `w`, so that `w * x` matches the data, using exactly that loop:

```python
# Data secretly follows y = 3 * x. The "model" has to discover the 3.
data = [(1, 3), (2, 6), (3, 9), (4, 12)]

w = 0.0              # start with a bad guess
learning_rate = 0.01

for step in range(200):
    # Measure: how wrong are we, and which way should w move?
    gradient = sum(2 * (w * x - y) * x for x, y in data) / len(data)
    # Adjust: take a small step downhill
    w -= learning_rate * gradient
    if step % 40 == 0:
        loss = sum((w * x - y) ** 2 for x, y in data) / len(data)
        print(f"step {step:3}: w = {w:.3f}, loss = {loss:.3f}")

print(f"learned w = {w:.3f}")   # very close to 3.0
```

A real network does this with billions of knobs at once, but the loop is the same. The `learning_rate` controls the size of each step: too big and you overshoot the valley; too small and training takes forever.

<div class="lesson-note" markdown="1">

#### Nobody wrote the rules

The most important idea in this lesson: after training, the knowledge is spread across the weights in a way no person designed and nobody can easily read. Researchers have a whole field, **interpretability**, devoted to figuring out what's going on inside. That's why we evaluate models by testing what they do, which you'll take very seriously in the Evals section, rather than by inspecting their code.

</div>

### From next-word prediction to assistant

A large language model (LLM) is a neural network trained on one deceptively simple task: given some text, predict the next piece of text. Training text is free and enormous (a large fraction of the public internet, books and code), and every sentence provides its own right answers. Hide the last word of "The capital of France is ___," let the model guess, measure the loss, adjust.

To get very good at predicting the next word across all of that text, a model has to pick up grammar, facts, styles of argument, how code works, and much more. This first stage is called **pretraining**, and it produces a **base model**: a powerful autocomplete that will happily continue any document but doesn't follow instructions or hold conversations.

Two more stages turn it into the assistants you've used:

- **Supervised fine-tuning (SFT).** Continue training on many examples of helpful conversations, written or reviewed by people, so the model learns to respond like an assistant.
- **Reinforcement learning (RL).** Let the model produce answers, score them (with human preferences, automated checks such as "did the code pass its tests," or another model acting as a grader), and adjust the weights to make high-scoring answers more likely. This stage is also where "reasoning models" learn to think step by step, which you'll meet in the Reasoning Models lesson.

Keep this picture in mind, because it explains a lot of behavior. A model's knowledge stops at the date its training data was collected (its **knowledge cutoff**). And because the underlying skill is "produce plausible text," a model can produce plausible text that happens to be false, which is the subject of the Why Models Hallucinate lesson.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Watch the first chapters of 3Blue1Brown's [Neural Networks series](https://www.3blue1brown.com/topics/neural-networks). Grant Sanderson's animations are the best free visual introduction to neural networks anywhere.
   - Watch chapters 1 ("But what is a neural network?") and 2 ("Gradient descent, how neural networks learn"). Chapters 3 and 4 cover backpropagation in more depth and use some calculus; they are optional.
   - You'll come back to this series for the transformer chapters in the Transformers and Attention lesson.
1. Watch Andrej Karpathy's [Intro to Large Language Models](https://www.youtube.com/watch?v=zjkBMFhNj_g), a one-hour talk for a general audience by one of the founders of OpenAI and former head of AI at Tesla.
   - Focus on the first half: what an LLM is, how pretraining works, and how fine-tuning turns a base model into an assistant. The later security section is useful background for the Safety section of this curriculum.
1. Run the toy gradient descent example from this lesson and experiment with it.
   - Change `learning_rate` to `0.1` and then to `0.0001`. What happens to `w` in each case, and why?
   - Change the data to follow `y = 2 * x + 1`. Can a single knob `w` fit it? Add a second knob `b` so the model is `w * x + b` and update both. Write a sentence in your learning journal about what this tells you about why real models need so many parameters.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- Karpathy's [Deep Dive into LLMs like ChatGPT](https://www.youtube.com/watch?v=7xTGNNLPyMI) is a three-hour, still beginner-friendly walk through pretraining, fine-tuning and reinforcement learning. It's assigned in pieces later in this section, but it's worth watching end to end if you have the time.
- Anthropic's [Tracing the thoughts of a large language model](https://www.anthropic.com/research/tracing-thoughts-language-model) gives a readable look at interpretability research: what scientists find when they peek inside a trained model.
