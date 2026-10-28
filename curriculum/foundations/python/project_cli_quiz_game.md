### Introduction

Time to put the first half of this section together. You'll build a quiz game that runs in the terminal. It loads its questions from a JSON file, asks them in a random order, checks the player's answers, keeps score, and offers to play again.

It is a small program, but it uses everything you've learned so far: variables and strings, conditionals and loops, functions, lists and dicts, and files and JSON. It also has the same basic shape as many AI tools you'll build later: load data from a file, loop over items, compare an answer to an expected answer, and report a score. That last part is, in miniature, what an evaluation script does.

### Before you start

1. Create a new project with uv and a GitHub repository for it named `mimir-quiz-game`. Refer back to Project: Hello, uv and Project: Hello, GitHub if you need a reminder.

   ```bash
   uv init mimir-quiz-game
   cd mimir-quiz-game
   ```

1. Create a file called `questions.json` in the project folder. Start with this, then add at least seven more questions of your own on any topic you like:

   ```json
   [
     {
       "question": "What does len('agent') return?",
       "answer": "5"
     },
     {
       "question": "Which collection type stores key-value pairs?",
       "answer": "dict"
     },
     {
       "question": "What keyword sends a value back from a function?",
       "answer": "return"
     }
   ]
   ```

1. You'll need one new tool. The `random` module, part of Python's standard library, can shuffle a list in place:

   ```python
   import random

   items = [1, 2, 3, 4]
   random.shuffle(items)
   print(items)  # for example [3, 1, 4, 2]
   ```

   Shuffle a *copy* of your questions list (remember the shared-references section of the Lists, Dicts, Sets and Tuples lesson) if you want to keep the original order around.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Plan before you code

Before writing any Python, write out the steps of one game in plain English, in a comment at the top of your file or on paper. For example: load questions, shuffle them, set score to zero, for each question ask and compare, print the final score, ask whether to play again. Each step will become roughly one function or one loop.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Load the questions from `questions.json` in a function, for example `load_questions(path)`, that returns a list of dicts. The program must not have questions hard-coded in the Python file.
1. Ask every question once per game, in a random order that changes between games.
1. Read the player's answer with `input()` and compare it to the correct answer in a forgiving way: ignore uppercase versus lowercase and extra spaces at either end, so `" Dict "` counts as correct for `"dict"`.
1. After each question, tell the player whether they were right, and show the correct answer when they were wrong.
1. At the end of each game, print the score as both a count and a percentage, such as `You scored 7/10 (70%)`.
1. After each game, ask whether the player wants to play again. Accept `y`/`yes` and `n`/`no` in any case. If they type anything else, ask again rather than guessing.
1. Organize the code into functions with clear names and docstrings, with a `main()` function and an `if __name__ == "__main__":` block at the bottom. At least one function must `return` a value that another function uses, rather than printing it.
1. Make the game run with `uv run main.py` (or whatever you name your file) from a fresh clone of your repo.
1. Push your project to GitHub with a README that explains what it does, how to run it, how to add your own questions, and what you learned. Include the evidence listed below.

#### Evidence

You'll start writing automated tests in Testing with pytest later in this section. For now, prove the game works with real output copied from your terminal into fenced code blocks in the README:

- A transcript of one complete game, from the first question to the final score line, that includes at least one right answer, one wrong answer showing the correct answer, and one right answer typed with different capitals or extra spaces.
- A transcript of the play-again prompt rejecting an unexpected reply (such as `maybe`), asking again, and then starting a second game whose questions come in a different order.
- A short REPL session that shows your answer-checking function returning a value rather than printing it. Start the REPL in the project folder with `uv run python`, then import and call your function, for example `from main import is_correct` and `is_correct(" Dict ", "dict")` (use your own file and function names). This works because of your `if __name__ == "__main__":` block, which stops the game from starting on import.
- The repo link, and a fresh clone that runs with the single command in your README.

#### Extra credit

- Support multiple-choice questions: if a question has a `"choices"` list in the JSON, print the choices with letters (A, B, C) and accept the letter as an answer.
- Let a question have more than one accepted answer, such as `"answers": ["dict", "dictionary"]`.
- Save a high-score table to `scores.json` (player name, score, date) and show the top five at the end of each game.
- Let the player choose a different question file, or a number of questions per game, when the game starts.

</div>

### Submitting your work

A strong submission is one a stranger could clone and play within a minute. Its README says exactly which command to run, shows the expected JSON format for questions, and includes a real terminal transcript. Its code reads top to bottom like the plan you wrote: a handful of small, well-named functions, with no question text inside the Python file.

Check before you submit: does your game crash if the player just presses Enter? Does it handle a question file with a single question? Fixing those small cases is good practice for the next lesson, Errors and Exceptions, where you'll also make the game survive a missing or broken `questions.json`.
