### Introduction

Every project so far has told you what to build. The Weather CLI named the API, the functions, the options and even the test cases. This one doesn't. You'll pick a public API, decide what useful tool to build on top of it, design the interface, and build it to the standard you've learned: typed, tested, linted and checked by CI on every push.

That shift is the point. In a job, nobody hands you a list of function signatures. You get a fuzzy goal ("can we get a daily summary of new earthquakes near our offices?") and you turn it into a design, a plan and working code. The same will be true when you build agents: an agent's tools are small programs that call APIs and return clean results, and designing those tools well is a large part of the job. This project is your first rehearsal for both.

You've already learned everything you need. If you get stuck, the answer is in a lesson you've done, and the requirements below say which one. You choose how to put the pieces together.

### Before you start

#### Choose an API

Pick a public HTTP API that returns JSON. Good choices are free, well documented and stable, and either need no key or give you a free key without a credit card. A few that work well:

- [Open Library](https://openlibrary.org/developers/api): books, authors and covers. No key.
- [USGS Earthquake API](https://earthquake.usgs.gov/fdsnws/event/1/): every recorded earthquake, searchable by time, place and magnitude. No key.
- [Frankfurter](https://frankfurter.dev/): current and historical currency exchange rates. No key.
- [PokéAPI](https://pokeapi.co/docs/v2): Pokémon, moves and types, with deeply nested JSON that's good parsing practice. No key.
- [The Hacker News API](https://github.com/HackerNews/API): stories and comments, one request per item, which makes concurrency worthwhile. No key.
- [TVmaze](https://www.tvmaze.com/api): TV shows, episodes and schedules. No key.
- [The GitHub REST API](https://docs.github.com/en/rest): repos, issues and releases. Works without a key at a low [rate limit](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api), and with a free personal access token at a much higher one.
- [NASA's open APIs](https://api.nasa.gov/): images, asteroids and more. Needs a free key, which is good practice for API Keys and Secrets.

The [public-apis list](https://github.com/public-apis/public-apis) has hundreds more. Before you commit to one, call it with `curl`, read its terms of use and rate limits, and make sure it's still alive. Don't use Open-Meteo, which you used for the Weather CLI, and don't scrape websites that don't offer an API.

#### Design it on paper first

Before writing any Python, write a short `DESIGN.md` in a new repository named `mimir-<your-tool-name>`. Answer these questions in plain language:

1. **Who is it for, and what problem does it solve?** "A tool that shows the API's data" isn't a problem. "I want to know which books by an author I haven't read are available as e-books" is.
1. **What does using it look like?** Write three to five example commands with the output you expect, as you'd want them to appear in your README. This is your interface, and it's much cheaper to change now than after you've written the code.
1. **Which endpoints will you call, with which parameters?** Paste a trimmed sample response for each.
1. **What can go wrong?** List every failure you can think of: no network, a timeout, a 404, a 429 rate limit, an empty result, a bad date or number from the user, a missing API key. For each one, write what the user should see and which exit code the tool should return.
1. **What will you test, and how will you test it without the network?**

Commit `DESIGN.md` before you write any code. It's fine, and normal, for the design to change as you build. When it does, update the file and say what changed and why in your README.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Keep the scope small

Aim for a tool you can finish in one to two weeks. Two or three subcommands that work well, fail gracefully and are tested beat ten that half work. Write your extra ideas down under a "Next steps" heading in your README and come back to them once the requirements are done.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

There is no step-by-step guide for this project. These are the requirements your finished tool must meet; how you meet them is up to you.

#### The interface

1. Set the project up with `uv init --package`, and expose your tool as a command in `[project.scripts]` so it runs as `uv run <your-tool>`, as you did in the Project: Weather CLI.
1. Build the interface with `argparse`, with at least two subcommands or two meaningfully different modes, and options with sensible defaults, `type=` conversion and `choices=` where they fit. `--help` must explain every subcommand and option well enough that a stranger can use the tool without your README. (Command-Line Apps)
1. At least one feature must involve dates or times, for example filtering by a date range, showing how long ago something happened or grouping results by week. Parse dates from the user with `datetime`, and handle time zones correctly where the API returns timestamps. (Command-Line Apps)
1. The tool must do real work on the data, not just print the API's response. Combine several requests, filter, sort, count, compare or summarize, or save results to a file the tool reads back later. (Pythonic Python, Files and JSON)

#### The code

1. Call the API with `httpx`, with an explicit timeout and query parameters passed with `params=`. If your tool makes more than a handful of independent requests, make them concurrently, and limit concurrency if the API has a rate limit. (Working with APIs, Async Basics)
1. Keep fetching, parsing and presentation separate. Parse functions take a decoded JSON response and return your own dataclasses, and never make a network call. Printing and argument parsing live in a thin layer at the edge, such as `main(argv=None)`. (Working with APIs, Classes and Objects)
1. Handle every failure from your design's "What can go wrong?" list. The tool must never show a traceback for an expected failure. Print a short, specific message to standard error and exit with a non-zero code. Document your exit codes in the README. (Errors and Exceptions, Command-Line Apps)
1. If the API needs a key, read it from an environment variable, load it from a `.env` file that is in `.gitignore`, and commit a `.env.example` with a placeholder. A missing key must produce a helpful message, not a traceback. (API Keys and Secrets)
1. Add a `-v`/`--verbose` flag that turns on `DEBUG` logging, including each request's URL, status code and duration. Never log an API key. (Debugging and Logging)
1. Annotate every function, and make `uv run mypy .` pass. (Type Hints)

#### The tests

1. Write at least eight meaningful pytest tests. None of them may touch the network: `uv run pytest` must pass with Wi-Fi turned off. (Testing with pytest)
1. Test your parse functions against real responses you saved as JSON fixtures, including at least one awkward case, such as an empty result or a missing optional field.
1. Test at least two failure paths, such as a 404, a 429 or a timeout. Simulate them with `httpx.MockTransport` (see [the HTTPX transports docs](https://www.python-httpx.org/advanced/transports/)), or by passing a fake client into your fetch functions, or with `monkeypatch`, as in the Testing with pytest lesson.
1. Test the command layer: call `main([...])` with an argument list and check the exit code it returns. To check what it printed too, use pytest's `capsys` fixture, described in [the pytest guide to capturing output](https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html).

#### The write-up

1. Push your project to GitHub with a README that explains what the tool does and who it's for, how to install and run it (with an example of each subcommand), how to run the tests, the exit codes, and what you learned.
1. In the README, describe one design decision you changed while building, and one bug you found and how you tracked it down.

#### Evidence

- A GitHub Actions workflow in `.github/workflows/` runs `ruff check`, `ruff format --check` and `pytest` on every push, and the latest run on `main` passes. Show its status badge at the top of the README. (Linting, Formatting and CI)
- The README includes a real terminal transcript of the tool working, and of at least one failure, such as a not-found result or a network error, followed by `echo $?` showing the exit code.
- The README includes the output of `uv run pytest` run with your network turned off, showing all tests passing.

#### Extra credit

- Publish your tool so anyone can install it with `uv tool install git+https://github.com/<you>/<repo>`, and show that command in your README.
- Cache responses on disk with an expiry time, and add a `--no-cache` flag. Test that a fresh cache entry skips the network and an expired one doesn't.
- Retry `429` and `5xx` responses with exponential backoff, respecting a `Retry-After` header if the API sends one, and test it with a `MockTransport` that fails twice before succeeding.
- Add a `--json` option that prints machine-readable output instead of a table, so other programs (or, later, an agent) can use your tool.
- Ask someone who has never seen your tool to use it with only `--help`, without your help. Write down where they got stuck and fix it.

</div>

### Submitting your work

A strong submission reads like a small, real product. A reviewer should understand in the first screen of your README what the tool is for, see the green CI badge, and find a copy-pasteable command that works. They should be able to clone the repo, run `uv run pytest` with no network and no API key, and see everything pass.

Your `DESIGN.md` and README together tell the story of how the tool came to be: what you planned, what changed and why. That story matters as much as the code. When you apply for jobs, "I designed and built a tested CLI on the USGS API, and here's how my plan changed when I hit its rate limit" is a far better interview answer than "I followed a tutorial". Keep this repo. Later in the curriculum you'll see how a function like your fetch-and-parse layer becomes a tool that an agent can call.
