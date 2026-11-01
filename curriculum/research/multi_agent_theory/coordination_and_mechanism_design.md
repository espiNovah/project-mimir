### Introduction

In [Game Theory Basics](#/lesson/research/multi_agent_theory/game_theory_basics), we analyzed the behavior of rational agents given an established game with fixed rules. We observed that rational, self-interested agents often end up in sub-optimal equilibria (such as mutual defection in the Prisoner's Dilemma) that destroy collective surplus.

**Mechanism design** (often called *reverse game theory*) flips the problem:
> Rather than taking the rules as given and predicting agent behavior, how do we design the rules, communication protocols, and payoff functions so that self-interested agents, each pursuing their own private utility, autonomously produce a globally desirable social outcome?

As multi-agent autonomous systems proliferate—negotiating API rates, booking travel itineraries, allocating GPU cluster nodes, and transacting digital goods—the engineers building these ecosystems are acting as mechanism designers.

This lesson explores social choice theory, Arrow's Impossibility Theorem, the Revelation Principle, classical auction formats, the Vickrey-Clarke-Groves (VCG) mechanism, and how strategic incentives apply to markets populated by language model agents.

### Social choice theory and voting rules

How should a collective of `n` agents choose among a set of alternatives `A = {a, b, c, ...}` when each agent `i` has a private preference ranking `>_i` over the options?

#### Common preference aggregation rules

1. **Plurality:** Each agent casts one vote for their top choice. The alternative with the most votes wins. Highly susceptible to the spoiler effect and tactical voting.
2. **Borda Count:** If there are `k` alternatives, each agent assigns `k - 1` points to their top choice, `k - 2` to their second, down to 0 points for their least favorite. Sum points across voters.
3. **Instant Runoff Voting (Alternative Vote):** Eliminate the alternative with the fewest first-place votes, redistributing their ballots to each voter's next choice, until one alternative secures a strict majority (>50%).
4. **Condorcet Criterion:** If an alternative defeats every other alternative in head-to-head pairwise majority contests, that alternative should win. (A Condorcet winner does not always exist; the **Condorcet Paradox** shows that pairwise preferences can form cyclic majorities: `A > B > C > A`).

#### Arrow's Impossibility Theorem (1951)

Kenneth Arrow mathematically proved that it is impossible to design a ranked voting system for three or more alternatives that satisfies four seemingly elementary fairness properties:

1. **Unrestricted Domain:** The rule must produce a valid ranking for any possible combination of voter preference profiles.
2. **Pareto Efficiency (Unanimity):** If every voter prefers `a` over `b`, the collective ranking must place `a` above `b`.
3. **Independence of Irrelevant Alternatives (IIA):** The collective ranking between `a` and `b` must depend only on individual preferences between `a` and `b`, completely unaffected by how voters rank alternative `c`.
4. **Non-Dictatorship:** No single agent's preference profile can dictate the collective outcome regardless of everyone else's votes.

**Arrow's Theorem:** *Any preference aggregation rule satisfying Unrestricted Domain, Pareto Efficiency, and IIA is necessarily a dictatorship.* Every real-world voting system is a mathematical compromise.

Furthermore, the **Gibbard-Satterthwaite Theorem** established that in any general voting system with three or more outcomes, every non-dictatorial voting rule is **manipulable**: voters can achieve a more preferred outcome by lying about their true preferences (strategic voting).

### Mechanism design and the revelation principle

To circumvent the impossibility theorems of pure social choice, mechanism design introduces **transferable utility (payments)**: agents can exchange money or compute credits to compensate each other.

#### Direct revelation mechanisms and incentive compatibility

A mechanism designer specifies:
- An **outcome function** `g(θ_1, ..., θ_n)` choosing the physical allocation (e.g. who gets the GPU, which path is taken).
- A **payment function** `p_i(θ_1, ..., θ_n)` determining how much agent `i` pays or receives.
where `θ_i` represents agent `i`'s private type (their true valuation of the outcomes).

A mechanism is **Dominant-Strategy Incentive Compatible (DSIC)** (or *truthful*) if for every agent `i`, reporting their true valuation `θ_i` is a dominant strategy, regardless of what reports the other agents submit:

```text
u_i( g(θ_i, θ_{-i}) ) - p_i(θ_i, θ_{-i}) >= u_i( g(θ_i', θ_{-i}) ) - p_i(θ_i', θ_{-i})
```

A mechanism is **Individually Rational (IR)** if participating guarantees non-negative net utility: agents are never forced into deals worse than their fallback reservation utility.

#### The revelation principle

The **Revelation Principle** is the fundamental theorem of mechanism design:

> *"If any indirect mechanism (no matter how complex its multi-round bidding or negotiation protocol) has an equilibrium that yields a certain outcome, there exists an equivalent direct-revelation mechanism in which agents simply report their private types truthfully in a single step, yielding the identical outcome and payments."*

This allows mechanism designers to restrict their search to direct, truthful mechanisms without loss of generality.

### Single-item auctions and revenue equivalence

Auctions are mechanisms for allocating scarce resources among agents with private valuations `v_i`:

![Mechanism Design: Second-Price Auctions and VCG Externality](assets/images/mechanism_design_vcg_auction.svg)

#### First-price sealed-bid auction (FPSB)

Bidders submit sealed bids `b_i`. The highest bidder wins and pays their own bid `b_i`.
- If an agent bids their true value `b_i = v_i` and wins, their net utility is `v_i - b_i = 0`.
- Therefore, rational bidders **shade their bids**: they balance the probability of winning against the profit margin upon winning.
- For `n` risk-neutral bidders with private valuations distributed uniformly on `[0, 1]`, the symmetric Bayes-Nash equilibrium bid is:
  ```text
  b_i*(v_i) = ( (n - 1) / n ) * v_i
  ```

#### Second-price sealed-bid auction (Vickrey auction)

William Vickrey (1961) designed the sealed-bid auction where the highest bidder wins, but pays the **second-highest bid**:

```text
Winner: i = argmax_j b_j
Payment: p_i = max_{j != i} b_j
```

**Proof that truthful bidding (`b_i = v_i`) is a dominant strategy:**
Let `b* = max_{j != i} b_j` be the highest bid among all other players.
- **Case 1: `v_i > b*`.**
  - If you bid truthfully `b_i = v_i`, you win and pay `b*`, earning surplus `v_i - b* > 0`.
  - Shading your bid down: If you bid `b_i' > b*`, you still win and pay `b*` (no change). If you bid `b_i' < b*`, you lose the auction and earn 0, which is strictly worse.
- **Case 2: `v_i < b*`.**
  - If you bid truthfully `b_i = v_i`, you lose and earn 0.
  - If you overbid `b_i' > b*` to win, you pay `b*`, earning negative surplus `v_i - b* < 0`, which is strictly worse.

Your bid controls *whether* you win, but the price you pay is completely determined by the other bidders. Truthful bidding is a strictly dominant strategy!

#### The Revenue Equivalence Theorem

The **Vickrey-Myerson Revenue Equivalence Theorem** states:
> *Assume each bidder's valuation is independently drawn from a strictly increasing distribution, and bidders are risk-neutral. Any auction mechanism that (1) allocates the good to the bidder with the highest valuation, and (2) gives zero expected surplus to a bidder with the lowest possible valuation, yields the exact same expected revenue to the seller.*

First-price auctions, second-price auctions, English open-outcry auctions, and Dutch descending auctions all produce identical expected revenue for the seller on average.

### The Vickrey-Clarke-Groves (VCG) mechanism

The **VCG mechanism** generalizes the second-price auction to arbitrary combinatorial environments with multiple goods, public projects, and complex constraints.

#### The VCG allocation and Clarke pivot payment rule

1. **Social Welfare Maximization:** Every agent reports their valuation function `v_i(x)`. The mechanism selects the outcome `x*` that maximizes total social welfare:
   ```text
   x* = argmax_x Σ_{i=1}^n v_i(x)
   ```
2. **Clarke Pivot Payment:** Each agent `i` pays the **externality** they impose on the rest of society—the difference between the welfare others *would have received* without agent `i` versus the welfare others *actually receive* when agent `i` is present:
   ```text
   p_i = [ max_x Σ_{j != i} v_j(x) ] - [ Σ_{j != i} v_j(x*) ]
   ```

#### Properties and limitations of VCG

- **DSIC & Efficient:** Truthful reporting is always a dominant strategy, and the chosen allocation maximizes total social welfare.
- **Practical Limitations:**
  - **Vulnerability to Collusion:** Two losing bidders can coordinate to bid high and lower the winner's payment to zero.
  - **Non-Monotonicity:** Adding an additional bidder can sometimes *decrease* the seller's total revenue.
  - **Computational Complexity:** Solving `argmax_x Σ v_i(x)` for combinatorial auctions (e.g. spectrum auctions) is NP-hard.

### Bargaining and the Nash bargaining solution

When two agents must divide a shared surplus (such as an LLM buyer and seller agreeing on a contract price), mechanism design interfaces with **bargaining theory**.

Let `d = (d_1, d_2)` denote the **disagreement point (BATNA: Best Alternative to a Negotiated Agreement)**—the payoffs agents receive if negotiations break down.

John Nash (1950) proved that any bargaining solution satisfying four axioms (Pareto efficiency, Symmetry, Invariance to affine transformations, and Independence of Irrelevant Alternatives) must maximize the **Nash product**:

```text
max_{(u_1, u_2)}  ( u_1 - d_1 ) * ( u_2 - d_2 )   subject to  u_1 >= d_1,  u_2 >= d_2
```

In Ariel Rubinstein's (1982) model of **alternating offers** with discount factors `δ_1, δ_2`, the subgame-perfect equilibrium yields a unique price split determined by the relative patience of the negotiators: the more patient agent captures the majority of the surplus.

### Python implementation: simulating first-price and second-price auctions

Here is a simulation comparing First-Price and Second-Price auctions across 50,000 trials, empirically verifying Revenue Equivalence:

```python
import numpy as np

def simulate_auctions(num_trials: int = 50_000, num_bidders: int = 5):
    # True valuations drawn uniformly from [0, 1]
    valuations = np.random.uniform(0.0, 1.0, size=(num_trials, num_bidders))

    # Second-Price Auction: Bidders bid truthfully b_i = v_i
    sp_bids = valuations
    # Winner is highest bidder; price paid is 2nd highest bid
    sorted_sp = np.sort(sp_bids, axis=1)
    sp_revenues = sorted_sp[:, -2] # 2nd highest

    # First-Price Auction: Bidders shade bids to equilibrium b_i = (n-1)/n * v_i
    fp_shading_factor = (num_bidders - 1) / num_bidders
    fp_bids = valuations * fp_shading_factor
    # Winner is highest bidder; price paid is their own bid (highest bid)
    sorted_fp = np.sort(fp_bids, axis=1)
    fp_revenues = sorted_fp[:, -1] # Highest shaded bid

    print(f"Auction Simulation ({num_trials:,} trials, {num_bidders} bidders):")
    print(f"  Second-Price Mean Revenue: {np.mean(sp_revenues):.4f} +/- {np.std(sp_revenues):.4f}")
    print(f"  First-Price Mean Revenue:  {np.mean(fp_revenues):.4f} +/- {np.std(fp_revenues):.4f}")
    print(f"  Theoretical Expected Revenue: {(num_bidders - 1) / (num_bidders + 1):.4f}")

if __name__ == "__main__":
    simulate_auctions()
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read Chapters 9 to 11 of [Multiagent Systems: Algorithmic, Game-Theoretic, and Logical Foundations](https://www.masfoundations.org/) by Shoham and Leyton-Brown.
   - Chapter 9 (Social Choice and Arrow's Theorem)
   - Chapter 10 (Mechanism Design and VCG)
   - Chapter 11 (Auctions)
2. Watch lectures 17 (Ultimatums and Bargaining) and 24 (Auctions and the Winner's Curse) of Yale's [ECON 159: Game Theory](https://oyc.yale.edu/economics/econ-159).
3. Read the lecture notes for Lectures 2 to 4 and Lecture 7 of Tim Roughgarden's [Algorithmic Game Theory](https://timroughgarden.org/f13/f13.html).
   - Review Myerson's Lemma and the structural proof of the VCG mechanism.
4. Read [Cooperation, Competition, and Maliciousness: LLM-Stakeholders Interactive Negotiation](https://arxiv.org/abs/2309.17234).
   - Study how multi-issue bargaining between LLM agents is evaluated when private valuation rubrics conflict.
5. Run the Python auction simulation above for `n = 2, 3, 5, 10` bidders. Confirm that the empirical difference between first-price and second-price revenue converges to zero within standard error, demonstrating the Revenue Equivalence Theorem.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Truth, Justice, and Algorithms (CMU 15-896)](https://www.cs.cmu.edu/~arielpro/15896s16/): Ariel Procaccia's course slides covering fair division, kidney exchange, and voting algorithms.
- [Improving Language Model Negotiation with Self-Play](https://arxiv.org/abs/2305.10142): Research on RL and in-context training for LLM bargaining agents.
- [An Introduction to the Theory of Mechanism Design](https://global.oup.com/academic/product/an-introduction-to-the-theory-of-mechanism-design-9780199734023): Tilman Borgers's definitive graduate textbook on mechanism design.

### Knowledge check

Use these questions to verify your understanding of coordination and mechanism design:

1. [What are the four fairness conditions in Arrow's Impossibility Theorem, and what is its mathematical conclusion?](#social-choice-theory-and-voting-rules)
2. [What does the Revelation Principle state, and why is it considered the foundation of mechanism design?](#mechanism-design-and-the-revelation-principle)
3. [Why is bidding your exact true valuation a strictly dominant strategy in a second-price (Vickrey) auction?](#single-item-auctions-and-revenue-equivalence)
4. [How does the Vickrey-Clarke-Groves (VCG) mechanism determine the payment charged to each agent using the concept of externality?](#the-vickrey-clarke-groves-vcg-mechanism)
5. [What four axioms uniquely characterize the Nash Bargaining Solution, and what quantity does it maximize?](#bargaining-and-the-nash-bargaining-solution)
