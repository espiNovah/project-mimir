### Introduction

When a program ends, every variable it created disappears. To keep anything (high scores, settings, a conversation history, a dataset), you have to write it to a file and read it back later.

This lesson covers plain text files and **JSON** (JavaScript Object Notation), a text format for structured data. JSON is the language of web APIs. When your code sends a request to a model provider, the body is JSON; the reply is JSON; tool definitions are JSON; the structured outputs you'll ask models for are JSON. Python makes JSON easy because it maps almost one-to-one onto the dicts and lists you just learned.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- File paths and the `pathlib` module.
- Reading and writing text files with `open()` and `with`.
- Text encodings and why to always say UTF-8.
- What JSON looks like and how it maps to Python.
- Loading and saving JSON with the `json` module.
- JSON Lines, a common format for datasets.

### Paths

A **path** is the address of a file, such as `data/questions.json`. A **relative path** is interpreted from the folder you ran the program from (the current working directory, which you met in Command Line Basics). An **absolute path** starts from the root of the drive, such as `/Users/ada/project/data/questions.json`.

Python's `pathlib` module represents paths as objects that work the same way on macOS, Linux and Windows:

```python
from pathlib import Path

data_dir = Path("data")
data_dir.mkdir(exist_ok=True)          # create the folder if it doesn't exist
notes = data_dir / "notes.txt"         # the / operator joins path parts
print(notes)                           # data/notes.txt
print(notes.exists())                  # False, until we write it
print(notes.suffix, notes.stem)        # .txt notes
```

`from pathlib import Path` is an **import**: it pulls a tool out of Python's standard library so you can use it. The Modules and Packages lesson explains imports properly.

### Reading and writing text

The standard way to open a file is with a `with` block. It opens the file, gives it to you as `f`, and guarantees the file is closed afterward, even if something goes wrong in the middle:

```python
from pathlib import Path

path = Path("data/notes.txt")

with open(path, "w", encoding="utf-8") as f:   # "w" = write (replaces the file)
    f.write("First line\n")
    f.write("Second line\n")

with open(path, "a", encoding="utf-8") as f:   # "a" = append to the end
    f.write("Third line\n")

with open(path, encoding="utf-8") as f:        # default mode is "r" = read
    for line in f:
        print(line.rstrip("\n"))
```

`"\n"` is the **newline** character that ends a line. `write()` doesn't add one for you, and lines you read keep theirs, which is why we strip it before printing. You can also read a whole file at once with `f.read()`, which returns one big string.

For quick one-off jobs, `Path` objects have shortcuts: `path.read_text(encoding="utf-8")` and `path.write_text("hello", encoding="utf-8")`.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Always pass encoding="utf-8"

Text files are stored as bytes, and an **encoding** is the rule for turning bytes into characters. UTF-8 handles every language and emoji, and it is what nearly all modern tools and APIs use. On some systems, especially Windows, Python's default is different, so a file that works on your laptop breaks on a classmate's. Writing `encoding="utf-8"` every time avoids the whole problem.

</div>

### What JSON looks like

Here is a JSON file of quiz questions:

```json
{
  "title": "Python basics",
  "questions": [
    {"prompt": "What does len('abc') return?", "answer": "3", "points": 1},
    {"prompt": "Is a tuple mutable?", "answer": "no", "points": 2}
  ],
  "shuffle": true,
  "time_limit": null
}
```

It looks almost exactly like Python. The mapping is:

| JSON | Python |
| --- | --- |
| object `{...}` | `dict` |
| array `[...]` | `list` |
| string `"..."` | `str` |
| number `3`, `2.5` | `int`, `float` |
| `true`, `false` | `True`, `False` |
| `null` | `None` |

The differences to watch for: JSON strings *must* use double quotes, JSON keys must be strings, and JSON doesn't allow trailing commas or comments. A single misplaced comma makes a whole file invalid.

### Loading and saving JSON

The `json` module converts between JSON text and Python objects. There are four functions, and the trailing "s" means "string":

```python
import json
from pathlib import Path

# From a file into Python
with open("data/quiz.json", encoding="utf-8") as f:
    quiz = json.load(f)

print(quiz["title"])
for q in quiz["questions"]:
    print(q["prompt"], "->", q["answer"])

# From Python into a file
results = {"player": "Ada", "score": 3, "answers": ["3", "no"]}
with open("data/results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

# Strings, which is what you get from and send to web APIs
text = json.dumps(results)       # Python -> JSON string
back = json.loads(text)          # JSON string -> Python
print(back == results)           # True
```

`indent=2` makes the file readable by humans. Without it, everything goes on one line, which is fine for machines.

Once loaded, JSON is *just dicts and lists*. Everything from the last lesson applies: index into lists, look up keys, loop with `.items()`, use `.get()` when a key might be missing.

This is the pattern you will use again and again with AI. You ask a model to reply in JSON, you get back a string, you call `json.loads()` on it, and then you work with ordinary Python data. When the model's reply isn't valid JSON, `json.loads()` raises `json.JSONDecodeError`. Catching that error is one of the first things you'll do in the Errors and Exceptions lesson.

### JSON Lines

One more format is worth knowing now because you'll meet it in evaluation and fine-tuning datasets. **JSON Lines** (`.jsonl`) puts one complete JSON object on each line:

```python
import json

examples = [
    {"input": "2 + 2", "expected": "4"},
    {"input": "capital of France", "expected": "Paris"},
]

with open("data/examples.jsonl", "w", encoding="utf-8") as f:
    for example in examples:
        f.write(json.dumps(example) + "\n")

with open("data/examples.jsonl", encoding="utf-8") as f:
    loaded = [json.loads(line) for line in f if line.strip()]
print(len(loaded))  # 2
```

JSON Lines lets you add records one at a time and read huge files line by line without loading everything into memory.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Watch [CS50P Lecture 6: File I/O](https://cs50.harvard.edu/python/weeks/6/). It covers `open()`, `with`, reading and writing, and CSV files.
   - The CSV part is a preview of the Project: Expense Tracker at the end of this section. Watch it now and you'll be ready.
1. Read [chapter 10, "Reading and Writing Files", of Automate the Boring Stuff](https://automatetheboringstuff.com/3e/chapter10.html), which explains paths and `pathlib` in more depth than this lesson.
   - Skip the section on the `shelve` module.
1. Read the "JSON" part of the "Versatile Plaintext Formats" section in [chapter 18, "CSV, JSON, and XML Files", of Automate the Boring Stuff](https://automatetheboringstuff.com/3e/chapter18.html). Skim the CSV section too, since you'll use it in the Project: Expense Tracker; skip XML.
1. Read the "Basic Usage" section of [the official json module docs](https://docs.python.org/3/library/json.html), focusing on the four functions above and the `indent` parameter. Then look at [json.org](https://www.json.org/json-en.html), which defines the whole format on one page.
1. Practice:
   - Do Lines of Code from [CS50P Problem Set 6](https://cs50.harvard.edu/python/psets/6/).
   - Save the conversation log you built in the previous lesson to `conversation.json` when the user quits, and load it again at startup if the file exists, so the conversation continues between runs. Open the file in VS Code and confirm it looks like the messages list.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Why use pathlib instead of building paths out of strings?](#paths)
- [Why open files with a with block?](#reading-and-writing-text)
- [Why should you always pass encoding="utf-8" when opening text files?](#reading-and-writing-text)
- [How do JSON's types map onto Python's types?](#what-json-looks-like)
- [What is the difference between json.load() and json.loads(), and when would you use each with an LLM?](#loading-and-saving-json)
- [What is JSON Lines, and why is it popular for datasets?](#json-lines)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The official tutorial's section on reading and writing files](https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files) covers file modes and methods concisely.
- [The pathlib docs](https://docs.python.org/3/library/pathlib.html) list every path operation, such as `glob()` for finding files that match a pattern.
- [JSON Lines](https://jsonlines.org/) is the short official description of the format.
