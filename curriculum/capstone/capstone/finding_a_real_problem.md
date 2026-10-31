### Introduction

Your capstone is the project you will talk about in every interview, so the problem you choose matters more than the technology. A clever agent that nobody needs is a weak portfolio piece. A simple agent that saves a real person two hours a week is a strong one. This lesson is about finding that person and that problem: talking to people, watching how they actually work, and picking a workflow that an AI system can genuinely improve.

None of this needs code, and that's the point. Every project so far handed you the problem, even the Core Open Brief, where you chose from a list. Real jobs don't. Someone says "our team is drowning in supplier emails", and it's on you to find out what that actually means, whether a model can help, and which small piece to build first. The skills here, interviewing, mapping a workflow and cutting scope, are the ones that decide whether the next 100 hours produce something people use.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why a real user beats an imagined one, and where to find one.
- How to interview people without leading them to the answer you want.
- Watching the work and mapping a workflow step by step.
- Judging whether a task suits an LLM, an agent, plain code or nothing at all.
- Scoring candidate problems and picking one small enough to finish.
- Getting a commitment from users, and handling their data with care.

### Start with a person, not a technology

"I want to build a multi-agent RAG system" is a solution looking for a problem. "My friend who runs a small bakery spends Sunday nights answering supplier emails" is a problem. The first sentence leads to a demo. The second leads to a system with a user, a measurable before and after, and a story an interviewer can follow in ten seconds.

A real user gives you three things you can't invent. First, **real inputs**: the actual emails, invoices or tickets, with all their typos, forwarded chains and odd formats. Your eval set will be built from these, and they are far harder than anything you would make up. Second, **a definition of "done well"** that comes from someone whose job depends on it. Third, **feedback that can hurt**. Your friends will tell you a demo looks great. A user who tries your system on Monday's real inbox will tell you it put the wrong price in a reply, and that is the information you need.

Good places to look, roughly from easiest to hardest:

- **Your own job, or a past one.** You already know the tasks, the tools and the people. Ask your manager before using work data.
- **Friends' and family members' jobs.** Ask "what's the most tedious part of your week?" and keep asking follow-up questions.
- **A club, nonprofit or volunteer group.** These run on spreadsheets, email and goodwill, and are often glad of help.
- **A small local business.** A dentist's office, a bookkeeper, a repair shop. Small businesses can't afford custom software, so a working tool is a real gift.
- **An open-source project you use.** Maintainers have repetitive work (triaging issues, answering the same questions) and public data you can use freely.

Pick a domain where you can reach several people with the same problem. One user is a start, but the capstone needs at least three, and you'll learn more from the differences between them.

### Interviewing without leading questions

The obvious way to test an idea is to describe it and ask "would you use this?". It doesn't work. People are kind, they like you, and saying yes costs them nothing. Rob Fitzpatrick's short book *The Mom Test* is named after this trap: even your mom will lie to you about your business idea, not out of malice but to be nice. His fix is a set of rules for conversations that people can't lie to you in, even if they want to.

**Talk about their life, not your idea.** Don't mention what you plan to build. The moment you pitch, the conversation becomes about being polite to you. Ask about the work instead.

**Ask about specific past events, not opinions about the future.** People are bad at predicting what they would do and good at describing what they did. "Would you use a tool that drafts supplier replies?" gets a polite yes. "Tell me about the last time you answered supplier emails. When was it? How many were there? Which one took longest, and why?" gets facts.

**Talk less, listen more.** Aim for them to speak 80% of the time. When they say something interesting, ask "can you tell me more about that?" or "what happened next?", then stop talking. Silence feels awkward, and people fill it with the details you want.

**Dig into what it costs them.** Problems people care about already cost them something: time, money, stress, a workaround. Ask "what have you tried to fix this?" If someone complains about a task but has never tried a template, a spreadsheet formula or a paid tool, the pain may be smaller than it sounds.

**Watch for compliments and fluff.** "That sounds great!" is not data. Neither are generic claims like "I always" or "I usually". When you hear one, steer back to a specific example: "When was the last time that happened?"

Here are some questions to avoid, with better ones to ask instead:

| Avoid | Ask instead |
| --- | --- |
| Would you use an app that does X? | How do you handle X today? Walk me through the last time. |
| Is X a big problem for you? | How much time did X take last week? What did you drop to make room for it? |
| Would you pay for this? | What do you currently spend on X, in money or tools? |
| Don't you find it annoying when...? | What's the hardest part of X? |
| How would an AI assistant help you? | What would you do with the time if X took no time at all? |

The left-hand questions are **leading questions**: they suggest the answer you want, and people go along with it. The right-hand ones ask for facts the person has and you don't.

Write notes during or right after each interview, quoting the person's own words where you can. Their words will go straight into your spec's problem statement, and "I spend every Sunday night on this, and I still miss some" is far more convincing than your summary of it.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Talk to more people than you think you need

After three interviews, patterns start to appear. After five or six, you'll hear the same complaints again and stop learning much new. That's your signal to stop interviewing and decide. If every conversation surprises you, the problem isn't clear yet, so keep going or narrow the group of people you're talking to.

</div>

### Watching the work

Interviews tell you what people remember. Watching tells you what they do, and the two differ. Ask to sit with someone while they do the task, or have them share their screen on a call and narrate as they go. User researchers call this **contextual inquiry**: observing work in its real setting, and asking questions as it happens.

You will see steps nobody mentions in an interview, because they've stopped noticing them: copying an order number between three browser tabs, checking last month's spreadsheet to remember a price, rewriting the same polite sentence for the twentieth time. These invisible steps are often where the time goes, and often what a model handles well.

Pay special attention to the moments when the person **makes a judgment**. "This one's urgent because it's from our biggest client." "I'd never send that without checking the delivery date first." Those judgments are your future success criteria and your future eval cases. They also mark the places where your system must not act alone.

### Mapping the workflow

After watching, write the workflow down as a numbered list of steps. For each step, note what comes in, what the person does, what goes out, how long it takes, and whether it's a mechanical step or a judgment call. Here is a map from the bakery example:

```text
Workflow: answer supplier emails (Sunday evening, about 25 emails, about 2 hours)

1. Open inbox, skim subjects, sort into "orders", "invoices", "other"   10 min  judgment (light)
2. For each order confirmation: check quantities against the order sheet 40 min  mechanical, error-prone
3. If quantities differ: write to supplier asking to correct              20 min  judgment + writing
4. For each invoice: copy total and due date into the payments sheet     25 min  mechanical
5. Flag anything unusual (price rise, late delivery) for the owner        15 min  judgment
6. Reply to "other" emails, or leave for Monday                           10 min  judgment

Pain: steps 2 and 4 (65 min, tedious, mistakes cost money)
"Done well": every mismatch caught, nothing paid twice, owner sees price rises
```

A map like this does three jobs. It shows where the time actually goes (here, the mechanical checking, not the writing). It shows which steps are judgment calls a human should keep. And it gives you a **baseline**: the time and error rate of the task done by hand today, which you will need in your spec to show your system improved anything.

### Does it suit an LLM or an agent

Not every tedious task is a good fit for a model. A good capstone problem has the right shape:

- **Repetitive.** It happens weekly or daily, not once a year. Frequent pain is worth solving and gives you plenty of examples to evaluate on.
- **Text-heavy or messy.** Emails, documents, notes, forms that never quite match. This is where models beat plain code.
- **A clear definition of "done well".** If the person can't tell you what a good result looks like, you can't build an eval for it.
- **Tolerant of a human check.** The output can be reviewed before it matters, or mistakes are cheap and easy to undo.
- **Reachable data.** You can actually get the inputs, with permission, through an export, an API or a forwarding rule.

Then climb the spectrum from Workflows vs Agents, one stop at a time. **Can plain code do it?** Matching an order quantity against a spreadsheet row is a lookup, not a language task. **Can one model call do it?** Pulling the quantities out of a messy order email is one structured-output call. **Can a fixed workflow do it?** Extract, compare in code, draft a reply if they differ: three steps you can write down in advance. **Only then, an agent:** use a loop only for the part where the steps genuinely depend on what the model finds, such as investigating an unusual invoice across several systems.

Just as important is knowing when **not** to use a model at all. Say no, or pick a different problem, when:

- the rules are fully known and stable, so code is cheaper, faster and always right;
- a single mistake is serious and can't be caught before it lands, such as medical dosing, legal filings or moving money without review;
- the task happens too rarely to save meaningful time or give you enough examples to test with;
- the real problem is something else, such as a missing process, a broken tool or a disagreement between people. A model won't fix that.

Google's Rules of Machine Learning open with the same advice: don't be afraid to launch without machine learning. If your interviews show that the best solution is a spreadsheet template, tell your user. You'll have helped, and you can keep looking for a capstone problem.

### Scoring your candidates

You'll probably end up with two to four candidate problems. Score each from 1 to 3 on a few questions and compare them honestly:

| Question | 1 | 3 |
| --- | --- | --- |
| How often does it happen? | A few times a year | Daily or weekly |
| How much time or money does it cost? | Minutes | Hours, or real money lost to mistakes |
| Can you get real inputs? | No, or only invented ones | Yes, with permission |
| Is "done well" clear? | "It should be helpful" | "Every mismatch flagged, nothing paid twice" |
| How many users can you reach? | One | Three or more with the same problem |
| Does it fit a model? | Plain code would do, or mistakes are dangerous | Messy text, reviewable output |

A problem that scores 1 on reachable inputs or reachable users is out, however interesting it is. You can't build an eval set from data you don't have, and you can't meet the capstone's user requirement without users.

### Small enough to finish

You have roughly 100 hours for the capstone build. That sounds like a lot until you list what the project requires beyond the core feature: an eval suite, a deployment with staging, tracing, CI, a security review, a runbook, user sessions, a write-up and a demo. Realistically, the AI part gets maybe 40 of those hours.

So scope ruthlessly. The Shape Up method from Basecamp calls the time you're willing to spend your **appetite**: fix the time, and let the scope change to fit it, rather than fixing the scope and letting the time grow. For your capstone, that means:

- **One kind of user.** The bakery owner, not "small businesses".
- **One workflow.** Checking order confirmations, not "managing supplier email".
- **One happy path, done well,** plus graceful handling of the inputs that don't fit. Everything else goes on a "later" list.

A good test: can you describe the system in one sentence that names the user, the input and the output? "It reads the bakery's supplier order confirmations, compares them with the order sheet, and drafts a correction email for any mismatch, which the owner approves before sending." If your sentence needs "and also" three times, cut until it doesn't.

Smaller also means more reliable, and reliability is what convinces people. A narrow system that works on 90% of real inputs and says "I'm not sure" on the rest beats an ambitious one that half works on everything. You can always widen the scope after the capstone. You can't get back hours spent on features nobody asked for.

### Getting a commitment

Before you build, go back to your users with the problem you picked, described in their words, and ask for something concrete: "When I have a first version in about three weeks, will you try it on a week of your real emails and tell me what's wrong with it?" A real yes comes with a date or a next step. "Sure, sounds cool" without one is a compliment, not a commitment. You need at least three people to say yes for the capstone project.

Agree on data too. Ask permission before you copy any of their emails, files or records, explain where the data will go (including to a model provider's API), and agree on what you'll remove before anything reaches your repo or traces. Names, email addresses, phone numbers and account numbers should be masked in any example you commit, as you practiced in Logging and Tracing and the Security Review lesson. Being careful here is part of being trusted with a real problem, and it's a story worth telling in an interview.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Watch Y Combinator's [How to Talk to Users](https://www.youtube.com/watch?v=z1iF1c8w5Lg), a short, practical guide to user interviews from Startup School.
   - Write down the questions it suggests asking and the mistakes it warns against, and compare them with the table in this lesson.
1. Read Michael Lynch's [book report on The Mom Test](https://mtlynch.io/book-reports/the-mom-test/), a free, detailed summary of the book's rules with examples, and the Nielsen Norman Group's [Avoid Leading Questions](https://www.nngroup.com/articles/leading-questions/).
   - Together they cover how to ask about past behavior, and how small wording changes push people toward an answer.
1. Read Paul Graham's [Do Things That Don't Scale](https://paulgraham.com/ds.html) for why serving a handful of users very well is the right start.
   - Focus on the parts about recruiting your first users by hand.
1. Reread [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents), this time asking of each pattern: "Which real workflow I've seen would fit this?"
1. Practice: interview at least three people about a task they do repeatedly, and watch at least one of them do it.
   - Keep notes for each interview: the task, how often they do it, how long it takes, what goes wrong and what "done well" looks like, with direct quotes.
   - Write a workflow map like the one in this lesson for the most promising task, with time per step and which steps are judgment calls.
   - Score your candidates with the table in this lesson, pick one, and write a short paragraph: why it's worth solving, why a model helps, whether it needs code, a workflow or an agent, and your one-sentence scope.
   - Get at least three people to agree, with a date, to try your prototype once it exists, and agree with them how their data will be handled.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What three things does a real user give you that an imagined one can't?](#start-with-a-person-not-a-technology)
- [Why is "Would you use an app that does X?" a bad interview question, and what would you ask instead?](#interviewing-without-leading-questions)
- [What can you learn by watching someone work that an interview usually misses?](#watching-the-work)
- [What should a workflow map record for each step, and what does it give your spec?](#mapping-the-workflow)
- [Name three situations where you should not use a model for a task.](#does-it-suit-an-llm-or-an-agent)
- [What does it mean to fix your appetite rather than your scope?](#small-enough-to-finish)
- [What's the difference between a compliment and a commitment from a future user?](#getting-a-commitment)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [A Field Guide to Rapidly Improving AI Products](https://hamel.dev/blog/posts/field-guide/) explains why involving domain experts early makes AI products better, which applies directly to your capstone user.
- The Nielsen Norman Group's [Contextual Inquiry](https://www.nngroup.com/articles/contextual-inquiry/) explains how to observe people working, with practical tips on what to watch for.
- The Nielsen Norman Group's [Task Analysis](https://www.nngroup.com/articles/task-analysis/) goes deeper on breaking a workflow into steps, which helps when your map gets complicated.
- [Set Boundaries](https://basecamp.com/shapeup/1.2-chapter-03), a chapter from Basecamp's free book Shape Up, explains appetite and fixed time with variable scope.
- Rule #1 of Google's [Rules of Machine Learning](https://developers.google.com/machine-learning/guides/rules-of-ml) argues for launching without machine learning when simple rules will do.
