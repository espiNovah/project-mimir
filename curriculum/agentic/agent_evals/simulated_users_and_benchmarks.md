<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Many agents talk to people: a support agent asks follow-up questions, a booking agent confirms details. You can't hire a person to chat with your agent every time you change a prompt, so you build a simulated user, which is another model playing a customer with a goal, a personality and private information it reveals only when asked. This lesson covers how to build simulated users that test your agent well, and how public benchmarks such as SWE-bench and the τ-bench family fit into your evaluation work.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What a simulated user is and when you need one.
- Writing user personas with goals, hidden facts and behaviors.
- Keeping simulated users realistic and stopping them from helping too much.
- Benchmarks with simulated users and checked environment state, such as τ-bench.
- Coding benchmarks such as SWE-bench.
- Why your own task suite matters more than public leaderboards.

### Key ideas

- **A simulated user is a second model with a script.** Give it a goal ("change my flight to Friday"), facts it only shares when asked (a booking code), constraints ("refuse a fee over $50") and a style (impatient, vague). Your harness alternates turns between it and your agent until the simulated user says it's done or a turn limit is hit.
- **Grade the outcome, not the chat.** As in the previous lesson, the strongest check is the final state: was the right booking changed, and nothing else? The simulated user's satisfaction is a weak signal on its own.
- **Simulators have failure modes too.** They can be too cooperative, leak their hidden goal in the first message, break character or end early. Read their side of transcripts as carefully as the agent's, and use a capable model with firm instructions for them.
- **Vary personas on purpose.** Cover cooperative, confused, impatient and adversarial users, plus users who change their mind. Many real failures come from the messy ones.
- **τ-bench tests agent, user and policy together.** Its tasks put an agent with tools and a policy document in a simulated domain, such as airline or retail support, with a simulated customer, and check the final database state. It popularized pass^k because agents that pass once often fail on repeats. Use the current version (τ³-bench in the `tau2-bench` repository), since the original tasks are outdated.
- **SWE-bench tests coding agents on real issues.** An agent gets a repository and a GitHub issue, and passes if the project's hidden tests pass after its change.
- **Benchmarks pick models, your evals pick changes.** Public scores help you shortlist models. Only tasks drawn from your own users and failures tell you whether your agent got better.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Reread the simulated users section of [Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents), along with the parts on benchmarks for conversational agents.
1. Read the README of [τ³-bench (the tau2-bench repository)](https://github.com/sierra-research/tau2-bench).
   - Note how domains, policies, user simulators and final-state checks are defined. If you have time, install it with `uv` and run one domain on a cheap model.
1. Browse the [SWE-bench site](https://www.swebench.com/) and read how a task instance is defined and scored.
1. Read the [Inspect agents docs](https://inspect.aisi.org.uk/agents.html) sections on multi-turn and agent evaluation, and see how Inspect runs agents against tasks.
1. Write a simulated user for one of your agents with three personas (cooperative, confused, adversarial). Run ten conversations per persona, grade the final state and record which persona causes the most failures.

</div>
