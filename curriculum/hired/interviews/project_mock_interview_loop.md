### Introduction

Interviews are a skill, and skills improve with practice under realistic conditions. In this project you'll run yourself through a full mock interview loop of the kind AI engineering candidates face: a resume tailored to a real posting, a 45-minute timed system design of a customer-support agent, a recorded mock interview with a peer, and a take-home assignment completed in four hours or less. You'll collect feedback at every step and turn it into a plan.

By the end you'll have done the hard parts once already, which is the best cure for interview nerves.

### Before you start

- Create a repo named `mimir-mock-interview-loop` to hold your resume, design doc, feedback notes and links. Keep anything personal you don't want public (phone number, address) out of the repo, or make the repo private and share it with reviewers.
- Pick one real, current posting for your target role from your Role Map. Save its text in the repo.
- Find a peer for the mock interview: someone else working through this curriculum, a friend who works as an engineer, or a member of a developer community. Agree on a time and on recording the session, and offer to interview them in return.
- Have the draft resume from Resume for AI Roles and the practice design from AI System Design.
- Have a way to record: [OBS Studio](https://obsproject.com/) or the recording feature of whatever video call tool you use.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. **Tailored resume.** Produce a one-page resume tailored to your chosen posting. In the README, include a short table mapping the posting's top five requirements to the resume line that addresses each. Get written feedback from at least one person and record what you changed.
1. **Timed system design.** Set a 45-minute timer and write a design for a customer-support agent for the company in your posting (or a similar product). Stop when the timer ends, even if unfinished. The document must cover:
   - Requirements and clarifying assumptions.
   - Success metrics and how you'd measure them.
   - An architecture diagram and the reasoning behind workflow versus agent choices.
   - Evals: offline test set, online monitoring, and how failures become new tests.
   - Safety: prompt injection, tool permissions, human escalation and PII handling.
   - A cost and latency estimate with your arithmetic shown.
   Commit it exactly as it was when time ran out, then add a separate "with hindsight" section listing what you missed.
1. **Recorded mock interview.** Do a 45 to 60 minute mock interview with your peer: about 15 minutes of behavioral questions (built on your resume stories) and 30 to 45 minutes of the support-agent design, talked through live. Record it with consent. Afterward, write feedback notes covering what your peer said, what you noticed watching the recording, and your three biggest improvements to make. Store the recording privately and link to it only if both of you agree.
1. **Take-home.** Complete a self-timed take-home in four hours or less, submitted as its own repo named `mimir-take-home`. Use a take-home from a real company if you have one; otherwise, build this: a small HTTP service that classifies incoming support messages, answers common ones with retrieval over a provided FAQ, and escalates the rest, with at least 20 eval cases and a reported score. Record your start and end times in its README, along with what you'd do with more time.
1. Push your project to GitHub with a README that explains what each part is, links to the take-home repo, and ends with a written plan: the three things you'll practice before your next real interview, and how.

#### Extra credit

- Swap roles and interview your peer, then write down what you learned from being the interviewer.
- Repeat the timed design a week later with a different prompt (for example, "design an agent that triages bug reports") and compare how much you covered.
- Submit the tailored resume for the real posting.

</div>

### Submitting your work

A strong submission shows the loop actually ran: a timestamped, unedited 45-minute design, real feedback notes from a real person, and a take-home that runs, has tests or evals with a reported score, and states honestly what was left undone. The self-critique matters more than the polish. Interviewers hire people who can see their own gaps and close them, and this repo is proof that you can.
