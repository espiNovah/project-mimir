### Introduction

A huge share of real AI work is turning messy human text into clean data: invoices into spreadsheet rows, job postings into searchable fields, emails into tickets. In this project you will build a command-line tool that does exactly that for a type of document you choose. It will read pasted text, photos and PDFs, use a Pydantic schema with nested and optional fields, validate every output, retry with the validation error when something fails, and report its accuracy, with a confidence interval, on a test set of 20 real examples.

You will reuse this extractor in the next section, where it becomes the engine behind the LLM-Powered API project, so build it cleanly.

### Before you start

- Create a new GitHub repository called `mimir-messy-text-extractor` as a `uv` project. Add `anthropic`, `pydantic` and `numpy`, plus `pytest` and `ruff` as dev dependencies (`uv add --dev pytest ruff`).
- Choose one document type that is genuinely messy and has information worth extracting. Some ideas:
  - Job postings (title, company, location, remote policy, salary range if given, required skills).
  - Apartment listings (rent, bedrooms, neighborhood, pets allowed, available date).
  - Event announcements or meeting emails (event name, date and time, location or link, attendees, action items).
  - Receipts or invoices pasted as text (vendor, date, line items, tax, total).
- Collect 20 real examples. Copy them from public websites or your own inbox, and remove any personal information about other people before you commit them. At least 5 of the 20 must be images or PDFs, such as a phone photo of a receipt, a screenshot of a listing or a PDF invoice, as in Images, PDFs and Audio. Choose a document type where that's natural.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Label before you look

Write the correct answer for each example by hand, in `data/expected/`, before you run your extractor on it. If you label after seeing the model's output, you will unconsciously agree with it and your accuracy number will be inflated.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Define a Pydantic schema for your document type in `extractor/schema.py`. It must include:
   - At least one nested model (for example, `salary: SalaryRange` or `items: list[LineItem]`).
   - At least two optional fields for information that is often missing.
   - At least one constrained field (a `Literal`, an enum or a numeric bound).
   - At least one custom validator for a rule the schema alone cannot express (for example, "maximum salary must be at least the minimum").
1. Write an `extract(content: list[dict]) -> YourModel` function that takes content blocks, calls a model and returns a validated object, as in the "One schema, many inputs" tip in Images, PDFs and Audio. Add small helpers that turn a text string, an image file and a PDF file into blocks, and an `extract_text(text: str)` wrapper for the common case. Use native structured outputs or a library such as Instructor; explain your choice in the README.
1. Handle failures with retries. When validation fails, send the model its previous output and the `ValidationError` message and ask it to fix the problem. Cap retries at three, and log each attempt (input ID, attempt number, error) to a file.
1. Build a test set of your 20 examples in `data/`, each with a hand-written expected JSON file.
1. Write `evaluate.py` that runs the extractor on all 20 examples and reports:
   - Per-field accuracy (what percentage of examples got each field exactly right, using simple normalization such as lowercasing and stripping whitespace).
   - Overall accuracy (the share of all fields across all examples that were correct).
   - How many examples needed at least one retry, and how many failed after all retries.
   - Overall accuracy separately for text inputs and for image or PDF inputs.
   - A 95% bootstrap confidence interval on overall accuracy, with a fixed seed, as in Eval Statistics. Resample the 20 examples, not individual fields, because fields from the same document succeed or fail together. With only 20 examples the interval will be wide; report it anyway.
1. Write pytest tests that run without calling any model: for your schema and validators (for example, check that an invalid salary range raises an error, and that a missing optional field becomes `None`), for your block helpers (the right block type and media type for a text, image and PDF input), and for the retry loop, using a fake client that returns one invalid output and then a valid one.
1. Look at every wrong field and group the errors into two or three categories, as in Error Analysis and Labeling (for example, "hallucinated a value that was not in the text" or "wrong date format"). Make one change to your prompt or schema to fix the biggest category, rerun the evaluation, and record the before and after numbers, with a paired bootstrap interval on the difference, as in Comparing two prompts in Eval Statistics.
1. Push your project to GitHub with a README that explains what it does, how to run it, and what you learned.

#### Evidence

- A GitHub Actions workflow runs `ruff check`, `ruff format --check` and `pytest` on every push, and the latest run on `main` passes. Show its status badge at the top of the README. The tests use fakes, so CI needs no API key. (Linting, Formatting and CI)
- An eval score: the output of `evaluate.py`, with overall accuracy reported in the shape from Reporting a score honestly, for example "overall field accuracy 87% (95% bootstrap CI 79% to 93%, n = 20)". Record the prompt version and model the score belongs to.
- The before-and-after numbers from your one improvement, with the paired difference and its interval, and the number of examples that got better and worse.
- The attempt log from one full evaluation run is committed, so a reader can see which inputs needed retries and why.

#### Extra credit

- Add a command-line interface so you can run `uv run extract path/to/file.txt` and get JSON on standard output.
- Compare the [cheap model](#/models) with the capable one on accuracy and cost per document.
- Add a confidence or `source_quote` field for each extracted value, and check whether low-confidence fields are more often wrong.

</div>

### Submitting your work

A strong README shows your schema, a sample input next to its extracted JSON (include one image or PDF input), the accuracy table (per field and overall), the before-and-after numbers from your one improvement, and an honest list of the error categories you could not fix. Your tests should pass with one command, and the evaluation should be reproducible by anyone with an API key.
