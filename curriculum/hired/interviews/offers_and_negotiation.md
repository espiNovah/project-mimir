### Introduction

An offer is the moment all your work pays off, and also the moment many people make expensive mistakes. They accept the first number without reading the details, compare two offers by base salary alone, treat startup stock as if it were cash, or panic when a recruiter says the offer expires on Friday.

Negotiating is also uncomfortable for most people, especially career changers who feel lucky to have an offer at all. The good news is that a respectful negotiation is normal in many countries and industries. Recruiters expect it, and a polite, well-researched question almost never makes an offer disappear. The goal isn't to squeeze every dollar out of an employer you're about to work with. It's to understand what you're being offered, make sure it's fair for the market, and start the job without resentment on either side.

This lesson walks through the parts of an offer, how to research pay with free sources, how to compare offers side by side, when and how to ask for more, and what to check before you sign. It's honest about the limits too: a first AI role after a career change often comes with less leverage than the internet's negotiation stories suggest, and norms vary a lot between countries.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The parts of an offer: base, bonus, equity, benefits, and remote and visa terms.
- How startup equity really works, and how to value it.
- Researching market pay with free sources.
- Comparing offers in a simple table.
- How and when to negotiate, with scripts for asking.
- Exploding offers, competing deadlines and declining gracefully.
- Your leverage as a career changer, and what to check before signing.

### The parts of an offer

An offer for a full-time engineering job is a bundle. **Total compensation** ("total comp") is the yearly value of the parts you're paid in money or stock, and it's the number to compare, not base salary alone.

- **Base salary.** The fixed pay you receive every month. It's the most certain part, and later raises are usually a percentage of it, so a higher base compounds.
- **Bonus.** Extra pay tied to company or personal performance, usually stated as a target percentage of base, such as "10% target." A target isn't a promise. Ask what share of the target people actually received in recent years.
- **Signing bonus.** A one-time payment for joining, often used to cover a bonus you'd lose by leaving your current job, or to close a gap when base salary is fixed. Many come with a **clawback**: if you leave within a year, you pay some or all of it back.
- **Equity.** A share of ownership in the company, through stock options or restricted stock units. The next section covers it in detail, because it's the part most often misunderstood.
- **Benefits.** Health insurance, retirement contributions (such as a 401(k) match in the US or a pension contribution elsewhere), paid time off, parental leave, and budgets for learning or equipment. In countries where employers provide health insurance, a difference in benefits can be worth thousands a year.
- **Level and title.** Your level, such as "Engineer I" or "L3," sets your pay band and how soon you can be promoted. A higher level at the start can matter more than a few thousand in base.
- **Start date and work terms**, covered in Remote and visa terms below.

Before you compare or negotiate, get the full offer in writing, with every number. A verbal offer is a good sign but it isn't the offer.

### How startup equity really works

At public companies, equity usually comes as **RSUs** (restricted stock units): shares you receive over time that you can sell on the stock market. Their value is easy to estimate, because the share price is public, though it moves.

At private startups, equity usually comes as **stock options**: the right to buy a number of shares at a fixed price, the **strike price**, at some point in the future. If the company's shares later become worth more than the strike price and you're able to sell them, the difference is your gain. If they don't, the options are worth nothing.

Both kinds usually **vest**: you earn them gradually. A common schedule is four years with a one-year **cliff**, which means nothing vests until your first anniversary, then a quarter vests at once and the rest monthly. If you leave after eleven months, you get nothing.

The honest truth about startup options is that most end up worth little or nothing. Most startups don't reach a successful sale or public listing. Even when they do, you can only sell your shares at that point, often years away. Investors hold **preferred shares** that are paid back first, which can leave little for employees' **common shares** in a modest sale. Each funding round also **dilutes** you: new shares are created, so your slice gets smaller. And to keep options when you leave, you may have to pay to **exercise** them, buying the shares at the strike price, often within 90 days, sometimes with a tax bill attached.

So a statement like "50,000 options" tells you nothing on its own. Ask these questions; a good startup will answer them:

- How many shares are outstanding in total, on a fully diluted basis? This turns your options into a percentage of the company.
- What's the strike price, and what was the price per share in the latest funding round?
- What's the vesting schedule, and is there a cliff?
- How long do I have to exercise after I leave?

Then, for comparing offers, value startup options **at zero** or close to it, and treat any upside as a lottery ticket. Choose a startup because you want the salary, the work and the learning, not because of the equity. Tax treatment of options varies by country and by the type of option, and in the US there are choices with real tax consequences, so read the guide in the Assignment and ask an accountant before exercising.

### Remote and visa terms

Some of the most important terms aren't money:

- **Where you can work.** Fully remote, hybrid or in the office, and whether that's written into the offer or just current practice. Some companies adjust pay by location, so ask whether moving later would change your salary.
- **Employment type.** Employee, contractor, or employed through an **employer of record** (a company that employs you on the real employer's behalf, often for cross-border hires). A contractor usually gets no benefits and pays their own taxes, so a contract rate must be well above an equivalent salary to be comparable. The Freelance and Contract Work lesson covers this.
- **Visa sponsorship.** If you need a work visa, get the company's commitment to sponsor in writing, including who pays the legal fees, what happens if the application fails, and, for the US H-1B, the lottery timing. Visa rules are set by governments and change, so read the official source for the country, such as USCIS for the US, rather than relying on the recruiter's summary.
- **Probation period**, notice period and any **non-compete** clause that restricts where you can work afterward. Their enforceability varies a lot between places.

### Researching market pay

You can't judge an offer, or ask for more, without knowing the market rate for this role, level and location. Free sources include:

- **Levels.fyi**, a large, free database of self-reported tech compensation with base, bonus and equity broken out, searchable by company, level and city.
- **Pay ranges in postings.** A growing number of places require employers to publish salary ranges, including several US states and, under an EU directive being brought into national law, EU member states. Collect the ranges from the postings in your Role Map.
- **Government data.** In the US, the Department of Labor publishes the wages employers file for H-1B workers, by company and job title. Many countries publish official wage statistics by occupation.
- **People.** Ask the contacts you made in Networking and Referrals: "For a junior AI engineer at a company like this in this city, what range would you expect?" People are often more willing to share a range than their own salary.

Look for a range, not a single number, and match it carefully. Self-reported data skews toward large, well-paying companies, and a "machine learning engineer" at a big lab isn't the same job or level as an entry-level AI engineer at an agency. Write down the low, middle and high of what you find for your target level and location.

### Comparing offers in a table

When you have more than one offer, or one offer and your current job, put them side by side. A table makes the trade-offs visible and keeps you from deciding on the most exciting number. Here's a small script that turns offers into a first-year and a four-year view, with startup options valued at zero by default:

```python
# compare_offers.py: put offers side by side.
# Edit the numbers; run with: uv run compare_offers.py
OFFERS = {
    "Startup":  {"base": 95_000, "bonus_pct": 0.00, "signing": 5_000,
                 "equity_per_year": 0, "benefits": 6_000},   # options valued at 0
    "Mid-size": {"base": 105_000, "bonus_pct": 0.10, "signing": 0,
                 "equity_per_year": 8_000, "benefits": 12_000},  # RSUs at today's price
}

def yearly(o, first_year=False):
    total = o["base"] * (1 + o["bonus_pct"]) + o["equity_per_year"] + o["benefits"]
    return total + (o["signing"] if first_year else 0)

print(f"{'Offer':<10}{'Year 1':>12}{'4 years':>12}")
for name, o in OFFERS.items():
    four = yearly(o, first_year=True) + 3 * yearly(o)
    print(f"{name:<10}{yearly(o, True):>12,.0f}{four:>12,.0f}")
```

Then add the things that don't fit in a number as extra rows in a written table: the work you'd do, who you'd learn from, how much evidence you'd get for your next job, remote terms, commute, stability, and whether the role matches the target you set in AI Roles Explained. For a first AI role, **what you'll learn and ship in the first two years** often matters more than a few thousand in pay, because it sets your pay for the rest of your career. Fill in each row, then sleep on it.

### When and how to negotiate

Timing matters. The main rule is: **don't discuss numbers in detail until you have an offer.** Before an offer, the company is still deciding whether it wants you. After an offer, it has decided, and that's when you have the most room.

Recruiters often ask early, "What are your salary expectations?" You have honest options:

- Deflect politely: "I'd like to learn more about the role first. I'm sure we can find a number that works if it's a good fit. What's the range for this position?"
- Give a researched range whose bottom you'd be happy with, if they insist or if it's normal where you are.

In many places, including several US states, employers can't ask about your current or past salary. Where they can, you don't have to answer, and it's usually better to talk about expectations for this role than about your history.

Once you have the offer, the process is simple:

1. **Thank them and show enthusiasm.** Negotiation goes best when they believe you want to join.
1. **Ask for time** to review it, usually a few days to a week, and for the full details in writing.
1. **Ask questions** about anything unclear, especially equity and bonus.
1. **Make one clear, reasoned request.** Base on market data, a competing offer, or the level of the role. Ask for something specific, slightly above what you'd be happy with.
1. **Let them respond.** Then decide. Don't negotiate in many rounds over small amounts.

Be truthful at every step. Never invent a competing offer or inflate one. It's easy to check, it's dishonest, and if it's discovered you lose the offer and a reputation in a small industry. Also don't negotiate unless you'd accept if they meet your request: walking away after they say yes burns the bridge.

If base salary truly can't move, which is common at large companies with fixed bands and in the public sector, other parts often can: a signing bonus, a higher level, more equity, an earlier review date, a learning budget, a later start date or an extra week of leave.

### Scripts for asking

Most negotiation happens by email or a short call. Short, warm and specific works best. Adapt these:

**Asking for time:**

> Thank you so much, I'm really excited about this offer and the team. Could you send the full details in writing? I'd like a few days to review everything, and I'll get back to you by Thursday.

**Asking for more, based on market data:**

> I'm excited to join and want to make this work. Based on my research for junior AI engineer roles in [city], including published ranges and Levels.fyi data, I was expecting a base closer to [number]. Is there flexibility to get there? If base is fixed, I'd be glad to talk about a signing bonus instead.

**Asking with a competing offer:**

> I have another offer at [total, briefly broken down], with a deadline of [date]. Your team is my first choice because of [specific reason]. If you could get closer to [number], I'd be ready to accept.

**Accepting:**

> Thank you for working on this. I'm happy to accept. Please send the final offer letter, and let me know the next steps.

On a call, it's fine to say "Let me think about that and come back to you tomorrow" rather than deciding on the spot. Silence after you've asked is also fine. Let them fill it.

### Exploding offers and competing deadlines

An **exploding offer** has a short deadline, sometimes 24 or 48 hours. Some are genuine, for example when a company has another candidate waiting. Many are pressure tactics.

Respond calmly and ask for what you need: "I'm very interested, and I want to make a careful decision. I'm finishing another process and expect an answer by next Wednesday. Could you extend the deadline until then?" Most reasonable employers will give you some extra days. If a company refuses any reasonable time for a decision this big, that tells you something about how it treats people.

When offers arrive at different times, manage the timing deliberately. Tell the companies earlier in their process that you have an offer and a deadline, and ask whether they can speed up. Tell the company that made the offer, honestly, that you're finishing other conversations and when you'll decide. This is normal and recruiters handle it every week.

### Your leverage as a career changer

Most negotiation advice online comes from experienced engineers with several competing offers. Your situation may be different. Leverage comes from alternatives: a competing offer, a current job you're happy in, rare skills, or a company that badly needs to fill the seat. A career changer with one offer after a long search has less of it, and it's honest to admit that.

That doesn't mean you shouldn't ask. A polite, researched request costs very little, and a reasonable employer won't withdraw an offer over it. It means you should **ask once, ask reasonably, and be ready to accept** if they say no. Your strongest moves are evidence-based: market data for the role, and the specific value you bring, such as a deployed capstone with real users or domain knowledge from your earlier career.

Remember too that norms vary by country and culture. In some places, open negotiation is expected; in others, pay follows published bands or **collective agreements** (pay scales agreed between unions and employers) and there's little room to move; in some cultures, a direct counteroffer can come across as rude. Ask people in your network what's normal where you're applying.

### Declining gracefully

You'll probably turn down an offer or a process at some point. Do it quickly, kindly and in writing, because the people you're declining may hire you, refer you or work with you later:

> Thank you for the offer and for the time your team spent with me. After a lot of thought, I've decided to accept another role that's a closer fit for what I want to focus on right now. I really enjoyed meeting [names], and I hope our paths cross again.

Don't over-explain, don't negotiate after declining unless you mean it, and don't just go silent. Once you've accepted an offer, withdraw from your other processes promptly so other candidates aren't kept waiting.

### Before you sign

Read the whole offer letter and contract, not just the summary email. Check that:

- Every number matches what you agreed: base, bonus target, signing bonus and clawback, equity amount and vesting.
- Your title, level, start date, location and remote terms are right.
- Visa sponsorship, relocation and any other promises are written down. If it isn't in writing, assume it won't happen.
- You understand any non-compete, non-solicitation, intellectual property or moonlighting clause. An IP clause that claims everything you build, even on your own time, matters if you plan to keep contributing to open source or freelancing. Ask for your existing projects to be listed as excluded.
- You know the probation and notice periods.
- Any **contingencies**, such as a background check or references, are ones you can meet.

If anything is unclear, ask the recruiter in writing. If the contract is unusual, or a lot of money or a visa is involved, a short review by an employment lawyer where you live is worth it. Then sign, tell your references thank you, and update your Role Map notes with what you learned about pay in your market.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the Tech Interview Handbook's [Understanding compensation](https://www.techinterviewhandbook.org/understanding-compensation/) and [Negotiation](https://www.techinterviewhandbook.org/negotiation/) guides, free, practical overviews of offer components and the negotiation process.
   - Compare their advice with Your leverage as a career changer, and note where it assumes more leverage than you may have.
1. Read Patrick McKenzie's [Salary Negotiation: Make More Money, Be More Valued](https://www.kalzumeus.com/2012/01/23/salary-negotiation/), the classic essay on why negotiating is normal and how to approach it respectfully.
   - Pay attention to the sections on not naming a number first and on negotiating things other than salary. Notice that it's written from a US perspective.
1. Read the Stock Options section of [The Holloway Guide to Equity Compensation](https://www.holloway.com/g/equity-compensation/sections/stock-options), free to read online.
   - Write down the four questions you'd ask about any startup option grant, and why.
1. Practice: research market pay for your target role and location.
   - Use [Levels.fyi](https://www.levels.fyi/), salary ranges from at least five current postings, and, if you're in the US, the H-1B wage disclosures on the [Department of Labor's FLAG site](https://flag.dol.gov/programs/lca). Write down a low, middle and high figure, with the sources.
   - Copy `compare_offers.py`, enter two realistic offers using your numbers, and add a written table with at least five non-money rows. Decide which you'd take and why in two sentences.
1. Practice the scripts aloud with a friend who plays a recruiter. Rehearse asking for time, asking for more with market data, and responding to a 48-hour deadline, then swap roles. If no one is available, record yourself saying each script and listen back for hedging and over-explaining.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What makes up total compensation, and why compare it rather than base salary?](#the-parts-of-an-offer)
- [What are vesting and a cliff, and why should you value startup options near zero when comparing offers?](#how-startup-equity-really-works)
- [Which free sources can you use to research market pay, and what are their biases?](#researching-market-pay)
- [Why shouldn't you discuss numbers in detail before you have an offer?](#when-and-how-to-negotiate)
- [How should you respond to an exploding offer?](#exploding-offers-and-competing-deadlines)
- [Why might a career changer have less leverage, and how should that change the way they negotiate?](#your-leverage-as-a-career-changer)
- [What should you check in the contract before signing?](#before-you-sign)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- Haseeb Qureshi's [Ten Rules for Negotiating a Job Offer](https://haseebq.com/my-ten-rules-for-negotiating-a-job-offer/) and its follow-up, [How Not to Bomb Your Offer Negotiation](https://haseebq.com/how-not-to-bomb-your-offer-negotiation/), are a detailed account from a career changer who became an engineer. They assume several competing offers, so adjust for your situation.
- Index Ventures' [Rewarding Talent handbook](https://www.indexventures.com/rewardingtalent/handbook) explains how startups design equity plans, including how option grants differ across European countries and the US.
- USCIS's [H-1B Specialty Occupations](https://www.uscis.gov/working-in-the-united-states/h-1b-specialty-occupations) page is the official source on the most common US work visa for engineers.
- The European Commission's [EU action for equal pay](https://commission.europa.eu/strategy-and-policy/policies/justice-and-fundamental-rights/gender-equality/equal-pay/eu-action-equal-pay_en) page covers the pay transparency directive, which gives job seekers in the EU the right to see a salary range.
