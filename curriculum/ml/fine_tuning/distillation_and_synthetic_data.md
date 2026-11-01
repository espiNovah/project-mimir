### Introduction

Fine-tuning a custom model requires training data: hundreds or thousands of high-quality examples of inputs paired with ideal outputs. In many practical business domains, however, real human-labeled data is scarce, expensive to create, or locked behind strict privacy regulations that forbid shipping customer records to an external labeling team.

The solution that powers modern small models is **synthetic data generation** and **knowledge distillation**.

Instead of paying human annotators to write thousands of demonstrations, you use a frontier model as a "teacher" to generate, critique, and label training examples. You then train a compact, lightweight open model (the "student") on this curated dataset using the techniques from [LoRA Fine-Tuning](#/paths/ml). The resulting student model matches or exceeds the teacher's accuracy on the target task, while running at 10x lower latency and a fraction of the cost.

This lesson covers the end-to-end distillation pipeline: how to prompt teacher models to generate diverse datasets, how to filter out low-quality and repetitive generations, how to apply rejection sampling, and how to avoid the pitfalls of synthetic data loops and provider licensing restrictions.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The distinction between classical logit-level distillation and modern sequence-level text distillation.
- Prompting strategies for generating diverse synthetic training pairs (Self-Instruct, evol-instruct, and personas).
- Automated quality filtering: schema validation, rule-based heuristics, and LLM-as-judge scoring.
- Rejection sampling and execution-based verification: keeping only verified outputs.
- The risk of model collapse and synthetic degradation across multiple generations.
- How to generate synthetic datasets across different model providers, and understanding provider terms of service.

### Classical distillation versus sequence distillation

Knowledge distillation has evolved through two distinct eras:

#### 1. Classical logit distillation (Hinton et al., 2015)
In classical machine learning, distillation trains a student model to match the exact probability distribution (the output logits) of a larger teacher model. The loss function minimizes the Kullback-Leibler (KL) divergence between the teacher's softmax probabilities and the student's softmax probabilities.

This requires access to the teacher's full internal probability vector across the entire vocabulary. For proprietary frontier models served over HTTP APIs, providers do not return full probability distributions. Consequently, logit distillation is only possible when both the teacher and student are locally hosted open models.

#### 2. Sequence-level distillation (Black-box distillation)
In modern generative AI, distillation is treated as a dataset creation problem:
1. Prompt a frontier teacher model (such as the [capable model](#/models)) to generate thousands of input-output pairs.
2. Filter and score the generated pairs to remove hallucinations and formatting errors.
3. Train the compact student model using standard Supervised Fine-Tuning (SFT) cross-entropy loss on the filtered dataset.

The student model never sees the teacher's internal weights or logits. It simply learns to imitate the teacher's high-quality reasoning and output formatting.

### Generating synthetic training pairs with frontier models

If you ask a model: "Write 1,000 customer service inquiries and responses," it will quickly produce repetitive variations of the same three scenarios. Generating a dataset that trains a robust model requires deliberate prompt diversity techniques:

#### 1. The Self-Instruct recipe
Introduced by Wang et al. (2022), **Self-Instruct** bootstraps a large dataset from a small seed set of human-written examples (typically 50 to 100):
- Sample 3 to 5 random seed tasks from the pool.
- Prompt the model: "Here are 3 diverse tasks. Generate 1 new, completely different task following the same format."
- Generate input data and corresponding output solutions for the new task.
- Filter out tasks with low diversity or high lexical overlap (e.g., using ROUGE similarity against existing items).
- Add the accepted task back into the seed pool and repeat.

#### 2. Persona and scenario expansion
Prompt the generator to adopt hundreds of distinct personas, experience levels, and emotional states:
- "You are a frustrated senior database administrator diagnosing an intermittent connection pool timeout."
- "You are a non-technical small business owner trying to understand why an invoice payment was flagged."

#### 3. Complexity evolution (Evol-Instruct)
Take a simple prompt and instruct the model to deepen its complexity:
- "Add a subtle edge case involving timezone transitions across daylight saving time."
- "Introduce contradictory constraints that require prioritizing data integrity over speed."

```python
# generate_synthetic.py: Generating diverse synthetic task pairs with a frontier model
import json
import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()
MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")

SEED_PROMPT = """
You are creating training data to teach a small 3B open model how to extract structured event logs.
Generate 1 realistic, messy, multi-line server log snippet containing timestamp, service name, log level, and an error message.
Then provide the exact JSON extraction.

Format your response as valid JSON matching this schema:
{
  "raw_log": "...",
  "extracted": {
    "timestamp": "ISO-8601 string",
    "service": "string",
    "level": "INFO | WARN | ERROR",
    "message": "string"
  }
}
"""

def generate_example() -> dict:
    response = client.messages.create(
        model=MODEL,
        max_tokens=600,
        temperature=0.8,  # Higher temperature encourages diverse scenarios
        messages=[{"role": "user", "content": SEED_PROMPT}]
    )
    raw_content = response.content[0].text
    # Parse and validate JSON structure
    return json.loads(raw_content)
```

### Quality filtering, deduplication, and schema validation

Raw synthetic output is noisy. If you train a small model on unfiltered model outputs, it will memorize the teacher's hallucinations, verbosity, and refusal patterns.

A production synthetic pipeline applies four filtering gates:

```text
[ Raw Teacher Generations ]
            |
            v
   [ 1. Syntax & Schema Gate ] ---> Drop invalid JSON / Malformed formats
            |
            v
   [ 2. Heuristic Filter ]   ---> Drop length outliers, refusals ("As an AI..."), repetitive loops
            |
            v
   [ 3. Deduplication ]      ---> Drop high-cosine-similarity or n-gram duplicates
            |
            v
   [ 4. Automated Judge ]    ---> LLM-as-judge or unit test verification
            |
            v
[ Clean Fine-Tuning Dataset ]
```

1. **Schema validation:** Using Pydantic or JSON Schema from [Structured Outputs](#/paths/core) to reject any sample that fails strict type checking.
2. **Rule-based heuristics:** Reject samples that contain model boilerplate ("Here is the extraction:", "Sure, I can help with that"), excessive repetition, or extreme length outliers.
3. **Semantic deduplication:** Compute embeddings for all generated inputs using a fast local embedding model. Reject any new example whose cosine similarity exceeds 0.85 against existing examples, ensuring broad coverage of the problem space.
4. **LLM-as-judge scoring:** Use a secondary prompt on a [capable model](#/models) to evaluate whether the extraction is faithful to the raw input, rejecting any sample that scores below a threshold.

### Rejection sampling and execution-based verification

For tasks with objectively verifiable answers (such as code generation, mathematical reasoning, SQL queries, or regex extraction), you can replace subjective LLM judges with **execution-based rejection sampling**.

Instead of asking the model once:
1. Sample `N` candidate answers (e.g. `N = 8`) from the teacher model at a high temperature (`T = 0.8`).
2. Run each candidate through an automated test suite, Python interpreter, or SQL database.
3. If an answer passes all unit tests, it is accepted into the training set.
4. If multiple candidates pass, keep the shortest or most readable solution.
5. If zero candidates pass, discard the prompt entirely.

This was the core methodology behind Microsoft's **Phi-1 ("Textbooks Are All You Need")** and OpenAI's **GSM8K/MATH** alignment. By training small models strictly on code and reasoning that passed unit tests, small 1.3B to 3B models matched the reasoning performance of models 20 times their size.

### The risk of model collapse and synthetic degradation

While synthetic data is powerful, training models iteratively on their own output carries a serious risk known as **model collapse** (Shumailov et al., 2024).

When a model generates data, it samples from the center of its probability distribution (the most probable words). The long tail of rare, idiosyncratic, or complex human language is underrepresented.

If Generation 1 trains on human data, Generation 2 trains on Generation 1's synthetic output, and Generation 3 trains on Generation 2, each generation loses information about the distribution's tails:
- Vocabulary shrinks and text becomes repetitive.
- Low-probability facts are forgotten entirely.
- Hallucinations and subtle systemic biases are amplified.

**How to prevent model collapse in practice:**
- Always anchor synthetic datasets with real human data (the "seed" dataset).
- Use execution verification (tests, compilers, deterministic parsers) rather than unconditional text generation.
- Combine synthetic task-specific training data with a small replay buffer of general human-written conversations to preserve general reasoning.

### Provider terms and licensing considerations

Before generating thousands of training examples with a commercial API, check the provider's Terms of Service (ToS):

- **Commercial API restrictions:** Many commercial API providers (including OpenAI and Anthropic) have terms stating that you may not use their model's outputs to train or fine-tune models that directly compete with their core commercial services.
- **Permissible use cases:** Using API outputs to train internal, domain-specific enterprise models (such as an internal ticket classifier or a proprietary invoice parser) is widely accepted in commercial practice.
- **Permissive open models:** If you need absolute legal certainty for distributing an open-source model weights release, use open-weights teacher models with permissive licenses (such as Llama 3.1, Qwen 2.5, or Mistral) hosted on your own infrastructure to generate synthetic datasets.

### On other providers

The code example in this lesson used the Anthropic Python SDK. The exact same data generation workflow works with OpenAI, Google Gemini, or local open models running on vLLM:

- **OpenAI:** Call `client.chat.completions.create` with `response_format={"type": "json_object"}` or use Pydantic with `client.beta.chat.completions.parse`.
- **vLLM / Open Models:** Set `base_url="http://localhost:8000/v1"` with an open teacher model like Qwen-2.5-72B-Instruct. Open teacher models have no restrictions on using outputs for fine-tuning smaller student models.
- **Structured output consistency:** Regardless of provider, always parse and validate synthetic data with Pydantic before saving it to your training JSONL file.

```python
# Calling an open-weights teacher model via vLLM
from openai import OpenAI

vllm_client = OpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY")
response = vllm_client.chat.completions.create(
    model="Qwen/Qwen2.5-72B-Instruct",
    messages=[{"role": "user", "content": SEED_PROMPT}],
    temperature=0.7,
)
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Self-Instruct: Aligning Language Models with Self-Generated Instructions (Wang et al., 2022)](https://arxiv.org/abs/2212.10560).
   - Read Sections 1 through 3. Pay special attention to the task generation prompt and how heuristic filtering removes redundant instructions.
1. Read the groundbreaking research paper on high-quality synthetic curricula: [Textbooks Are All You Need (Gunasekar et al., 2023)](https://arxiv.org/abs/2306.02707).
   - Read how the authors used a large language model to create synthetic Python textbooks and exercises, allowing a compact 1.3B model (Phi-1) to outperform much larger baselines.
1. Explore [Distilabel documentation](https://distilabel.argilla.io/latest/), a widely used open-source framework specifically built for LLM synthetic data generation and filtering.
   - Review their pipeline concepts: generator steps, preference rating steps, and dataset export.
1. Write a standalone Python script named `synthetic_pipeline.py`:
   - Define a Pydantic model representing a customer support ticket: `ticket_id`, `category` (one of "Billing", "Technical", "Account"), `priority` ("Low", "Medium", "High"), and `customer_message`.
   - Write a generator function that calls a model to produce 5 synthetic tickets using temperature 0.8.
   - Write a validation function that verifies the Pydantic schema and rejects any ticket containing fewer than 10 words in the message.
   - Save the valid tickets to a `synthetic_train.jsonl` file ready for Supervised Fine-Tuning.

</div>

### Knowledge check

The questions below confirm that you have mastered the core ideas in this lesson. Click any question to review the section that explains it.

- [What is the difference between logit distillation and sequence-level text distillation?](#classical-distillation-versus-sequence-distillation)
- [How does the Self-Instruct algorithm prevent synthetic data from becoming repetitive?](#generating-synthetic-training-pairs-with-frontier-models)
- [What four filtering gates should every production synthetic data pipeline enforce?](#quality-filtering-deduplication-and-schema-validation)
- [What is execution-based rejection sampling and why is it superior to subjective scoring for code tasks?](#rejection-sampling-and-execution-based-verification)
- [What is model collapse and how do you protect a fine-tuning dataset from it?](#the-risk-of-model-collapse-and-synthetic-degradation)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The Curse of Recursion: Training on Generated Data Makes Models Forget (Shumailov et al., Nature 2024)](https://arxiv.org/abs/2305.17493) is the landmark paper analyzing the mathematical causes of model collapse.
- [Hugging Face: Cosmopedia](https://huggingface.co/datasets/HuggingFaceTB/cosmopedia) is a 30-million-page synthetic dataset of textbooks, stories, and tutorials generated by Mixtral-8x7B.
- [Alpaca: A Strong, Replicable Instruction-Following Model (Stanford CRFM)](https://crfm.stanford.edu/2023/03/13/alpaca.html) is the original blog post demonstrating that a 7B model can be tuned for $500 of synthetic data.