### Introduction

In production software engineering, evaluations answer a practical operational question: *Does this agent solve our user tickets reliably enough to deploy?*

In scientific research, however, experiments must answer a much more demanding question:
> **Is our proposed method genuinely superior to alternative approaches, by exactly how much, and what specific architectural mechanism causes that improvement?**

Demonstrating that an agent scores 78% on a benchmark is not a research contribution if:
- The baseline against which it was compared was untuned, hobbled, or ran with a tenth of the token budget.
- The 5% improvement over the baseline is smaller than the random run-to-run seed variance.
- The improvement came from a longer system prompt rather than the novel memory module claimed in the title.

This lesson explores the principles of rigorous scientific experiment design: formulating falsifiable hypotheses, selecting fair baselines, isolating causal factors through ablation studies, calculating statistical confidence intervals and paired significance tests, and enforcing hermetic environment hygiene in agent evaluations.

### Formulating falsifiable research hypotheses

A valid scientific experiment begins with a **falsifiable hypothesis** specifying:
1. The **independent variable (manipulation):** The specific algorithmic intervention under test.
2. The **dependent variable (measurement):** The exact quantitative metric observed.
3. The **control conditions:** What variables are held constant (model checkpoint, temperature, token budget, tool interfaces).
4. The **expected effect size and direction:** The quantitative threshold for success.

```text
Vague Statement (Unscientific):
"Our multi-agent debate framework makes language models reason better."

Falsifiable Research Hypothesis (Scientific):
"On 100 GSM8K math problems, a 3-agent debate architecture with Claude 3.5 Haiku will achieve 
a higher pass@1 accuracy than a single-agent Chain-of-Thought baseline matched for total token budget 
(N=3 self-consistency samples), with a statistically significant paired difference (p < 0.05, McNemar's test)."
```

### Baselines: the cornerstone of empirical truth

A novel method is only as impressive as the baseline it defeats. In AI research, the most common form of unintentional self-deception is comparing against a strawman baseline:

1. **The Untuned Baseline Trap:** The authors spend three weeks tuning prompts, temperature, and few-shot examples for their new algorithm, but run the baseline using default parameters from an out-of-date library.
2. **The Compute/Token Disparity:** A paper claims that their multi-agent framework beats standard prompting by 12%, but omits that the multi-agent system consumed 15,000 tokens per problem across 6 API calls, while the baseline was given a single prompt limited to 500 tokens. A fair baseline must be **compute-matched** (e.g. comparing multi-agent against single-agent with `N=10` self-consistency or extended test-time thinking).
3. **The Simplest Possible Alternative:** Before claiming that a complex graph-based memory system is necessary, test the simplest alternative: does concatenating the raw history into the prompt achieve the same accuracy?

### Ablation studies: isolating causal mechanisms

An **ablation study** systematically removes or modifies individual components of a complex system to determine how much each component contributes to overall performance:

![Scientific Experiment Design: Ablations, Controls, and Paired Testing](assets/images/ablation_study_design.svg)

#### Best practices for ablation design

- **Leave-One-Out (Ablative) Testing:** Start with the full system `(A + B + C)`. Create variants where exactly one component is disabled: `w/o A`, `w/o B`, `w/o C`.
- **Cumulative (Constructive) Testing:** Start with the simplest bare baseline, adding components sequentially: `Base → Base + A → Base + A + B → Full`.
- **Negative Controls & Sanity Checks:** Replace an active component with random noise or an inverted operator. For example, if you claim that a dense vector retrieval module retrieves the most relevant memories for an agent, test an ablation where memories are retrieved in **completely random order**. If performance does not drop significantly, your retrieval module's semantic ranking is irrelevant.

### Statistical estimation and significance in evaluations

Every evaluation run on an LLM benchmark is a finite sample from a stochastic distribution. Reporting a single point estimate (e.g., *"Our agent achieved 64.0%"*) without error bars obscures whether differences are real or statistical noise.

#### Standard error of a proportion

For a benchmark of `N` independent tasks where each task is scored as success (`1`) or failure (`0`), the sample pass rate `p = S / N` has standard error:

```text
SE = sqrt( p * (1 - p) / N )
```

For `N = 100` and `p = 0.60`:
```text
SE = sqrt( 0.60 * 0.40 / 100 ) = sqrt( 0.0024 ) = 0.049 (4.9%)
```
A 95% confidence interval spans roughly `± 1.96 * SE ≈ ± 9.6%`. A score of 60% on 100 tasks means true performance lies anywhere between 50.4% and 69.6%! To detect a genuine 3% difference, you need thousands of tasks or paired statistical tests.

#### Paired comparisons: eliminating task-difficulty variance

In standard benchmarking, System A and System B are evaluated on the exact same set of `N` tasks. 

Comparing the independent mean pass rates of System A and System B ignores the fact that some tasks are universally easy (both pass) and some tasks are universally hard (both fail). 

**McNemar's Test** analyzes only the **discordant pairs**:
- `b`: Tasks where System A succeeded but System B failed.
- `c`: Tasks where System B succeeded but System A failed.

```text
χ² = ( |b - c| - 1 )^2 / ( b + c )
```

Paired testing subtracts out task-difficulty noise, dramatically increasing statistical power to detect real algorithmic differences with smaller sample sizes.

#### Statistical power analysis

Before running an expensive experiment, calculate the sample size `N` required to detect an expected difference `Δ = |p_A - p_B|` with statistical power `1 - β = 0.80` at significance `α = 0.05`:

```text
N ≈ 16 * p_avg * (1 - p_avg) / Δ^2
```

If you anticipate a 5% gain (`Δ = 0.05`) around baseline `p = 0.50`, you need roughly:
```text
N ≈ 16 * 0.25 / 0.0025 = 1,600 task evaluations!
```
Evaluating 50 tasks is incapable of resolving single-digit improvements with statistical confidence.

### Agent-specific experimental hygiene

Evaluating autonomous agents involves unique challenges compared to standard classification models:

1. **Hermetic Sandbox Isolation:** When an agent executes shell commands or edits code, it modifies files, environment variables, and installed packages. Running the next trial in the same container causes **state leakage** (e.g., test files left over from trial 1 allow trial 2 to pass trivially). Every trial must execute inside an ephemeral, freshly reset Docker container.
2. **Reliability Metrics: `pass@k` vs. `pass^k`:**
   - **`pass@k` (Exploration):** The probability that the agent succeeds at least once across `k` attempts. Useful for coding assistants where a human programmer reviews candidate patches.
   - **`pass^k` (Consistency / Tau-Bench):** The probability that the agent succeeds on **all `k` repeated attempts** on the identical task. Essential for fully autonomous customer-facing agents where even a 5% failure rate causes customer churn.
3. **Multi-Dimensional Scorecard:** Never report accuracy alone. Always report the joint Pareto frontier:
   - Success rate (%)
   - Input and output token consumption
   - Financial cost per task ($)
   - Wall-clock latency (seconds)
   - Unhandled tool exception rate (%)

### The reproducibility checklist

To guarantee that other researchers can replicate your findings, adhere to Joelle Pineau's **ML Reproducibility Checklist**:

- **Model Specification:** State exact frozen model snapshot strings (e.g., `claude-3-5-haiku-20241022`), never ephemeral aliases.
- **Decoding Hyperparameters:** Report exact temperature, `top_p`, presence/frequency penalties, and maximum output tokens.
- **System Prompts & Tool Schemas:** Commit the exact verbatim system prompts, few-shot examples, and JSON tool definitions to the public repository.
- **Environment & Seeds:** State Python version, package lockfiles (`uv.lock`), and fixed pseudo-random seeds.
- **Reporting Negative Results:** Report failed hypotheses and ablations that produced zero gain; negative results prevent the community from wasting collective compute.

### Python implementation: statistical tools for evaluation

Here is a Python utility to compute bootstrap confidence intervals, McNemar's paired significance test, and statistical power requirements:

```python
import numpy as np
from scipy import stats

def bootstrap_ci_mean(data: list[float], num_bootstraps: int = 10_000, ci: float = 0.95) -> tuple[float, float, float]:
    """Computes non-parametric bootstrap confidence intervals."""
    arr = np.array(data)
    boot_means = []
    for _ in range(num_bootstraps):
        sample = np.random.choice(arr, size=len(arr), replace=True)
        boot_means.append(np.mean(sample))
    
    alpha = 1.0 - ci
    lower = float(np.percentile(boot_means, 100 * (alpha / 2)))
    upper = float(np.percentile(boot_means, 100 * (1 - alpha / 2)))
    return float(np.mean(arr)), lower, upper

def mcnemar_paired_test(success_a: list[int], success_b: list[int]) -> tuple[float, float]:
    """
    Computes McNemar's test on paired binary task outcomes.
    Returns: (statistic, p_value)
    """
    assert len(success_a) == len(success_b), "Must be identical paired tasks"
    b = sum(1 for a, b_val in zip(success_a, success_b) if a == 1 and b_val == 0)
    c = sum(1 for a, b_val in zip(success_a, success_b) if a == 0 and b_val == 1)

    if (b + c) == 0:
        return 0.0, 1.0

    # Continuity corrected chi-squared
    stat = (abs(b - c) - 1.0) ** 2 / (b + c)
    p_val = 1.0 - stats.chi2.cdf(stat, df=1)
    return float(stat), float(p_val)

def required_sample_size(p_baseline: float, delta: float, alpha: float = 0.05, power: float = 0.80) -> int:
    """Estimates required sample size to detect a difference of delta with given power."""
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    p_target = p_baseline + delta
    p_avg = (p_baseline + p_target) / 2
    
    numerator = (z_alpha * np.sqrt(2 * p_avg * (1 - p_avg)) + z_beta * np.sqrt(p_baseline * (1 - p_baseline) + p_target * (1 - p_target))) ** 2
    n = numerator / (delta ** 2)
    return int(np.ceil(n))

if __name__ == "__main__":
    # Example: 100 paired benchmark tasks
    a_scores = [1]*70 + [0]*30
    b_scores = [1]*60 + [0]*40
    stat, p = mcnemar_paired_test(a_scores, b_scores)
    print(f"McNemar test statistic: {stat:.4f}, p-value: {p:.4f}")
    
    n_needed = required_sample_size(0.60, 0.05)
    print(f"Sample size needed to detect 5% gain with 80% power: {n_needed} tasks")
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read Anthropic's [Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents):
   - Review the formal definitions of task, trial, transcript, and grader.
   - Note the distinction between `pass@k` and `pass^k`.
2. Read [Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations](https://arxiv.org/abs/2411.00640) by Evan Miller (or Anthropic's [summary of the paper](https://www.anthropic.com/research/statistical-approach-to-model-evals)).
   - Study paired differences, clustered standard errors, and power analysis.
3. Review [Joelle Pineau's Machine Learning Reproducibility Checklist](https://www.cs.mcgill.ca/~jpineau/ReproducibilityChecklist.pdf) and the official [NeurIPS Paper Checklist Guidelines](https://neurips.cc/public/guides/PaperChecklist).
4. Read [Deep Reinforcement Learning that Matters](https://arxiv.org/abs/1709.06560) (Henderson et al.), noting how seeds, codebases, and evaluation protocols change empirical outcomes.
5. Practice: Take an evaluation script from one of your prior projects. Calculate 95% bootstrap confidence intervals for its pass rate, perform a power analysis to determine how many test cases are required to detect a 4% improvement with 80% power, and add McNemar's paired test to your evaluation pipeline.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The Deep Learning Tuning Playbook](https://github.com/google-research/tuning_playbook) from Google Research: Systematic scientific guidelines for hyperparameter tuning.
- [A Recipe for Training Neural Networks](https://karpathy.github.io/2019/04/25/recipe/) by Andrej Karpathy: Practical advice for finding silent bugs and building solid baselines.
- [Improving Reproducibility in Machine Learning Research](https://arxiv.org/abs/2003.12206): Meta-analysis of the NeurIPS reproducibility challenge.

### Knowledge check

Use these questions to verify your understanding of experiment design:

1. [What is the difference between a vague hypothesis and a falsifiable scientific hypothesis in machine learning research?](#formulating-falsifiable-research-hypotheses)
2. [Why is matching the total token budget essential when comparing a multi-agent system against a single-agent baseline?](#baselines-the-cornerstone-of-empirical-truth)
3. [How do ablation studies isolate the true causal source of improvement in a complex agent architecture?](#ablation-studies-isolating-causal-mechanisms)
4. [Why do paired comparisons like McNemar's test have significantly higher statistical power than unpaired two-sample t-tests?](#statistical-estimation-and-significance-in-evaluations)
5. [What is the critical difference between the pass@k metric and the pass^k metric in agent evaluation?](#agent-specific-experimental-hygiene)
