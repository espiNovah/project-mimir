### Introduction

Time to put the whole section together. You'll build a command-line tool that takes one or more city names and prints the current weather and a short forecast for each:

```text
$ uv run weather Lagos Oslo "Buenos Aires" Atlantisville
Lagos, Nigeria          30.5°C  wind 6.8 km/h   next 3 days: 30/26, 30/25, 29/25
Oslo, Norway             4.1°C  wind 12.2 km/h  next 3 days: 6/1, 5/0, 7/2
Buenos Aires, Argentina 18.9°C  wind 15.0 km/h  next 3 days: 22/14, 24/15, 21/13
Atlantisville: city not found
```

It uses [Open-Meteo](https://open-meteo.com/), a free weather API that needs no key, so you can focus on the code. Under the hood, each city takes two requests: one to the **geocoding** API to turn a name into latitude and longitude, and one to the **forecast** API. You'll run the lookups for all cities concurrently, handle every kind of failure gracefully, and prove your parsing code works with tests.

This is the same shape as a huge amount of AI engineering work: call an external service, turn messy JSON into clean data, handle failure, and do it concurrently. An agent's tool that "looks up the weather" would be a few lines wrapped around exactly this code.

### Before you start

- Create a new public GitHub repository named `mimir-weather-cli` and clone it.
- Inside it, run `uv init --package` so you get a `src/` layout, then `uv add httpx` and `uv add --dev pytest`.
- `uv init --package` creates a command named after the project. To run it as `uv run weather`, edit the `[project.scripts]` table in `pyproject.toml` to read `weather = "mimir_weather_cli:main"`.
- Read the [Open-Meteo forecast API docs](https://open-meteo.com/en/docs) and the [geocoding API docs](https://open-meteo.com/en/docs/geocoding-api). Use the interactive form on the forecast page to build a URL, then call it with `curl` to see the response.
- Try these two requests with `curl` and save each response into a `tests/fixtures/` folder as a JSON file. You'll use them as test data:
  - `https://geocoding-api.open-meteo.com/v1/search?name=Lagos&count=1`
  - `https://geocoding-api.open-meteo.com/v1/search?name=Atlantisville&count=1` (notice what's missing from this one)
  - A forecast call with `current=temperature_2m,wind_speed_10m`, `daily=temperature_2m_max,temperature_2m_min`, `timezone=auto` and `forecast_days=3`.

<div class="lesson-note lesson-note--tip" markdown="1">

#### Look at the shape before you write code

The forecast API returns daily data as parallel lists: `daily.time`, `daily.temperature_2m_max` and `daily.temperature_2m_min` are separate lists where index 0 is today, index 1 tomorrow and so on. Your parse function's job is to zip them back together into something sensible, such as a list of `DayForecast` dataclasses.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Structure your code so fetching and parsing are separate.
   - Write `parse_location(data: dict) -> Location | None` that turns a geocoding response into a dataclass with name, country, latitude and longitude, or returns `None` when the city wasn't found.
   - Write `parse_forecast(data: dict) -> Forecast` that turns a forecast response into a dataclass holding current temperature, wind speed and a list of daily highs and lows.
   - Neither parse function may make a network call.
1. Write async fetch functions that use a single shared `httpx.AsyncClient` with an explicit timeout, and pass query parameters with `params=` rather than building URLs by hand.
1. Accept any number of city names on the command line (use `argparse` from the standard library) and look them all up concurrently with `asyncio.gather` or `asyncio.TaskGroup`.
1. Handle failures gracefully. The program must never print a traceback for these cases, and one failing city must not stop the others from printing:
   - An unknown city prints "city not found."
   - No internet connection (test it with Wi-Fi off) prints a clear network error.
   - A timeout or a 4xx/5xx response from Open-Meteo prints a short error naming the city.
   - Running with no city names prints a usage message.
1. Add a `--days` option (1 to 7, default 3) that controls how many days of forecast are shown, and a `--units` option for `celsius` or `fahrenheit` (Open-Meteo has a `temperature_unit` parameter for this).
1. Write tests with pytest. At minimum:
   - `parse_location` with your saved Lagos fixture returns the right name and coordinates.
   - `parse_location` with your saved not-found fixture returns `None`.
   - `parse_forecast` with your saved forecast fixture returns the right number of days with the right highs and lows.
   - Your tests must pass without an internet connection. Run `uv run pytest` with Wi-Fi off to prove it.
1. Measure the benefit of concurrency. Add a `--sequential` flag that looks cities up one at a time, then time both modes for at least five cities and record the numbers in your README.
1. Push your project to GitHub with a README that explains what it does, how to install and run it, an example of its output, your timing measurements, and what you learned.

#### Extra credit

- Use `httpx.MockTransport` (see the [HTTPX transports docs](https://www.python-httpx.org/advanced/transports/)) to test your fetch functions too, including a simulated 500 error and a simulated timeout, all without touching the network.
- Add a semaphore so no more than three cities are looked up at once, and explain in your README why a real API might require this.
- Cache geocoding results in a local JSON file so repeat lookups of the same city skip the first request.
- When a city name is ambiguous (try "Springfield"), ask the geocoding API for several results and let the user pick, or show the country and region for each.

</div>

### Submitting your work

A strong submission is one a stranger can clone and run in under a minute. Your README should show the exact commands to install and run the tool, a copy of real output (including a "city not found" line), a screenshot or text capture of `uv run pytest` passing, and a small table comparing sequential and concurrent timings. Mention one thing that went wrong while you built it and how you figured it out. That kind of reflection is exactly what reviewers and employers look for.
