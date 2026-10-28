### Introduction

A huge share of real AI work is turning messy human text into clean data: invoices into spreadsheet rows, job postings into searchable fields, emails into tickets. In this project you will build a command-line tool that does exactly that for a type of document you choose. It will use a Pydantic schema with nested and optional fields, validate every output, retry with the validation error when something fails, and report its accuracy on a test set of 20 real examples.

You will reuse this extractor in the next section, where it becomes the engine behind the LLM-Powered API project, so build it cleanly.

### Before you start

- Create a new GitHub repository called `mimir-messy-text-extractor` as a `uv` project. Add `anthropic` and `pydantic`, plus `pytest` as a dev dependency (`uv add --dev pytest`).
- Choose one document type that is genuinely messy and has information worth extracting. Some ideas:
  - Job postings (title, company, location, remote policy, salary range if given, required skills).
  - Apartment listings (rent, bedrooms, neighborhood, pets allowed, available date).
  - Event announcements or meeting emails (event name, date and time, location or link, attendees, action items).
  - Receipts or invoices pasted as text (vendor, date, line items, tax, total).
- Collect 20 real examples. Copy them from public websites or your own inbox, and remove any personal information about other people before you commit them.

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
1. Write an `extract(text: str) -> YourModel` function that calls a model and returns a validated object. Use native structured outputs or a library such as Instructor; explain your choice in the README.
1. Handle failures with retries. When validation fails, send the model its previous output and the `ValidationError` message and ask it to fix the problem. Cap retries at three, and log each attempt (input ID, attempt number, error) to a file.
1. Build a test set of your 20 examples in `data/`, each with a hand-written expected JSON file.
1. Write `evaluate.py` that runs the extractor on all 20 examples and reports:
   - Per-field accuracy (what percentage of examples got each field exactly right, using simple normalization such as lowercasing and stripping whitespace).
   - Overall accuracy (the share of all fields across all examples that were correct).
   - How many examples needed at least one retry, and how many failed after all retries.
1. Write pytest tests for your schema and validators that run without calling any model (for example, check that an invalid salary range raises an error, and that a missing optional field becomes `None`).
1. Look at every wrong field and group the errors into two or three categories (for example, "hallucinated a value that was not in the text" or "wrong date format"). Make one change to your prompt or schema to fix the biggest category, rerun the evaluation, and record the before and after numbers.
1. Push your project to GitHub with a README that explains what it does, how to run it, and what you learned.

#### Extra credit

- Add a command-line interface so you can run `uv run extract path/to/file.txt` and get JSON on standard output.
- Compare the [cheap model](#/models) with the capable one on accuracy and cost per document.
- Add a confidence or `source_quote` field for each extracted value, and check whether low-confidence fields are more often wrong.

</div>

### Submitting your work

A strong README shows your schema, a sample input next to its extracted JSON, the accuracy table (per field and overall), the before-and-after numbers from your one improvement, and an honest list of the error categories you could not fix. Your tests should pass with one command, and the evaluation should be reproducible by anyone with an API key.
