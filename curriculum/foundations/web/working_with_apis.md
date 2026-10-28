### Introduction

An **API** (Application Programming Interface) is a door into someone else's software that's designed for programs rather than people. A website gives you a page to look at; an API gives you data your code can use. When people say "REST API" or "web API," they usually mean a set of URLs you can send HTTP requests to, which reply with JSON.

In the last lesson you made requests by hand with `curl`. Now you'll make them from Python, turn the JSON into dictionaries you can work with, and, just as important, handle the many ways a request can fail. The model SDKs you'll use later are built on exactly these ideas, so when something goes wrong inside one of them, you'll know what is happening underneath.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What a REST API is and how to read its documentation.
- How to make GET and POST requests from Python with HTTPX.
- How to send query parameters, headers and JSON bodies.
- How to turn a JSON response into Python data.
- The failures every API call can hit: timeouts, network errors and error status codes.
- How to keep API code tidy by separating fetching from parsing.

### Installing HTTPX

Python's standard library can make HTTP requests, but it's clumsy. Almost everyone uses a third-party library. We'll use [HTTPX](https://www.python-httpx.org/), a modern library that supports both regular and async code (which you'll need in the Async Basics lesson). You may also see `requests` in older tutorials; the code looks nearly identical.

Create a scratch project and add HTTPX:

```bash
uv init api-practice
cd api-practice
uv add httpx
```

### Your first request from Python

Put this in `main.py` and run it with `uv run main.py`:

```python
import httpx

response = httpx.get("https://api.github.com/users/octocat")

print(response.status_code)               # 200
print(response.headers["content-type"])   # application/json; charset=utf-8

user = response.json()                    # parse the JSON body into a dict
print(user["name"], "has", user["public_repos"], "public repos")
```

`httpx.get()` sends a GET request and returns a `Response` object. `response.json()` parses the body into ordinary Python dicts and lists, exactly like `json.loads()` did in the Files and JSON lesson. From there it's just data.

### Parameters, headers and bodies

Never build query strings by gluing strings together. Pass a dict to `params` and HTTPX will encode it correctly:

```python
import httpx

response = httpx.get(
    "https://api.github.com/users/octocat/repos",
    params={"sort": "updated", "per_page": 3},
    headers={"Accept": "application/vnd.github+json"},
)
for repo in response.json():
    print(repo["name"], "-", repo["stargazers_count"], "stars")
```

The `headers` dict adds request headers. APIs use headers for things like the format you want back and, most often, your credentials, which you'll handle properly in the next lesson.

To send data, use `POST` with a JSON body. Pass a dict to `json=` and HTTPX converts it to JSON and sets `Content-Type: application/json` for you. The free service httpbin echoes your request back, so you can see what was sent:

```python
import httpx

response = httpx.post("https://httpbin.org/post", json={"city": "Lagos", "days": 3})
print(response.json()["json"])   # {'city': 'Lagos', 'days': 3}
```

Keep this shape in mind. A call to a language model API is a POST request whose JSON body contains a model name and a list of messages.

### When things go wrong

On your laptop, with a good connection and a valid request, API calls just work. In real software, they fail all the time. There are three kinds of failure to plan for:

1. **The server answers with an error status.** HTTPX does *not* raise an exception for a 404 or 500 by default; you get a `Response` with that status code. Call `response.raise_for_status()` to turn any 4xx or 5xx into an `httpx.HTTPStatusError`.
1. **The server doesn't answer in time.** HTTPX waits 5 seconds by default, then raises `httpx.TimeoutException`. Set your own limit with `timeout=`.
1. **The network fails entirely.** No internet, a typo in the hostname, a refused connection. HTTPX raises `httpx.ConnectError` or another subclass of `httpx.RequestError`.

Here's a function that handles all three and gives its caller a clear, specific error:

```python
import httpx


class GitHubError(Exception):
    """Raised when we can't get data from GitHub."""


def fetch_user(username: str) -> dict:
    try:
        response = httpx.get(f"https://api.github.com/users/{username}", timeout=10)
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise GitHubError(f"No GitHub user called {username!r}") from e
        raise GitHubError(f"GitHub returned {e.response.status_code}") from e
    except httpx.RequestError as e:
        raise GitHubError(f"Could not reach GitHub: {e}") from e
    return response.json()


if __name__ == "__main__":
    try:
        print(fetch_user("octocat")["name"])
        print(fetch_user("this-user-should-not-exist-12345")["name"])
    except GitHubError as e:
        print("Error:", e)
```

Notice the pattern from the Errors and Exceptions lesson: catch the low-level library error, then raise your own error with a message that makes sense to the rest of your program. Code that calls `fetch_user` only has to know about `GitHubError`, not every exception HTTPX can raise.

<div class="lesson-note lesson-note--warning" markdown="1">

#### Always set a timeout you've thought about

The right timeout depends on the API. A weather lookup should take well under a second, so 10 seconds is generous. A language model writing a long answer can legitimately take minutes. Pick a number on purpose rather than accepting whatever the default happens to be.

</div>

### Separating fetching from parsing

API responses often contain far more than you need. Open-Meteo's forecast, for example, returns metadata, units and parallel lists of times and values. The cleanest approach is to split your code into two kinds of function:

- A **fetch** function that does the HTTP call and returns the raw JSON (as a dict).
- A **parse** function that takes that dict and returns exactly the data your program cares about, in a shape you chose, such as a dataclass.

The parse function never touches the network, so you can test it with pytest by handing it a saved JSON example. That makes your tests fast, free and reliable, and it's the approach you'll use in the Weather CLI project.

```python
from dataclasses import dataclass


@dataclass
class Repo:
    name: str
    stars: int


def parse_repos(data: list[dict]) -> list[Repo]:
    return [Repo(name=item["name"], stars=item["stargazers_count"]) for item in data]


def test_parse_repos():
    sample = [{"name": "hello-world", "stargazers_count": 42, "fork": False}]
    assert parse_repos(sample) == [Repo(name="hello-world", stars=42)]
```

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Work through the [HTTPX quickstart](https://www.python-httpx.org/quickstart/), typing each example into a file and running it rather than just reading.
   - Focus on "Making a request," "Passing Parameters in URLs," "JSON Response Content," "Custom Headers," "Sending JSON Encoded Data," "Response Status Codes" and "Timeouts."
1. Skim the [HTTPX exceptions page](https://www.python-httpx.org/exceptions/) and find where `TimeoutException`, `ConnectError` and `HTTPStatusError` sit in the exception hierarchy. Understanding the tree tells you which `except` clause will catch what.
1. Read GitHub's [Getting started with the REST API](https://docs.github.com/en/rest/using-the-rest-api/getting-started-with-the-rest-api) as an example of what good API documentation looks like.
   - Pay attention to how they describe authentication, headers and pagination. You'll read docs like this constantly.
1. Build a small `repo_report.py` script:
   - It takes a GitHub username as a command-line argument (`sys.argv[1]` is fine for now).
   - It fetches that user's public repositories and prints the five with the most stars, with their star counts.
   - It prints a friendly message, not a traceback, when the user doesn't exist, when you're offline (turn off Wi-Fi to test it), and when GitHub returns any other error.
   - Write a `parse_repos` function and at least two pytest tests for it, using a small JSON sample saved in your `tests/` folder.
   - Commit it to your practice repository.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- GitHub's [rate limits for the REST API](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api) explains a real-world rate limiting scheme and the headers that report it.
- The [HTTPX transports page](https://www.python-httpx.org/advanced/transports/) covers `MockTransport`, which lets you test code that makes HTTP calls without touching the network.
