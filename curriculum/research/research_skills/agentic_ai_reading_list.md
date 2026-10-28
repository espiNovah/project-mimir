<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Every field has a set of papers that everyone in it is assumed to have read. In agentic AI the set is young, since most of it was written after 2020, but it is already the shared vocabulary of interviews, lab meetings and master's seminars. This lesson gives you an annotated list of 19 papers in a sensible reading order, each with one line on why it matters. You have met several of them already in this curriculum. Now read them as primary sources.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The foundation papers behind modern language models.
- How models were taught to follow instructions and to reason.
- The papers that defined tool use, reflection and planning for agents.
- Memory and long-running agents.
- The benchmarks used to measure agents.
- Securing agents against prompt injection.

### Key ideas

- **Read in order, not by date.** The list is grouped so that each paper builds on the ones before it: first the models, then how they were aligned, then how they act, remember, are measured and are secured.
- **Most of these papers are claims about a capability.** ReAct claims interleaving reasoning and acting helps; Reflexion claims verbal self-critique helps; SWE-agent claims the interface matters as much as the model. Read each one asking what experiment would falsify the claim.
- **Benchmarks shape the field.** SWE-bench, tau-bench and similar papers define what "a good agent" means in practice. Understanding how a benchmark is built, scored and gamed is as important as knowing the leaderboard.
- **Many results are tied to a specific model generation.** A prompting trick that gave a large gain on GPT-3 may give none on a current model. When you read an older paper, note the model it used and ask whether the finding is about the method or the model.
- **Several of these papers have public code.** ReAct, Tree of Thoughts, Reflexion, Voyager, Generative Agents, SWE-agent, tau-bench and DPO all released code, which makes them good candidates for the Reproduce a Paper project.
- **The list is a starting point.** Use the citation-tracing skills from Reading Papers to follow each paper forward to the work that challenged or extended it.

### The reading list

Foundations of large language models:

1. [Attention Is All You Need](https://arxiv.org/abs/1706.03762) (Vaswani et al., 2017): introduced the transformer, the architecture behind every model in this curriculum, and the one you built in Building a Tiny GPT.
1. [Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165) (Brown et al., 2020): GPT-3 showed that scale alone produces in-context learning, which is what makes prompting work.
1. [Chain-of-Thought Prompting Elicits Reasoning in Large Language Models](https://arxiv.org/abs/2201.11903) (Wei et al., 2022): asking for intermediate steps unlocks multi-step reasoning, the seed of every reasoning technique since.

Alignment and post-training:

1. [Training language models to follow instructions with human feedback](https://arxiv.org/abs/2203.02155) (Ouyang et al., 2022): InstructGPT defined the RLHF recipe that turned base models into assistants.
1. [Constitutional AI: Harmlessness from AI Feedback](https://arxiv.org/abs/2212.08073) (Bai et al., 2022): replaced most human harm labels with AI feedback guided by written principles.
1. [Direct Preference Optimization](https://arxiv.org/abs/2305.18290) (Rafailov et al., 2023): showed preference tuning can skip the reward model and RL loop, and became the default open-source alignment method.
1. [DeepSeek-R1](https://arxiv.org/abs/2501.12948) (DeepSeek-AI, 2025): RL from verifiable rewards produced long reasoning chains, with an open recipe that reshaped post-training.

Reasoning and acting:

1. [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) (Yao et al., 2022): the thought-action-observation loop at the core of nearly every agent.
1. [Toolformer: Language Models Can Teach Themselves to Use Tools](https://arxiv.org/abs/2302.04761) (Schick et al., 2023): a model learned when to call APIs by training on its own useful tool calls, an early step toward native function calling.
1. [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366) (Shinn et al., 2023): agents improve across attempts by writing feedback to themselves, learning without changing weights.
1. [Tree of Thoughts](https://arxiv.org/abs/2305.10601) (Yao et al., 2023): turned reasoning into an explicit search over partial solutions, linking LLMs to classical search.

Memory, environments and architecture:

1. [Generative Agents: Interactive Simulacra of Human Behavior](https://arxiv.org/abs/2304.03442) (Park et al., 2023): memory streams, reflection and planning produced believable social behavior in a simulated town.
1. [Voyager: An Open-Ended Embodied Agent with Large Language Models](https://arxiv.org/abs/2305.16291) (Wang et al., 2023): a Minecraft agent that writes and stores reusable code skills, an early version of today's agent skill libraries.
1. [MemGPT: Towards LLMs as Operating Systems](https://arxiv.org/abs/2310.08560) (Packer et al., 2023): treats the context window like RAM and external storage like disk, with the model managing its own memory.
1. [Cognitive Architectures for Language Agents](https://arxiv.org/abs/2309.02427) (Sumers et al., 2023): CoALA gives a shared vocabulary for comparing agent designs, drawn from cognitive science.

Evaluation:

1. [SWE-bench: Can Language Models Resolve Real-World GitHub Issues?](https://arxiv.org/abs/2310.06770) (Jimenez et al., 2023): real issues with hidden tests became the standard benchmark for coding agents.
1. [SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering](https://arxiv.org/abs/2405.15793) (Yang et al., 2024): showed that designing the tools and interface for the agent matters as much as the model.
1. [tau-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains](https://arxiv.org/abs/2406.12045) (Yao et al., 2024): simulated users, domain policies and the pass^k metric for measuring whether agents are reliable, not just occasionally right.

Security:

1. [Design Patterns for Securing LLM Agents against Prompt Injections](https://arxiv.org/abs/2506.08837) (Beurer-Kellner et al., 2025): a catalog of architectures that limit what an injected instruction can do, trading some capability for provable safety properties.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Do a first pass, using the method from Reading Papers, on all 19 papers. Record each in your reading log with one sentence on its main claim.
1. Do a full second pass on at least six papers, one from each group, and write a one-page summary of each.
1. For two papers, trace forward with [Semantic Scholar](https://www.semanticscholar.org/): find one later paper that extended the result and one that challenged or failed to replicate it, and add both to your log.
1. Pick the paper you will reproduce in Reproduce a Paper. Check that it has public code or a clearly described method, and write down the one result you will target and what it would cost to rerun at small scale.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) is the paper that named RAG, worth reading if you want the origin of the Core path's retrieval section.
- [WebArena](https://arxiv.org/abs/2307.13854) and [AgentBench](https://arxiv.org/abs/2308.03688) are two more widely cited agent benchmarks, covering web browsing and a mix of environments.
- [A Survey on the Memory Mechanism of Large Language Model based Agents](https://arxiv.org/abs/2404.13501) organizes the fast-growing agent memory literature.
