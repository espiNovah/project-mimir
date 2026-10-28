### Introduction

Most job seekers guess at what employers want. In this project you'll measure it. You'll collect 20 real postings for your target role, tally the skills they ask for, map each skill to a project you've already built (or mark it as a gap), and write a six-week plan to close your three biggest gaps. The result is a short, data-backed document that tells you what to put first on your resume and portfolio, and what to build next.

It's also a useful thing to share. A clear write-up of "what 20 agent engineer postings actually ask for" makes a good first blog post for your Portfolio Site.

### Before you start

- Create a new repo named `mimir-role-map`. A spreadsheet is fine for collecting data, but commit it as a CSV so it's versioned and readable on GitHub.
- Have the target role you chose in AI Roles Explained, and the five postings you analyzed in Reading Job Postings.
- Make a list of every project you've completed in this curriculum, from Hello, uv through your Capstone, with a one-line description of each. You'll map skills to these.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Collect 20 real, current postings for your target role (posted within the last three months). Use a mix of company sizes and at least three different job boards or company career pages. In `postings.csv`, record company, title, date, link, location or remote policy, seniority, and the full list of skills or requirements. Save a copy of each posting's text in `postings/`, because postings disappear.
1. Normalize the skills into a consistent vocabulary (for example, merge "RAG," "retrieval" and "vector search" into one skill). Document your merging rules in the README.
1. Produce a skills tally table: each skill, how many of the 20 postings mention it, and whether it was usually a must-have or a nice-to-have. Sort by frequency. Include a bar chart of the top 15 skills.
1. Map each of the top 20 skills to evidence: the specific project (by title and repo link) that proves you have it, or "gap" if you don't. Rate each mapping strong, partial or gap.
1. Choose your top three gaps, weighted by how often they appear and how much they matter. For each, write a six-week plan with weekly goals, the resources you'll use, and one concrete deliverable (a small project, a contribution or a blog post) that will become new evidence.
1. Push your project to GitHub with a README that explains what it does, how to run it, and what you learned. Lead with the three most surprising findings from the tally.

#### Extra credit

- Write a short Python script that reads `postings.csv`, normalizes skills with your rules, and regenerates the tally table and chart, so you can rerun the analysis next quarter.
- Repeat the tally for a second, adjacent role and compare the two.
- Publish your findings as a blog post and link it from your Portfolio Site.

</div>

### Submitting your work

A strong role map is honest. Gaps are named plainly, not hidden, and each strong rating links to a real repo. The six-week plan is specific enough that a friend could check in on week three and tell whether you're on track. Revisit the map after you finish Getting Hired and update the ratings as you close gaps.
