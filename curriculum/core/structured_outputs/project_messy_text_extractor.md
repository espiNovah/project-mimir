### Introduction

A huge share of real AI work is turning messy human text into clean data: invoices into spreadsheet rows, job postings into searchable fields, emails into tickets. In this project you will build a command-line tool that does exactly that for a type of document you choose. It will read pasted text, photos and PDFs, use a Pydantic schema with nested and optional fields, validate every output, retry with the validation error when something fails, and report its accuracy, with a confidence interval, on a test set of 20 real examples, for a Claude model and for a model from a second provider.

You will reuse this extractor in the next section, where it becomes the engine behind the LLM-Powered API project, so build it cleanly.

### Before you start

- Create a new GitHub repository called `mimir-messy-text-extractor` as a `uv` project. Add `anthropic`, `openai`, `pydantic` and `numpy`, plus `pytest` and `ruff` as dev dependencies (`uv add --dev pytest ruff`).
- Choose one document type that is genuinely messy and has information worth extracting. Some ideas:
  - Job postings (title, company, location, remote policy, salary range if given, required skills).
  - Apartment listings (rent, bedrooms, neighborhood, pets allowed, available date).
  - Event announcements or meeting emails (event name, date and time, location or link, attendees, action items).
  - Receipts or invoices pasted as text (vendor, date, line items, tax, total).
- Choose your second model, from a different provider. The free option is a local vision model through Ollama, such as `gemma3:4b`, called with the OpenAI SDK as in the "On other providers" sections of Getting Structured Output and Images, PDFs and Audio. A hosted model from OpenAI or another provider with an OpenAI-compatible API works too, if you have credit.
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
1. Make the extractor work on two providers: a Claude model and your second model. Keep one schema, one prompt and one retry loop, and put the provider-specific parts behind a `backend` argument: the API call, and a small function that converts your content blocks into that provider's format. For an OpenAI-style API, an image block becomes an `image_url` part with a base64 data URL; a PDF becomes a `file` part on OpenAI, while on Ollama, which takes no PDFs, you send the text from `pypdf` instead, as in Long Context and Context Engineering. Note in the README which PDF route each model used.
1. Handle failures with retries. When validation fails, send the model its previous output and the `ValidationError` message and ask it to fix the problem. Cap retries at three, and log each attempt (input ID, attempt number, error) to a file.
1. Build a test set of your 20 examples in `data/`, each with a hand-written expected JSON file.
1. Write `evaluate.py` that runs the extractor on all 20 examples, once per model, and reports for each model:
   - Per-field accuracy (what percentage of examples got each field exactly right, using simple normalization such as lowercasing and stripping whitespace).
   - Overall accuracy (the share of all fields across all examples that were correct).
   - How many examples needed at least one retry, and how many failed after all retries.
   - Overall accuracy separately for text inputs and for image or PDF inputs.
   - A 95% bootstrap confidence interval on overall accuracy, with a fixed seed, as in Eval Statistics. Resample the 20 examples, not individual fields, because fields from the same document succeed or fail together. With only 20 examples the interval will be wide; report it anyway.
   - Cost per document, from each response's usage fields ("$0.00 (local)" for Ollama), and average latency.
   - Finally, the difference in overall accuracy between the two models, with a paired bootstrap interval, as in Comparing two prompts in Eval Statistics. Both models saw the same 20 examples, so the comparison is paired.
1. Write pytest tests that run without calling any model: for your schema and validators (for example, check that an invalid salary range raises an error, and that a missing optional field becomes `None`), for your block helpers (the right block type and media type for a text, image and PDF input), and for the retry loop, using a fake client that returns one invalid output and then a valid one. Test the block conversion for your second provider too (an image block becomes a data URL with the right media type).
1. Look at every wrong field and group the errors into two or three categories, as in Error Analysis and Labeling (for example, "hallucinated a value that was not in the text" or "wrong date format"). Note which categories are shared by both models and which belong to one. Make one change to your prompt or schema to fix the biggest category, rerun the evaluation on your better model, and record the before and after numbers, with a paired bootstrap interval on the difference, as in Comparing two prompts in Eval Statistics.
1. Push your project to GitHub with a README that explains what it does, how to run it, and what you learned.

#### Evidence

- A GitHub Actions workflow runs `ruff check`, `ruff format --check` and `pytest` on every push, and the latest run on `main` passes. Show its status badge at the top of the README. The tests use fakes, so CI needs no API key. (Linting, Formatting and CI)
- An eval score: the output of `evaluate.py`, with overall accuracy reported in the shape from Reporting a score honestly, for example "overall field accuracy 87% (95% bootstrap CI 79% to 93%, n = 20)". Record the prompt version and model the score belongs to. Report one such line for each model, using the same metrics.
- A comparison table with one column per model: per-field accuracy, overall accuracy with its interval, text versus image or PDF accuracy, retries and failures, cost per document and average latency. Below it, the paired difference between the models with its interval, and two or three sentences on which model you'd use in the LLM-Powered API and why.
- The before-and-after numbers from your one improvement, with the paired difference and its interval, and the number of examples that got better and worse.
- The attempt log from one full evaluation run per model is committed, so a reader can see which inputs needed retries and why.

#### Extra credit

- Add a command-line interface so you can run `uv run extract path/to/file.txt` and get JSON on standard output.
- Add the [capable model](#/models) or a third provider as another column, and compare accuracy against cost per document.
- Add a confidence or `source_quote` field for each extracted value, and check whether low-confidence fields are more often wrong.

</div>

### Submitting your work

A strong README shows your schema, a sample input next to its extracted JSON (include one image or PDF input), the accuracy table for both models (per field and overall), the before-and-after numbers from your one improvement, and an honest list of the error categories you could not fix. Your tests should pass with one command, and the evaluation should be reproducible by anyone with an API key.
