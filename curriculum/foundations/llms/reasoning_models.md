### Introduction

For a few years, the way to get better answers from a language model was to make it bigger and train it on more data. Then a second approach took off: let the model **think before it answers**. A **reasoning model** writes out a stretch of working, trying approaches, checking intermediate results and backing out of dead ends, before it produces its final response.

Reasoning models are dramatically better at math, coding, planning and multi-step problems, and they power most serious agents today. They're also slower and more expensive per request. As a builder, you'll constantly decide how much thinking a task deserves. This lesson explains where the improvement comes from and how to make that call.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why writing out intermediate steps helps a next-token predictor.
- How reasoning models are trained with reinforcement learning.
- What thinking looks like in an API response.
- How thinking affects cost, speed and your token budget.
- How to control how much a model thinks.
- When reasoning helps, and when it's wasted.

### Why thinking out loud helps

Recall from Transformers and Attention that a model produces each token with a fixed amount of computation, and then that token becomes part of the input for the next one. Ask a hard question, demand the answer immediately, and the model has to squeeze all the work into the handful of tokens that make up the answer. Often there just isn't enough computation available in that space.

Let it write "First, let's figure out how many apples Sam has left: 12 minus 5 is 7. Now..." and every intermediate result is now sitting in the context window, where attention can use it. In a real sense, **models think with tokens**. More tokens of working means more total computation spent on the problem.

People noticed this early on: simply adding "Let's think step by step" to a prompt measurably improved accuracy on reasoning problems. This was called **chain-of-thought prompting**. Reasoning models take the idea much further, by training the model to produce long, useful chains of thought on its own.

### How reasoning models are trained

Remember the three training stages from Neural Networks, Intuitively: pretraining, supervised fine-tuning, and reinforcement learning. Reasoning models get their abilities mainly from that last stage, scaled up:

1. Give the model a large set of problems with checkable answers: math problems with known solutions, coding tasks with tests, puzzles.
1. Let it attempt each one many times, writing whatever reasoning it likes before its answer.
1. Reward the attempts that reached a correct answer and adjust the weights to make that kind of reasoning more likely.

Nobody tells the model *how* to reason. Through trial and error over millions of problems, models discover strategies on their own: breaking problems into parts, double-checking work, noticing a mistake ("wait, that's not right") and trying another approach. Because the rewards come from checkable answers, reasoning models improved fastest at math and code, where answers can be verified automatically.

### Thinking in an API response

When you call a model with thinking enabled, the response contains separate **thinking blocks** before the regular text. With Claude, a response's content looks like this:

```json
{
  "content": [
    {
      "type": "thinking",
      "thinking": "The user wants the cheapest route. Let me compare the three options...",
      "signature": "WaUjzkypQ2mUEVM36O2Txu..."
    },
    {
      "type": "text",
      "text": "The cheapest option is the overnight train, at $48."
    }
  ]
}
```

Other providers use different field names, but the idea is the same everywhere. A few things are important to know:

- **You may not see the real reasoning.** Many providers show only a summary of the model's thinking, or hide it entirely. Claude's current models, for example, return an empty thinking block by default unless you ask for a summary.
- **You pay for it anyway.** Thinking tokens are billed as output tokens, the expensive kind, whether or not the text is shown to you. They also count toward the response's maximum token limit.
- **Your code must read content by type.** Because a response can start with a thinking block, code that assumes the first block is the answer will break. You'll handle this properly in Your First API Call.

### Controlling how much a model thinks

Modern APIs increasingly let the model decide how much to think per request, with a dial you set. Claude's current models use **adaptive thinking**: the model judges each request's difficulty, skipping thinking for "What's the capital of Peru?" and thinking at length for a tricky bug. You steer it with an **effort** setting (such as `low`, `medium` or `high`): lower effort means less thinking, faster answers and lower cost. OpenAI's reasoning models have a similar "reasoning effort" setting, and open models often have a thinking mode you can switch on or off.

The question to ask for each task is: *does more thinking change the answer?*

- **Reasoning pays off** for math, logic, multi-step planning, tricky code, analyzing long documents for subtle issues, and agents deciding what to do next.
- **Reasoning is mostly wasted** on simple lookups, rewriting or translating text, classification, short chat replies and anything where speed matters more than depth.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Measure instead of guessing

You won't always know in advance whether more thinking helps a task. Later in the curriculum you'll learn to test this properly: run the same set of examples at different effort levels, and compare quality against cost and speed. Often a lower effort level is just as good, and much cheaper.

</div>

### What reasoning doesn't fix

Thinking makes models better at working things out, not at knowing things they never learned. A reasoning model can still state false facts with confidence, and it can produce a long, convincing chain of reasoning that rests on a wrong assumption. The visible reasoning also isn't guaranteed to be a faithful record of how the model actually reached its answer. Treat it as a helpful signal, not as proof. The next lesson digs into where wrong answers come from.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Watch the reinforcement learning chapters of Andrej Karpathy's [Deep Dive into LLMs like ChatGPT](https://www.youtube.com/watch?v=7xTGNNLPyMI).
   - Watch "models need tokens to think" (1:46:56 to 2:01:11), then "supervised finetuning to reinforcement learning," "reinforcement learning" and "DeepSeek-R1" (2:07:28 to 2:42:07). These explain, better than anything else available for free, why reasoning models work.
1. Read Anthropic's [thinking documentation](https://platform.claude.com/docs/en/build-with-claude/thinking).
   - Read the introduction and "How thinking works." Skim the configuration table to see how different models handle thinking. Skip the sections on tools, caching and streaming for now; you'll meet those later.
1. Read the "Effort levels" section of Anthropic's [steering thinking guide](https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost) to see how a real API lets you trade depth against cost.
1. Compare quick and careful answers yourself, using any free chat app that offers a reasoning or "thinking" mode.
   - Pick three questions: a simple fact, a multi-step word problem, and a logic puzzle (search for "river crossing puzzle" if you need one). Ask each with thinking off and with thinking on.
   - Record in your learning journal whether the answers differed, which were correct, and roughly how long each took. Did thinking help on the simple fact?

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- Anthropic's [Claude's extended thinking](https://www.anthropic.com/research/visible-extended-thinking) discusses the benefits and open questions of making a model's reasoning visible, including whether it faithfully reflects what the model is doing.
