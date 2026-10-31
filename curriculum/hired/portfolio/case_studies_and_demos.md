### Introduction

A list of repos is not a portfolio. Reviewers rarely clone your code. They skim a page, watch part of a video, and decide whether to talk to you. A **case study** turns a project into a story they can follow in two minutes: the problem, what you built, how you know it works, and what you'd do next. A short **demo video** shows the thing working without asking anyone to install it.

You're in a better position than most candidates here, because every project you built since the Expense Tracker had to produce **evidence**: a CI run, traces, an eval score with a confidence interval, prompt-injection tests, cost and latency numbers. Most people applying for AI roles have a chatbot and a screenshot. You have measurements. This lesson shows you how to put them where a busy reader will see them, how to record a demo with free tools, and how to be honest about which parts you built yourself.

You'll use everything here in the next project, Portfolio Site, where you publish three case studies with a demo video each.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- How hiring managers actually read a portfolio.
- Choosing which projects to showcase.
- The structure of a case study: problem, constraints, approach, evidence, next steps.
- Turning the Evidence from your projects into headline numbers.
- Being honest about what you built versus what a framework or AI assistant did.
- Writing for a reader who skims, and a README that works as a front door.
- Planning and recording a demo video of three minutes or less with free tools.

### How reviewers read your work

Picture the person on the other side. A hiring manager for an AI engineering role has thirty applications open in browser tabs and an hour before their next meeting. They click your portfolio link. In the first ten seconds they want to know what role you're after and what your best project is. If that's clear, they read the first screen of the case study. If the first screen is convincing, they might watch the video, open the repo, or scroll down for details. Each step is optional, and most readers stop early.

That has two consequences. First, **order matters more than length**. The strongest material has to be at the top, because a lot of readers will never reach the bottom. Second, **every layer must stand on its own**. The headline alone should say something true and interesting. The first screen alone should make the case. The details below are for the reader who is already interested and wants to check your work, often an engineer on the team who joins the process later.

Technical reviewers also read differently from recruiters. A recruiter checks that the project matches the role. An engineer looks for signs that you understand what you built: why you chose this design, what broke, how you measured it. Your case study has to serve both, which is easier than it sounds: plain language at the top, evidence and decisions below.

### Choosing what to showcase

Three strong case studies beat ten thin repos. A reviewer who sees ten projects can't tell which ones matter, and usually assumes the weakest one is typical.

Your Final Capstone is case study number one. It has a real user, a deployed system, evals and usage data, which is as close to a job as a portfolio project gets. Pick two more using your Role Map: choose projects that prove the skills your target postings ask for most, and that show *different* skills from the Capstone. For an agent engineer, a good set might be the Capstone, the Workflow Automation Agent (agent evals at scale, approvals, injection defenses) and Cut the Bill (cost and latency work with no loss in quality). For an AI product engineer, swap one in for the Docs Chatbot UI to show front-end work.

Prefer projects with a measured result and a story of improvement. "I built X" is weak. "I built X, measured it, found it failed on Y, changed Z and the score went from A to B" is the shape that gets interviews.

### The shape of a case study

Almost every good case study follows the same five-part arc. Keep the first four parts to about one screen, and put the details underneath.

1. **The problem.** One or two sentences: who has the problem, and what it costs them. "A three-person bookkeeping firm spends about six hours a week chasing unpaid invoices by email." Avoid starting with the technology. Nobody cares that it uses an agent until they care about the problem.
1. **The constraints.** What made it hard or shaped your choices: a budget per task, a latency limit, private data, a user who only works in email, actions that can't be undone. Constraints are what turn a tutorial into engineering, because they explain *why* you made the decisions you did.
1. **The approach.** What you built and the two or three key decisions, each with its reason. "A fixed workflow for drafting, not an agent, because every invoice follows the same steps." "Human approval before any email is sent, because a wrong reminder to a client is expensive." Include a simple diagram if it helps.
1. **The evidence.** How you know it works, with numbers, test set sizes and at least one failure. This is the part most candidates skip, and it's where you stand out. The next section covers it in detail.
1. **What you'd do next.** Two or three honest next steps, tied to what the evidence showed. This signals that you can see the limits of your own work, which is what senior engineers do all day.

Finish with links: the repo, the live demo (or a note on why there isn't one), the video and any related blog post.

### Turning Evidence into headlines

Every project in this curriculum ended with an `#### Evidence` section, and those requirements built up as you went. Here's how each kind of evidence becomes a line in a case study:

- **CI with ruff and pytest.** A passing badge at the top of the repo says your code is tested and linted on every push. In the case study, mention it in one clause ("tests and evals run in CI on every pull request") and let the badge do the rest.
- **Traces.** Traces let you show a real run: a short excerpt of the steps an agent took on one task, or a link to the trace of a failure you fixed. A reader who sees a trace knows the system actually ran.
- **Eval scores with confidence intervals.** This is your headline number. Always give the test set size and the interval: "correct on 91% of 120 held-out cases (95% CI 85–96%)." The interval shows you know that 120 examples can't pin a score down exactly, which is a skill many working engineers lack. If you have a before-and-after result, show both, as in Eval Statistics: "pass@1 rose from 64% to 82% (paired bootstrap 95% CI for the change: +9 to +27 points)."
- **Prompt-injection tests.** A sentence like "all 8 injection scenarios failed to trigger a forbidden action across 5 runs each, stopped by the approval gate and a read-only tool scope" tells a reviewer you think about security, which is rare in junior candidates and essential in agent work.
- **Cost and latency.** "$0.012 per invoice, p50 latency 3.1 s, p95 9.4 s, against a budget of $0.02 and 15 s." Numbers against a budget are stronger than numbers alone, because they show you set a target before you measured.

You don't need all of these on the first screen. Pick the two or three that matter most for the problem, usually the quality score and one cost or safety number, and put the rest in a results table further down.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Don't oversell small numbers

A score of 100% on 12 examples is weak evidence, and an experienced reader knows it. Report the size of every test set and the interval, and don't round a wide interval into a confident claim. Honest, modest numbers are more convincing than impressive ones that fall apart under one question.

</div>

### Being honest about what you built

Modern projects are built with a lot of help. You may have used a framework for the agent loop, a template for the front end, and an AI coding assistant for much of the typing, as you practiced in Working With AI Coding Assistants and Pair With an Agent. That's normal, and employers expect it. What they don't forgive is finding out in an interview that the impressive part was done by something else.

So say plainly who did what. A short "How I built it" paragraph near the end of the case study is enough:

- Name the frameworks and libraries that carry real weight, and what they did. "The agent loop uses LangGraph; I wrote the tools, the approval gate and the eval suite."
- Say how you used AI assistants and how you checked their work. "An AI coding assistant drafted most of the React components. I reviewed every change, and I wrote the tests and the eval harness myself."
- Credit tutorials, templates and other people's code you adapted.

The test is simple: **could you explain and change every part you claim, in an interview, without the tools?** If the answer for some part is no, either learn it before you publish or describe your role in it accurately. Being clear about what you directed versus what you typed is also a good signal in itself, because "I can get good work out of AI tools and verify it" is a real job skill.

### Writing for a skimming reader

A few habits make a case study readable in two minutes:

- **Lead with the result.** The first paragraph should contain the problem and the headline number, as in Learning in Public.
- **Use headings that say something.** "Evidence" is fine; "91% correct, no unsafe emails sent" is better.
- **Keep paragraphs short**, and use a table for results. Tables are the fastest way to read numbers.
- **Define jargon once or avoid it.** A non-technical recruiter should follow the first screen; "pass^k" belongs in the details, with a one-line explanation.
- **Show one picture early**: a screenshot, a GIF or the video thumbnail. It proves the thing exists before the reader has to trust your words.
- **Cut the throat-clearing.** Skip "In today's fast-moving AI landscape." Start with the user.

### An example case study

Here is a short case study for an imagined Capstone. The numbers are illustrative; yours will differ.

> **Invoice Chaser: an approval-gated agent that cuts invoice follow-up time by two thirds**
>
> **Problem.** A three-person bookkeeping firm spent about six hours a week writing reminder emails for overdue invoices, and some slipped through for months.
>
> **Constraints.** No email may go out without a human approving it. Client data stays in the firm's own database. Budget: under $0.02 and 15 seconds per invoice.
>
> **Approach.** A nightly workflow finds overdue invoices in the accounting export, and a small agent with three read-only tools (invoice history, client notes, past emails) drafts a reminder in the firm's tone. Drafts wait on an approval page; only an approved draft can call the send tool. I chose a workflow around a narrow agent because the steps are fixed and only the drafting needs judgment.
>
> **Evidence.**
>
> | Measure | Target | Result |
> | --- | --- | --- |
> | Drafts approved without edits (120 held-out invoices) | 80% | 87% (95% CI 80–92%) |
> | Injection scenarios that caused a forbidden send (8 scenarios × 5 runs) | 0 | 0 |
> | Cost per invoice | under $0.02 | $0.012 |
> | p95 latency | under 15 s | 9.4 s |
> | Weekly follow-up time (3 users, 2 weeks) | under 3 h | about 2 h |
>
> The main failure was tone: drafts for clients more than 90 days overdue were too soft. Error analysis on 40 traces found the prompt had no examples of firm escalation; adding three raised approval on that group from 61% to 84% (n = 38, so the interval is wide). Tests, ruff and the eval suite run in CI on every pull request.
>
> **How I built it.** I wrote the workflow, tools, approval gate and evals. An AI coding assistant drafted the approval page's HTML, which I reviewed and tested.
>
> **Next.** Test on a second firm's data, because all eval cases came from one firm, and add a weekly report of approval rates so the firm can spot drift.
>
> [Repo] · [Live demo, access code on request] · [3-minute video]

Notice what it does. The title states the result. The table puts the evidence in one place, with targets. It names a real failure and the fix, admits the small sample, credits the assistant, and the "Next" section follows from a weakness the reader can see.

### Your README is the front door

Many reviewers will land on your GitHub repo before your portfolio, so the README needs to work as a landing page too. At the top: one sentence on what the project does and for whom, the CI badge, a screenshot or GIF, and links to the case study and video. Below that: one-command setup, how to run the tests and evals, and the results table. [Make a README](https://www.makeareadme.com/) has a good checklist.

A GIF of a few seconds of the app working is the fastest proof you can offer. If you have `ffmpeg` installed, this turns the first eight seconds of a recording into a GIF small enough for a README:

```bash
# fps=10 and a width of 800 pixels keep the file small; -t 8 takes 8 seconds.
ffmpeg -i demo.mp4 -t 8 -vf "fps=10,scale=800:-1" demo.gif
```

### Planning a demo video

A demo video should be **three minutes or less**. Most viewers stop well before that, so front-load it. A structure that works:

1. **0:00–0:20, the problem.** One or two sentences, ideally while showing the user's world: the inbox, the spreadsheet, the support queue.
1. **0:20–1:30, the happy path.** One real task, start to finish. Don't explain every button; narrate what the user gets.
1. **1:30–2:15, a hard case.** Show the system handling something difficult or failing safely: an injected instruction ignored, an approval requested, a question it declines to answer without a source.
1. **2:15–2:45, the evidence.** Flash the results table and the CI badge, and say the headline number out loud.
1. **2:45–3:00, close.** Where to find the repo and case study. Stop.

Write a short script, even as bullets, and rehearse it twice. Prepare the demo state in advance: seed the database, log in, close other tabs, and turn off notifications. Never show a real API key or a user's personal data; use a demo account and test data, and check the recording before publishing.

### Recording with free tools

You don't need studio equipment. You need clear audio and readable text.

- **Recording.** [OBS Studio](https://obsproject.com/) is free, open source and works on Windows, macOS and Linux. macOS also has a built-in screen recorder (press Shift-Command-5), and Windows has one in the Snipping Tool.
- **Audio.** A cheap headset microphone in a quiet room beats an expensive microphone in an echoing one. Record ten seconds and listen back before the real take.
- **Readability.** Increase your editor and terminal font size, and record at 1080p or less so text stays legible on a laptop screen.
- **Editing.** Usually you don't need to. If you do, [Shotcut](https://shotcut.org/) is free and open source and handles trimming and joining clips. Doing three takes and keeping the best is often faster than editing.
- **Hosting.** An unlisted YouTube video is easy to embed and adds automatic captions; check and fix them. Short clips can also be attached directly to a GitHub README or issue. Keep a copy of the original file yourself.

Finally, test it on a stranger. Ask someone who hasn't seen the project to watch the video and tell you what it does. If they can't, the video needs another take, not more features.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [Make a README](https://www.makeareadme.com/) for a practical checklist of what a good README contains.
   - Use it to audit your Capstone README, and fix the two weakest sections.
1. Reread the eval sections of [Hamel Husain's Your AI Product Needs Evals](https://hamel.dev/blog/posts/evals/) with a case-study lens.
   - Notice how he presents evidence that a system improved, and copy one technique into your own write-up.
1. Install [OBS Studio](https://obsproject.com/) (or use your operating system's built-in recorder) and read the [OBS quick start guide](https://obsproject.com/kb/quick-start-guide).
   - Set up a scene with your screen and microphone, record a 30-second test, and check that the audio is clear and the text readable.
1. Revise the case-study post you published for your Final Capstone into the five-part arc in The shape of a case study, with a results table and a "How I built it" paragraph. Keep the first four parts to one screen. Reuse its numbers and story; don't start from scratch.
1. Re-cut or re-record the Capstone demo video to three minutes or less, following Planning a demo video. Ask one person who hasn't seen the project to watch it and tell you what it does. If they can't, revise. Keep both the case study and the video; Project: Portfolio Site needs them, plus two more like them.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Why must the strongest material in a case study be at the top?](#how-reviewers-read-your-work)
- [How should you pick the two showcase projects besides your Capstone?](#choosing-what-to-showcase)
- [What are the five parts of a case study, and why do constraints matter?](#the-shape-of-a-case-study)
- [How should you report an eval score so a reviewer can trust it?](#turning-evidence-into-headlines)
- [What test tells you whether you can claim a part of a project as your own work?](#being-honest-about-what-you-built)
- [What belongs at the top of a project README?](#your-readme-is-the-front-door)
- [What are the five beats of a three-minute demo video?](#planning-a-demo-video)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Shotcut](https://shotcut.org/) is a free, open-source video editor for trimming takes and adding a title card.
- [Attaching files on GitHub](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/attaching-files) explains how to put images, GIFs and short videos directly in a README, issue or pull request.
