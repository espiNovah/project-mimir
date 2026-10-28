### Introduction

A hiring manager looking at your application has a few minutes and one question: can this person do the job? A resume *claims* you can. Public work *shows* it. Learning in public means sharing what you build and learn as you go, through blog posts, READMEs, short write-ups and demos. For career changers without a prior AI job, it's the most reliable way to build credibility, and it compounds over time.

You're learning about it now, at the end of Core, instead of at the end of the curriculum, because compounding needs time. Someone who starts writing today will have a dozen honest, specific posts by the time they apply for jobs. Someone who starts the week before applying will have one. So from this lesson on, this curriculum asks you to publish **at least one public post for every path you complete**, starting with this one.

This lesson covers why it works, what to write, and how to start without feeling like a fraud.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What learning in public means, and why it works for getting hired.
- Getting past "I'm not an expert yet."
- What to write about: TILs, project write-ups and experiment results.
- Writing for a technical reader: specific, short and evidence-first.
- Where to publish, and owning your own site.
- The one-post-per-path habit.

### Why public work gets you hired

Think about the difference between these two lines:

- On a resume: "Built RAG systems with evaluation."
- In a post: "My docs chatbot answered 71% of 50 test questions correctly. Error analysis showed most failures were multi-passage questions, so I added a reranker. Correctness rose to 84% (95% CI 74–93%), and here's the trace of the question that still fails."

The first is a claim anyone can write. The second is evidence: numbers, a method, an honest failure. It also gives an interviewer something concrete to ask about, which turns an interview from an interrogation into a conversation about your work.

Public work helps in quieter ways too. Writing about a project forces you to understand it, and you'll often find a bug or a better explanation while drafting. Posts get shared, and people who read them sometimes reach out with jobs, questions or collaborations. None of that happens to work that lives only on your laptop.

### You only need to be one step ahead

The most common reason people don't write is "I'm not an expert yet. Who am I to explain this?" The answer is that you're not writing for experts. You're writing for the person who is where you were last month.

That person is a large audience. Experts have forgotten what was confusing about embeddings, or why their first judge prompt passed everything. You haven't. Honest notes about what tripped you up and how you got unstuck are useful precisely *because* you're new. "I spent two hours confused about why my CI eval passed locally and failed on GitHub; it was a missing secret" will save someone else two hours.

Two rules keep this honest. Don't claim expertise you don't have; write "here's what I found" rather than "here's how it's done." And show your evidence, so readers can judge for themselves.

### What to write about

You don't need big ideas. Three kinds of posts cover almost everything:

- **TIL (today I learned).** A short note on one thing you learned: a library behavior, an error message and its fix, a trick. Three paragraphs and a code snippet is plenty.
- **Project write-ups.** The problem, what you built, the key decisions, the measured result and what you'd do differently. Every project in this curriculum is a candidate, and your READMEs are already drafts.
- **Experiment results.** "I compared three chunk sizes on my eval set; here are the numbers." These are especially valuable in AI, where tools change fast and careful, small measurements are rare. Your eval harness makes them easy.

Sharing good work by others, with a paragraph of your own commentary on what you tried and what you think, counts too.

### Writing for a technical reader

Technical readers are busy and skeptical. Write for them like this:

- **Lead with the result.** Put the finding in the first two sentences. "Adding a reranker raised correctness from 71% to 84%" goes at the top, not at the end.
- **Be specific.** Name the model tier, the dataset size, the metric and the confidence interval. "It works well" is not a finding; "accuracy went from 71% to 86% on 200 held-out examples" is.
- **Show the evidence.** Include the code, a table, a trace excerpt or a screenshot. Link to the repo.
- **Include a failure.** What didn't work, and what you think the reason was. It makes the whole post more believable.
- **Keep it short.** 300 to 800 words is plenty for most posts. Cut the introduction about how fast AI is moving; everyone knows.

### Where to publish

Post wherever your readers are: a personal blog, a developer platform, LinkedIn, or a well-written GitHub README. Wherever you post, keep the *canonical* copy, the original version that others link to, on a site you own. Platforms change their rules, rank posts differently, or disappear; your own site doesn't. You'll build that site in Project: Portfolio Site in Getting Hired. Until then, publish anywhere public and keep the source text in a Git repo so you can move it later.

### One post per path

Writing is a habit, not a campaign. A short post every week or two, tied to whatever you're building, is sustainable. Long silences followed by one perfect post are not.

To make the habit concrete, this curriculum now asks for **at least one public post for each path you complete from here on**: one for Core (this lesson's assignment), one for Agentic Systems, one for Production, one for the Capstone, and one for any elective path you take. Each later path's final project will remind you. More is welcome. Each post must:

- be publicly readable without a login;
- be about something you built or measured in that path;
- include at least one code snippet, number or trace excerpt;
- link to the relevant repo.

Keep a list of your posts with links in a `posts.md` file in your Role Map repo. By the time you reach Getting Hired, you'll have a body of work that speaks for you.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Learn in Public by swyx](https://www.swyx.io/learn-in-public), the essay that popularized the idea among developers.
   - Note the specific forms of public learning it suggests, and pick the two that suit you best.
1. Read [What to blog about by Simon Willison](https://simonwillison.net/2022/Nov/6/what-to-blog-about/), which argues for two easy post types: things you learned and descriptions of projects.
1. Browse [Simon Willison's TILs](https://til.simonwillison.net/) and his [main blog](https://simonwillison.net/) as a model of learning in public done consistently for years.
   - Read three of his short TILs or project posts and notice how short and specific they are, and how often they lead with the result.
1. Write and publish your Core post: 300 to 800 words about something you built or measured in Core, such as your eval harness's before-and-after result or what your judge got wrong.
   - Follow the checklist in One post per path. Start your `posts.md` list with its link.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Why does a public post count as stronger evidence than a resume bullet?](#why-public-work-gets-you-hired)
- [How do you write usefully when you aren't an expert yet?](#you-only-need-to-be-one-step-ahead)
- [What are three easy kinds of posts to write?](#what-to-write-about)
- [What makes a post convincing to a technical reader?](#writing-for-a-technical-reader)
- [Why keep the canonical copy of your posts on a site you own?](#where-to-publish)
- [What does the one-post-per-path requirement ask of each post?](#one-post-per-path)
