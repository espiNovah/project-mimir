### Introduction

A first full-time AI job can take months to land. Paid project work can fill that gap, and it does more than pay bills. A small contract gives you a real client, real data, a deadline and someone who will vouch for you afterward. On a resume, "Freelance AI engineer: built an invoice-triage workflow for a 12-person accounting firm, now handling 300 emails a week" reads as experience, because it is.

Many working AI engineers got their start this way. Companies of every size want to "do something with AI" and don't have anyone who knows how. Your projects already cover the work they need: extraction, retrieval, workflows, agents, evals and deployment. What this lesson adds is the business side: finding clients, scoping the job, pricing it, getting a contract signed, protecting the client's data, delivering with evidence, and turning the result into a case study and a reference.

A **freelancer** (or **contractor**) is someone who sells work to a client for a project or a period of time, without becoming their employee. You pay your own taxes, use your own tools and carry your own risk. That freedom comes with responsibilities, and this lesson is about handling them well enough that your first client wants to hire you again.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why contract work is a good bridge into a first full-time role.
- The kinds of AI freelance and contract work that exist.
- Where first clients come from, and the trade-offs of each source.
- Scoping a small project and writing a one-page proposal with success criteria.
- Pricing: fixed price versus hourly, and how to avoid underpricing.
- Simple contracts, payment terms and protecting client data and API keys.
- Delivering with evidence, and turning the contract into a case study and a reference.

### Why contract work is a bridge

Contract work solves the career changer's oldest problem: jobs want experience, and experience needs a job. A paid project is experience. It has a stakeholder who isn't you, requirements that change, data you didn't choose, and consequences if it breaks. Those are exactly the parts a portfolio project can only simulate.

It also strengthens the rest of your search. Each client is a new person in your network, often a business owner who knows other business owners. A good result becomes your strongest case study, because a hiring manager trusts "used weekly by a real firm" more than any demo. Some contracts turn into job offers directly: a client who likes your work may ask you to stay on, or a contract-to-hire role may start as a contract by design.

Be clear-eyed about the costs. Freelancing pays unevenly, takes time away from applications, and puts sales, admin and accounting on your plate. Treat it as part of your search, not a replacement for it. A reasonable plan is one or two small, well-chosen projects running alongside the steady job search you planned in Running a Job Search.

### Kinds of AI contract work

Most small AI contracts fall into a few families. Match them to the projects you've already done:

- **Automations and workflows.** Turning a repetitive task into a pipeline: sorting inbound email, extracting fields from invoices or forms into a spreadsheet, drafting replies for a human to approve. Your Messy Text Extractor and the workflow patterns from Agentic Systems are the core skills. These are the most common first contracts, because the value is easy to see in hours saved.
- **RAG and chatbot builds.** A question-answering assistant over a company's documents, help center or policies, with citations. Your Chat With Your Docs and Docs Chatbot UI projects map directly onto this.
- **Evals and audits.** A company already has an AI feature and doesn't know how good it is. You build an eval set from their real cases, run error analysis, report scores with confidence intervals, and recommend fixes. This work is underrated and in demand, because few people do it well, and it's exactly what Measuring Quality and Evals in Practice taught you.
- **Integration work.** Connecting a model to the tools a business already uses: a CRM, a ticketing system, a shared drive or a database, often through an API or an MCP server. This is unglamorous plumbing, and clients pay for it because it's where most projects get stuck.
- **Cost and reliability fixes.** A prototype that works but is slow, expensive or flaky. Caching, routing to a cheaper model, retries and tracing, as in Cut the Bill and the Production path.

Pick one or two you can point to evidence for and say them plainly: "I build document Q&A assistants and email automations for small businesses, with an eval report so you know they work." A narrow offer is easier to sell than "I do AI."

### Finding your first clients

First clients nearly always come from people who already trust you a little. Here are the main sources, roughly from best to hardest for a beginner.

- **Your capstone user.** You've already solved one problem for them. Ask whether there's a second one, or whether a friend's business has the same problem. A capstone user who sees real hours saved is the warmest lead you have.
- **Your network.** Former colleagues, managers, friends and the people you've met through Networking and Referrals. Your earlier career is a strength here: a former teacher knows schools, a former nurse knows clinics. A short message works: what you build, one example with a number, and a question about whether they know anyone drowning in a repetitive task.
- **Local businesses.** Accountants, law firms, clinics, property managers, shops and nonprofits often have obvious paperwork problems and no technical staff. Meeting in person, through a local business group or an introduction, builds trust faster than cold email.
- **Freelance platforms.** Marketplaces such as Upwork, Fiverr and Contra list many AI jobs. They handle payment and give you a steady supply of postings, but they take a fee, competition on price is fierce, and a new profile with no reviews is hard to get noticed. If you use them, apply only to well-described projects, write a specific reply that restates the client's problem, and expect to win a small first job at a modest price to earn your first review.
- **Your public work.** Posts from Learning in Public bring in leads slowly but steadily. A write-up titled "How I cut a firm's invoice triage from six hours to one" is a sales page.

Watch for warning signs in any lead: a client who wants "ChatGPT for our whole company" for a few hundred dollars, asks for a large unpaid "test project," won't describe the problem, or wants to pay through unusual channels. Scammers also target new freelancers with overpayment schemes, where they "accidentally" send too much and ask for the difference back. Walk away from all of these.

### Scoping a small first project

Your first contract should be small: one to four weeks of part-time work, one clear outcome, and one person on the client side who can answer questions. Small projects are easier to deliver well, easier for a nervous client to say yes to, and still produce a full case study.

Scoping works exactly like the [Writing a Spec](#/lessons/capstone/writing-a-spec) lesson from the Capstone. Start with a short conversation and ask the same questions you asked your capstone user: What task takes the most time? How often does it happen? What does it cost when it goes wrong? Can you show me ten real examples? Then shrink the problem until it fits. "Automate our inbox" becomes "sort incoming supplier invoices into three folders and extract five fields into the existing spreadsheet, with a human checking every row before it's saved."

If the problem is genuinely unclear, sell a **paid discovery** phase first: a few days to look at their data, build a rough prototype and come back with a proposal for the real build. It protects you from committing to a fixed price on a guess, and it lets the client find out what working with you is like before spending more.

### Writing a one-page proposal

A **proposal** is the client-facing version of your spec. It's shorter, uses no jargon, and ends with a price. One page is enough for a small project:

```markdown
# Proposal: Invoice sorting for Rivera & Co. Accounting

## The problem
Staff spend about 6 hours a week sorting ~300 supplier invoices from the shared inbox
and typing 5 fields into the tracking sheet. Typos cause about 2 late payments a month.

## What I'll build
A workflow that reads new invoice emails, extracts supplier, date, amount, due date and
invoice number, and adds a row to a review tab. A staff member approves each row before
it moves to the main sheet. Nothing is paid or sent automatically.

## Not included
Paying invoices, other inboxes, invoices in languages other than English, a mobile app.

## How we'll know it works (success criteria)
- Fields correct on at least 95% of 100 past invoices you provide, checked field by field.
- Weekly sorting time under 2 hours, measured by your team for 2 weeks after launch.
- Running cost under $20 a month at current volume.

## Timeline and deliverables
Week 1: working prototype on past invoices, with an accuracy report.
Week 2: connected to the live inbox, staff trained, handover notes and a short video.

## Price and terms
Fixed price: $X, 40% to start, 60% on handover. Includes 2 weeks of fixes after launch.
Model and hosting costs are billed to your own accounts.
```

Notice what carries over from the spec: a measured baseline, non-goals, success criteria with a size and a threshold, and a human approval step for anything risky. Clients rarely ask for success criteria, which is exactly why including them makes you stand out. They also protect you: when the project ends, you can show the criteria were met instead of arguing about whether it "works."

### Pricing your work

There are two common ways to charge.

**Hourly** (also called **time and materials**) means you bill for the hours you work. It's fair when the scope is unclear, because the client pays for the extra work that unclear scope causes. The downside is that the client carries the risk, so they may watch your hours closely, and you earn less as you get faster.

**Fixed price** means one price for a defined result. Clients prefer it because they know the cost up front. It rewards you for being efficient, but you carry the risk if the job takes longer than planned. Only offer a fixed price when the scope is written down, including what's not included, and add a buffer of 25 to 50% to your estimate, because first estimates are almost always low.

A good pattern for beginners is a fixed price for paid discovery, then a fixed price for a tightly scoped build, then an hourly or monthly rate for later changes.

The most common beginner mistake is **underpricing**. A low price feels safe, but it signals low confidence, attracts the clients most likely to demand endless changes, and is hard to raise later with the same client. Work out a floor before you quote. Start with what you'd need to earn in a year, then remember that a freelancer can't bill every working hour: finding clients, admin and unpaid gaps eat a large share, and many freelancers bill only half their working time or less. Add your costs, such as software, equipment and any insurance, and set money aside for tax, which you now pay yourself. The result is usually far higher per hour than a salary of the same size works out to, and that's correct.

Then think about value. If your workflow saves a firm five staff hours a week, it's worth thousands a year to them, and a price that's a fraction of that is easy to say yes to. Patrick McKenzie's essay in the Assignment makes this argument well.

### Contracts and payment terms

Always have a written agreement, even with a friend. It doesn't need to be long. For a small project, a short contract or a signed proposal plus terms should cover:

- **Scope and deliverables**, by reference to the proposal, including what's not included.
- **Changes.** New requests get a written estimate and approval before you start them. This one clause prevents most freelance disputes.
- **Payment.** The amount, the schedule (a deposit of 30 to 50% before you start is normal for new clients), when invoices are due, often within 14 or 30 days, and what happens if they're late.
- **Ownership.** Who owns the code once it's paid for. A common arrangement is that the client owns the deliverables after full payment, while you keep your general tools and know-how.
- **Confidentiality** of the client's data and business details.
- **Portfolio rights.** Permission to describe the project in a case study, with or without their name. Ask now, not afterward.
- **Liability.** A cap, usually the amount paid, and a statement that the system assists staff and that the client reviews its outputs.
- **Ending the contract**, and what's paid for work done if either side stops early.

Templates are a fine starting point, but contract law differs between countries and states, so treat a template as a checklist, not legal advice. For a larger contract, paying a local lawyer for an hour's review is cheap insurance.

Send invoices promptly, with a number, the date, what they cover and your payment details. Track what's been paid in a simple spreadsheet. If a payment is late, a polite reminder on the due date usually solves it. If it doesn't, pause work until you're paid.

### Protecting client data and keys

A client is trusting you with their data, and for an AI project that data may pass through a model provider. Treat it the way the Production and Agentic Safety lessons taught you to treat your own systems, only more carefully, because it isn't yours.

- **Use the client's accounts.** The model provider account, cloud project and API keys should belong to the client, paid with their card, with a spending limit set. You get access as a user. When the project ends, they remove your access and nothing breaks. Never run a client's production system on your personal API key.
- **Keep secrets out of code**, in environment variables locally and a secret manager in production, as in One Real Cloud. Turn on secret scanning in the repo.
- **Ask for the minimum data**, and remove names and other personal details from examples when you can. Store it in one place, not scattered across laptops and chat tools.
- **Check the provider's data terms** before sending client data to a model: whether inputs are stored, for how long, and whether they're used for training. Business API terms usually differ from consumer chat apps, so never paste client data into a consumer chatbot. If the data includes personal information about people in the EU, the GDPR applies, and other places have their own privacy laws.
- **Delete what you hold** at the end, and say in writing that you did.

The threat model from your spec applies too. An email-reading workflow for a client has the same prompt-injection risks as your capstone, so keep the approval step and the injection tests.

### Delivering with evidence

The evidence habits you built across the curriculum are what make you look senior on a first contract. Most freelancers deliver code and a "let me know if you have questions." You'll deliver proof:

- **An accuracy report** on the client's real examples, measured against the proposal's success criteria, with the size of the test set and a confidence interval, plus the two or three failure types you found in error analysis.
- **Tests and evals in CI**, so the next person who changes the prompt finds out if they broke something.
- **Traces and a cost report**: cost per task and latency at the client's actual volume.
- **Safety checks**: the approval step working, and the injection cases you tested.
- **Handover notes**: a README that explains how to run it, where the secrets live, what to do when it fails, and how to update the eval set. Add a three-minute video walkthrough, recorded as in Case Studies and Demo Videos.

Show progress early and often. A rough demo at the end of the first week catches misunderstandings while they're cheap, just as your capstone milestones did. After launch, measure the user outcome from the proposal, such as time saved, because that's the number the client will repeat to others.

### From contract to case study

When the project is done and paid for, turn it into career evidence while it's fresh.

**Write the case study** using the five-part shape from Case Studies and Demo Videos: problem, constraints, approach, evidence, next steps. Respect what the contract says. If the client prefers not to be named, write "a 12-person accounting firm" and leave out anything that could identify them, and send them the draft before you publish.

**Ask for a testimonial and a reference.** People are happy to help but bad at writing from a blank page, so ask specific questions: "What were you doing before? What changed? Would you recommend working with me, and for what?" Ask whether you can list them as a reference for job applications. A business owner who says "they cut our invoice work by two thirds and explained everything clearly" is persuasive to hiring managers.

**Put it on your resume** as experience, not a project: "Freelance AI Engineer, self-employed," with dates and evidence-led bullets as in Resume for AI Roles. Two or three contracts can sit under one entry.

**Keep the relationship.** Check in a month later to see how it's going. Small fixes lead to repeat work, and happy clients refer other clients.

### Taxes and the legal side

Being self-employed has tax and legal consequences, and the rules vary a lot between countries and even within them. Depending on where you live, you may need to register as self-employed or as a business, charge sales tax or VAT, keep records for several years, and pay tax in installments during the year rather than once. Some countries also have rules about when a "contractor" is really an employee. Examples include the US distinction between independent contractors and employees, and the UK's off-payroll (IR35) rules. These affect both you and the client.

This lesson can't give you legal or tax advice for your situation. Use your government's official guidance, linked in the Assignment for the US, the UK and the EU, and talk to an accountant once you're earning regularly. Set aside a share of every payment for tax as soon as it arrives, so the bill never comes as a surprise.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read Patrick McKenzie's [Don't Call Yourself A Programmer, And Other Career Advice](https://www.kalzumeus.com/2011/10/28/dont-call-yourself-a-programmer/), a classic essay on why businesses pay for outcomes, not code.
   - Focus on the parts about describing your work in terms of revenue and costs, and about charging more. Then rewrite your one-line offer from Kinds of AI contract work in those terms.
1. Read the official guidance for where you live. Pick the one closest to your situation, or find your own country's equivalent on a government site:
   - US: the IRS [Self-Employed Individuals Tax Center](https://www.irs.gov/businesses/small-businesses-self-employed/self-employed-individuals-tax-center) and [Independent contractor or employee](https://www.irs.gov/businesses/small-businesses-self-employed/independent-contractor-self-employed-or-employee).
   - UK: [Working for yourself](https://www.gov.uk/working-for-yourself) and [Understanding off-payroll working (IR35)](https://www.gov.uk/guidance/understanding-off-payroll-working-ir35).
   - EU: the [Your Europe business portal](https://europa.eu/youreurope/business/index_en.htm), which links to each member state's rules.
   - Write down three things you'd need to do before sending your first invoice.
1. Read GitHub's [About secret scanning](https://docs.github.com/en/code-security/secret-scanning/introduction/about-secret-scanning) and check that it's turned on for the repos you'd use for client work.
1. Practice: write a one-page proposal for a real or realistic small client.
   - Use your capstone user, a business in your network, or a local business you could plausibly approach. Follow the template in Writing a one-page proposal, including non-goals, at least two success criteria with a size and threshold, a timeline, and a price you've worked out with the floor calculation from Pricing your work.
   - Write a one-page terms sheet to go with it, covering every item in Contracts and payment terms.
   - Ask someone who runs or manages a business to read both and tell you what's unclear or what would make them hesitate. Revise.
1. Write a short list of five people or businesses you could offer this to, with the reason each might need it. Keep the list for Project: Outreach Sprint.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Why does contract work help a career changer get a full-time role, and what does it cost?](#why-contract-work-is-a-bridge)
- [What are the main kinds of AI contract work, and which earlier projects prepare you for each?](#kinds-of-ai-contract-work)
- [What are the trade-offs of finding clients on freelance platforms compared with your network?](#finding-your-first-clients)
- [When should you sell paid discovery instead of a fixed-price build?](#scoping-a-small-first-project)
- [What does a proposal borrow from a capstone spec, and why do success criteria protect you?](#writing-a-one-page-proposal)
- [When is a fixed price better than hourly, and how do you work out a price floor?](#pricing-your-work)
- [Why should the API keys and model accounts belong to the client?](#protecting-client-data-and-keys)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- The US Department of Labor's page on [misclassification of employees as independent contractors](https://www.dol.gov/agencies/whd/flsa/misclassification) explains why the line between contractor and employee matters to both sides.
- The SBA's guide to [choosing a business structure](https://www.sba.gov/business-guide/launch-your-business/choose-business-structure) compares sole proprietorships, LLCs and other options, if you're in the US and freelancing becomes regular.
- [GDPR.eu](https://gdpr.eu/) is a plain-language guide to the EU's data protection rules, useful if a client's data includes personal information about people in the EU.
