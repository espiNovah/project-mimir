### Introduction

Every established discipline in computer science possesses an implicit "canon"—a curated collection of foundational papers that researchers, research engineers, and doctoral candidates are expected to know intimately.

Because modern agentic AI emerged largely after 2020, the literature is fast-moving. Yet within this compressed timeline, a core body of roughly twenty seminal papers has defined the field's concepts, architectures, and benchmarks:
- When colleagues discuss the "ReAct pattern," they refer to Yao et al. (2022).
- When a coding agent uses an agent-computer interface, they draw on Yang et al. (2024).
- When developers debate verifiable rewards and test-time compute, they reference DeepSeek-R1 (2025).

This lesson provides an annotated reading roadmap through the 19 seminal papers that built the agentic AI landscape, grouped into six logical themes. Rather than reading randomly by publication date, this roadmap traces the conceptual evolution: from base transformers and alignment, to tool use, reflective cognitive loops, memory architectures, benchmarks, and defensive security.

### Foundations of large language models

Modern autonomous agents are built upon autoregressive foundation models. Understanding their mechanics and emergent capabilities is the prerequisite for all downstream systems:

1. **[Attention Is All You Need](https://arxiv.org/abs/1706.03762)** (Vaswani et al., 2017)
   - *Why it matters:* Introduced the Transformer architecture, replacing recurrent and convolutional neural networks with multi-head self-attention. It made massive parallel pretraining on GPUs computationally feasible.
   - *Key takeaway:* Self-attention allows any token to dynamically attend to any other token across the context window with `O(1)` path length, eliminating vanishing gradients across sequences.
2. **[Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165)** (Brown et al., 2020)
   - *Why it matters:* GPT-3 proved that scaling parameter count and dataset size alone causes **in-context learning** to emerge. A single frozen model can perform diverse tasks purely from in-context natural language demonstrations without gradient updates.
   - *Key takeaway:* Prompt engineering is not a trick; it is programming a general-purpose in-context pattern processor.
3. **[Chain-of-Thought Prompting Elicits Reasoning in Large Language Models](https://arxiv.org/abs/2201.11903)** (Wei et al., 2022)
   - *Why it matters:* Showed that prompting models to generate intermediate steps (`"Let's think step by step"`) dramatically boosts accuracy on multi-step arithmetic, symbolic reasoning, and logic benchmarks.
   - *Key takeaway:* Autoregressive transformers can dedicate variable test-time compute to difficult problems by generating additional reasoning tokens.

### Alignment and post-training

Raw pretrained base models simply predict the next token on the web. Post-training is the discipline that aligns these engines into helpful assistants and rigorous reasoning systems:

4. **[Training language models to follow instructions with human feedback](https://arxiv.org/abs/2203.02155)** (Ouyang et al., 2022)
   - *Why it matters:* InstructGPT introduced the three-stage RLHF pipeline: Supervised Fine-Tuning (SFT), Bradley-Terry Reward Modeling, and PPO with a per-token KL divergence penalty.
   - *Key takeaway:* A 1.3B parameter model trained with RLHF was preferred by human annotators over an untuned 175B base model, proving that post-training alignment yields orders of magnitude in effective quality.
5. **[Constitutional AI: Harmlessness from AI Feedback](https://arxiv.org/abs/2212.08073)** (Bai et al., 2022)
   - *Why it matters:* Anthropic demonstrated that human preference annotation can be automated by having an AI critique and revise its own outputs against a written constitution of principles (RLAIF).
   - *Key takeaway:* Scalable oversight can be achieved through self-critique guided by explicit rules, reducing human labeling bottleneck.
6. **[Direct Preference Optimization: Your Language Model is Secretly a Reward Model](https://arxiv.org/abs/2305.18290)** (Rafailov et al., 2023)
   - *Why it matters:* Proved that the KL-constrained RLHF objective can be solved analytically, eliminating the reward model and reinforcement learning rollouts entirely in favor of a stable binary cross-entropy loss.
   - *Key takeaway:* DPO democratized alignment, becoming the standard fine-tuning recipe for open-weights models.
7. **[DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning](https://arxiv.org/abs/2501.12948)** (DeepSeek-AI, 2025)
   - *Why it matters:* Demonstrated that training base models purely with reinforcement learning against programmatic verifiable rewards (unit tests, mathematical equality) autonomously elicits long chains of thought, self-correction, and backtracking without human demonstrations.
   - *Key takeaway:* Post-training with verifiable rewards creates a new scaling law along the test-time compute axis.

### Reasoning, tool use, and reflection

Once models could reason in prose, researchers gave them the ability to act on the world, call APIs, and inspect their own failures:

8. **[ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)** (Yao et al., 2022)
   - *Why it matters:* Interleaved internal reasoning traces (`"Thought"`) with external tool calls (`"Action"`) and feedback (`"Observation"`). This became the ubiquitous architectural skeleton of autonomous agents.
   - *Key takeaway:* Reasoning grounds action execution; observations ground subsequent reasoning.
9. **[Toolformer: Language Models Can Teach Themselves to Use Tools](https://arxiv.org/abs/2302.04761)** (Schick et al., 2023)
   - *Why it matters:* Showed that models can self-supervisedly annotate corpora with API calls (calculator, search, calendar) and fine-tune themselves to invoke tools natively whenever doing so reduces cross-entropy loss.
   - *Key takeaway:* Tool calling is not an external wrapper; it can be learned natively as part of language modeling.
10. **[Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366)** (Shinn et al., 2023)
    - *Why it matters:* Introduced episodic self-reflection: when an agent fails a task, an evaluator summarizes the mistake, and the agent writes a verbal critique into an episodic memory buffer that conditions its next attempt.
    - *Key takeaway:* Agents can perform trial-and-error learning at inference time without modifying model weights.
11. **[Tree of Thoughts: Deliberate Problem Solving with Large Language Models](https://arxiv.org/abs/2305.10601)** (Yao et al., 2023)
    - *Why it matters:* Generalized linear Chain-of-Thought into a tree search (BFS/DFS/A*), where the model generates multiple candidate thoughts, evaluates their promise, and prunes or backtracks from dead ends.
    - *Key takeaway:* Classical heuristic search algorithms can be grafted directly onto neural language generation.

### Memory, cognitive architectures, and embodiment

Long-horizon tasks require agents that persist across sessions, build skills, and navigate complex simulated or digital environments:

12. **[Generative Agents: Interactive Simulacra of Human Behavior](https://arxiv.org/abs/2304.03442)** (Park et al., 2023)
    - *Why it matters:* Deployed 25 autonomous agents in a sandbox town using a composite memory stream, periodic higher-level reflection, and recursive plan decomposition.
    - *Key takeaway:* Believable multi-agent social behavior emerges from clean cognitive memory and retrieval architectures.
13. **[Voyager: An Open-Ended Embodied Agent with Large Language Models](https://arxiv.org/abs/2305.16291)** (Wang et al., 2023)
    - *Why it matters:* The first autonomous lifelong learning agent in Minecraft. Voyager iteratively writes, executes, tests, and stores executable JavaScript control programs in an external skill library.
    - *Key takeaway:* An agent can build an open-ended curriculum of reusable procedural code skills, bootstrapping complex competencies from simple primitives.
14. **[MemGPT: Towards LLMs as Operating Systems](https://arxiv.org/abs/2310.08560)** (Packer et al., 2023)
    - *Why it matters:* Applied operating system memory virtualization concepts to LLMs: treating the context window as RAM and vector databases/disk as virtual storage, with the model managing its own paging via function calls.
    - *Key takeaway:* Context window constraints can be mitigated by giving the model explicit tools to read, write, and evict long-term memories.
15. **[Cognitive Architectures for Language Agents (CoALA)](https://arxiv.org/abs/2309.02427)** (Sumers et al., 2023)
    - *Why it matters:* Unified diverse LLM agent frameworks under the formal taxonomy of cognitive science: working, episodic, semantic, and procedural memory paired with action and decision cycles.
    - *Key takeaway:* Provides the standard academic taxonomy for evaluating and designing language agents.

### Benchmarks and evaluation methodology

In AI research, progress is defined by what we can measure. The transition from multiple-choice tests to execution-based interactive benchmarks shaped modern agent engineering:

16. **[SWE-bench: Can Language Models Resolve Real-World GitHub Issues?](https://arxiv.org/abs/2310.06770)** (Jimenez et al., 2023)
    - *Why it matters:* Replaced synthetic coding puzzles (HumanEval) with 2,294 real-world GitHub issues from popular Python repositories. Agents are given a repo and issue description, must locate the bug, edit files, and pass unseen regression test suites.
    - *Key takeaway:* Established the gold standard for evaluating autonomous software engineering agents.
17. **[SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering](https://arxiv.org/abs/2405.15793)** (Yang et al., 2024)
    - *Why it matters:* Demonstrated that the design of the **Agent-Computer Interface (ACI)**—such as custom file viewers, linters, and search tools—has an enormous impact on agent performance, rivaling gains from model scaling.
    - *Key takeaway:* Human command-line interfaces are poorly matched to LLMs; tools must be custom-tailored to model context windows.
18. **[tau-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains](https://arxiv.org/abs/2406.12045)** (Yao et al., 2024)
    - *Why it matters:* Evaluated customer service and booking agents interacting with simulated users and complex databases. Introduced the `pass^k` metric to measure consistency across repeat trials.
    - *Key takeaway:* Reliability requires consistent success across repeated runs, not merely high single-trial pass rates.

### Defensive security and safety

As agents are granted write access to file systems, databases, and financial credentials, security against untrusted inputs becomes paramount:

19. **[Design Patterns for Securing LLM Agents against Prompt Injections](https://arxiv.org/abs/2506.08837)** (Beurer-Kellner et al., 2025)
    - *Why it matters:* Analyzed the architectural vulnerabilities of LLM agents to indirect prompt injections and cataloged structural security design patterns (such as dual-LLM architectures, capability confinement, and privilege separation).
    - *Key takeaway:* Robust security cannot be achieved with prompting alone; it requires formal architectural isolation between untrusted input channels and privileged tool execution.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Execute **Pass 1** (5–10 minutes each) across all 19 papers in the list above, recording each in your research notebook with its 5 Cs.
2. Select **at least six papers** (one from each of the six thematic sections) and execute a full **Pass 2** reading, producing a structured 1-page summary for each.
3. Choose one seminal paper (e.g., ReAct, Reflexion, or DPO) and use [Semantic Scholar](https://www.semanticscholar.org/) or [Connected Papers](https://www.connectedpapers.com/) to trace forward three years: identify one paper that extended the method and one paper that identified an empirical vulnerability or failure mode.
4. Prepare for your capstone [Reproduce a Paper](#/lesson/research/research_skills/project_reproduce_a_paper) project: select one paper with accessible public code and small-scale reproduction requirements, and verify that its evaluation dataset and baseline code run locally.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) (Lewis et al., 2020): The paper that formulated RAG for generative question answering.
- [WebArena: A Realistic Web Environment for Building Autonomous Agents](https://arxiv.org/abs/2307.13854): The standard benchmark for web navigation and browsing agents.
- [A Survey on the Memory Mechanism of Large Language Model based Agents](https://arxiv.org/abs/2404.13501): Comprehensive taxonomy of short-term, long-term, and hybrid agent memory systems.

### Knowledge check

Use these questions to verify your understanding of the agentic AI reading list:

1. [How did the Chain-of-Thought paper (Wei et al.) demonstrate that intermediate tokens function as test-time compute scaling?](#foundations-of-large-language-models)
2. [Why was the Direct Preference Optimization (DPO) paper considered a breakthrough for open-source LLM post-training?](#alignment-and-post-training)
3. [What is the core distinction between ReAct and Reflexion regarding the role of memory?](#reasoning-tool-use-and-reflection)
4. [What does the SWE-agent paper by Yang et al. show about the importance of custom Agent-Computer Interfaces (ACIs)?](#benchmarks-and-evaluation-methodology)
5. [Why is prompt engineering alone insufficient to secure autonomous agents against indirect prompt injection attacks?](#defensive-security-and-safety)
