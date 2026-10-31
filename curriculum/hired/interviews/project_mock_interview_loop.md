### Introduction

Interviews are a skill, and skills improve with practice under realistic conditions. In this project you'll run yourself through a full mock interview loop of the kind AI engineering candidates face: a resume tailored to a real posting, a 45-minute timed system design of a customer-support agent, a 45-minute live coding round with no AI help, a timed build where you work with an AI coding assistant, a recorded mock interview, and a take-home assignment completed in four hours or less. You'll collect feedback at every step and turn it into a plan.

By the end you'll have done the hard parts once already, which is the best cure for interview nerves.

### Before you start

- Create a repo named `mimir-mock-interview-loop` to hold your resume, design doc, coding rounds, feedback notes and links. Keep anything personal you don't want public (phone number, address) out of the repo, or make the repo private and share it with reviewers.
- Pick one real, current posting for your target role from your Role Map. Save its text in the repo.
- Find an interviewer for the live rounds: a friend who works as an engineer, a working engineer you met while Running the Search, or a member of a developer community. Agree on a time and on recording the session, and offer to interview them in return. If you can't find anyone, you can still do every round; see [If you can't find an interviewer](#if-you-can-t-find-an-interviewer).
- Have the tailored resume and feedback from Resume for AI Roles, the practice design from AI System Design, the stories you prepared in Behavioral Interviews, and the practice log from Coding Interviews.
- Have a way to record: [OBS Studio](https://obsproject.com/) or the recording feature of whatever video call tool you use.

### If you can't find an interviewer

Don't skip the live rounds; run them solo. Before you start, write down a fixed question list and a rubric, and commit both, so you can't adjust them after seeing how you did.

- **Question list.** Four behavioral questions taken from the [Tech Interview Handbook's behavioral questions](https://www.techinterviewhandbook.org/behavioral-interview-questions/), the support-agent design prompt, and, for the coding round, a problem picked at random from the Grind 75 list among those not in your practice log.
- **Rubric.** One line per thing you're checking, scored 1 to 3. For behavioral answers: a clear STAR structure, your own role stated, a number, under three minutes. For the design: structure stated at the start, requirements clarified, metrics, evals, safety and cost math covered. For coding: each step of the talk-out-loud routine.
- **Run and review.** Record yourself on camera answering out loud, with a timer running, as if someone were listening. Wait at least a day, then watch the recording and score it against the rubric with timestamps. If you can, also post the design or a short clip in a developer community and ask for written comments; any reply counts as outside feedback.

A solo mock is weaker than a real one, because nobody interrupts or asks follow-ups, so say in your README that you ran it solo. It still shows you every silence, filler word and skipped step.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. **Tailored resume.** Produce a one-page resume tailored to your chosen posting, following Tailoring to a posting in Resume for AI Roles. In the README, include a short table mapping the posting's top five requirements to the resume line that addresses each. Run `pdftotext` on the PDF as in ATS basics without the myths and fix anything that comes out jumbled. Get written feedback from at least one person and record what you changed.
1. **Timed system design.** Set a 45-minute timer and write a design for a customer-support agent for the company in your posting (or a similar product), using the time-boxed structure from AI System Design. Stop when the timer ends, even if unfinished. The document must cover:
   - Requirements and clarifying assumptions.
   - Success metrics and how you'd measure them.
   - An architecture diagram and the reasoning behind workflow versus agent choices.
   - Evals: offline test set, online monitoring, and how failures become new tests.
   - Safety: prompt injection, tool permissions, human escalation and PII handling.
   - A cost and latency estimate with your arithmetic shown.
   Keep a time log as you go: the clock time you started each section and when you stopped. Commit the document exactly as it was when time ran out, then add a separate "with hindsight" section listing what you missed. If your target loop also includes a general design round, note which parts of System Design Basics (caches, queues, databases) your design used or should have used.
1. **Live coding round (45 minutes, no AI).** Have your interviewer give you one problem you haven't seen, at the Easy-to-Medium level from Coding Interviews (they can pick one from the [Grind 75 list](https://www.techinterviewhandbook.org/grind75/) that isn't in your practice log). Solve it in 45 minutes in a plain editor with no AI assistant, following the talk-out-loud routine out loud: clarify, work an example, state the brute force, find the pattern, code, test it yourself, and state the final complexity. Record the session. Afterward, commit the code exactly as it was at the 45-minute mark, with the `assert` tests you wrote during the round, then a corrected version if it needed one. Note the minutes spent on each step of the routine and score yourself on each step.
1. **AI-assisted build round (60 minutes).** This round practices the fourth kind of coding round from Coding Interviews, where an AI assistant is allowed and what's graded is your judgment. Set a 60-minute timer and build this, using an AI coding assistant as you learned in Working With AI Coding Assistants: a function that takes a raw support message, asks a model for a structured result (category, urgency, and whether it needs a human) as in Getting Structured Output, validates it with Pydantic (JSON Schema and Pydantic), and retries once on invalid output, as in Timeouts, Retries and Rate Limits. Include pytest tests that use a fake model client, as in Testing with pytest, so they run without an API key. Rules for the round:
   - Narrate as you go (record it, or keep a running log): what you asked the assistant to do and why, and what you decided to do yourself.
   - Read every line the assistant writes before you accept it. In a `REVIEW.md`, list each bug, wrong assumption or unneeded code you caught in its output, and how you found it.
   - When time is up, explain the finished code in your own words: what each function does, why the retry is safe, and one way it could still fail. If you can't explain a part, say so; that's a gap for your plan.
1. **Recorded mock interview.** Do a 45 to 60 minute mock interview with your interviewer: about 15 minutes of behavioral questions answered with STAR stories from your projects, as in Behavioral Interviews, and 30 to 45 minutes of the support-agent design, talked through live. Record it with consent. Afterward, write feedback notes covering what your interviewer said, what you noticed watching the recording (with timestamps), and your three biggest improvements to make. Store the recording privately and link to it only if both of you agree. You can run this in the same session as the live coding round if your interviewer has time.
1. **Take-home.** Complete a self-timed take-home in four hours or less, submitted as its own repo named `mimir-take-home`. Use a take-home from a real company if you have one; otherwise, build this: a small HTTP service that classifies incoming support messages, answers common ones with retrieval over a provided FAQ, and escalates the rest, with at least 20 eval cases and a reported score. Record your start and end times in its README, along with what you'd do with more time. If you use AI tools, say how, as you would for a real company that allows them.
1. Push your project to GitHub with a README that explains what each part is, links to the take-home repo, and ends with a written improvement plan (see Evidence).

#### Evidence

Your README must show each of these, with links a reviewer can follow:

- **The tailored resume.** The PDF, the requirements-to-resume table, a note that the `pdftotext` output is clean, and the feedback you got with the changes you made. (Resume for AI Roles)
- **The timed design and its time log.** The design as it was when the timer ended, its commit timestamp, the per-section time log, and the "with hindsight" section kept separate. (AI System Design)
- **The live coding round.** The code as it stood at 45 minutes with its tests, any corrected version, the minutes spent on each step of the talk-out-loud routine, and your self-score. (Coding Interviews)
- **The AI-assisted build.** The code and passing tests, start and end times, the log of what you asked the assistant, `REVIEW.md` with the problems you caught in its output, and your plain-language explanation of the finished code. (Coding Interviews; Working With AI Coding Assistants)
- **The recorded mock interview.** Who interviewed you (or that it was a solo mock, with the committed question list and rubric), the length, the feedback notes with timestamps, and the recording link if both of you agreed to share it.
- **The take-home, with tests and CI.** The `mimir-take-home` repo meets the full evidence ladder: a GitHub Actions workflow running ruff and pytest on every push (Linting, Formatting and CI), traces of every model call in JSONL or a database (Logging and Tracing), an eval score on the 20+ cases reported with its 95% confidence interval and `n` (Eval Statistics; expect it to be wide with this few cases, and say so), and at least one prompt-injection test case, such as a support message that tells the service to ignore its instructions, with what the service did. (Prompt Injection and the Lethal Trifecta) The README states the start and end times and what was left undone.
- **An improvement plan.** The three things you'll practice before your next real interview, each tied to a specific piece of evidence above (a timestamp, a rubric score, a bug you missed), with how you'll practice it, how often, and the date you'll rerun that round to check.

#### Extra credit

- Swap roles and interview your partner, then write down what you learned from being the interviewer.
- Repeat the timed design a week later with a different prompt (for example, "design an agent that triages bug reports") and compare how much you covered.
- Rerun the live coding round two weeks later with a new problem and compare the time log and rubric scores.
- Submit the tailored resume for the real posting.

</div>

### Submitting your work

A strong submission shows the loop actually ran: a timestamped, unedited 45-minute design, coding rounds committed as they stood when time ran out, real feedback notes (from a person, or an honest solo review against a rubric you wrote first), and a take-home that runs, has tests, CI and evals with a reported score, and states honestly what was left undone. The self-critique matters more than the polish. Interviewers hire people who can see their own gaps and close them, and this repo is proof that you can.
