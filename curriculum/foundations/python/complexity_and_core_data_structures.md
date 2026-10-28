### Introduction

Your Expense Tracker handles fifty rows in a blink. What about a million? Some programs get a little slower as their input grows; others go from "instant" to "still running after lunch". The difference is usually the shape of the work your code does, and that usually comes down to which data structure you picked.

This lesson gives you the vocabulary for that shape, called **Big-O notation**, and connects it to the Python collections you already know. You'll see why a `set` can answer "is this in here?" thousands of times faster than a `list`, why removing from the front of a list is a trap, and how to measure all of this yourself with `timeit` instead of taking anyone's word for it.

This matters twice over. In real AI work, you'll deduplicate documents, cache responses and queue jobs, and the wrong structure turns a quick script into an expensive one. In interviews, almost every coding question ends with "what's the time complexity of your solution?" This lesson lays the groundwork for the Coding Interviews lesson in Getting Hired.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What Big-O notation describes, and the common complexity classes.
- Why dictionaries and sets look things up in constant time (hash maps).
- Which list operations are fast and which are slow.
- Stacks and queues, and when to use `collections.deque`.
- Sorting, and searching a sorted list with binary search.
- Measuring code with `timeit`.
- How to talk about complexity in an interview.

### Counting steps instead of seconds

Timing code tells you how fast it ran today, on your machine, with that input. It doesn't tell you what happens when the input is ten times bigger. For that question, programmers count **steps**: roughly how many basic operations (comparisons, additions, lookups) the code does, as a function of the input size. By convention, the input size is called **n**: the number of items in a list, rows in a file or characters in a string.

Look at this function:

```python
def total(amounts: list[float]) -> float:
    result = 0.0
    for amount in amounts:
        result += amount
    return result
```

It does one addition per item. With 10 items it does 10 additions; with a million items, a million. The work grows in a straight line with n. We say it runs in **O(n)** time, read "big O of n" or "linear time".

**Big-O notation** describes how the work grows as n grows, ignoring details that don't change the overall shape. Two rules make it simple:

- **Drop constants.** A loop that does three things per item is still O(n), not O(3n). Constants depend on the machine; the shape doesn't.
- **Keep only the biggest term.** If code does n² steps and then another n steps, it's O(n²). When n is a million, the extra n barely matters.

Big-O usually describes the **worst case**: the most work the code could have to do. Searching a list for an item might get lucky and find it first, but we plan for when it's last or missing.

### The common complexity classes

You'll meet the same handful of shapes over and over. Here they are from fastest to slowest, with the number of steps for a million items:

| Big-O | Name | Example | Steps for n = 1,000,000 |
| --- | --- | --- | --- |
| O(1) | constant | look up a key in a dict | 1 |
| O(log n) | logarithmic | binary search in a sorted list | about 20 |
| O(n) | linear | loop over a list once | 1,000,000 |
| O(n log n) | linearithmic | sort a list | about 20,000,000 |
| O(n²) | quadratic | compare every item with every other item | 1,000,000,000,000 |

**Logarithmic** needs a word of explanation. log n (base 2, in computing) is how many times you can halve n before you reach 1. Halving a million takes about 20 steps, which is why algorithms that throw away half the remaining data each step are so fast.

The jump from O(n) to O(n²) is the one that bites beginners most often. A **nested loop**, a loop inside a loop over the same data, is the usual cause. And it can hide: `if item in some_list` inside a `for` loop is a nested loop, because `in` on a list is itself a loop.

Big-O applies to memory as well. **Space complexity** describes how much extra memory code needs as n grows. Building a set of everything you've seen costs O(n) space. Often you trade one for the other: spend memory to save time.

### Hash maps: why dicts and sets are fast

To check whether an item is in a list, Python has no choice but to look at each element in turn: O(n). Dictionaries and sets work differently. They're built on a **hash table** (also called a **hash map**). When you store a key, Python runs it through a **hash function** that turns it into a number, and uses that number to decide where in memory the key lives. To look the key up again, Python hashes it again and jumps straight to that spot. No scanning. On average, adding, finding and deleting a key take **O(1)**, constant time, however big the dict is.

This is also why dict keys and set items must be **hashable**: their hash must never change. Strings, numbers and tuples of them are hashable. Lists aren't, because they can change, which is why `{["a", "b"]: 1}` raises `TypeError: unhashable type: 'list'`.

You can watch the difference with `timeit`, a standard-library module that runs a piece of code many times and reports how long it took. Save this as `membership.py` and run it with `uv run membership.py`:

```python
import timeit

for n in [1_000, 10_000, 100_000]:
    numbers_list = list(range(n))
    numbers_set = set(numbers_list)
    missing = -1  # worst case: not in the collection, so a list checks every item

    # Run each check 1,000 times and report the total in milliseconds.
    t_list = timeit.timeit(lambda: missing in numbers_list, number=1_000)
    t_set = timeit.timeit(lambda: missing in numbers_set, number=1_000)
    print(f"n={n:>7,}  list: {t_list * 1000:8.2f} ms   set: {t_set * 1000:6.3f} ms")
```

On one laptop it printed:

```text
n=  1,000  list:     7.09 ms   set:  0.047 ms
n= 10,000  list:    70.94 ms   set:  0.049 ms
n=100,000  list:   780.70 ms   set:  0.050 ms
```

Your numbers will differ, but the pattern won't. Each time n grows tenfold, the list gets about ten times slower (linear), while the set stays flat (constant).

### Lists: fast at the end, slow at the front

A Python list stores its items side by side in one block of memory, like numbered seats in a row. That makes some operations cheap and others expensive:

- **Fast, O(1):** reading or replacing `items[i]`, `len(items)`, `append` and `pop()` from the end.
- **Slow, O(n):** `x in items`, `items.index(x)`, `items.remove(x)`, and `insert(0, x)` or `pop(0)` at the front, because every other item has to shift one seat over.

(Strictly, `append` is **amortized** O(1): now and then the list runs out of room and copies itself into a bigger block, but that happens so rarely that the average cost per append stays constant.)

The official [TimeComplexity page on the Python wiki](https://wiki.python.org/moin/TimeComplexity) lists the cost of every operation on lists, dicts, sets and deques. Bookmark it.

### Stacks and queues

Two simple patterns show up constantly, from parsing to job processing to agent loops:

- A **stack** is last in, first out (LIFO), like a pile of plates. You push onto the top and pop from the top. A plain list is a perfect stack: `append` to push and `pop()` to pop, both O(1). Your browser's back button and Python's own call stack (the list of frames in a traceback) work this way.
- A **queue** is first in, first out (FIFO), like a line at a shop. You add at the back and remove from the front. A list is a bad queue, because `pop(0)` is O(n).

For queues, use `collections.deque` (pronounced "deck", short for double-ended queue). It's designed so that adding and removing at **both** ends is O(1). Compare them in `queues.py`:

```python
import timeit
from collections import deque


def drain_list(n: int) -> None:
    queue = list(range(n))
    while queue:
        queue.pop(0)  # removes the first item: every other item shifts left


def drain_deque(n: int) -> None:
    queue = deque(range(n))
    while queue:
        queue.popleft()  # removes the first item: nothing shifts


for n in [10_000, 100_000]:
    t_list = timeit.timeit(lambda: drain_list(n), number=1)
    t_deque = timeit.timeit(lambda: drain_deque(n), number=1)
    print(f"n={n:>7,}  list.pop(0): {t_list:.3f} s   deque.popleft(): {t_deque:.4f} s")
```

With 100,000 items, the list took over a second and the deque a few milliseconds. Draining the list is O(n) work per pop, done n times, so O(n²) overall. The deque is O(1) per pop, so O(n) overall.

The trade-off is that a deque is slow to index in the middle (`d[50_000]`), so use it when you only touch the ends. A deque with `maxlen` is also a handy "keep the last N items" buffer: `deque(maxlen=10)` drops the oldest item when a new one arrives.

### Sorting and searching

Python's `sorted()` and `list.sort()` run in **O(n log n)**, which is as good as a general-purpose sort can do. You won't need to write your own sort at work, but you should know that sorting is not free: sorting inside a loop is a common hidden cost.

Once data is sorted, searching it gets much faster with **binary search**. Look at the middle item. If your target is smaller, throw away the right half; if bigger, the left half. Repeat. Each step halves what's left, so it's O(log n): about 20 steps for a million items. The standard library's `bisect` module does it for you:

```python
from bisect import bisect_left


def contains_sorted(items: list[int], target: int) -> bool:
    """Binary search: items must already be sorted."""
    i = bisect_left(items, target)  # where target would be inserted
    return i < len(items) and items[i] == target


prices = sorted([42, 7, 19, 3, 88])  # [3, 7, 19, 42, 88]
print(contains_sorted(prices, 19))  # True
print(contains_sorted(prices, 20))  # False
```

If you only need "is it there?", a set is simpler and faster. Binary search earns its place when you need order too, such as "find the first expense on or after March 1" in a sorted list of dates.

### Measuring with timeit

Big-O predicts how code scales, but only measurement tells you whether something is actually slow enough to matter. A few habits make measurements trustworthy:

- **Measure, don't guess.** Programmers are famously bad at guessing where time goes. Time the real thing.
- **Repeat.** A single run is noisy. `timeit.timeit(func, number=1_000)` runs the code many times; `timeit.repeat` repeats that whole measurement so you can take the fastest.
- **Grow n.** Run with 1,000, 10,000 and 100,000 items. If the time grows tenfold, it's linear; a hundredfold, quadratic. This is how you check your Big-O reasoning against reality.
- **Try the command line.** `uv run python -m timeit -s "s = set(range(10_000))" "5000 in s"` times a one-liner without writing a file. `-s` is setup code that runs once and isn't timed.

Here's the whole lesson in one example. Both functions answer "does this list contain any duplicates?":

```python
import random
import timeit


def has_duplicates_slow(items: list[str]) -> bool:
    """Compare every pair: O(n^2)."""
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                return True
    return False


def has_duplicates_fast(items: list[str]) -> bool:
    """Remember what we've seen in a set: O(n) time, O(n) extra space."""
    seen: set[str] = set()
    for item in items:
        if item in seen:
            return True
        seen.add(item)
    return False


for n in [1_000, 2_000, 4_000]:
    emails = [f"user{i}@example.com" for i in range(n)]  # no duplicates: worst case
    random.shuffle(emails)
    slow = timeit.timeit(lambda: has_duplicates_slow(emails), number=1)
    fast = timeit.timeit(lambda: has_duplicates_fast(emails), number=1)
    print(f"n={n:>5}  slow: {slow:.3f} s   fast: {fast:.5f} s")
```

Each time n doubles, the slow version takes about four times as long (that's n² at work) while the fast one merely doubles. At 4,000 emails the gap is roughly a thousandfold. At a million, the slow version would run for hours.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Fast enough is fast enough

Don't rewrite every loop for speed. For a list of 50 items, O(n²) is instant, and clear code beats clever code. Reach for Big-O when the input can grow, when code runs inside another loop, or when a measurement says something is slow.

</div>

### Why it matters for interviews and real code

In a **coding interview**, you'll typically get a small problem, such as "return the two numbers in this list that add up to a target", and talk through a solution while you write it. Interviewers listen for a pattern like this:

1. State a simple solution and its complexity: "Checking every pair works, but it's O(n²)."
1. Spot the repeated work: "For each number I'm searching the list for its partner."
1. Pick a structure that removes it: "If I store numbers I've seen in a dict, finding the partner is O(1), so the whole thing is O(n) time and O(n) space."

That move, swapping a repeated search for a dict or set lookup, solves a surprising share of interview questions. Stacks (matching brackets), queues (processing things in order), sorting first and binary search cover much of the rest. You'll practice these patterns properly in the Coding Interviews lesson; this lesson gives you the vocabulary to explain them.

In real code, the same reasoning shows up in less tidy forms. Deduplicating scraped documents before you embed them (paying per item) is a set problem. Caching model responses by prompt is a dict problem. A job worker pulling tasks in order is a queue. When a script that was fine on test data crawls on real data, the first question to ask is "is there a hidden nested loop?"

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read from [*Problem Solving with Algorithms and Data Structures using Python*](https://runestone.academy/ns/books/published/pythonds3/index.html) by Brad Miller and David Ranum, a free interactive textbook that teaches this lesson's ideas in Python, with code you can run in the page.
   - Read the "Analysis" chapter. It covers Big-O with worked examples, including an anagram problem solved several ways at different costs, and the performance of Python's lists and dictionaries.
   - In the "Basic Data Structures" chapter, read the sections on stacks, queues and deques. Skip the linked-list sections for now.
1. Read [Using Lists as Stacks and Using Lists as Queues](https://docs.python.org/3/tutorial/datastructures.html#using-lists-as-stacks) in the official Python tutorial (two short sections), which show the list-as-stack pattern and explain why a deque makes a better queue.
1. Read [the TimeComplexity page on the Python wiki](https://wiki.python.org/moin/TimeComplexity) for the lists, deque, set and dict tables. You don't need to memorize it; notice which operations are O(n) and get in the habit of looking things up here.
1. Read the [deque section of the collections docs](https://docs.python.org/3/library/collections.html#collections.deque) and the [bisect module docs](https://docs.python.org/3/library/bisect.html) up to and including "Searching Sorted Lists". Then skim the [timeit docs](https://docs.python.org/3/library/timeit.html), focusing on the "Basic Examples" and "Command-Line Interface" sections.
1. Watch [CS50x Week 3: Algorithms](https://cs50.harvard.edu/x/weeks/3/) for a vivid, visual explanation of linear search, binary search and sorting, and why their running times differ. The code is in C, but you only need the ideas.
1. Practice:
   - Do the [complexity exercise set](https://github.com/espiNovah/project-mimir/tree/main/exercises/complexity). Each exercise has a starter file and failing tests; make the tests pass with `uv run pytest complexity/<exercise>` from the `exercises/` folder. Before you write code, write a comment stating the Big-O of the naive approach and of yours.
   - Open your Expense Tracker and find one operation that would get slow with a million expenses, for example a category summary that loops over all expenses once per category. Measure it with `timeit` at three sizes of fake data, improve it if you can, and record the before-and-after numbers in your README.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What does Big-O notation describe, and why do we drop constants?](#counting-steps-instead-of-seconds)
- [Why is a loop that contains `x in some_list` quadratic?](#the-common-complexity-classes)
- [Why can a set check membership in constant time when a list can't?](#hash-maps-why-dicts-and-sets-are-fast)
- [Which list operations are O(n), and why is pop(0) one of them?](#lists-fast-at-the-end-slow-at-the-front)
- [What is the difference between a stack and a queue, and which Python type suits each?](#stacks-and-queues)
- [When does binary search work, and how many steps does it take for a million items?](#sorting-and-searching)
- [How can timing code at several input sizes confirm your Big-O reasoning?](#measuring-with-timeit)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Rob Bell's "A beginner's guide to Big O Notation"](https://rob-bell.net/2009/06/a-beginners-guide-to-big-o-notation/) is a short classic that walks through O(1), O(n), O(n²) and O(log n) with tiny examples. It's a good quick refresher.
- [freeCodeCamp's "Big O Cheat Sheet"](https://www.freecodecamp.org/news/big-o-cheat-sheet-time-complexity-chart/) charts the common classes with more examples. Its code is in JavaScript, but it reads almost like Python.
- [The Big-O Cheat Sheet](https://www.bigocheatsheet.com/) charts the complexity of common data structures and sorting algorithms on one page.
- [VisuAlgo's sorting visualizations](https://visualgo.net/en/sorting) animate sorting algorithms step by step, so you can see why some take n² steps and others n log n.
- [The NeetCode roadmap](https://neetcode.io/roadmap) groups classic interview problems by pattern, starting with "Arrays and Hashing". It's where the Coding Interviews lesson picks up.
