### Introduction

Most useful APIs want to know who you are. They identify you with an **API key**: a long, random string that works like a password for your program. Model providers bill you per request, so an API key is effectively a credit card number. If it leaks, someone else can run up your bill, and leaked keys are found and abused within minutes of being pushed to a public GitHub repository. Automated bots scan for them constantly.

This lesson teaches the habits professionals use so that keys never end up in code, in Git history or in screenshots. You'll need these habits in the very next section, when you get your first model API key.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- What API keys and tokens are and how APIs receive them.
- Why secrets must never be written in your source code.
- Environment variables and how to read them from Python.
- Using a `.env` file with python-dotenv.
- Keeping secrets out of Git with `.gitignore`.
- What to do if you leak a key anyway.

### How APIs receive keys

An API key is usually sent in a request header. Different APIs use different header names, so always check the docs:

```text
Authorization: Bearer ghp_abc123...     # the most common style (GitHub, OpenAI, Anthropic and many others)
x-api-key: abc123...                    # some APIs use a custom header instead
```

The word "Bearer" means "whoever bears (holds) this token is allowed in." That's exactly why leaking one is so dangerous: the API has no way to tell your program apart from a thief's.

You'll sometimes see the related term **token**, as in GitHub's "personal access token." For our purposes, tokens and keys are the same kind of thing: secret strings that grant access. (Don't confuse these with the *tokens* language models read, which you'll learn about in the next section. Same word, different meaning.)

### Never put secrets in code

This is the mistake every beginner is tempted to make:

```python
# DON'T DO THIS
API_KEY = "ghp_abc123realkeyhere"
```

It works, and that's the problem. The moment you commit this file, the key is in your Git history forever, even if you delete the line in the next commit. Push it, and it's public. Paste the file into a chat to ask for help, and it's been shared.

Instead, your code should read the key from its surroundings at runtime. The standard place to put it is an **environment variable**: a named value that the operating system hands to every program you start from that terminal.

### Environment variables

Set one in your terminal (macOS, Linux and WSL):

```bash
export GITHUB_TOKEN="ghp_abc123realkeyhere"
echo $GITHUB_TOKEN
```

It lasts until you close that terminal window. Read it from Python with `os.environ`:

```python
import os

import httpx

token = os.environ["GITHUB_TOKEN"]   # raises KeyError if it isn't set
response = httpx.get(
    "https://api.github.com/user",
    headers={"Authorization": f"Bearer {token}"},
)
print(response.status_code, response.json().get("login"))
```

Using `os.environ["NAME"]` (square brackets) is deliberate: if the variable is missing, your program fails immediately with a clear `KeyError` instead of sending a request with no key and getting a confusing 401 later. Use `os.environ.get("NAME", "default")` only for settings that genuinely have a sensible default, like a log level. Never for a secret.

This idea, that configuration (anything that changes between your laptop, a teammate's laptop and a production server) lives in the environment rather than the code, is one of the principles in the well-known [Twelve-Factor App](https://12factor.net/config) guidelines.

### .env files and python-dotenv

Typing `export` in every new terminal gets old fast. The common solution is a file named `.env` in your project folder:

```text
# .env (never commit this file)
GITHUB_TOKEN=ghp_abc123realkeyhere
ANTHROPIC_API_KEY=sk-ant-api03-abc123realkeyhere
```

The [python-dotenv](https://pypi.org/project/python-dotenv/) package reads that file and copies its values into `os.environ`:

```bash
uv add python-dotenv
```

```python
import os

from dotenv import load_dotenv

load_dotenv()   # reads .env from the current folder (or a parent), if one exists

token = os.environ["GITHUB_TOKEN"]
```

By default `load_dotenv()` won't overwrite a variable that's already set in your terminal, so a real environment variable always wins over the file. That's what you want on a server, where secrets are usually provided as real environment variables and there is no `.env` file at all.

### Keep .env out of Git

A `.env` file is only safe if Git never sees it. Add it to `.gitignore` *before* you create it:

```text
# .gitignore
.env
.venv/
__pycache__/
```

Then confirm Git is ignoring it:

```bash
git status --ignored
git check-ignore -v .env
```

`git check-ignore` should print the `.gitignore` line that matches. If `.env` appears under "Untracked files" in plain `git status`, stop and fix your `.gitignore` first.

So your teammates (and future you) know which variables the project needs, commit a `.env.example` file with the names but fake values:

```text
# .env.example (safe to commit)
GITHUB_TOKEN=your-token-here
```

<div class="lesson-note lesson-note--critical" markdown="1">

#### If you leak a key, revoke it first

If a real key ever ends up in a commit, a screenshot, a chat or a public paste, **revoke it immediately** in the provider's dashboard and create a new one. Deleting the commit is not enough; copies of public repositories are scraped within minutes. Revoke first, clean up the history second. GitHub's push protection may block some pushes containing known key formats, but treat that as a safety net, not a plan.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read GitHub's [Ignoring files](https://docs.github.com/en/get-started/git-basics/ignoring-files) guide to understand how `.gitignore` patterns work, including the global ignore file.
   - Set up a global gitignore that includes `.env`, so you're protected in every repository on your machine.
1. Read the [python-dotenv page on PyPI](https://pypi.org/project/python-dotenv/), focusing on "Getting Started" and the section about `.env` file syntax.
1. Read [the Twelve-Factor App's page on config](https://12factor.net/config). It's short, and it explains *why* configuration belongs in the environment.
1. Read GitHub's [Managing your personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens), then practice the whole workflow.
   - Create a fine-grained personal access token with read-only access to public repositories and a short expiration.
   - In a new project, add `.env` to `.gitignore`, create `.env` with `GITHUB_TOKEN=...`, and commit a `.env.example`.
   - Write a script that loads the token with python-dotenv and calls `https://api.github.com/user` to print your login name. Check the `x-ratelimit-limit` header: authenticated requests get a much higher limit than the anonymous ones from the last lesson.
   - Run `git status` and `git log -p` and confirm the real token appears nowhere.
   - When you're done, revoke the token in GitHub's settings. Practicing revocation now means you'll know where the button is when it matters.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- GitHub's [About secret scanning](https://docs.github.com/en/code-security/secret-scanning/introduction/about-secret-scanning) and [About push protection](https://docs.github.com/en/code-security/secret-scanning/introduction/about-push-protection) explain the automated checks that catch some leaked keys.
- GitHub's [Removing sensitive data from a repository](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository) covers rewriting history after a leak, once you've revoked the key.
