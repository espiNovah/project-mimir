### Introduction

Reading about networking is easy. Sending a message to a stranger whose work you admire is not. In this project you'll do it twenty times: over about two weeks, you'll send twenty targeted, personal messages to real people in the field, follow up once where it makes sense, and track every message, reply and outcome. Then you'll analyze what happened, the way you'd analyze any experiment, and write down what you'll change.

The goal is not a job offer, and it isn't even a high reply rate. Many cold messages go unanswered, for reasons that have nothing to do with you, and a sprint with only two or three replies is completely normal. The goal is to build the habit, learn which kinds of messages work *for you*, and start a handful of relationships that can grow over months. A careful tracker and an honest retrospective are what make this a success.

This project practices everything from Networking and Referrals and Running a Job Search: giving before asking, writing short, specific cold messages, informational conversations, following up, and tracking a pipeline with conversion rates.

### Before you start

- Create a GitHub repository named `mimir-outreach-sprint`. It will hold your redacted tracker, the script or spreadsheet that computes your rates, and your retrospective. It must never hold anyone's real name or private message (see the box below).
- Keep a **private** tracker with the real details, such as names, links to profiles and message threads, somewhere outside the repo: a private spreadsheet, or a file listed in `.gitignore`. Give every message an ID like `M01` to `M20`. The public tracker uses only the IDs.
- Have your materials ready: your Portfolio Site with its case studies, a short line describing who you are and the role you're targeting (from AI Roles Explained and your Role Map), and the three draft messages from Networking and Referrals.
- Block out time: about 30 minutes per message to research the person and write it, spread over ten working days, plus time for any calls that come out of it.
- Finish the "give before you ask" step from Networking and Referrals, if you haven't. Several of your best messages will grow out of it.

<div class="lesson-note lesson-note--critical" markdown="1">

#### Protect other people's privacy

The people you contact didn't agree to be part of your portfolio. Never publish their names, photos, profile links, employers (where that would identify them), or the text of their replies, unless you have asked and they have said yes in writing. In everything you commit, replace identifying details with neutral descriptions, such as "M07: staff engineer at a mid-size health-tech company," and paraphrase replies rather than quoting them. Before every push, search the repo for names and links to profiles. Your own messages are yours to share, but redact the recipient's details from them too.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

#### Plan

1. Build a target list of about 25 people, so you have spares. Each one should be someone whose work you've actually read, used or watched: an author, a speaker, a maintainer, an engineer at a company on your target list, someone from your "people I already know" list, or a member of a community you've joined. For each, write one sentence on *why this person* and what specific thing you'd mention.
1. Mix your targets on purpose so you can compare. Include at least three of these **message types** and at least two **channels**:
   - **Advice question**: one specific question only they are well placed to answer.
   - **Informational call request**: a 20-minute conversation about their work or team.
   - **Thank-you with results**: thanks for something specific, plus what you did with it, and no request.
   - **Warm contact**: someone you already know, catching up and asking a specific question about their company or field.
   - **Community or open source follow-up**: building on an earlier public interaction, such as an issue thread or forum answer.
   - **Small project offer**: a short, specific offer to someone on the list of five people or businesses you made in Freelance and Contract Work, as that lesson describes.
   - Channels might be email, LinkedIn, a community Discord or Slack, an issue or discussion thread, or in person at a meetup with a written follow-up.
1. Before sending anything, write down your predictions in your README: which type and channel you expect to get the most replies, and why. You'll compare these with what actually happens.
1. Don't ask a stranger for a referral. Referral requests are only allowed for warm contacts who know your work and a specific open role, as described in How referrals work in Networking and Referrals.

#### Send

1. Send twenty messages over about ten working days, no more than three or four a day, so each gets real attention. Each must be written for its recipient, follow the four parts from Writing a short cold message (who you are, why them, one small ask, an easy out), and stay under about 120 words. A shared structure is fine; a template with the name swapped in is not.
1. It's fine to ask an AI model to point out vague wording in a draft. Write every message yourself, and never let a tool send messages for you.
1. If there's no reply after about seven days, send one short follow-up in the same thread, ideally adding something new. Then stop. Never send a second follow-up.
1. For every conversation that happens, prepare questions, keep to time, ask who else you should talk to, and send a thank-you within a day, as in Informational conversations.

#### Track

1. Log every message in your private tracker as it happens, with at least: `id`, `date_sent`, `type`, `channel`, `recipient` (a neutral description, such as "maintainer of an eval library"), `hook` (the specific thing you mentioned, redacted if it would identify them), `ask`, `followed_up` (yes or no, and date), `replied` (yes or no), `reply_days` (days until the reply), and `outcome` (no reply, declined, answered question, call held, introduction offered, other).
1. At the end of the sprint, export a **redacted** copy as `tracker.csv` in the repo, keeping every column except anything identifying.
1. Compute your response rates overall, by message type, by channel, and with versus without a follow-up. You can use a spreadsheet, or adapt `funnel.py` from Running a Job Search into a `rates.py` script that reads `tracker.csv`. Report each rate as a count and a total, such as "3 of 7," and not just as a percentage.
1. Thirty days after your last message, update the tracker with anything that happened later: late replies, calls, introductions, a closed loop where you told someone what you did with their advice.

#### Retrospective

1. Write a retrospective of 400 to 800 words in your README:
   - What happened, with your rates table at the top.
   - How the results compared with your predictions.
   - Your two best messages and two that got no reply, redacted, with your honest guess at what made the difference.
   - What surprised you, and what felt hardest.
   - **What you'll change**: at least three concrete changes for your next round, such as a different hook, a smaller ask, a different channel or more giving before asking.
1. Be careful with conclusions. With twenty messages, a difference like "2 of 6 versus 1 of 7" could easily be chance, as you learned in Eval Statistics. Say which differences you think are real, which might be noise, and what you'd need to see to be sure.
1. Push your project to GitHub with a README that explains what you did, how you tracked it, and what you learned.

#### Evidence

Your README must show:

- A redacted `tracker.csv` with all twenty messages and every follow-up, reply and outcome, including the 30-day update. No names, profile links, identifying employer details or quoted replies unless the person gave written consent, which the README notes.
- Response rates overall, by message type, by channel, and with versus without a follow-up, each given as a count out of a total. If a script computes them, one command reproduces the table from `tracker.csv`.
- Your written predictions from before the sprint, next to the actual results.
- The retrospective, ending with at least three specific changes you'll make next time.
- This is an outreach project rather than software, so the engineering rungs of the evidence ladder (CI, traces, eval scores, prompt-injection tests) don't apply.

#### Extra credit

- Run a second round of ten messages that applies your three changes, and compare the two rounds, being honest about how small the samples are.
- Write `rates.py` with a pytest test or two, such as one that checks that a follow-up which got a reply counts once, and run ruff and pytest in GitHub Actions.
- Publish a public post about what you learned from the sprint, with no names or identifying details, and add it to your `posts.md`.
- Turn one conversation into something useful in public, such as a write-up of advice (with permission) or a contribution the person suggested, and close the loop with them.

</div>

### Submitting your work

A strong submission is honest and careful, not impressive. A reviewer should be able to read the tracker and see twenty real, individually written messages, each with a specific reason for choosing that person, and should find no way to identify anyone in it. The rates table gives counts, not just percentages, and the retrospective doesn't overclaim from small numbers. The most valuable part is usually the list of changes: it shows that you treat outreach like any other system, by measuring, learning and adjusting. Keep your private tracker: the people who replied are the start of your network, and the follow-ups and closed loops over the next months are where the sprint pays off.
