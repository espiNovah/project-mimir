<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

Game theory asks how agents will behave given the rules. Mechanism design flips the question: what rules should you write so that self-interested agents, each pursuing their own goals, produce a good outcome? As more decisions are delegated to AI agents (bidding for ads, booking travel, negotiating contracts, splitting compute), the people building those systems are writing the rules. This lesson covers social choice, auctions, bargaining and the basics of mechanism design.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Social choice: turning many preferences into one decision.
- Arrow's impossibility theorem and why voting rules involve trade-offs.
- Mechanism design and incentive compatibility.
- First-price, second-price (Vickrey) and other auctions.
- The VCG mechanism.
- Bargaining, the Nash bargaining solution and negotiation protocols.
- Applying these ideas to LLM agent marketplaces.

### Key ideas

- **Aggregating preferences is harder than it looks.** Plurality, Borda count, instant runoff and Condorcet methods can pick different winners from the same ballots. Arrow's theorem shows that no ranked voting rule with three or more options satisfies a short list of reasonable fairness conditions at once, so every rule is a compromise.
- **Mechanism design is reverse game theory.** You choose the rules (what agents report, and how reports map to outcomes and payments) so that the resulting game has good equilibria. A mechanism is *incentive compatible* if each agent does best by reporting its true preferences. The revelation principle says that, for many purposes, you only need to consider such truthful mechanisms.
- **Second-price auctions make honesty optimal.** In a sealed-bid Vickrey auction, the highest bidder wins but pays the second-highest bid. Bidding your true value is a dominant strategy, so bidders do not need to model each other. In a first-price auction, bidders shade their bids below their values, and the optimal amount depends on beliefs about the others.
- **VCG generalizes the idea.** The Vickrey-Clarke-Groves mechanism chooses the outcome that maximizes total value and charges each agent the harm its presence imposes on the others. It is truthful and efficient, but it can produce low revenue and is vulnerable to collusion.
- **Bargaining splits a surplus.** When a buyer values an item above the seller's cost, any price in between benefits both, and the question is where they settle. The Nash bargaining solution picks the split that maximizes the product of the two players' gains over their fallback options. Rubinstein's alternating-offers model shows how patience shapes the split. In practice, each side's best alternative to a negotiated agreement (its fallback) drives the result.
- **LLM agents bring new questions.** Do LLM agents report truthfully when the mechanism rewards it? Can they be manipulated through the messages they read? Do two agents from the same model collude without being told to? Classic mechanisms assume rational agents that follow incentives precisely, so these are open empirical questions.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read chapters 9 to 11 of Shoham and Leyton-Brown's free [Multiagent Systems](https://www.masfoundations.org/) book.
   - Chapter 9 (Aggregating Preferences: Social Choice) through Arrow's theorem; chapter 10 (Protocols for Strategic Agents: Mechanism Design) through the VCG mechanism; chapter 11 (Auctions) sections on single-good auctions.
1. Watch lectures 17 (Ultimatums and Bargaining) and 24 (Auctions and the Winner's Curse) of Yale's [ECON 159: Game Theory](https://oyc.yale.edu/economics/econ-159) for the intuition behind bargaining and auctions.
1. Work through the first lectures of [Tim Roughgarden's Algorithmic Game Theory course](https://timroughgarden.org/f13/f13.html) (Stanford CS364A), which teaches mechanism design from a computer science perspective.
   - Read the notes for lectures 2 to 4 (mechanism design basics, Myerson's lemma and algorithmic mechanism design), and lecture 7 on VCG.
1. Read [Cooperation, Competition, and Maliciousness: LLM-Stakeholders Interactive Negotiation](https://arxiv.org/abs/2309.17234), a benchmark in which several LLM agents with private goals negotiate a multi-issue deal.
   - Read the setup and results. Note how the authors score agreements and how they test for agents that try to manipulate others.
1. Practice: simulate first-price and second-price sealed-bid auctions with 5 bidders whose values are drawn uniformly from 0 to 1. Compute the seller's average revenue under truthful bidding in the second-price auction, and under the equilibrium bid of (n - 1) / n times one's value in the first-price auction. Compare the two (revenue equivalence says they should match on average).

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Ariel Procaccia's Truth, Justice, and Algorithms course](https://www.cs.cmu.edu/~arielpro/15896s16/) (Carnegie Mellon) has free lecture slides on computational social choice, fair division and voting.
- [Improving Language Model Negotiation with Self-Play and In-Context Learning from AI Feedback](https://arxiv.org/abs/2305.10142) studies LLM buyers and sellers bargaining and improving over rounds, a close match to the buyer-seller game in the project.
