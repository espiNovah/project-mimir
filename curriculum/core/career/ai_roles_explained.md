### Introduction

You can now build a real AI feature end to end: prompts, structured outputs, a backend with a database and auth, retrieval, evals and a TypeScript front end. That's a good moment to look up from the code and ask what all of this is *for*. Which jobs use these skills, and which one do you want?

It's worth asking now, not at the end. The rest of the curriculum, Agentic Systems, Production, the Capstone and the electives, is large, and you'll get far more from it if you know which role you're aiming at. A learner targeting forward-deployed work will want to practice demos and write-ups. One targeting agent engineering will want to go deep on evals for agents. One targeting AI product engineering will want to keep sharpening TypeScript and React.

Job titles in AI are new and inconsistent. One company's "AI engineer" is another's "applied AI engineer," "agent engineer" or "software engineer, LLM." This lesson maps the main roles, what each does day to day, and which parts of this curriculum prepare you for them, so you can read past the titles to the work.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Where the "AI engineer" role came from and how it differs from ML engineering.
- AI engineer and agent engineer roles.
- Forward-deployed engineers and solutions engineers.
- ML engineers, research engineers and data scientists.
- Adjacent roles: AI product engineer, developer relations, evals and safety.
- How company size changes the job.
- Choosing a target role.

### Where the AI engineer came from

For most of the 2010s, "doing AI" at a company meant training models. You collected data, engineered features, trained a classifier, and deployed it. That work belonged to data scientists and machine learning (ML) engineers, and it required a lot of statistics and math.

Large foundation models changed the shape of the work. A *foundation model* is a big, general model trained by a lab, such as the Claude models you've been calling, that you use through an API instead of training yourself. Suddenly most of the value came not from training a model but from *using* one well: writing prompts, giving it the right context, retrieving documents, calling tools, validating outputs, measuring quality and shipping a product. Around 2023, people started calling this job the *AI engineer*. It sits closer to software engineering than to research.

That is the role this curriculum targets most directly. Look back at what you've built: an extractor with validation and retries, an API with auth and a queue, a RAG system with citations, an eval harness in CI, a chat UI. That is an AI engineer's portfolio.

### AI engineers and agent engineers

An **AI engineer** builds product features on top of foundation models. Day to day, that means designing prompts and context, building retrieval pipelines, wiring models into backends, writing evals, watching traces, and controlling cost and latency. Postings for this role usually ask for strong Python, API and backend experience, RAG, evals, and the ability to ship.

An **agent engineer** is an AI engineer who specializes in systems where the model decides what to do next: agents that call tools in a loop. The skills are tool design, agent loops, the Model Context Protocol (MCP), memory, multi-agent orchestration, sandboxing and agent evaluation. The title is newer and less common, but the work matches the Agentic Systems path you're about to start. Many "AI engineer" postings are really agent engineering jobs, so read the responsibilities, not the title.

### Forward-deployed and solutions engineers

A **forward-deployed engineer (FDE)** builds with customers. Instead of working on one product for everyone, an FDE embeds with a client's team and ships an AI solution on the client's real data and systems: messy PDFs, old databases, strict security rules. The job mixes engineering, consulting and communication. Demand for FDEs grew sharply as AI companies started selling to large enterprises.

What matters most for FDE work is being able to scope a vague problem, build a convincing demo quickly, explain trade-offs to non-engineers, and write clearly. The Open Brief project at the end of Core is close to a day in the life of an FDE: a business problem, some constraints and a deadline.

**Solutions engineers** (sometimes *sales engineers*) are a nearby role. They help customers evaluate and adopt a product, run technical demos and answer hard questions before a sale. There's less building and more explaining than in FDE work, but the communication skills overlap.

### Closer to the model

**ML engineers** and **research engineers** work on the model itself. They train and fine-tune models, build training and evaluation pipelines, and serve models efficiently on GPUs. These roles usually expect more math, PyTorch and experience with training runs, which you can build in the optional ML Foundations path. Research engineers additionally help researchers run experiments, so they read papers and reproduce results.

**Data scientists** focus on analysis, experiments and classic models: forecasting, A/B tests, dashboards and the kind of supervised learning you saw in ML Essentials. Many data scientists now also build LLM features, so the boundary with AI engineering is blurring.

You don't need these roles to get an AI job, but you should understand them, because you'll work alongside them and because postings sometimes use these titles for AI engineering work.

### Product, devrel and evals roles

Several adjacent roles are real entry points, and some may suit you better than a pure engineering title.

- **AI product engineers** own a feature end to end, from the database to the screen. They talk to users, decide what to build, and build all of it. These roles almost always expect solid **TypeScript and React** (often Next.js) alongside Python, because the product the user touches is a web app. Your Docs Chatbot UI project is direct evidence for this role; keep building front ends in later projects if this is your target.
- **Developer relations (devrel)** engineers write tutorials, build sample apps, speak and help developers succeed with a platform. They reward people who write and teach well, and a public portfolio of posts is a big advantage.
- **Eval and AI safety roles** focus on measuring and constraining model behavior: building eval suites, red-teaming, and designing guardrails. The testing discipline you built in Measuring Quality and Evals in Practice is the core skill.

### Startups versus large companies

The same title means different work at different company sizes. At a startup, especially an early one, an AI engineer might own the database, the prompts, the front end, the deployment and the customer call, all in one week. Scope is broad, process is light, and you learn fast. You'll need to be comfortable shipping imperfect things and fixing them.

At a large company, scope is narrower and deeper. You might own the retrieval layer for one product, with a high bar for reliability, security reviews, on-call rotations and code review. You'll learn how production systems are run at scale, which the Production path previews.

Neither is better. Notice which one excites you, because it changes which projects you should emphasize.

### Choosing a target role

A focused portfolio beats a generic one. A reviewer who sees three projects that all point at "agent engineer" understands you immediately; a reviewer who sees one of everything doesn't. So pick one target role now. You can change course later, and many learners do, but you can't aim at everything at once.

To choose, weigh three things: what you enjoyed most so far (the backend? the evals? the UI? explaining things?), what you're already strong at from earlier work or study, and what the market around you actually hires for. You'll measure that third one properly in Reading Job Postings and Project: Role Map.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [The Rise of the AI Engineer by swyx on Latent Space](https://www.latent.space/p/ai-engineer), the essay that named and defined the role.
   - Note how it separates AI engineers from ML engineers, and which skills it lists as core.
1. Read [I analyzed 1,000 forward deployed engineer jobs by Bloomberry](https://bloomberry.com/blog/i-analyzed-1000-forward-deployed-engineer-jobs-what-i-learned/), a January 2026 data-driven look at one of the fastest-growing roles.
   - Write down the five skills or traits it finds most often, and which of them you can already show evidence for.
1. Read [Chip Huyen's Building A Generative AI Platform](https://huyenchip.com/2024/07/25/genai-platform.html) as a map of the components AI engineers work on in production.
   - Tick off each component you have built so far in this curriculum, and circle the ones you haven't. Many of the circled ones are coming in Agentic Systems and Production.
1. Write a half-page note choosing one target role. Explain why it fits your interests and strengths, list three things from your projects that prove you can do it, and name one part of the remaining curriculum you'll go deeper on because of this choice. You'll use this note in Project: Role Map.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [How does an AI engineer's work differ from an ML engineer's?](#where-the-ai-engineer-came-from)
- [What does an agent engineer specialize in?](#ai-engineers-and-agent-engineers)
- [What skills matter most for a forward-deployed engineer?](#forward-deployed-and-solutions-engineers)
- [Which roles usually need more math and PyTorch depth?](#closer-to-the-model)
- [Why do AI product engineer roles usually expect TypeScript and React?](#product-devrel-and-evals-roles)
- [How does the same job title change between a startup and a large company?](#startups-versus-large-companies)
- [Why pick a single target role now?](#choosing-a-target-role)
