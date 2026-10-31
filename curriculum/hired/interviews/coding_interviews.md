### Introduction

Most AI engineering interview loops include at least one round where you write code while someone watches. For a career changer this round is often the scariest, and it's also the one where focused practice pays off most. The skills it tests can be learned, and the problems repeat a small set of patterns.

The format is changing, though. Alongside the classic "solve this algorithm puzzle in 45 minutes" screen, many companies now run practical builds, take-home projects, and rounds where you're expected to work with an AI coding assistant. Others ban AI tools completely. This lesson shows you what each format looks like in 2026, which patterns to learn, how to talk through a problem, and how to practice without grinding hundreds of problems you won't remember.

You already have the foundations. Complexity and Core Data Structures gave you Big-O, hash maps, stacks, queues and binary search. Working With AI Coding Assistants taught you to direct an agent and review its diff. Testing with pytest gave you the habit of checking your work. This lesson turns those into interview performance.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- The four kinds of coding rounds you're likely to meet.
- How company policies on using AI during interviews differ, and how to find out the rules.
- The seven core patterns behind most algorithm questions.
- Three worked examples in Python.
- A talk-out-loud routine for any coding problem.
- A realistic practice plan with spaced review and mock interviews.
- How to practice deliberately instead of grinding blindly.

### The four kinds of coding round

There's no standard interview loop. Every company designs its own and changes it often. Still, most coding rounds you'll meet fall into four kinds, and one loop may include several.

**1. The classic algorithm screen (DSA round).** DSA stands for data structures and algorithms. You get one or two short, well-defined problems, such as "given a list of meeting times, find the minimum number of rooms", and 30 to 60 minutes to solve them in a shared editor, usually without running code against a big test suite. Problems are typically at the level that practice sites label Easy or Medium. Interviewers grade more than whether the code works: did you clarify the problem, pick a sensible approach, explain the complexity, and test your own code? Large tech companies still use this format a lot, especially as an early filter.

**2. The practical coding round.** Instead of a puzzle, you build or fix something small and realistic in 45 to 90 minutes: parse a log file and report the slowest endpoints, write a rate limiter, add a feature to a small existing codebase, or call an API and handle its errors. For AI roles this might be "call a model, validate its JSON output, and retry on failure." These rounds reward the everyday skills you've practiced throughout this curriculum: reading unfamiliar code, writing clear functions, handling edge cases and testing.

**3. The take-home project.** You get a task and a few hours, or a few days, to complete it on your own time, then often walk the interviewer through it in a follow-up call. A typical AI take-home: "build a small retrieval service over these documents and report how well it answers these questions." Reviewers look at structure, tests, a README that explains decisions, and honesty about what you left out. Respect the suggested time limit and say how long you spent. A take-home that took you 30 hours instead of 4 doesn't show what they asked to see.

**4. The AI-assisted coding round.** This is the newest format. You get a realistic, often deliberately ambiguous problem, and you're allowed or expected to use an AI assistant. Canva, for example, [announced in June 2025](https://www.canva.dev/blog/engineering/yes-you-can-use-ai-in-our-interviews/) that it expects candidates for several engineering roles to use tools like Copilot, Cursor and Claude, and that the problems are harder and less textbook-like as a result. Meta's [hiring process page](https://www.metacareers.com/hiring-process/) says many of its interviews now include an AI assistant built into the interview environment, and that candidates are expected to use it. What's graded is your judgment: breaking the problem down, giving the assistant well-defined subtasks, reading what it produces, and catching its bugs. Canva's write-up says candidates who simply accepted the AI's output struggled. This is the workflow from Working With AI Coding Assistants, under time pressure.

### The rules on using AI

Here's the part that trips people up: **the rules differ by company, and sometimes by round within one company.** Three real, published policies show the range:

- **AI expected, inside the provided tool.** Meta's hiring page says candidates use the AI assistant built into its interview environment, and that no outside AI tools are authorized.
- **AI expected, with your own tools.** Canva asks candidates to use the AI tools they'd normally use at work.
- **No AI unless told otherwise.** Anthropic's [guidance for candidates](https://www.anthropic.com/candidate-ai-guidance) says live interviews and take-homes are done without AI assistance unless Anthropic says otherwise for that task, and it encourages AI for preparation, such as practicing answers.

Many other companies don't publish a policy at all. So the rule for you is simple: **ask your recruiter before every round**, in writing if you can. "Will I be allowed to use AI tools in the coding round, and if so, which ones?" is a normal, professional question. If the answer is no, using AI anyway, for example a hidden tool that feeds you answers, is cheating. It can get you rejected or fired later, and it skips the very thing the round is trying to measure. If the answer is yes, use AI openly and narrate what you're doing: "I'll have the assistant write the CSV parsing boilerplate while I think about the ranking logic, then I'll review it."

The practical upshot is that you need **both** skills. You must be able to solve a Medium-level problem with no help, and you must be able to direct an assistant well when one is allowed. Practice each separately.

### The core patterns

Most classic interview problems are variations on a few patterns. When you can name the pattern, you're most of the way to a solution. Here are the seven to learn first, with the clue in the problem that usually points to each:

| Pattern | Clue in the problem | Core tool |
| --- | --- | --- |
| Hashing | "find a pair", "count", "seen before?", "group by" | `dict`, `set`, `Counter` |
| Two pointers | sorted input, "pair that sums to", palindromes, merging | two indexes moving toward each other or in step |
| Sliding window | "longest/shortest substring or subarray that..." | a left and right edge over a contiguous range |
| Stack | matching brackets, "next greater element", undo, nesting | a `list` used with `append` and `pop` |
| BFS / DFS | grids, graphs, trees, "connected", "fewest steps" | `deque` for BFS (breadth-first search), recursion or a stack for DFS (depth-first search) |
| Binary search | sorted data, "minimum value that works", O(log n) asked for | halve the search range each step, `bisect` |
| Heap | "top k", "k smallest", "next event in time order", merging sorted lists | `heapq` |

A **heap** is the one structure you haven't met yet. It's a list arranged so that the smallest item is always at index 0. Adding an item or removing the smallest takes O(log n), so a heap is the right tool when you repeatedly need "the smallest (or largest) thing so far" without sorting everything. Python's `heapq` module gives you a min-heap on a plain list. For a max-heap, push negated values.

**BFS** explores a graph level by level: everything one step from the start, then everything two steps away, and so on. That's why it finds the **fewest steps** in an unweighted graph or grid. **DFS** goes as deep as it can down one path before backing up, and it's the natural fit for "visit everything that's connected" or "try every possibility". A **graph** here just means things (nodes) and connections between them (edges): a grid of cells, a network of web pages, a tree of folders.

Two patterns are worth naming but can wait until after these seven: **dynamic programming** (breaking a problem into overlapping subproblems and caching the answers) and **backtracking** (trying choices and undoing them). They show up in harder interviews. Learn them after the seven above feel comfortable.

### Worked examples

Each example below is a well-known interview problem. Every file ends with `assert` checks so you can run it with `uv run <file>.py` and see `all passed`. Don't just read them: close the page, solve each one yourself, then compare.

**Sliding window plus hashing.** "Given a string, find the length of the longest substring without repeating characters." The naive approach checks every substring, which is O(n²) or worse. The clue "longest substring" suggests a window: grow the right edge one character at a time, and when a character repeats, jump the left edge past its previous position. A dict remembers where each character was last seen.

```python
def longest_unique_run(s: str) -> int:
    """Length of the longest substring with no repeated characters."""
    last_seen: dict[str, int] = {}  # character -> index where we last saw it
    left = 0  # the window is s[left : right + 1]
    best = 0
    for right, ch in enumerate(s):
        # If ch is already inside the window, slide the left edge past it.
        if ch in last_seen and last_seen[ch] >= left:
            left = last_seen[ch] + 1
        last_seen[ch] = right
        best = max(best, right - left + 1)
    return best


assert longest_unique_run("abcabcbb") == 3  # "abc"
assert longest_unique_run("bbbbb") == 1
assert longest_unique_run("pwwkew") == 3  # "wke"
assert longest_unique_run("") == 0
assert longest_unique_run("abba") == 2  # the >= left check matters here
print("all passed")
```

Each character is visited once and dict operations are O(1), so this is O(n) time. The `"abba"` test is the kind of edge case interviewers love: without the `>= left` check, the second `a` would drag the left edge backward. Finding that case yourself, before the interviewer does, is a strong signal.

**BFS on a grid.** "Given a maze, return the fewest steps from S to E, or -1 if it can't be reached." The clue "fewest steps" points to BFS. Use a `deque` as the queue (from the complexity lesson, `popleft` is O(1)) and a set of visited cells so you never process a cell twice.

```python
from collections import deque


def shortest_path(grid: list[str]) -> int:
    """Fewest steps from S to E, moving up/down/left/right. '#' is a wall.

    Returns -1 if E can't be reached.
    """
    rows, cols = len(grid), len(grid[0])
    start = next((r, c) for r in range(rows) for c in range(cols) if grid[r][c] == "S")

    queue = deque([(start, 0)])  # (position, steps taken to get there)
    visited = {start}
    while queue:
        (r, c), steps = queue.popleft()
        if grid[r][c] == "E":
            return steps
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            if (
                0 <= nr < rows
                and 0 <= nc < cols
                and grid[nr][nc] != "#"
                and (nr, nc) not in visited
            ):
                visited.add((nr, nc))  # mark when queued, not when popped
                queue.append(((nr, nc), steps + 1))
    return -1


maze = [
    "S.#.",
    "..#E",
    "....",
]
assert shortest_path(maze) == 6
assert shortest_path(["S#E"]) == -1
assert shortest_path(["SE"]) == 1
print("all passed")
```

Every cell enters the queue at most once, so this is O(rows × cols) time and space. Swap the `deque` for a list used as a stack and you get DFS. It still finds E, but not necessarily by the shortest route. Being able to explain that difference is exactly what interviewers want.

**Heap plus hashing.** "Return the k most frequent words, most frequent first, breaking ties alphabetically." You might get this exact problem in an AI role dressed up as "which errors appear most in these agent logs?"

```python
import heapq
from collections import Counter


def top_k_words(words: list[str], k: int) -> list[str]:
    """The k most frequent words, most frequent first; ties break alphabetically."""
    counts = Counter(words)  # hashing: O(n) to count everything
    # heapq.nsmallest keeps a heap of size k: O(m log k) for m distinct words.
    # Negating the count makes "smallest" mean "most frequent".
    return heapq.nsmallest(k, counts, key=lambda w: (-counts[w], w))


logs = ["timeout", "ok", "ok", "rate_limit", "timeout", "ok", "auth", "timeout"]
assert top_k_words(logs, 2) == ["ok", "timeout"]  # both 3; "ok" wins the tie
assert top_k_words(logs, 3) == ["ok", "timeout", "auth"]
assert top_k_words([], 3) == []
print("all passed")
```

A perfectly good first answer is `sorted(counts, key=...)[:k]`, which is O(m log m). Say it, then offer the heap as the improvement when k is much smaller than m. Starting simple and then improving is the shape of a good interview answer.

### A talk-out-loud routine

In a live round, the interviewer can't read your mind. Silence for ten minutes followed by perfect code scores worse than a clear, spoken path to slightly imperfect code. Use the same routine on every problem, in practice and for real, so it becomes automatic:

1. **Restate and clarify (2–3 minutes).** Say the problem back in your own words. Ask about input size, empty inputs, duplicates, negative numbers and what to return when there's no answer. Clarifying is part of the job, not stalling.
1. **Work one example by hand.** Write a small input and its expected output. Then write a tricky one. These become your tests later.
1. **State the brute-force solution and its Big-O.** "Checking every pair works, but it's O(n²)." This proves you can solve it at all, and it gives you something to improve on.
1. **Find the pattern.** Ask: what work is repeated? Which clue from the pattern table matches? Say your candidate idea and its complexity *before* coding, and check that the interviewer is happy with it.
1. **Code it, narrating.** Use clear names. Say what each block is for. If you get stuck, say what you're stuck on. Interviewers often give hints, but only when they know where you are.
1. **Test it yourself.** Walk through your examples line by line, including the edge cases. Fix bugs out loud, without panic. Every engineer writes bugs. What's graded is how you find them.
1. **State the final complexity and trade-offs.** Time, space, and what you'd change for much bigger input.

In an AI-assisted round, the routine is the same. Steps 1 to 4 are still yours. In step 5 you hand the assistant well-scoped pieces, and step 6 grows into reading and testing everything it wrote.

### A realistic practice plan

No study proves that a particular number of problems gets you hired, so be wary of anyone who quotes one confidently. What the widely used free resources agree on is this: a curated list of problems, organized by pattern, worked through over weeks rather than crammed. The [Tech Interview Handbook's study plan](https://www.techinterviewhandbook.org/coding-interview-study-plan/), for example, suggests about three months at roughly 11 hours a week, ending with about 75 carefully chosen problems. A plan sized for someone finishing this curriculum:

- **Weeks 1–4: learn the patterns.** Work through the [NeetCode roadmap](https://neetcode.io/roadmap) one topic at a time, in its order (arrays and hashing, two pointers, sliding window, stack, binary search, and so on). Do the Easy problems in a topic, then the first few Mediums. Aim for roughly 3–5 problems per session, several sessions a week.
- **Weeks 5–8: mixed, timed practice.** Pick problems without knowing their topic (the [Grind 75 list](https://www.techinterviewhandbook.org/grind75/) works well for this), and give yourself 25–40 minutes each. Recognizing the pattern without the topic label is the real skill.
- **From about week 4: mock interviews.** At least one a week, with a friend who codes or someone from a developer community, taking turns as interviewer. Record them if your partner agrees. If you can't find anyone, record a solo session against a fixed problem and review it the next day. You'll hear every silent stretch and skipped test. Being the interviewer teaches you what a good answer sounds like.
- **Every week: one practical build.** Set a 60-minute timer and build something small: a log analyzer, a retry wrapper around a model call, a CLI that dedupes a CSV. Alternate between solo and AI-assisted builds so you practice both kinds of round.
- **Spaced review throughout.** Revisit each problem you struggled with about 1 day, 1 week and 1 month later, and solve it again from a blank file. Retrieving something from memory at growing intervals is called **spaced repetition**, and it's one of the best-supported findings in learning research. Re-solving a few old problems a session is worth more than adding new ones.

Keep a practice log: one row per attempt, with the problem, its pattern, the minutes you spent, whether you solved it unaided, and a one-line "the key insight was...". The log drives your spaced review and shows you which patterns are weak.

### Avoiding blind grinding

The trap is easy to fall into: solve a problem, peek at the answer when stuck, move on, repeat a few hundred times, and find that a slightly different problem in a real interview still leaves you blank. Counting solved problems feels like progress, but it isn't the goal. The goal is recognizing the pattern and explaining it. A few habits keep practice deliberate:

- **Time-box being stuck.** Give a new problem a real attempt, about 20–30 minutes. If you're still stuck, read a hint or the solution, which is fine, then close it and write the solution from memory. Mark the problem for review.
- **Explain, don't just pass.** After each problem, write two sentences: which clue pointed to which pattern, and the complexity. If you can't write them, you haven't learned the problem yet.
- **Use AI as a tutor, not an answer key.** When practicing for no-AI rounds, ask an assistant for a hint, an edge case you missed, or a review of your solution's complexity, not for the solution. Asking it to play interviewer and push back on your reasoning is a great use of it.
- **Stop when returns flatten.** Once you can reliably solve unseen Mediums in about 30 minutes while talking, more problems add little. Your time is better spent on projects, system design and behavioral stories, which the next lessons cover.
- **Keep it in proportion.** For many AI engineering roles, your portfolio, evals and shipped projects matter as much as the coding round. The algorithm round is a bar to clear, not the whole job.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Write in plain Python

Use the language you know best, and for you that's Python. Interviewers don't penalize `collections.Counter`, `deque` or `heapq`. Knowing the standard library is a plus. Just be ready to explain what each one costs.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read the [Tech Interview Handbook's coding interview techniques](https://www.techinterviewhandbook.org/coding-interview-techniques/) and its [best practices cheatsheet](https://www.techinterviewhandbook.org/coding-interview-cheatsheet/). They are free and widely used, and they expand the talk-out-loud routine with concrete phrases to use before, during and after coding. Then skim its [study plan](https://www.techinterviewhandbook.org/coding-interview-study-plan/) and adapt it to your weekly hours.
1. Read Canva's ["Yes, you can use AI in our interviews"](https://www.canva.dev/blog/engineering/yes-you-can-use-ai-in-our-interviews/), Meta's [hiring process page](https://www.metacareers.com/hiring-process/) (the section on AI in interviews) and Anthropic's [guidance on candidates' AI usage](https://www.anthropic.com/candidate-ai-guidance). Together they show the range of policies you'll meet, and what an AI-assisted round actually grades.
1. Warm up with the [complexity exercise set](https://github.com/espiNovah/project-mimir/tree/main/exercises/complexity). From the `exercises/` folder, run `uv run pytest complexity/<exercise>`. This time, before coding each one, say steps 1–4 of the talk-out-loud routine out loud and set a 25-minute timer.
1. Start the pattern practice on the [NeetCode roadmap](https://neetcode.io/roadmap). The problem lists and video explanations are free. Logging in is optional and only saves progress, so a spreadsheet log works just as well.
   - Solve at least 15 problems this week across the first four topics (arrays and hashing, two pointers, sliding window, stack), mostly Easy with a few Medium.
   - Start your practice log with the columns described in [A realistic practice plan](#a-realistic-practice-plan), and schedule your first spaced reviews.
1. Do one 60-minute practical build twice, once without AI and once AI-assisted: read a JSONL file of fake agent traces (generate 1,000 lines with a script), and print the five slowest tool calls and the most common error type, with pytest tests. Compare the two attempts in a short note: what was faster, and what did you have to fix in the AI's code?
1. Book one mock coding interview with a friend or someone from a developer community this week and swap roles, and record what the interviewer noticed. If you can't find a partner, record yourself solving an unseen problem out loud and review it the next day. You'll run a fuller version in the Mock Interview Loop project.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What are the four kinds of coding round, and what does each one grade?](#the-four-kinds-of-coding-round)
- [How should you find out whether AI tools are allowed in a round, and why does it matter?](#the-rules-on-using-ai)
- [Which clue in a problem suggests a sliding window, and which suggests a heap?](#the-core-patterns)
- [Why does BFS find the fewest steps in a grid while DFS might not?](#worked-examples)
- [What are the steps of the talk-out-loud routine, and why state the brute-force solution first?](#a-talk-out-loud-routine)
- [What is spaced review, and how would you schedule it for a problem you struggled with?](#a-realistic-practice-plan)
- [What habits turn problem grinding into deliberate practice?](#avoiding-blind-grinding)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Sean Prashad's LeetCode Patterns](https://seanprashad.com/leetcode-patterns/) lists classic problems that you can filter by pattern and difficulty. It's another good source of mixed practice once the NeetCode topics feel familiar.
- [The `heapq` docs](https://docs.python.org/3/library/heapq.html) explain the heap invariant and include a priority-queue recipe that comes up in scheduling-style problems.
- [*Problem Solving with Algorithms and Data Structures using Python*](https://runestone.academy/ns/books/published/pythonds3/index.html), the textbook from the complexity lesson, has chapters on recursion, trees and graphs (including BFS and DFS) for when you want the theory behind the patterns.
