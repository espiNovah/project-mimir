### Introduction

A job posting is a wish list written by a busy person, often copied from an older posting and edited by three other people. Read literally, most postings ask for more than any one person has. Read carefully, they tell you exactly what a team needs, which skills are table stakes, and which ones would make you stand out.

This lesson teaches you to read postings like data. You'll learn to separate what a team truly needs from the decorations around it, and to tally skills across many postings so you know what to emphasize in the rest of this curriculum. You'll also set up a small, sustainable way to stay current in a field that changes every month, without drowning in hype.

You're doing this at the end of Core on purpose. You still have Agentic Systems, Production and the Capstone ahead, and what you learn from real postings should shape where you spend that time.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The anatomy of a job posting.
- Separating must-haves from nice-to-haves.
- Reading between the lines for stage, team and real responsibilities.
- Tallying skills across many postings to find what's in demand.
- Applying when you don't meet every requirement.
- Staying current with a small, reliable set of sources.

### The anatomy of a posting

Almost every posting follows the same pattern:

1. **The pitch.** A paragraph about the company and its mission. Skim it, but note what the product is and who its customers are.
1. **The responsibilities.** What you'll actually do. This is the most honest part of the posting, because it was usually written by the hiring manager about the real work.
1. **The requirements.** Skills and experience they ask for. These are often inflated: "5+ years" is a filter, not a law, and a list of twelve tools rarely means all twelve are needed.
1. **The nice-to-haves.** Extra skills that would help. Having two or three of these is often what gets you noticed.
1. **Logistics.** Location, remote policy, salary range, visa sponsorship and benefits.

Read the responsibilities first and ask: "Could I describe how I'd do each of these, with an example from a project?" That question tells you more than counting matched keywords.

### Must-haves and nice-to-haves

Not every requirement carries the same weight. A few clues separate the must-haves from the rest:

- **Repetition.** A skill that appears in the title, the first responsibilities *and* the requirements is a must-have. "Build RAG pipelines" in the responsibilities plus "experience with retrieval" in the requirements means retrieval is central.
- **Position.** The first few requirements are usually the ones the hiring manager wrote; the long tail is often boilerplate.
- **Specificity.** "Strong Python" is a must-have. A list of specific tools ("LangGraph, LlamaIndex, Pinecone, Weaviate, Qdrant") is usually a nice-to-have that means "some vector database and some agent framework."

If you have most of the must-haves, apply. Hiring managers rarely expect a candidate to match every line, and waiting until you do means waiting forever, because the list keeps growing.

### Reading between the lines

Postings also tell you about the team, if you know where to look:

- "Zero to one," "first AI hire" or "wear many hats" means an early team and broad scope. Expect to own everything from the database to the demo.
- "Scale," "reliability," "platform" and "on-call" mean a mature product. Expect a narrower scope and a high bar for production engineering.
- Mentions of customers, travel or "working directly with clients" signal forward-deployed or solutions work.
- "TypeScript," "React" or "full-stack" in an AI posting signals AI product engineering, where you'll build the interface too.
- "Evaluation," "quality" or "benchmarks" listed among the first responsibilities means the team already knows evals are its bottleneck. Your Eval Harness project is exactly what they want to see.

Translate tool names into concepts. "LangGraph" is agent orchestration. "Pinecone" is a vector database. "Langfuse" is tracing and observability. A team that names one framework will usually hire someone who knows a comparable one well and shows they learn fast. When you apply, point to where you've done the concept, even if you used a different tool.

### From anecdotes to data

One posting is an anecdote; twenty are data. If you read five postings for "AI engineer," you'll remember the strangest one. If you tally twenty, the pattern shows. In most recent tallies, Python, evals, RAG, agents and tool use, cloud deployment and clear communication sit near the top.

You already have every skill needed to do this properly. Put each posting's skills into a CSV, normalize the names, and count:

```python
# tally.py: count how many postings mention each skill.
# postings.csv has columns: company,title,skills   (skills separated by ";")
import csv
from collections import Counter

SYNONYMS = {  # your merging rules: many spellings -> one concept
    "retrieval": "rag",
    "vector search": "rag",
    "llm evaluation": "evals",
    "evaluation": "evals",
    "ts": "typescript",
}

counts = Counter()
with open("postings.csv", newline="") as f:
    rows = list(csv.DictReader(f))
for row in rows:
    skills = {s.strip().lower() for s in row["skills"].split(";") if s.strip()}
    counts.update({SYNONYMS.get(s, s) for s in skills})  # a set, so each posting counts once

for skill, n in counts.most_common(15):
    print(f"{skill:<20} {n:>2}/{len(rows)}  {'#' * n}")
```

The `SYNONYMS` dictionary is where the real thinking happens. Deciding that "retrieval" and "vector search" are the same skill is a judgment call, so write your rules down. You'll scale this up to twenty postings in Project: Role Map.

### Applying without every box ticked

Hiring managers know their postings are wish lists. What they're really asking is "Can this person do the responsibilities, and will they learn the rest quickly?" You answer that with evidence:

- Lead with the must-haves you can prove, each tied to a project with a link.
- For a missing tool, name the concept and where you've done it: "I haven't used Pinecone, but I built hybrid search on pgvector with reciprocal rank fusion."
- For a missing skill that's central, consider whether the next part of this curriculum covers it, and say so honestly if you're applying early.

Don't apply to roles where you have almost none of the must-haves. That's not confidence; it's noise for both of you.

### Staying current without drowning

AI changes weekly, and there are a thousand newsletters, feeds and influencers competing for your attention. You need a small, reliable system:

- **One daily digest**, skimmed in five minutes. A good digest summarizes what happened across many communities so you don't have to follow them all.
- **One or two trusted practitioners** who test things hands-on and write clearly.
- **A weekly habit** of going deep on only the one or two developments that affect your target role.
- **Build to learn.** When something new matters, make a tiny demo with it instead of reading ten takes about it. A one-hour experiment teaches more than a week of threads, and it can become a public post.

Everything else is optional. Missing a week of news costs you almost nothing; missing a week of building costs a lot.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [The Rise of the AI Engineer](https://www.latent.space/p/ai-engineer) again with postings in mind, and list the skills it predicts. Compare them with what you find in real postings in this lesson's final exercise.
1. Subscribe to or bookmark [AI News on Latent Space](https://latent.space/news/), a daily digest that summarizes what's happening across AI communities so you don't have to follow them all.
   - Skim one week of issues and write down the one development that most affects the work you'd do in your target role.
1. Bookmark [Simon Willison's blog](https://simonwillison.net/), one of the most reliable practitioners writing about LLMs, with frequent hands-on notes on new models and tools.
   - Read his five most recent posts and note how he tests new tools by building small things.
1. Find five real postings for your target role, posted within the last three months. For each, highlight the must-haves, list the nice-to-haves, translate any tool names into concepts, and write one sentence on what the team actually needs.
   - Put them in a `postings.csv` and run the tally script above on them. Keep the file; these will be the first five of the twenty in Project: Role Map.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Which part of a posting best describes the real job, and why?](#the-anatomy-of-a-posting)
- [What clues tell you a requirement is a must-have rather than a nice-to-have?](#must-haves-and-nice-to-haves)
- [What does "first AI hire" suggest about a team, compared with "platform" and "on-call"?](#reading-between-the-lines)
- [Why should you translate tool names into concepts?](#reading-between-the-lines)
- [Why are twenty postings more useful than five, and what do synonym rules do?](#from-anecdotes-to-data)
- [How should you apply when you're missing a listed tool?](#applying-without-every-box-ticked)
- [What does a small, sustainable system for staying current look like?](#staying-current-without-drowning)
