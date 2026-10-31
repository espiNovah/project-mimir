### Introduction

A job search is a project with an unusually frustrating feedback loop. You do a lot of work, most of it gets no response, and the responses that do come are slow and rarely explain themselves. Left unmanaged, that loop wears people down: they apply in bursts when they feel hopeful, stop when they feel rejected, and never find out what's actually working.

You already know a better way to handle a noisy system you can't fully control: measure it. In this curriculum you've built evals, read traces and made decisions from data with honest confidence intervals. This lesson applies the same habits to your search. You'll keep a pipeline tracker, look at your funnel and its conversion rates, set weekly targets for things you control, and change your approach based on evidence instead of mood.

It also covers the parts no spreadsheet fixes: where to find roles, why fewer, better applications beat mass-applying, how to handle silence and rejection, how to spot job scams, and how to look after yourself during what may be a long search. To be direct about that last point: for career changers, the market for junior AI roles is competitive, and searches of several months are common. Running it well improves your odds and makes it sustainable. It doesn't guarantee a result, and a slow search is not proof that you're doing it wrong.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Running your search as a project with a pipeline tracker.
- The hiring funnel and its conversion rates.
- Weekly targets for things you control.
- Where to find roles, and applying well instead of mass-applying.
- Handling silence and rejection.
- Recognizing and avoiding job scams.
- Looking after yourself, and changing the plan when the data says so.

### A pipeline tracker

A **pipeline** is every opportunity you're pursuing, each at some stage: found, applied, screening call, interviews, offer, or closed. A **pipeline tracker** is the one place you record them all. Without one, you'll forget who you talked to, miss follow-ups, apply twice to the same role, and have no idea what's working.

A spreadsheet is fine. So is a [GitHub project](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects) board, where each opportunity is an item and each stage is a column you drag it through. Use whatever you'll actually open every day. Whatever you choose, give each opportunity one row with these columns:

| Column | Example |
| --- | --- |
| `company` | Acme Health |
| `role` | AI Engineer |
| `link` | the posting URL |
| `source` | careers page, referral, job board, recruiter, community |
| `date_applied` | 2026-11-03 |
| `stage` | applied, screen, interview, offer, closed |
| `tailored` | yes or no |
| `contact` | who you know there, if anyone |
| `next_action` | "follow up with recruiter" |
| `next_date` | 2026-11-10 |
| `notes` | why it fits, what you learned, why it closed |

Two columns do most of the work. `next_action` and `next_date` turn the tracker into a to-do list: each morning, sort by `next_date` and do what's due. `source` lets you learn which channels actually lead somewhere.

Also save a copy of each posting's text when you apply, as you did in Project: Role Map. Postings disappear, and you'll want to reread one before an interview.

### The funnel and conversion rates

Hiring is a **funnel**: many opportunities go in at the top and few come out at the bottom. A typical funnel looks like this:

1. **Applied** (or reached out).
1. **Screen**: a first call, usually with a recruiter.
1. **Interviews**: technical and behavioral rounds with the team.
1. **Offer.**

A **conversion rate** is the share of opportunities that move from one stage to the next. If you applied to 40 roles and got 4 screens, your application-to-screen rate is 10%. Each rate tells you about a different part of your search:

- **Low application-to-screen** means your materials or targeting aren't landing. Maybe you're applying to roles that need more experience, or your resume and portfolio don't make the match obvious, or your applications arrive cold.
- **Low screen-to-interview** usually means your story in a short call isn't clear: what role you want, why, and your best evidence.
- **Low interview-to-offer** points at interview skills, which the Resume & Interviews section covers.

Your tracker makes these rates easy to compute. If you export it as `pipeline.csv`, this short script prints your funnel. It uses only the standard library, so you can run it with `uv run funnel.py` in any folder:

```python
# funnel.py: print stage counts and conversion rates from pipeline.csv.
# Each row's "stage" is the furthest stage it reached, or "closed:<stage>"
# when it ended there (for example "closed:screen" for a rejection after the screen).
import csv
from collections import Counter

STAGES = ["applied", "screen", "interview", "offer"]

with open("pipeline.csv", newline="") as f:
    rows = list(csv.DictReader(f))

furthest = Counter()
for row in rows:
    stage = row["stage"].strip().lower().removeprefix("closed:")
    furthest[stage] += 1

# An opportunity that reached "interview" also passed "applied" and "screen",
# so the count for each stage includes everything that got further.
reached = {}
for i, stage in enumerate(STAGES):
    reached[stage] = sum(furthest[s] for s in STAGES[i:])

for prev, stage in zip(STAGES, STAGES[1:]):
    n, k = reached[prev], reached[stage]
    rate = f"{k / n:.0%}" if n else "n/a"
    print(f"{prev:>9} -> {stage:<9} {k:>3} of {n:<3} {rate}")

by_source = Counter(row["source"] for row in rows)
screens = Counter(row["source"] for row in rows
                  if row["stage"].strip().lower().removeprefix("closed:") != "applied")
for source, n in by_source.most_common():
    print(f"{source:<15} {screens[source]} screens from {n} applications")
```

Read the output the way you learned to read a small eval in Eval Statistics. Your numbers will be tiny, and tiny numbers are noisy. "1 screen from 12 applications" and "3 from 12" can easily come from the same underlying rate. So don't change everything after a bad week. Look at trends over four to six weeks, and treat a difference between sources as a hint worth testing, not a fact. "Referrals: 3 screens from 5; job boards: 1 from 30" is a big enough gap to act on.

### Weekly targets you control

You can't control whether a company replies. You can control what you put in. So set weekly targets on **inputs**, not outcomes:

- **Tailored applications** sent, each one a role you've read carefully and genuinely match.
- **Personal messages** sent: cold messages, follow-ups and thank-yous, as in Networking and Referrals.
- **Conversations** held: informational calls, meetups, community calls.
- **Building time**: hours spent on a project, a contribution or a post, so your evidence keeps growing.

A realistic starting week for someone searching while doing other things might be five tailored applications, ten personal messages, one or two conversations and five hours of building. If you're searching full time, you might double the first three. The exact numbers matter less than picking ones you can sustain for months, then checking each Friday whether you hit them.

Input targets protect your morale too. A week with no replies but all targets met is a good week: you did your part. That framing keeps you going through the stretches where results lag behind effort, which they always do.

### Where to find roles

Spread your search over a few channels, and use `source` in your tracker to learn which ones work for you.

- **Company career pages.** Make a list of 30 to 50 companies you'd like to work for, ones that build with AI in a domain you understand, and check their career pages weekly. Applying directly is often better than applying through a job board, because some boards resell or repost stale listings.
- **Community job channels.** The Discords, Slacks and forums you joined in Networking and Referrals often have job channels where hiring managers post themselves.
- **Hacker News "Who is hiring?"** A thread posted on the first weekday of each month, with hundreds of roles from companies of all sizes, many of them startups. You'll find them listed under [the whoishiring account](https://news.ycombinator.com/submitted?id=whoishiring).
- **Startup job boards** such as [Y Combinator's job listings](https://www.ycombinator.com/jobs) and [Wellfound](https://wellfound.com/). Early-stage startups are often more open to candidates with unusual backgrounds and strong project evidence.
- **General job boards** such as LinkedIn and Indeed. They have the most listings and the most competition.
- **Recruiters.** An *in-house* recruiter works for one company; an *agency* recruiter is paid by companies to fill roles. Both can help, and neither should ever charge you money.
- **Your network.** Former colleagues, people from your conversations, maintainers of the project you contributed to. Ask them what's open at their company, not just whether they're "hiring."
- **Your old field.** A company in healthcare, finance, logistics or education that's adding AI may value your domain knowledge more than an AI-first startup would.

Also consider **adjacent roles**: forward-deployed, solutions, support engineering at an AI company, or a technical role at your current employer that touches AI. They can be a bridge, as can the paid projects in the next lesson, Freelance and Contract Work.

### Applying well beats mass-applying

When results are slow, it's tempting to apply to everything. Some tools will even auto-apply to hundreds of postings for you. Resist this. Mass-applying usually lowers your results:

- An untailored application rarely makes the match obvious, and for a career changer the match must be obvious, because your job titles don't make it for you.
- It burns through the companies you'd most like to work for with your weakest version.
- It floods your tracker with noise, so your conversion rates stop telling you anything.
- It's demoralizing: two hundred applications and no replies feels much worse than twenty applications and two screens, even though the second is a better search.

An application done well takes 30 to 60 minutes. Read the posting as in Reading Job Postings and check that you meet most of the must-haves. Tailor your resume (Resume for AI Roles, the previous lesson, shows how in about twenty minutes). Lead with the one or two case studies from your Portfolio Site that match the role, look for anyone you know at the company, and answer the form's questions honestly. Where a short note is allowed, write two or three specific sentences, not a generic cover letter.

### Silence and rejection

Most applications get no reply at all. Some get an automated rejection weeks later. Some candidates are **ghosted**: a company goes silent even after interviews. This is common, it's rude, and it usually says more about the company's process than about you. Roles get frozen, filled internally or quietly reprioritized.

Some practical habits help:

- **Set a time limit.** If an application has had no response after three or four weeks, mark it closed in your tracker and stop waiting. If it comes back to life, great.
- **Follow up once after interviews.** A short, polite note a week after the date you were told to expect an answer is fine.
- **Ask for feedback, without expecting it.** After an interview rejection, a brief "Thank you; if you're able to share anything I could improve, I'd be grateful" is reasonable. Many companies have a policy of not giving feedback. Don't push.
- **Treat rejection as data.** Note in your tracker the stage and any reason you can infer. Across many rejections, patterns show up, such as "every system design round" or "always after the recruiter screen," and patterns are fixable.
- **Reapply later.** A rejection usually isn't permanent. Many companies are happy to see you again in six months to a year, especially with new evidence.

Rejection still stings, and it should be allowed to. Feel it, write down what you learned, and go back to your weekly targets.

### Avoiding job scams

Job seekers are a favorite target for scammers, and remote technical roles are a common lure. The U.S. Federal Trade Commission's guide to [job scams](https://consumer.ftc.gov/articles/job-scams) lists the main patterns. Be suspicious when:

- **You're asked to pay anything**: for training, equipment, a background check or a "starter kit." Real employers don't charge you to work for them.
- **You receive a check** and are asked to deposit it and send some money back, or buy equipment from a particular vendor. The check will bounce, and the money you sent is gone.
- **The whole process happens over chat**, with no video call and no conversation with an engineer, and an offer arrives fast.
- **They ask for sensitive details early**, such as your bank account, tax ID or a copy of your passport, before a written offer from a verifiable company.
- **The contact uses a free email address** or a domain that's slightly different from the company's real one. Scammers impersonate real companies and real recruiters.
- **The pay is far above market** for a junior role with vague duties, or the "job" is simple paid tasks that start requiring deposits.

A specific risk for engineers: **malicious take-home tests**. Some attackers pose as recruiters and send a "coding exercise" repository that installs malware when you install its dependencies or run it, aiming to steal passwords, browser data or cryptocurrency wallets. Before running any code from a company you haven't verified, check that the recruiter and company are real, read the repository's setup scripts and dependency list, and run it inside a Docker container or a throwaway virtual machine, never directly on the laptop where you keep your accounts. You learned to isolate untrusted code for agents; untrusted code from strangers deserves the same care.

To verify a role, find it on the company's own careers page, reached by typing the company's address yourself rather than following a link in a message, and check that the recruiter exists and works there. If something feels off, stop. In the U.S., you can report scams at [ReportFraud.ftc.gov](https://reportfraud.ftc.gov/); most countries have an equivalent consumer protection or fraud reporting agency.

### Looking after yourself

A long search is hard on anyone. It's especially hard when you've already invested months in learning a new field and every silence feels like a verdict on that choice. It isn't. Hiring is slow, noisy and shaped by forces you can't see: budgets, reorganizations, internal candidates.

Some things that help people keep going:

- **Give the search working hours.** Search during set hours, and stop at the end of them. Checking email at midnight doesn't make anyone reply faster.
- **Keep building.** Spend some of each week on a project, a contribution or a post. It keeps your skills sharp, gives you new things to talk about in interviews, and gives you a part of the week where effort turns directly into results.
- **Make a financial plan early.** Know how many months you can search, and decide in advance what you'll do if you approach that limit: part-time work, contract work, an adjacent role. Deciding early, while calm, is much easier than deciding in a panic.
- **Don't search alone.** A friend, a study partner or a community channel where people share wins and setbacks makes a real difference. Celebrate inputs ("sent all my messages this week"), not only offers.
- **Keep the rest of your life.** Sleep, exercise, time with people who don't care about your job search. They're part of what keeps you effective, not a distraction from it.

If the stress starts affecting your sleep, health or relationships for weeks at a time, talk to someone: a friend, a doctor or a counselor. That's a normal and sensible thing to do, not a sign of failure.

### Changing the plan

Every four to six weeks, look at your funnel and ask what it's telling you. A few common patterns:

- **Lots of applications, almost no screens.** Your targeting or materials are off. Check that you meet most of the must-haves, get feedback on your resume and portfolio, and shift effort from cold applications toward referrals and direct messages.
- **Screens, but few interviews.** Practice your two-minute story about who you are, which role you want and your best evidence, until it's clear and confident.
- **Interviews, but no offers.** Find which round you're losing in and practice that specifically. The rest of Getting Hired is built for this.
- **Very little of anything.** Look at whether you're hitting your input targets at all. If you are, consider widening the search: adjacent roles, other company types, other locations, or contract work as a bridge.

Write the decision down in your tracker's notes, with the date and the reason. Six weeks later, you'll be able to check whether it helped. That's the same loop you've run on every system in this curriculum: measure, change one thing, measure again.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the GitHub Docs page [About Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects) if you plan to track your search on a GitHub project board. Otherwise skip it and use a spreadsheet.
1. Read the FTC's guide to [job scams](https://consumer.ftc.gov/articles/job-scams), then write down the three warning signs you'd be most likely to miss, and what you'll do if you see one.
1. Set up your pipeline tracker with the columns from A pipeline tracker. Add every opportunity you're already pursuing, plus your list of 30 target companies with a link to each careers page.
1. Write your weekly targets for the next four weeks, covering tailored applications, personal messages, conversations and building time. Put a fifteen-minute review on your calendar every Friday to check them.
1. Create a small `pipeline.csv` with ten made-up rows across different stages and sources, then run `funnel.py` on it with `uv run funnel.py`. Check by hand that each rate is right. Once your real tracker has a month of data, export it and run the script on that.
   - For more practice reading and summarizing CSV data, try the [data exercise set](https://github.com/espiNovah/project-mimir/tree/main/exercises/data).
1. Write a half-page "search plan": your target role, your channels, your weekly targets, how many months you plan to search and what you'll do if you near that limit. Keep it next to your tracker and reread it at each four-to-six-week review.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Which two tracker columns turn it into a daily to-do list, and why does the source column matter?](#a-pipeline-tracker)
- [What does a low application-to-screen rate suggest, and why shouldn't you react to one bad week?](#the-funnel-and-conversion-rates)
- [Why set weekly targets on inputs instead of outcomes?](#weekly-targets-you-control)
- [Why does mass-applying usually make a search worse?](#applying-well-beats-mass-applying)
- [What should you do about an application with no response after a few weeks?](#silence-and-rejection)
- [What are the warning signs of a job scam, and how should you handle a take-home repository from an unverified company?](#avoiding-job-scams)
- [What would you change if you were getting screens but almost no interviews?](#changing-the-plan)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The Tech Interview Handbook](https://www.techinterviewhandbook.org/) is a free, thorough guide to the software engineering hiring process, from resumes through interviews to negotiation.
- [Brag documents by Julia Evans](https://jvns.ca/blog/brag-documents/) explains how to keep a running list of your work and wins. During a search, it doubles as a record of progress on days when results are slow.
