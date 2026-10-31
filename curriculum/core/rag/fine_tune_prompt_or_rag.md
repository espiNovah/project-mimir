### Introduction

"Should we fine-tune a model on our data?" is one of the most common questions an AI engineer gets, and the most common right answer is "not yet." **Fine-tuning** means continuing to train a model on your own examples, which changes its weights. Prompting and retrieval change what the model *sees*, and leave the weights alone. Each solves different problems, at very different costs, and choosing badly wastes weeks.

You've now used all the cheaper tools: prompting in the Prompt Lab, a classic classifier in Beat the Baseline, and retrieval through this whole section. This lesson closes the RAG section with a decision framework you can defend in a design review or an interview, built on the evaluation habits you've practiced since Why Evals Matter. The hands-on side of fine-tuning lives in the optional [ML Foundations elective](#/lessons/ml/lora-fine-tuning); here you'll learn when it's worth going there.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What prompting, retrieval (RAG) and fine-tuning each change.
- Knowledge problems versus behavior problems.
- The usual order to try things in, and why.
- When fine-tuning genuinely wins: format, style, narrow tasks, cost and latency.
- The hidden costs of fine-tuning: data, evaluation, serving and maintenance.
- Using an eval and cost math to make the decision with numbers.
- A decision checklist, with worked scenarios.

### What each option changes

Think of a model call as three layers, from fastest to change to slowest:

- **Prompting changes the instructions.** The system prompt, a few examples, the output format, the rules. A change ships in minutes, and you can test it against your eval set the same afternoon.
- **Retrieval changes the knowledge in the context.** RAG fetches relevant documents at request time and puts them in front of the model, so it answers from your data instead of from memory. Updating the knowledge means re-indexing documents, which you built to do incrementally in Chat With Your Docs. No training involved.
- **Fine-tuning changes the model itself.** You train on hundreds to thousands of input-output examples, and the model's weights shift so the behavior you showed it becomes its default. A change means collecting data, training, evaluating and redeploying a model.

A fourth option sits underneath all three, and it's easy to forget once you have LLMs: a **classic model**, like the TF-IDF classifier from Beat the Baseline. For narrow, high-volume classification, it may be good enough on its own.

### Knowledge problems and behavior problems

The most useful question to ask about a failing system is: **does the model lack facts, or does it have the facts and behave wrongly?** Error analysis tells you which. Read the failing traces and sort them.

**Knowledge problems** look like this: the answer is wrong because the model doesn't know your refund policy, last week's release notes or a customer's order history. The fix is almost always retrieval. Fine-tuning is a poor and expensive way to add facts. Models trained on a few documents learn the facts unreliably, can't tell you where an answer came from, and go stale the moment a document changes, while RAG gives you citations and updates with a re-index. You built the citations-and-grounding machinery in the previous lesson exactly because answers need to be traceable to sources, which a fine-tuned model's memory can't offer.

**Behavior problems** look like this: the model has what it needs, but the output is in the wrong format, the wrong tone, too long, or inconsistent about which label to use. The fixes, in order, are better prompting (clearer instructions, a few good examples, structured outputs), and then, if prompting plateaus, fine-tuning. Fine-tuning is at its best here, because behavior is a pattern that hundreds of examples can teach.

Many real failures are both. A support bot might give a vague answer (behavior) about a policy it never saw (knowledge). Fix the knowledge first with retrieval, re-run your eval, and see what behavior problems remain.

### Try them in order of cost

The usual order follows cost and speed of iteration:

1. **A clear prompt** with a few examples and, if needed, structured outputs. Measure it on your eval set.
1. **Add retrieval** if the failures are missing knowledge.
1. **Improve the prompt and retrieval together** using error analysis: better chunking, hybrid search, a reranker, clearer rules for when to say "I don't know."
1. **Try a different model.** A more capable model, or the same one with more thinking, can fix behavior problems with no training. Price it at your real volume.
1. **Consider fine-tuning** only when you have an eval showing prompting has plateaued, and enough good labeled examples (often hundreds to thousands) to train on.

Each step is cheaper and faster to undo than the next. Most teams that jump straight to fine-tuning skip the steps that would have told them whether they needed it, and then they have no baseline to prove the fine-tuned model is better. Prompting first also produces something you need later anyway: a working eval set, and often the labeled data that a fine-tune would be trained on.

### When fine-tuning wins

Fine-tuning shines on **narrow, high-volume tasks with a stable definition of "correct."** Good fits:

- **Classification** into a fixed set of labels, such as the 77 Banking77 intents.
- **Extraction into a fixed schema**, like your Messy-Text Extractor, at millions of documents a month.
- **A house style** that's hard to describe but easy to show: a specific brand voice, or a terse format your downstream code expects.
- **Shrinking the prompt.** If your prompt has grown to 3,000 tokens of rules and examples, a fine-tuned model can learn them, so each call sends 300 tokens instead.

The big prize is cost and latency. A fine-tuned *small* open model can often match a much larger prompted model on such a task, while being far cheaper and faster, and it can run on your own hardware, which matters when data isn't allowed to leave your servers. A popular way to get the training data is **distillation**: label inputs with a large, capable model, check the labels, then train a small model to copy it. The ML elective's [Distillation and Synthetic Data](#/lessons/ml/distillation-and-synthetic-data) lesson covers it.

Fine-tuning is a weak fit for tasks that change often, for open-ended reasoning, and for anything where the facts move. It's also not always available: some hosted providers let you fine-tune their models and some don't, while open models can always be fine-tuned if you can run them.

There's one more kind of fine-tuning worth knowing in a RAG context: fine-tuning the **embedding model**, so retrieval itself improves on your domain's vocabulary. It leaves the generating model alone, and it's covered in the elective's [Fine-Tuning Embeddings](#/lessons/ml/fine-tuning-embeddings) lesson.

### The hidden costs of fine-tuning

The training run is the cheap part. A fine-tuned model also needs:

- **Clean training data.** Hundreds to thousands of examples with correct labels. Wrong labels get learned faithfully. Someone has to write or review them, which is the same labeling work as in Error Analysis and Labeling, only more of it.
- **A held-out test set and a baseline.** Without them, you can't show the fine-tuned model is better than the prompt it replaced. The test set must be frozen before training, as in Beat the Baseline.
- **GPU time and a way to serve the model.** For an open model, that's a GPU host that's up when traffic arrives, which you'll explore in the elective's [Serving Open Models](#/lessons/ml/serving-open-models) lesson.
- **A plan to retrain.** When the task changes (a new intent, a new field in the schema) or a better base model comes out, you redo the data, training and evaluation. A prompt change ships in minutes; a retrain does not.
- **Owning the failures.** A fine-tuned model can lose general abilities it used to have, and when it misbehaves there's no prompt to read to see why.

### The techniques combine

These aren't exclusive choices. Many production systems use several at once:

- A **fine-tuned model inside a RAG pipeline**: retrieval supplies the facts, fine-tuning makes the answer format and tone consistent.
- A **router**: a small classic or fine-tuned model handles the easy bulk of requests, and only the uncertain ones (low confidence) go to a capable frontier model.
- A **classic classifier in front of an LLM**: TF-IDF decides which of five prompts or indexes to use, in well under a millisecond, before the expensive call.

### Decide with an eval

Decide with numbers, not a hunch. Compare the options on **the same held-out test set**, with the metrics that matter: quality (with a confidence interval and a paired comparison, as in Eval Statistics), cost per 1,000 calls, and latency. Your traces from the LLM-Powered API already record tokens and timings, so you have the inputs.

Cost depends heavily on volume, so put your real numbers into a small script. Here's one for a routing task at 2 million messages a month. The prices are the [cheap and capable models'](#/models) prices at the time of writing; the GPU price and throughput are assumptions you'd replace with measurements.

```python
# monthly_cost.py: what each option costs at a given volume. Every number is an
# assumption you should replace with your own measurements.
CALLS_PER_MONTH = 2_000_000

# API models: (price per million input tokens, per million output, input tokens, output tokens)
api_options = {
    "capable model, long few-shot prompt": (2.00, 10.00, 2_500, 20),
    "cheap model, long few-shot prompt":   (0.10, 0.50, 2_500, 20),
    "cheap model, short prompt":           (0.10, 0.50, 300, 20),
}
for name, (in_price, out_price, in_tok, out_tok) in api_options.items():
    per_call = (in_tok * in_price + out_tok * out_price) / 1_000_000
    print(f"{name:38} ${per_call * 1000:6.3f} per 1k calls   ${per_call * CALLS_PER_MONTH:9,.0f} / month")

# A fine-tuned small open model on a rented GPU: you pay for hours, not tokens.
GPU_PER_HOUR = 1.00          # assumed rental price for one small GPU
MESSAGES_PER_SECOND = 50     # assumed throughput, measured with batching
hours = CALLS_PER_MONTH / MESSAGES_PER_SECOND / 3600
print(f"{'fine-tuned small model, rented GPU':38} {hours:5.1f} GPU hours      ${hours * GPU_PER_HOUR:9,.0f} / month"
      "  (if the GPU is only on while working)")
print(f"{'  ...same GPU kept on all month':38} {24 * 30:5} GPU hours      ${24 * 30 * GPU_PER_HOUR:9,.0f} / month")
```

```text
capable model, long few-shot prompt    $ 5.200 per 1k calls   $   10,400 / month
cheap model, long few-shot prompt      $ 0.260 per 1k calls   $      520 / month
cheap model, short prompt              $ 0.040 per 1k calls   $       80 / month
fine-tuned small model, rented GPU      11.1 GPU hours      $       11 / month  (if the GPU is only on while working)
  ...same GPU kept on all month          720 GPU hours      $      720 / month
```

Three lessons hide in that output. First, the model you pick moves cost by a factor of 20, so check whether the cheap model is good enough before anything else. Second, prompt length is a cost lever too: shortening the prompt saved more than switching models would have. Third, the fine-tuned model is only dramatically cheaper if the GPU is busy. A GPU kept on all month for traffic that arrives a little at a time costs more than the cheap API model. Real numbers vary with traffic shape, batching and provider features (such as prompt caching, covered in the Production path), which is exactly why you write the script with your own inputs instead of trusting a rule of thumb. And don't forget the classic baseline: the TF-IDF classifier from Beat the Baseline costs effectively nothing on a CPU, so the question is always whether the extra macro-F1 of the alternatives is worth their bill.

### A decision checklist

Work through these questions in order, writing down the evidence for each answer:

1. **What does failure look like?** Do error analysis on real traces first. Without it, you're guessing which problem you have.
1. **Is it a knowledge problem?** If answers need facts the model doesn't have, or facts that change, use retrieval.
1. **Is it a behavior problem that a better prompt fixes?** Try clearer instructions, examples, structured outputs and a more capable model, measured on your eval set.
1. **Has prompting plateaued, by the numbers?** You need an eval showing several serious prompt versions, with intervals, all stuck below the bar you need.
1. **Is the task narrow, stable and high-volume?** If it changes monthly or runs a few hundred times a day, fine-tuning rarely pays back.
1. **Do you have the data?** Hundreds to thousands of correct examples, plus a frozen test set the training never sees.
1. **Can you serve and maintain it?** Someone owns the GPU, the retraining and the regression tests.
1. **Does a classic model already do it?** Check the baseline numbers before any of the above.

Fine-tuning is the right answer only when questions 4 through 7 all come back "yes."

### Worked scenarios

**A legal team wants answers from 3,000 contracts that change every week.** The failures will be about specific clauses in specific contracts: a knowledge problem with fast-moving facts. Use RAG with citations, so lawyers can check every answer against the source page. Fine-tuning would bake in last month's contracts and couldn't cite them. Evidence that would change your mind: none for fine-tuning the generator, but if retrieval recall is poor on legal jargon, consider fine-tuning the embedding model.

**An insurer extracts 15 fields from 4 million claim forms a month.** Start with the cheap model and structured outputs, measured per field with intervals, as in your Messy-Text Extractor. If quality is good enough, run the cost script: at this volume the bill is real but may still be fine. If quality is good only with a long, expensive prompt or the capable model, the task is narrow, stable and huge, which is the textbook case for distilling into a fine-tuned small model. Evidence needed first: a frozen test set, a plateaued prompt, and a few thousand checked examples (which the capable model can help label).

**A startup's chatbot sometimes ignores the rule "never promise a delivery date."** That's a behavior problem, but one rule doesn't justify training. Put it clearly in the system prompt, add examples, add a code check or guardrail that catches dates in the output, and add these cases to the eval. If it still fails often after all that, a more capable model is the next step, not a fine-tune.

**A bank routes 500 internal IT tickets a day into 12 queues.** Low volume and a narrow task. A TF-IDF classifier trained on last year's labeled tickets may already be good enough, costs nothing to run, and the cheap model is a fine alternative if there's little labeled data. Compare both on the same test set. Fine-tuning an LLM here would add a GPU bill and a maintenance job to save almost nothing.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the fine-tuning section of [Eugene Yan's Patterns for Building LLM-based Systems and Products](https://eugeneyan.com/writing/llm-patterns/), a widely cited practitioner guide. It's from 2023, so the model names are dated, but the reasoning about when to fine-tune has held up.
   - Read the sections on fine-tuning and retrieval-augmented generation, and note his reasons for and against fine-tuning.
1. Read the opening page of the [fine-tuning chapter of the Hugging Face LLM Course](https://huggingface.co/learn/llm-course/chapter11/1) for the open-model view on when and why to fine-tune.
1. Read [What We've Learned From A Year of Building with LLMs](https://applied-llms.org/), written by a group of experienced practitioners.
   - Read the tactical and operational sections on prompting versus RAG versus fine-tuning, and on starting with evals.
1. Read [OpenAI's guide to optimizing LLM accuracy](https://developers.openai.com/api/docs/guides/optimizing-llm-accuracy). It frames the same decision as two axes, context optimization (what the model needs to know) and LLM optimization (how it needs to act), which matches this lesson's knowledge-versus-behavior split. The ideas apply to any provider.
1. Practice: for each of these scenarios, write one paragraph choosing prompting, RAG, fine-tuning or a classic model, using the checklist above, and say what evidence would change your mind.
   - An assistant that answers questions about a company's 500-page HR handbook.
   - A system that routes two million support messages a month to one of 77 intents. Use your own Beat the Baseline numbers and adapt `monthly_cost.py` with your real token counts.
   - A tool that rewrites marketing copy in a very specific brand voice.
   - A chatbot that must always reply in valid JSON.
   - Add your paragraphs to your Chat With Your Docs README under a "Design decisions" heading, since it's the kind of reasoning interviewers ask about.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What do prompting, retrieval and fine-tuning each change?](#what-each-option-changes)
- [Why is retrieval usually better than fine-tuning for adding knowledge?](#knowledge-problems-and-behavior-problems)
- [In what order should you try the options, and why?](#try-them-in-order-of-cost)
- [What kinds of tasks are good fits for fine-tuning?](#when-fine-tuning-wins)
- [Name four costs of fine-tuning besides the training run.](#the-hidden-costs-of-fine-tuning)
- [Why can a fine-tuned small model cost more than an API model, and what should you measure to find out?](#decide-with-an-eval)
- [Which checklist questions must all be "yes" before you fine-tune?](#a-decision-checklist)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Anthropic's Contextual Retrieval post](https://www.anthropic.com/news/contextual-retrieval) shows how far retrieval improvements alone can go before anyone reaches for training, with measured gains from contextual embeddings, BM25 and reranking.
- The ML elective's [Fine-Tune a Small Model](#/lessons/ml/project-fine-tune-a-small-model) project runs this lesson's decision for real: a LoRA fine-tune, a prompted frontier model and your Beat the Baseline classifier on one frozen test set, with cost and latency.
