### Introduction

Almost every interview loop includes at least one conversation with no code in it. Someone asks "Tell me about a time when..." and waits. This is the **behavioral interview**, and many technically strong candidates lose offers here: not because they lack good experiences, but because they tell them badly. They ramble through background, say "we" for ten minutes, and stop before the ending.

You have more material than you think. Every project since the Expense Tracker made you produce evidence, and several of them had a real plot: an agent that broke under attack, a trace that revealed a bug, a bill you cut without losing quality, a pull request a stranger reviewed and merged, a Capstone that real users surprised. This lesson shows you how to turn those projects, and the work you did before tech, into short, honest stories you can tell in about two minutes each.

The stories you prepare here feed straight into Project: Mock Interview Loop, whose mock interview opens with behavioral questions built on your resume.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What behavioral interviews test, and why AI teams use them.
- The STAR structure, and the three most common ways answers go wrong.
- A worked example, with a weak and a strong version of the same story.
- Building a story bank of 6–8 stories from your own projects.
- Questions specific to AI roles, and which stories answer them.
- Framing your earlier, non-tech career as a strength.
- Questions to ask the interviewer, and how to practice out loud.

### What behavioral interviews test

A behavioral question asks about something you actually did, on the assumption that how you handled real situations in the past is the best available guide to how you'll handle similar ones on the job. "How would you handle a disagreement?" invites a nice-sounding theory. "Tell me about a time you disagreed with a teammate" asks for evidence, and follow-up questions quickly show whether the evidence is real.

Most companies run these as **structured interviews**: every candidate gets the same questions, and the interviewer scores answers against a written rubric. The rubric usually lists a few qualities the company cares about. Amazon publishes its version as its [Leadership Principles](https://www.amazon.jobs/content/en/our-workplace/leadership-principles), and many other companies have similar internal lists. Across companies, the same themes come up:

- **Ownership.** Did you take responsibility for an outcome, or wait to be told?
- **Judgment under uncertainty.** How did you decide when the data was incomplete?
- **Learning from failure.** Can you describe a mistake plainly and say what changed afterward?
- **Collaboration and conflict.** Can you disagree, persuade, and accept being wrong?
- **Communication.** Can you explain something complicated to someone who isn't technical?

AI teams lean on these interviews for a reason specific to the field. AI systems fail in ways that ordinary software doesn't. A model can be confidently wrong, a prompt change can fix one case and silently break ten others, and an agent can be talked into doing something harmful. Teams need people who notice problems, measure before claiming, say "I don't know yet," and stop a launch when the evals say so. A coding round can't show any of that. A story about the time your eval changed your mind can.

### The STAR structure

**STAR** is the standard way to organize an answer. It stands for:

- **Situation.** The context, in two or three sentences: where you were, what the project was, and what made it matter.
- **Task.** Your specific responsibility or goal. What were *you* trying to achieve?
- **Action.** What you did, step by step, and *why* you chose each step over the alternatives. This is the heart of the answer.
- **Result.** What happened, with a number if one exists, plus what you learned or would do differently.

A useful rule of thumb for proportions: Situation and Task together take about 20% of the answer, Action about 60%, and Result about 20%. Spoken aloud, a full answer runs about two minutes, roughly 250 to 350 words. Shorter answers usually skip the reasoning in Action. Much longer ones lose the listener. If the interviewer wants more, they'll ask, and a good story invites follow-ups.

Some people add an **L** for Learning (STAR-L). Whether or not you use the letter, end with one sentence on what you'd do differently or what habit you kept. Interviewers for junior roles weigh that sentence heavily, because it shows you'll keep improving after they hire you.

### Common STAR failures

Most weak answers fail in one of three ways.

**Too much Situation.** The candidate spends ninety seconds explaining the project, the tech stack and the backstory, and the interviewer is still waiting to hear what they did. Nervous people over-explain context because it feels safe. The fix: write your Situation down and cut it to three sentences or fewer. If the interviewer needs more background, they'll ask.

**"We" instead of "I."** "We decided to add a reranker, then we ran the evals, and we found..." The interviewer can't hire "we." They need to know which decisions were yours. This matters even more in AI work, where a framework, a teammate or a coding assistant might have done part of it. Say "I" for what you did, and name the others plainly: "My teammate built the front end; I owned the eval suite." Being precise about credit is a sign of honesty, not of being a poor team player.

**No Result.** The story ends with the action: "...so I added the approval gate." Did it work? How do you know? A story without a result sounds like a story without one. For you this is the easiest failure to fix, because your projects all have an Evidence section. Use the number. If the result was bad, say so and say what you learned; a failure story with a clear lesson is worth more than a vague success.

Two smaller failures are worth naming. **Hypotheticals** ("I would usually...") answer a different question than the one asked, so bring it back to one specific time. **Polished fiction** is worse: an invented or inflated story falls apart under the second follow-up question, and interviewers are trained to ask it. Every story you tell must be true, and every number must be one you could show.

### A worked example

Here's a common AI-role question, "Tell me about a time a model or AI system behaved badly. What did you do?", answered from Trace Detective. The numbers are illustrative; use your own.

**The weak version:**

> So, for my curriculum I had to build a lot of projects, and one of them was a research agent, which is basically an agent that searches the web and writes summaries. It used tools and we had tracing with OpenTelemetry and Langfuse, which is a tracing tool, and the agent had a bunch of tools like search and fetch and a summarizer. We ran it on a bunch of queries and some of the answers weren't great, so we looked at the traces and saw it was calling search too much. So we changed the prompt and added a limit on the tool calls and it was better after that. It was a really good learning experience about how agents work.

Count the problems. Most of the answer is Situation, and it's mostly tool names. It says "we" throughout for a solo project. "Weren't great" and "better" are unmeasured. There's no reasoning: why a limit, and why a prompt change? And it ends on a generic lesson.

**The strong version:**

> In my Trace Detective project I investigated a research agent I'd built earlier, which answers questions by searching the web and summarizing sources. My goal was to find out how often it failed on realistic questions, and to fix the worst failure with proof that the fix worked.
>
> I traced every model call and tool call, ran it on 40 real questions that friends wrote for me, and read every trace. I labeled each failure by hand rather than guessing. The biggest group, 9 of 40, was the same pattern: when a search returned nothing useful, the agent searched again with almost the same query, sometimes six or seven times, then ran out of steps and gave a confident answer with no sources.
>
> I had two options: tell it in the prompt to stop repeating itself, or change the code. I chose code, because a prompt is a request and the trace showed the model ignoring the one it already had. I made the search tool return a clear message when a query nearly matched a previous one, and I made the agent say "I couldn't find a reliable source" instead of answering when it hit the step limit with no sources. Then I turned those 9 failures into eval cases, so the bug couldn't come back unnoticed.
>
> On the 40 questions, unsourced answers dropped from 9 to 1, and the eval score on my full set went from 68% to 81%, though with 40 cases the interval is wide, so I treated it as a strong signal rather than a precise number. The habit I kept: read traces before changing prompts. My first guess about the problem was wrong.

It runs about two minutes. Situation and Task take two sentences. Action shows a method (trace, label, count), a decision with its reason, and what the learner did themselves. Result has numbers, an honest caveat, and a lesson that sounds like an engineer's.

### Building your story bank

You can't predict every question, but you don't need to. Interviewers ask dozens of variations of about ten underlying questions, and one good story can answer several. A **story bank** is a written set of 6–8 stories, each tagged with the questions it can answer. Prepare the bank, and in the interview your job becomes picking the right story and adapting its opening.

Start from your projects. A strong bank for someone finishing this curriculum might include:

1. **The Capstone with real users.** Your richest story: a user who used the system in a way you didn't expect, and what you changed. It answers "a time you received difficult feedback," "a project you're proud of," and "a time you had to change direction."
1. **Break Your Own Agent.** You attacked your own agent, found it was vulnerable, and fixed it with structural defenses rather than prompt tweaks. It answers "a security or safety issue you handled" and "a time you found a flaw in your own work."
1. **Trace Detective.** A model behaving badly, diagnosed with evidence, as in the worked example. It answers "debugging a hard problem" and "a time data proved you wrong."
1. **Cut the Bill.** A cost or latency cut with no loss in quality, proved with a paired eval comparison. It answers "a trade-off you made" and "a time you improved something that already worked."
1. **The first merged PR.** Working in a stranger's codebase, to their standards, through their review. It answers "a time you learned something quickly," "a time you received critical feedback," and "working with people you don't know."
1. **Team work.** From Working in a Team, your Capstone collaboration, or an earlier job: a disagreement, a handoff, or a time you unblocked someone. It answers "conflict with a teammate" and "a time you influenced a decision without authority."
1. **One failure.** Something that went wrong because of a decision you made. Every loop asks for one, and a candidate without a failure story looks either inexperienced or evasive.
1. **One story from before tech**, covered in [Using your earlier career](#using-your-earlier-career).

For each story, write a one-page card: the four STAR parts as short bullets (not a script to memorize), the headline number, the link to the evidence (case study, PR, eval results), and the list of questions it answers. Then make a grid with your stories as rows and common questions as columns, and check that every common question has at least two stories. Two matters because you shouldn't tell the same story twice in one loop.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Bullets, not scripts

Memorized scripts sound recited, and they break when a question is phrased in an unexpected way. Memorize the structure and the key facts: the numbers, the decision and its reason, the lesson. Then tell it fresh each time.

</div>

### Questions for AI roles

Beyond the classic questions, AI engineering interviews now ask questions that only make sense if you've built AI systems. Prepare for these in particular, because a good answer is strong evidence and many candidates have nothing to say.

- **"Tell me about a time a model behaved badly in production or testing."** They want your debugging method: did you look at traces and count failures, or guess and tweak prompts? Trace Detective or your Capstone. Name what you measured and how you prevented a repeat.
- **"Describe a trade-off between quality and cost or latency."** They want to see that you set a budget, measured both sides, and decided deliberately. Cut the Bill is built for this. Mention what you were willing to give up and what you weren't.
- **"Tell me about an eval that changed your mind."** This is a favorite, because it tests whether you trust measurement over intuition. Maybe a prompt you were sure was better scored worse, or an LLM judge disagreed with your own labels until you fixed its rubric. The honest admission ("I was wrong, and here's how I found out") is the point.
- **"How have you handled a prompt injection or safety issue?"** Break Your Own Agent. Describe the attack, what it could have done, why a prompt-only defense wasn't enough, and the structural fix: a narrower tool scope, an approval gate, an output check. Give the before-and-after attack success rate.
- **"How do you use AI coding tools, and how do you make sure their output is right?"** Every team now asks some version of this. They want to hear that you direct the assistant, review every diff, write or check the tests yourself, and can explain any code you ship. A specific moment helps: the time an assistant's change passed the tests but was wrong, and how you caught it. Be honest about how much you rely on these tools; pretending you don't use them is as unconvincing as pretending they do everything.

Notice the pattern: each of these questions is really asking "do you measure, and are you honest about what you found?" Your Evidence sections were designed to make the answer yes.

### Using your earlier career

If you worked in another field before this, interviewers will ask about it, often with "Walk me through your background" or "Why are you moving into AI engineering?" Don't apologize for the change. Tell it as one story with a direction: what you did, what you noticed, what you built, and why this role is the next step.

> I spent four years in customer support at a software company. I kept seeing the same twenty questions answered by hand, and when I tried the early support chatbots, they were confidently wrong in ways that cost us customers. I wanted to build the version that works, so I spent the last year learning to build and evaluate AI systems. My Capstone is a support-ticket assistant that one team now uses daily, and the label set for its evals came straight from my support experience.

That takes about thirty seconds and answers the unspoken question, "Is this person serious?" with evidence.

Earlier jobs are also a source of behavioral stories, especially for conflict, pressure and communication. A nurse who caught a medication error, a teacher who changed a lesson plan because the test scores showed it wasn't working, a sales rep who handled an angry customer: these are real STAR stories about judgment and ownership, and they often carry more weight than a project because real stakes were involved. Keep at least one in your bank. Connect it to the role in your Result or Learning sentence: "That's the same instinct I use now when an eval score looks too good."

### Questions to ask the interviewer

Nearly every interview ends with "Do you have any questions for me?" Saying "No, I think you covered everything" wastes the best chance you'll get to learn whether you want the job. Good questions also show you understand the work. Prepare five or six, and ask two or three, choosing ones the conversation hasn't already answered:

- "How do you evaluate model or prompt changes before they ship? Who decides when a score is good enough?"
- "What does on-call or incident response look like for the AI features?"
- "What's the hardest problem the team is working on right now?"
- "How do engineers here use AI coding tools, and how are their changes reviewed?"
- "What would a successful first three months look like for this role?"
- "How do new engineers get feedback and mentorship?"

The answers are information. A team that can't say how it evaluates changes is telling you something important about what the job will be like. Avoid questions you could have answered from the company website, and save salary questions for the recruiter, as covered in Offers and Negotiation.

### Practicing out loud

Reading your story cards silently is not practice. Stories that look fine on paper come out long, tangled and full of "um" the first time you say them. You have to speak them, and ideally hear yourself.

**Record yourself.** It's the most useful practice you can do alone. Open a webcam recorder or [OBS Studio](https://obsproject.com/), read a question aloud, answer it with a timer running, and watch the playback. It's uncomfortable at first, and that's what makes it work. Watch for:

- **Length.** Over three minutes means cut Situation. Under a minute usually means no reasoning in Action.
- **"We" count.** Tally them. Each one should be a choice, not a habit.
- **A clear result.** Could a stranger repeat your headline number after one listen?
- **Filler and pace.** A short pause sounds more confident than "um, so, basically."

Re-record the same answer until it's clean, then move on. Two or three passes per story is usually enough.

**Practice with a person, if you can.** A friend, a former colleague or a family member can read questions from a list and tell you where they got lost. They don't need to be technical; if a non-engineer can follow your story, an interviewer will too. Ask them to throw in one follow-up per story ("Why did you choose that?" or "What would you do differently?"), since follow-ups are where weak preparation shows. If no one is available, recording yourself covers most of the benefit.

**Use AI as a practice partner, not an author.** An assistant can play interviewer, ask follow-ups, and point out where an answer was vague or long. That's a good use, and some companies' guidance for candidates, such as [Anthropic's](https://www.anthropic.com/candidate-ai-guidance), explicitly welcomes AI for preparation. Don't let it write your stories: generated stories sound generic, contain details you didn't live, and collapse under the first real follow-up. In the interview itself, use no AI help unless the company says otherwise.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [Tech Interview Handbook's behavioral interview guide](https://www.techinterviewhandbook.org/behavioral-interview/). It's free and covers STAR, how interviewers score answers, and how to prepare for company values. Skip the sections promoting paid courses.
   - Then skim its [list of common behavioral questions](https://www.techinterviewhandbook.org/behavioral-interview-questions/) and copy the ten that appear most relevant to AI engineering roles into your story grid.
1. Read MIT's [guide to the STAR method](https://capd.mit.edu/resources/the-star-method-for-behavioral-interviews/) and use its worksheet as a template for your story cards, adding a line for the headline number and the evidence link.
1. Skim Amazon's [Leadership Principles](https://www.amazon.jobs/content/en/our-workplace/leadership-principles) as an example of a published rubric. For each of three principles, note which story in your bank shows it best. If you're targeting a company that publishes its values, do the same with its list.
1. Build your story bank, as in [Building your story bank](#building-your-story-bank):
   - Write 6–8 story cards, including at least one AI-specific story from [Questions for AI roles](#questions-for-ai-roles), one failure, and one from teamwork or your earlier career.
   - Make the story-by-question grid and check that every common question has at least two stories.
   - Write your 30-second background story, as in [Using your earlier career](#using-your-earlier-career).
1. Practice out loud and record it. Pick five questions, including "Tell me about a time a model behaved badly" and "How do you use AI coding tools responsibly?", and record yourself answering each with a two-minute timer. Watch every recording, score it against the checklist in [Practicing out loud](#practicing-out-loud), and re-record your two weakest answers. If a friend is willing, do one round live with them asking follow-ups. Keep your cards and notes; you'll use them in Project: Mock Interview Loop.
1. Write your list of five or six questions for interviewers, tailored to one real posting from your Role Map.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Why do AI teams use behavioral interviews, and what qualities are they scoring?](#what-behavioral-interviews-test)
- [What are the four parts of STAR, and roughly how should time be split between them?](#the-star-structure)
- [What are the three most common STAR failures, and how do you fix each one?](#common-star-failures)
- [What made the strong version of the worked example better than the weak one?](#a-worked-example)
- [Why should every common question have at least two stories in your bank?](#building-your-story-bank)
- [What is an interviewer really checking when they ask about an eval that changed your mind?](#questions-for-ai-roles)
- [What should you watch for when you review a recording of yourself?](#practicing-out-loud)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Questions to ask the company during your interview](https://github.com/viraptor/reverse-interview) is a long, community-maintained list of "reverse interview" questions grouped by topic: role, tech, team, management and company.
- [The Tech Interview Handbook's final questions page](https://www.techinterviewhandbook.org/final-questions/) offers more questions to ask at the end of an interview, sorted by who you're talking to.
- [Julia Evans' "Get your work recognized: write a brag document"](https://jvns.ca/blog/brag-documents/) describes a habit of keeping a running record of your work. Start one at your first job and your story bank will refill itself.
