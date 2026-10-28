### Introduction

A lot of AI engineering is digging specific pieces out of messy text. A model was asked to finish with "Answer: B" but wrote "**Answer:** b) because...". A log file has thousands of lines and you want every request that took longer than two seconds. A document has dates in three formats. String methods like `.split()`, `.startswith()` and `in` get you surprisingly far, but at some point you need to describe a *pattern*, not an exact string.

A **regular expression** (regex for short) is a tiny language for describing patterns in text: "the word Answer, a colon, some spaces, then one letter from A to D." Python's built-in `re` module lets you search for those patterns, pull out parts of them, and replace them. Regexes look cryptic at first, but you only need a dozen or so symbols for everyday work, and good tools let you test a pattern before you trust it.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What a regular expression is, and the core pattern syntax.
- Why patterns go in raw strings.
- Searching with `re.search` and reading match objects.
- Capturing parts of a match with groups and named groups.
- Finding every match with `re.findall` and replacing with `re.sub`.
- Extracting answers from model output and fields from log lines.
- When not to use a regex.

### Pattern basics

Most characters in a pattern match themselves: the pattern `cat` matches the text "cat". A few characters have special meanings. These cover most of what you'll write:

| Pattern | Matches |
| --- | --- |
| `.` | any single character except a newline |
| `\d` | a digit, 0 to 9 |
| `\w` | a "word" character: a letter, digit or underscore |
| `\s` | whitespace: a space, tab or newline |
| `[ABCD]` | any one of the characters listed; `[A-D]` is the same as a range |
| `[^0-9]` | any character *not* listed |
| `^` and `$` | the start and the end of the text (or of a line, with a flag) |
| `\b` | a word boundary, the edge between a word character and anything else |

Then **quantifiers** say how many times the thing before them may repeat:

| Quantifier | Means |
| --- | --- |
| `*` | zero or more |
| `+` | one or more |
| `?` | zero or one (optional) |
| `{3}` / `{2,4}` | exactly 3 / between 2 and 4 |

So `\d+` means "one or more digits", `colou?r` matches both "color" and "colour", and `\d{4}-\d{2}-\d{2}` matches a date like 2026-10-28. To match a special character literally, put a backslash in front of it: `\.` matches a real dot and `\$` a real dollar sign.

Quantifiers are **greedy**: they grab as much text as they can. `<.+>` applied to `<b>hi</b>` matches the whole string, not just `<b>`. Add `?` after a quantifier to make it lazy, matching as little as possible: `<.+?>` matches `<b>`.

### Raw strings

Regexes use lots of backslashes, and so do Python strings: `"\n"` is a newline and `"\b"` is a backspace character. To stop Python from interpreting the backslashes before `re` sees them, always write patterns as **raw strings**, with an `r` before the quote:

```python
import re

re.search("\bcat\b", "the cat sat")    # None: "\b" became a backspace character
re.search(r"\bcat\b", "the cat sat")   # <re.Match object; span=(4, 7), match='cat'>
```

Make `r"..."` a reflex for every pattern, even ones without backslashes. It costs nothing and prevents a confusing class of bugs.

### Searching and match objects

`re.search(pattern, text)` scans the text for the first place the pattern matches. It returns `None` if there's no match, or a **match object** if there is. Always check for `None` before using the result:

```python
import re

reply = "Let me think step by step... The answer is 42 tokens."
match = re.search(r"\d+", reply)
if match:
    print(match.group())   # '42', the matched text
    print(match.start())   # 43, where it started in the string
else:
    print("no number found")
```

Two cousins are worth knowing. `re.fullmatch` succeeds only if the *entire* string matches, which is what you want for validation ("is this whole input a date?"). `re.match` only checks at the very start of the string, which surprises people; prefer `search` or `fullmatch`.

**Flags** change how matching works. `re.IGNORECASE` (or `re.I`) ignores case, and `re.MULTILINE` makes `^` and `$` match at every line. Pass them as the last argument: `re.search(r"^answer", text, re.I | re.M)`.

### Groups and extracting data

Parentheses create a **group**, which captures part of the match so you can pull it out separately. Groups are where regexes become really useful. Here's a function that extracts a multiple-choice answer from model output, coping with the different ways a model might phrase it:

```python
import re

ANSWER_RE = re.compile(r"answer\W*([A-D])\b", re.IGNORECASE)


def extract_choice(reply):
    """Return the letter after 'Answer', uppercased, or None if there isn't one."""
    matches = ANSWER_RE.findall(reply)
    if not matches:
        return None
    return matches[-1].upper()   # models sometimes restate; trust the last one


replies = [
    "Answer: B",
    "**Answer:** c) Because the loop never ends.",
    "I considered answer A, but my final answer: D.",
    "I'm not sure.",
]
for reply in replies:
    print(repr(extract_choice(reply)))
# 'B', 'C', 'D', None
```

Read the pattern piece by piece: the word `answer`, then `\W*` (any non-word characters, which soaks up colons, spaces and the `**` of Markdown bold), then a group `([A-D])` capturing one letter, then `\b` so that "Answer: Because" doesn't match the "B" of "Because". `re.compile` turns the pattern into an object you can reuse, which keeps the pattern in one named place at the top of your file.

When a pattern has several groups, give them names with `(?P<name>...)` so your code reads clearly. Here's a parser for log lines like `2026-10-28 14:03:11 INFO model=cheap latency_ms=1834 status=200`:

```python
import re

LINE_RE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>[\d:]{8}) (?P<level>[A-Z]+) "
    r"model=(?P<model>\S+) latency_ms=(?P<latency>\d+) status=(?P<status>\d{3})$"
)

log = """\
2026-10-28 14:03:11 INFO model=cheap latency_ms=1834 status=200
2026-10-28 14:03:15 WARNING model=capable latency_ms=4120 status=200
this line is garbage
2026-10-28 14:03:20 ERROR model=cheap latency_ms=30001 status=529
"""

slow = []
for line in log.splitlines():
    m = LINE_RE.fullmatch(line)
    if m is None:
        continue                       # skip lines that don't fit the format
    row = m.groupdict()                # {'date': '2026-10-28', 'time': ..., ...}
    if int(row["latency"]) > 2000:     # groups are always strings; convert them
        slow.append((row["time"], row["model"], int(row["latency"])))

print(slow)
# [('14:03:15', 'capable', 4120), ('14:03:20', 'cheap', 30001)]
```

`\S+` means "one or more non-whitespace characters", a handy way to say "a value with no spaces". Note that two adjacent strings in parentheses are joined into one, which is how the long pattern is split over two lines.

### Finding all matches and replacing

`re.findall` returns every match as a list. With no groups you get the matched strings; with one group you get that group's text; with several groups you get tuples:

```python
text = "Contact ada@example.com or grace@example.org for access."
re.findall(r"[\w.]+@[\w.]+", text)       # ['ada@example.com', 'grace@example.org']
re.findall(r"#(\d+)", "Fixes #12 and #340")  # ['12', '340']
```

`re.sub(pattern, replacement, text)` replaces every match. It's useful for cleaning text before sending it to a model, or redacting it before logging it:

```python
re.sub(r"\s+", " ", "too    many\n\nspaces")                 # 'too many spaces'
re.sub(r"sk-[A-Za-z0-9_-]{8,}", "[REDACTED]", "key=sk-abc123XYZ789")  # 'key=[REDACTED]'
```

In the replacement, `\1` (or `\g<name>`) inserts what a group captured, so `re.sub(r"(\d{2})/(\d{2})/(\d{4})", r"\3-\1-\2", "10/28/2026")` reorders a US date into `2026-10-28`.

### When not to use regex

Regexes are powerful, which makes them easy to overuse. Reach for something else when:

- **A string method will do.** `line.startswith("ERROR")`, `"timeout" in reply` and `text.split(",")` are clearer and faster than the equivalent regex.
- **The text is a real format.** Use `json.loads` for JSON, the `csv` module for CSV, and a proper parser for HTML. These formats nest and escape things in ways a regex can't handle reliably. If a model wraps JSON in a Markdown code fence, a regex to strip the fence is fine, but then hand the inside to `json.loads`.
- **You control the output.** If you're parsing a model's answer, it's usually better to ask for structured output in the first place, which you'll learn in the Structured Outputs section, than to write ever-more-clever regexes to cope with free text. Regex extraction is a useful fallback, not a foundation.
- **Nobody can read the pattern.** If a regex needs a paragraph of explanation, split the job into steps, or add a comment above it saying what it matches, with an example.

Whatever you write, test it against real examples, including ones that should *not* match. A pattern that matches everything you expected and also three things you didn't is a bug waiting to happen.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Watch [CS50P Lecture 7: Regular Expressions](https://cs50.harvard.edu/python/weeks/7/). It builds up an email validator one symbol at a time, which is a good way to see how patterns grow, and then covers groups and `re.sub`.
1. Work through the interactive lessons at [RegexOne](https://regexone.com/), at least lessons 1 to 12. Each one teaches a single symbol and has you write patterns against examples in the browser.
1. Read the [Regular Expression HOWTO](https://docs.python.org/3/howto/regex.html) in the Python docs, from "Simple Patterns" through "Grouping". It's the official, careful explanation of everything in this lesson.
   - Keep [regex101](https://regex101.com/) open in another tab while you read. Choose the "Python" flavor on the left, paste a pattern and some text, and it explains each part of the pattern and highlights the matches.
1. Do the [regex exercise set](https://github.com/espiNovah/project-mimir/tree/main/exercises/regex). Make the tests pass with `uv run pytest regex/<exercise>` from the `exercises/` folder.
1. Write a small log analyzer. In your practice project, save the four log lines from this lesson plus at least six of your own (vary the models, latencies and statuses, and include a couple of malformed lines) to `requests.log`. Write a script that reads the file and prints the number of requests per model, the average latency per model, and every line with a status other than 200. Malformed lines should be counted and skipped, not crash the script.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What do `\d`, `\s`, `+` and `?` mean in a pattern, and what does it mean that quantifiers are greedy?](#pattern-basics)
- [Why should you write patterns as raw strings?](#raw-strings)
- [What does re.search return when there's no match, and how does fullmatch differ from it?](#searching-and-match-objects)
- [How do you capture part of a match, and why give groups names?](#groups-and-extracting-data)
- [What does findall return when the pattern has one group?](#finding-all-matches-and-replacing)
- [Name two situations where you shouldn't use a regex.](#when-not-to-use-regex)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The re module reference](https://docs.python.org/3/library/re.html) lists every symbol, flag and function. Search it when you meet syntax you don't recognize.
- [CS50P Problem Set 7](https://cs50.harvard.edu/python/psets/7/) has five more regex problems, from IP address validation to extracting YouTube links from HTML, each with automated checks.
