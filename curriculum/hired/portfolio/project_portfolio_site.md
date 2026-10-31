### Introduction

In this project you'll build the page you send to every recruiter and hiring manager: a personal portfolio site, hosted free on GitHub Pages, with three detailed case studies, a demo video for each, an About section that says what role you want, and at least one technical blog post. Your Final Capstone is the centerpiece. The other two case studies come from the strongest projects you built along the way.

This is the most important artifact you'll make in Getting Hired. Your resume, applications and cold messages will all point here.

### Before you start

- Create a repo named `<your-github-username>.github.io`. GitHub Pages serves a repo with that exact name at `https://<your-github-username>.github.io`. If you'd rather keep that name free, use `mimir-portfolio` and enable Pages in the repo settings. Read [GitHub Pages](https://pages.github.com/) and the [GitHub Pages quickstart](https://docs.github.com/en/pages/quickstart).
- Choose how to build it. Plain HTML and CSS from HTML and CSS Essentials is enough. A static site generator such as Jekyll (built into GitHub Pages) or any other works too. Don't spend more than a day on design; content is what gets you hired.
- Pick your three showcase projects. The Capstone is number one. Choose two more that show different skills from your Role Map's top skills, such as an agent from Agentic Systems and a measured project such as Cut the Bill or Fine-Tune a Small Model.
- Have your Capstone case study and demo video from Case Studies and Demo Videos, and your posts from Learning in Public.
- Collect each showcase project's Evidence before you write: its CI badge and a link to a passing run, its eval score with `n` and confidence interval, a sample trace, its injection test results, and its cost and latency numbers. The case studies are built from these.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Publish a site on GitHub Pages with a home page, a case study page for each of your three projects, a blog section, and an About section. It must work and be readable on a phone.
1. Write the About section: two or three sentences naming your target role, what you build, and how to contact you. Link your GitHub, and add a link to your resume once you've written it in Resume for AI Roles.
1. Publish three case studies, with your Capstone first, following the five-part arc from The shape of a case study. The Capstone one is the version you revised in Case Studies and Demo Videos; for the other two, start from those projects' READMEs and Evidence sections rather than writing from scratch. Each one must include:
   - The problem, the constraints and your approach, in under 300 words before any details, so the first screen makes the case on its own.
   - Measured evidence near the top, in a results table: eval scores with the test set size and a 95% confidence interval, plus cost and latency against their budgets where relevant (Turning Evidence into headlines).
   - At least one failure case and what you did about it.
   - A "How I built it" paragraph saying what you wrote and what frameworks, templates and AI assistants did (Being honest about what you built).
   - Two or three next steps that follow from the evidence.
   - An embedded or linked demo video of three minutes or less.
   - Links to the GitHub repo and a live demo (or a clear note on why there isn't one).
1. Publish at least one technical blog post of 600 words or more on the site. Good choices are a deep dive on one decision in your Capstone, or your Role Map findings. Include code, numbers or both.
1. Check every link on the site works, and that each linked repo's README works as a front door: a one-line description, a CI badge, and links back to its case study and video (Your README is the front door).
1. Run a Lighthouse audit on the live site, as you did in HTML and CSS Essentials, for both the mobile and desktop settings. Fix what it reports, use the site with only the keyboard, and record the final scores.
1. Have at least one person read the site and tell you what they understood, ideally two: one technical and one not. A friend, a working engineer or someone from a developer community all count. Give them the 30-second test from Submitting your work, then record their feedback and what you changed in the repo's README.
1. Push your project to GitHub with a README that explains what it does, how to run or edit it, and what you learned.

#### Evidence

A static site has no model calls, so the engineering rungs of the evidence ladder are carried by the projects it links to. The site's job is to make that evidence easy to find, and to prove the site itself works. Your README must show:

- **The live URL**, at the top, and a screenshot of the home page on a phone-width screen.
- **A passing link check.** Ideally a GitHub Actions workflow (Linting, Formatting and CI) that runs a link checker such as [lychee](https://github.com/lycheeverse/lychee), through the [lychee action](https://github.com/lycheeverse/lychee-action), on every push, with its status badge and a link to a passing run. If you can't get it working in CI, run lychee locally against the live site and commit its output with the date. Either way, the check must include the links out to your repos, videos and demos, not just links between your own pages.
- **Accessibility and performance scores.** The [Lighthouse](https://developer.chrome.com/docs/lighthouse/overview) accessibility, performance and best-practices scores for the home page and one case study page, with the date, before and after your fixes. Note anything you fixed by hand after the keyboard test, since an automated audit misses many real problems.
- **Each case study's numbers, linked to their source.** A table with one row per case study: the repo link, the CI badge or a link to a passing run, the headline eval score with `n` and its 95% confidence interval, cost and latency per task, and a link to the injection tests. Every number on the site must link to the README, trace, eval report or CI run it came from, so a reviewer can check it in one click.
- **Which rungs come from where.** One line per case study naming where its CI (ruff and pytest), traces, eval score with a confidence interval, and prompt-injection test live. These rungs belong to the linked projects, not the site; if a showcase project predates a rung (for example an early project with no injection test), say so rather than implying it has one.
- **Reader feedback and the change you made.** Each reader's feedback, summarized with a quote or two, what they understood after 30 seconds, and the specific change you made in response, with a link to the commit.

#### Extra credit

- Add a custom domain.
- Add an RSS feed for your blog so others can subscribe.
- Post your case study or blog post where your target audience reads (a relevant community forum, social media or a newsletter submission) and record what happened.

</div>

### Submitting your work

A strong portfolio passes the 30-second test: a stranger can tell what role you want, see your best project, and find its evidence within half a minute. Every claim links to proof, every video is short, and the writing is plain and specific. Ask a working engineer in your target role to look at it, and treat their first confused question as a bug to fix.
