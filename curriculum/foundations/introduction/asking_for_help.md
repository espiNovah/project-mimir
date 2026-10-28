### Introduction

Every programmer gets stuck, every day. What separates people who make progress from people who stay stuck is often just how well they ask for help. A good question gets a useful answer in minutes. A vague one gets ignored, or gets an answer to the wrong problem.

You now have two kinds of helpers: people (in forums, chat communities and study groups) and AI models. Both work far better when you give them a clear, complete question. This lesson teaches you how to write one, and how to decide which helper to ask.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What to try before you ask for help.
- The parts of a good question.
- What the XY problem is and how to avoid it.
- How to share code and error messages properly.
- When to ask an AI and when to ask a person.

### Before you ask

Asking for help is not a last resort, but it works best after you've done a little work yourself. Before asking, try these:

1. **Read the error message, slowly, all of it.** Error messages usually say what went wrong and where. The most useful line is often the last one.
1. **Search for the exact error text.** Copy the key part of the message (leave out your own file names) into a search engine. Someone has almost certainly hit it before.
1. **Check the official documentation** for the tool or function you're using.
1. **Make the problem smaller.** Remove everything that isn't needed to show the problem. Often you'll find the bug while doing this.

This process takes about 20 minutes. If it doesn't solve the problem, you'll still have a much better question to ask.

### The parts of a good question

A good question gives the helper everything they need without making them ask follow-up questions. It has five parts:

- **What you're trying to do**, in one or two sentences. The goal, not just the step.
- **What you did**: the exact command or the smallest piece of code that shows the problem.
- **What you expected** to happen.
- **What actually happened**, including the full error message, copied as text.
- **What you already tried**, so nobody suggests it again.

Here is a bad question:

> My Python doesn't work. Help?

And a good one:

> I'm trying to run my first Python script on macOS. In the terminal I typed `python hello.py` from the folder that contains the file. I expected it to print "Hello", but I got `zsh: command not found: python`. I installed Python from python.org and `python3 --version` prints `Python 3.13.1`. I tried closing and reopening the terminal. Should I be typing `python3` instead?

The second question takes a minute longer to write, and it will probably be answered in one reply.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Share text, not screenshots

When you share code or an error, paste it as text in a code block, not as a screenshot or a phone photo. Text can be searched, copied and run; a picture can't. Most forums and chat apps format code when you put a line of three backticks above it and another below it. And never paste API keys, passwords or other secrets. Replace them with something like `YOUR_KEY_HERE`.

</div>

### The XY problem

The **XY problem** happens when you want to do X, decide that Y is the way to do it, get stuck on Y, and ask about Y without ever mentioning X. Your helpers then spend time on Y, which may be the wrong approach entirely.

Example:

- **The Y question:** "How do I get the last three characters of a filename in Python?"
- **The real goal, X:** "I want to find all the `.txt` files in a folder."

The Y question has an answer, but it's a fragile one: it breaks on `.json` files or on a file named `notes.txt.bak`. If you had asked about X, someone would tell you that Python has tools built for exactly that. Always include your real goal, even when you think you know the right approach. That's why "what you're trying to do" is the first part of a good question.

### Asking an AI versus asking a person

AI models are excellent for many beginner questions. They're available any time, they never get impatient, and they can explain the same thing five different ways. Use them to:

- Explain an error message or an unfamiliar term.
- Explain what a piece of code does, line by line.
- Give you a hint, not a solution, when you're stuck on a project.

But AI models can be confidently wrong. They sometimes invent functions that don't exist or describe old versions of a tool. (You'll learn why in the "Why Models Hallucinate" lesson.) So check what they tell you against the official docs, and run the code to see if it works.

Ask a person when:

- The AI's answers keep going in circles or contradict each other.
- The question is about judgment or experience, such as "Is this a reasonable way to structure my project?"
- You want feedback on work you've finished.

The same five-part question works for both. A clear question gets better answers from a model too, which is a preview of the prompting skills you'll learn in the AI Engineering Core path.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read The Odin Project's lesson on [Asking for Help](https://www.theodinproject.com/lessons/foundations-asking-for-help), which goes into more depth on asking good questions in programming communities.
   - Read the whole lesson. Note anything that's specific to their community; the rest applies everywhere.
1. Read [the XY problem](https://xyproblem.info/), a short page that explains the trap in a few minutes.
1. Read Stack Overflow's guide on [how to ask a good question](https://stackoverflow.com/help/how-to-ask). It's the standard reference for writing questions strangers can answer.
   - Pay particular attention to the section on creating a minimal, reproducible example.
1. Practice rewriting a question.
   - Think of something you were stuck on recently. It doesn't have to be about code: setting up a printer, a spreadsheet formula, anything. Write the question the way you first would have asked it. Then rewrite it using the five parts from this lesson, and make sure your real goal (the X) is stated. Save both versions; you'll use them in the next project.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [How to ask good questions](https://jvns.ca/blog/good-questions/) by Julia Evans is a friendly, practical essay on asking questions at work, with lots of examples.
