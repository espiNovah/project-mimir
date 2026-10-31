### Introduction

Your resume has one job: get you to the first conversation. It won't get you hired on its own, and it doesn't need to tell your whole story. It needs to make a recruiter and then a hiring manager think "this person might be able to do the job; let's talk."

For someone entering AI engineering without an AI job title, that's a real challenge, because the first thing most readers look at is your recent job history. The answer is to lead with evidence: projects with measured results, a merged open source pull request, and links to a portfolio that backs every claim. You already have the material. Your projects produced eval scores with confidence intervals, cost and latency numbers, injection tests and CI runs, and your Portfolio Site turns them into case studies. This lesson shows you how to compress all of that into one page.

You'll use the resume you draft here in Project: Mock Interview Loop, where you tailor it to a real posting and get feedback on it.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What AI engineer and agent engineer hiring managers look for.
- How a resume actually gets read, by software and by people.
- A clean, one-page layout, and applicant tracking systems without the myths.
- Turning projects into bullet points with numbers.
- Framing an earlier career for an AI role.
- Links that do the work, and tailoring to a posting.
- A before-and-after example, and common mistakes.

### What hiring managers look for

Go back to the tally from your Role Map. For AI engineer and agent engineer roles, the same themes come up again and again, and each one maps to evidence you can show:

- **You ship working software.** Strong Python, APIs, databases, deployment. Evidence: deployed projects with live links, CI badges, Docker, a production setup like Ship It.
- **You measure quality.** This is the signal that separates AI engineers from people who wired up a chatbot over a weekend. Evidence: eval scores with test set sizes and confidence intervals, judges you validated against your own labels, before-and-after results.
- **You understand agents and their risks.** Tool design, agent loops, MCP, memory, approvals, prompt injection. Evidence: an agent with an eval suite, injection tests that pass, approval gates for irreversible actions.
- **You care about cost and latency.** Evidence: cost per task and p95 latency against a budget, and a project where you made something cheaper or faster without losing quality.
- **You communicate clearly.** Evidence: case studies, blog posts, clear READMEs, and the resume itself.
- **You learn fast.** Evidence: a run of projects that get harder over time, and an open source contribution to a library you hadn't used before.

Notice that none of these is "knows tool X." Hiring managers want concepts backed by proof. Tools matter mostly as keywords that help you get found, which the ATS section covers.

### How a resume gets read

A resume usually passes through three readers.

The first is software. Most companies use an **applicant tracking system (ATS)**, a database that stores applications, extracts text from your resume into fields (name, jobs, dates, skills) and lets recruiters search and filter. The second is a **recruiter**, who often reads for well under a minute and checks basic fit: does this person want this role, are they in a location and work situation we can hire, do the skills match, is there something here worth a hiring manager's time? The third is the **hiring manager** or an engineer on the team, who reads more closely, clicks a link or two, and decides whether to interview you.

Design for all three. Clean, parseable text serves the software. A clear target role, location and top-line evidence near the top serve the recruiter. Specific, checkable bullets and links serve the hiring manager.

### A one-page layout

One page. Every recruiter and hiring manager you'll meet early in your career expects it, and the constraint forces you to keep only your strongest material. For a career changer, a good order is:

1. **Header.** Your name, target title ("AI Engineer" or "Agent Engineer"), city or "Remote, US time zones," email, and links to your portfolio, GitHub and LinkedIn.
1. **Summary** (optional, two lines at most). Your target role and your strongest evidence, not adjectives. "Career changer from customer support into AI engineering. Built and deployed agents with eval suites, approval gates and cost tracking; one merged PR to an open source agent library."
1. **Projects.** Your three showcase projects, each with a one-line description, two or three bullets and a link. This section does the work your job history can't yet.
1. **Skills.** A short, grouped list: languages, AI and agent concepts, backend and infrastructure, tools. Only list what you could discuss in an interview.
1. **Experience.** Earlier jobs, with bullets framed as described in Framing an earlier career.
1. **Open source** (or fold it into Projects). Your merged PR, with a link.
1. **Education and training.** Degrees if you have them, and this curriculum described plainly: "Project Mímir, a free, self-directed AI engineering curriculum, 2025–2026." A short line is enough; the projects carry the weight.

Use a single column, standard section headings ("Projects," "Experience," "Skills," "Education"), a common font at 10 to 12 points, and margins that leave white space. Write it in any word processor or a plain template, and export to PDF. Keep a plain text copy too, for the many application forms that ask you to paste it in.

### ATS basics without the myths

A lot of resume advice online is fear-driven, and much of it is wrong. Here's what's actually true about applicant tracking systems.

**Myth: an ATS automatically rejects most resumes.** Mostly, it doesn't. An ATS is a database with search, and most decisions are still made by people reading it. Automatic rejections usually come from **knockout questions** on the application form, such as work authorization, location or a required license, not from a robot scoring your prose. Answer those questions honestly; that's where filtering really happens.

**True: parsing can garble your resume.** The ATS extracts your text into fields. Two-column layouts, text boxes, tables, icons and text inside images can come out scrambled or missing. Contact details in a page header or footer are sometimes dropped. A single-column layout with plain text avoids all of this. Check it yourself: install the free poppler tools (`brew install poppler` on macOS, `sudo apt install poppler-utils` on Ubuntu) and print the text the way a simple parser would see it:

```bash
# Extract the PDF's text in reading order. If sections come out jumbled
# or your email is missing, a parser will have the same trouble.
pdftotext resume.pdf - | less
```

**True: keywords help you get found.** Recruiters search the ATS for terms like "RAG," "evals," "Python" or "LangGraph." If you have a skill, use the posting's exact words for it somewhere on the page, so a search finds you.

**Myth: you should stuff in keywords, or hide them in white text.** Recruiters see the extracted text, so hidden keywords show up as an obvious trick. Keyword lists with nothing behind them read as padding to the human who comes next.

**Mostly myth: PDFs can't be parsed.** Modern systems handle a text-based PDF fine. If a posting explicitly asks for a Word document, send one.

### Bullets that lead with evidence

The single biggest improvement to most resumes is rewriting bullets from duties into outcomes. A useful pattern is "**accomplished X, as measured by Y, by doing Z**":

- X is the result, in words a recruiter understands.
- Y is the number that proves it, with enough context to be meaningful.
- Z is the method, which is where you name the skills and keywords.

Your projects give you real numbers to use. Some examples, built from the Evidence you produced:

- "Built a cited docs Q&A system that answered 84% of 120 held-out questions correctly (95% CI 77–90%), up from 71%, by adding hybrid search and a reranker after error analysis."
- "Cut an agent's cost per task by 46% with no loss in eval score, using prompt caching and routing easy cases to a cheaper model."
- "Shipped a workflow automation agent with human approval for irreversible actions; 0 of 40 prompt-injection runs triggered a forbidden action."
- "Deployed a FastAPI service with Postgres, background jobs and auth on a managed cloud, with CI running ruff, pytest and evals on every pull request."

Every bullet should have a number if one exists: a score, a test set size, a cost, a latency, a count of users or tests. Context makes the number meaningful. "99% accuracy" means little; "99% on 500 labeled support tickets, against 81% for a keyword baseline" means a lot. Include the confidence interval where it fits, since few candidates do, and it shows you understand measurement. Keep each bullet to one or two lines, and start it with a strong verb: built, shipped, measured, cut, designed, deployed.

### Projects as experience

Without an AI job title, your Projects section carries the resume, so put it above Experience. Treat each project like a job entry: a name, a one-line description of what it does and for whom, two or three evidence bullets, and a link to the case study. Your Capstone goes first, because it had real users and a real deployment.

Three or four projects are enough. Listing every project from the curriculum makes it hard to see which ones matter, and suggests you're following a course rather than building things. Choose the ones that match the target role, the same way you chose case studies for your portfolio. A merged open source PR deserves its own line, because it's work reviewed and accepted by people who owe you nothing.

### Framing an earlier career

If you worked in support, operations, teaching, sales, healthcare, finance or anything else before this, that experience is an asset, not a gap to hide. AI systems are built for real users in real domains, and someone who has done the users' job understands the problem better than an engineer who hasn't. This is especially valuable for forward-deployed and solutions roles, which are about understanding customers.

Describe earlier jobs in terms of outcomes and the parts that transfer:

- Domain knowledge: "Handled 60+ billing tickets a day; later used this to design the label taxonomy for a support-ticket classifier."
- Process and measurement: "Cut average handling time by 20% by writing macros and a triage guide for the team."
- Communication: "Trained 15 new hires; wrote the internal knowledge base used by the whole support team."
- Any technical work you did: spreadsheets, scripts, automations, SQL reports.

Keep these bullets short, two or three per job, and drop jobs that are old and unrelated. Connect the dots where you can, so the reader sees one story: someone who understood a problem from the inside and learned to build the solution.

### Links that do the work

Links are how a skeptical reader checks your claims, so make them easy to use and worth clicking.

- **Portfolio.** Your Portfolio Site, at the top. Link to individual case studies from each project entry, not just the home page.
- **GitHub.** Pin your showcase repos, and make sure each README opens with a one-line description, a CI badge and a link to the case study.
- **LinkedIn**, if you use it, with the same target title and projects as the resume.

Write links as visible, short text such as `yourname.github.io/invoice-chaser`, not hidden behind words like "here." Printed resumes and some ATS parsers drop hyperlinks, and a visible address still works. Before you send any version, click every link.

### Tailoring to a posting

A generic resume is weaker than a tailored one, but tailoring doesn't mean rewriting from scratch. Keep a **master resume** with every bullet you might use, then make a version per application in about twenty minutes:

1. Read the posting as you learned in Reading Job Postings, and list its top five must-haves.
1. For each must-have, find the bullet that proves it. Move those bullets and projects to the top.
1. Use the posting's words for skills you genuinely have. If they say "retrieval-augmented generation" and you wrote "RAG," include both.
1. Cut what doesn't serve this role to keep it at one page.
1. Adjust the title and summary to match the role's name.

Your Role Map already tells you which skills your target postings value most, so your master resume should lead with those. In Project: Mock Interview Loop you'll make a table mapping a posting's top five requirements to the resume line that covers each; doing that for every application you care about is a good habit.

### A before and after example

Here's a project entry from a career changer's first draft:

```text
PROJECTS
Chatbot Project
- Worked on a chatbot using RAG, LangChain, OpenAI, Claude, Pinecone,
  pgvector, FastAPI, Docker, React
- Responsible for the backend and making the AI work well
- Learned a lot about prompt engineering and AI
```

It lists tools without saying what was built, describes duties instead of results, has no numbers and no link, and "making the AI work well" invites the question "how well?" Here's the same project rewritten:

```text
PROJECTS
Docs Q&A Assistant (case study: yourname.github.io/docs-qa)
Cited question answering over 400 pages of internal docs, deployed with a web UI.
- Raised correct, cited answers from 71% to 84% on 120 held-out questions
  (95% CI 77-90%) by adding hybrid search and a reranker after error analysis.
- Validated an LLM judge against 60 hand labels (TPR 0.92, TNR 0.88) and ran
  the eval suite in CI on every pull request.
- Built with Python, FastAPI, Postgres and pgvector, and a Next.js front end;
  $0.004 per answer, p95 latency 2.8 s.
```

The second version says what the project does in one line, leads with a measured result, shows evaluation skill, names the stack in context, and links to proof. A recruiter can match keywords; a hiring manager has three things to ask about.

### Common mistakes

- **Two pages, or a wall of text.** Cut until it fits on one page with white space.
- **Tool lists without evidence.** Every skill on the page should be backed by a project you can talk about.
- **Numbers without context.** A score needs a test set size, and ideally a baseline or interval.
- **Overclaiming.** Anything on your resume is fair game in an interview. Don't write "led" for solo work, "expert" after three months, or a tool you used once for ten minutes. Be honest about what frameworks and AI assistants did, as in Case Studies and Demo Videos.
- **An AI-written voice.** It's fine to ask a model to critique your resume or spot vague bullets. But generic phrasing ("leveraged cutting-edge AI to drive impact") is easy to spot and says nothing. Every claim must be yours and checkable.
- **Broken or missing links**, typos, and inconsistent dates. Proofread aloud, and ask someone else to read it.
- **Personal details that don't belong.** In the US and many other countries, leave off photos, age, marital status and full home address. Follow local norms where you apply.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [Tech Interview Handbook resume guide](https://www.techinterviewhandbook.org/resume/), a free, thorough guide to software engineering resumes.
   - Read all of it, and pay special attention to the sections on writing bullet points and on what to include for projects.
1. Read the "About" and project pages of three engineers whose work you admire (for example, people you found in Learning in Public), and note how they describe their projects in one line.
   - Borrow the clearest one-line structure for your own project entries.
1. Rewrite each of your three showcase projects as two or three resume bullets using the "accomplished X, as measured by Y, by doing Z" pattern. Every bullet must include a number from that project's Evidence.
1. Draft a one-page master resume with the projects-first layout from A one-page layout, including your earlier experience framed as in Framing an earlier career. Export it to PDF and run `pdftotext` on it, as in ATS basics without the myths. If the text comes out in the wrong order or is missing anything, fix the layout.
1. Tailor a copy to one real posting from your Role Map, following Tailoring to a posting, and ask one person to give you written feedback on it. Keep both versions and the feedback; you'll need them in Project: Mock Interview Loop.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What evidence signals that a candidate can measure the quality of an AI system?](#what-hiring-managers-look-for)
- [Who are the three readers of a resume, and what does each look for?](#how-a-resume-gets-read)
- [Where do most automatic rejections actually come from, and what really goes wrong with ATS parsing?](#ats-basics-without-the-myths)
- [What are the three parts of an evidence-led bullet, and why does a number need context?](#bullets-that-lead-with-evidence)
- [Why should a career changer put Projects above Experience?](#projects-as-experience)
- [How do you describe an earlier, non-technical job for an AI role?](#framing-an-earlier-career)
- [How do you tailor a resume to a posting in about twenty minutes?](#tailoring-to-a-posting)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The Tech Interview Handbook behavioral interview guide](https://www.techinterviewhandbook.org/behavioral-interview/) helps you turn the same resume stories into strong interview answers.
- [RenderCV](https://github.com/rendercv/rendercv) is a free, open-source tool that builds a clean, single-column PDF resume from a YAML file, so you can keep your master resume in Git and generate tailored versions.
