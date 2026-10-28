### Introduction

A one-word change to a prompt can fix one bug and quietly create three more. If prompts live as strings scattered through your code, nobody knows which version is running or when behavior changed. This lesson treats prompts like code: stored in files, versioned in Git, reviewed in pull requests and tested automatically.

You already run ruff and pytest in GitHub Actions, and in Evaluating RAG and Catching Regressions you added an eval job that compares against a saved baseline. Here you'll take that further and build the kind of eval gate a production team relies on: it runs a small eval on every pull request, scores the main branch the same way in the same job, and fails the build when the score drops, so a change that makes your app worse can't be merged by accident.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why prompts need version control.
- Storing prompts as files and loading them by name and version.
- Logging the prompt version with every trace.
- Prompt management tools and when they help.
- A GitHub Actions workflow that fails the build on an eval drop.
- Keeping CI evals fast, cheap and stable.
- Handling secrets and pull requests from forks.

### Prompts are code

A prompt changes your app's behavior as much as any function does. Swap "summarize" for "briefly summarize" and your average answer may lose half its length. Add one example to a classifier prompt and its labels shift. Yet prompts often get treated as text that anyone can tweak without review: pasted into a string in the middle of a function, edited in a hurry, never tested.

Treating prompts as code means three habits:

1. **They live in version control.** Every change is a commit with an author, a date and a message, so you can answer "what changed on Tuesday?" with `git log prompts/`.
1. **They're reviewed.** A prompt change goes through a pull request like any other change, and the reviewer sees a diff of exactly which words moved.
1. **They're tested.** The pull request runs your eval, and the numbers sit next to the diff. Nobody has to guess whether "more concise" helped.

The rest of this lesson builds each habit.

### Storing prompts as files

Put each prompt in its own file in a `prompts/` folder, and load it by name. A TOML file works well because it can hold the prompt text plus a few settings, and Python 3.11 and later can read it with the standard library's `tomllib`:

```toml
# prompts/triage.toml
version = 3
description = "Sort a support ticket into one queue."
template = """
Sort this support ticket into exactly one queue: billing, bug, feature or other.

<ticket>
{ticket}
</ticket>

Answer with the queue name only.
"""
```

And a small loader:

```python
# src/prompts.py: load prompts from files by name, with a version you can log.
import hashlib
import tomllib
from dataclasses import dataclass
from pathlib import Path

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"


@dataclass(frozen=True)
class Prompt:
    name: str
    version: int
    template: str

    @property
    def hash(self) -> str:
        # A fingerprint of the exact text. It changes even if someone forgets to bump `version`.
        return hashlib.sha256(self.template.encode("utf-8")).hexdigest()[:8]

    def render(self, **values: str) -> str:
        return self.template.format(**values)


def load_prompt(name: str) -> Prompt:
    data = tomllib.loads((PROMPT_DIR / f"{name}.toml").read_text(encoding="utf-8"))
    return Prompt(name=name, version=data["version"], template=data["template"])
```

Your app code then says `prompt = load_prompt("triage")` and `prompt.render(ticket=text)`, and never contains prompt text itself. Every Git commit now records exactly which prompt shipped. The `version` number is for humans ("we're on triage v3"); the `hash` is for machines, and catches the edit where someone changed the text but forgot to bump the number.

One gotcha: `str.format` treats curly braces as placeholders, so a prompt that contains literal JSON braces needs them doubled (`{{` and `}}`).

### Log the prompt version with every trace

When a trace looks wrong, the first question is "which prompt produced this?" Make sure the answer is in the trace. In Logging and Tracing you added attributes to each model-call span or JSONL record; add two more:

```python
trace["prompt"] = f"{prompt.name}@v{prompt.version}"   # "triage@v3"
trace["prompt_hash"] = prompt.hash                       # "9f2c41ab"
```

Now you can filter production traces by prompt version, compare error rates before and after a release, and turn a bad trace into a new eval case knowing exactly which prompt failed it. Add the Git commit hash of the deploy too if your platform exposes it, as most do through an environment variable.

### Do you need a prompt management tool

Tools like Langfuse prompt management store prompt versions outside your code, in a web app. You fetch the prompt at runtime by name and a label such as `production` or `staging`, and moving the `production` label to a new version changes the live prompt without a deploy.

That helps when non-engineers (a support lead, a domain expert) edit prompts, or when a team wants to roll a prompt back in seconds. The costs are real, though: one more service that can be down, prompt changes that skip code review unless you add a process for it, and a gap between the prompt in Git and the prompt in production.

For a solo project or a small team, files in Git are enough. They get review, history and CI for free. Reach for a prompt tool when you have a specific need that files can't meet, and when you do, keep the eval gate: run the eval against a new prompt version before it gets the `production` label.

### A workflow that fails on a score drop

A quick recap from Linting, Formatting and CI: GitHub Actions runs **workflows**, YAML files in `.github/workflows/`. Each workflow says *when* to run (its trigger events, such as `pull_request`) and *what* to run (jobs made of steps). A step that exits with a non-zero code fails the job, a failed job shows a red cross on the pull request, and if you mark the check as required in your branch protection settings, the merge button stays locked. Actions is free for public repositories.

The eval job in the RAG lesson compared the branch against a baseline file committed to the repo. That's cheap, but the baseline goes stale. Model providers update models behind the same name, judges drift, and a baseline from last month may differ from today's main branch for reasons that have nothing to do with your change. This workflow instead scores **both** the pull request and its base branch in the same job, on the same day, with the same model. It costs twice as much per run, which is why it only runs a small smoke set and only when relevant files change.

```yaml
# .github/workflows/prompt-evals.yml
name: prompt-evals

on:
  pull_request:
    paths: ["prompts/**", "src/**", "evals/**"]   # 1. only when behavior could change
  schedule:
    - cron: "0 6 * * *"                           # 2. full eval set nightly at 06:00 UTC
  workflow_dispatch:                              #    plus a manual "Run workflow" button

concurrency:
  group: prompt-evals-${{ github.ref }}
  cancel-in-progress: true                        # 3. a new push cancels the stale run

permissions:
  contents: read

jobs:
  eval:
    # 4. Pull requests from forks can't read secrets, so skip them instead of failing.
    if: github.event_name != 'pull_request' || github.event.pull_request.head.repo.full_name == github.repository
    runs-on: ubuntu-latest
    timeout-minutes: 20
    defaults:
      run:
        shell: bash                               # 5. turns on pipefail, so `| tee` can't hide a failure
    env:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      EVAL_SET: ${{ github.event_name == 'pull_request' && 'smoke' || 'full' }}
    steps:
      - uses: actions/checkout@v7
        with:
          fetch-depth: 0                          # 6. fetch the base branch too, not just this commit
      - uses: astral-sh/setup-uv@v10.3.3
      - run: uv sync --locked

      - name: Eval this branch
        run: uv run python -m evals.run --set "$EVAL_SET" --out "$RUNNER_TEMP/head.json"

      - name: Eval the base branch in the same job
        if: github.event_name == 'pull_request'
        run: |
          git worktree add "$RUNNER_TEMP/base" "origin/${{ github.base_ref }}"
          cd "$RUNNER_TEMP/base"
          uv sync --locked
          uv run python -m evals.run --set smoke --out "$RUNNER_TEMP/base.json"

      - name: Gate on a drop versus base
        if: github.event_name == 'pull_request'
        run: uv run python -m evals.gate "$RUNNER_TEMP/head.json" --base "$RUNNER_TEMP/base.json" --max-drop 0.05 --floor 0.80 | tee -a "$GITHUB_STEP_SUMMARY"

      - name: Gate on the floor (nightly)
        if: github.event_name != 'pull_request'
        run: uv run python -m evals.gate "$RUNNER_TEMP/head.json" --floor 0.80 | tee -a "$GITHUB_STEP_SUMMARY"

      - uses: actions/upload-artifact@v7
        if: always()                              # 7. keep the results even when the gate fails
        with:
          name: eval-results
          path: ${{ runner.temp }}/*.json
```

Walking through the numbered comments:

1. The `paths` filter skips the eval for pull requests that only touch docs or the README, which saves money. If you make this check required in branch protection, note that a skipped workflow never reports, so either drop the filter or make sure every pull request that can be merged triggers it.
1. `schedule` runs the full eval set every night on the main branch. Pull requests get a quick smoke set of 20 to 50 cases; the nightly run catches what the small set misses, including drift in the model itself.
1. `concurrency` cancels a run that's still going when you push a new commit to the same branch, so you don't pay for evals of code that's already outdated.
1. The `if:` on the job skips pull requests opened from forks. GitHub doesn't give fork pull requests your secrets, so the eval would fail with an authentication error that tells the contributor nothing.
1. By default, GitHub runs steps with `bash -e`, which ignores a failure in the middle of a pipe. `tee` would succeed and hide the gate's exit code. Setting `shell: bash` explicitly runs `bash -eo pipefail`, so the gate's failure fails the step.
1. `actions/checkout` normally fetches only one commit. `fetch-depth: 0` fetches everything, so `git worktree add` can check out the base branch in a second folder next to your code.
1. `always()` uploads the result files even after a failure, so you can download them from the run page and see which cases broke.

The `evals.run` module is your own script, like `run_evals.py` from the RAG lesson. It runs each case, grades it, and writes a file shaped like `{"prompt": "triage@v3", "cases": {"t01": 1, "t02": 0, ...}}`. Notice that the base branch is evaluated with *its own* code and cases. A pull request that adds new cases can't be compared on those, so the gate compares only the cases both runs share.

### The gate script

The gate is what turns two result files into a pass or a fail. It writes Markdown, which `tee -a "$GITHUB_STEP_SUMMARY"` appends to the run's summary page, so reviewers see the score without digging through logs.

```python
# evals/gate.py: fail CI when the eval score drops.
import argparse
import json
import random
import sys


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)["cases"]  # {"case_id": 1 or 0, ...}


parser = argparse.ArgumentParser()
parser.add_argument("head")
parser.add_argument("--base")
parser.add_argument("--max-drop", type=float, default=0.05)
parser.add_argument("--floor", type=float, default=0.0)
args = parser.parse_args()

head = load(args.head)
score = sum(head.values()) / len(head)
print(f"## Eval gate\n\nThis branch: **{score:.1%}** on {len(head)} cases (floor {args.floor:.0%})\n")
failed = score < args.floor

if args.base:
    base = load(args.base)
    shared = sorted(set(head) & set(base))  # only cases both runs scored
    diffs = [head[c] - base[c] for c in shared]
    change = sum(diffs) / len(diffs)
    random.seed(0)  # same data, same interval, every run
    boots = sorted(sum(random.choices(diffs, k=len(diffs))) / len(diffs) for _ in range(2000))
    print(f"Change vs base on {len(shared)} shared cases: **{change:+.1%}** "
          f"(95% CI {boots[50]:+.1%} to {boots[1949]:+.1%})\n")
    for c in shared:
        if head[c] < base[c]:
            print(f"- broke: `{c}`")
    failed = failed or change < -args.max_drop

print("\n**FAIL**" if failed else "\n**PASS**")
sys.exit(1 if failed else 0)  # a non-zero exit code fails the step
```

This is a **paired comparison**, the idea from Eval Statistics: because both runs score the same cases, you look at the per-case difference, which is much less noisy than comparing two separate averages. The bootstrap confidence interval doesn't decide the gate, but it tells the reviewer how much to trust the number. A change of -4% with an interval from -12% to +4% says "probably noise, but look at the broken cases." The `broke:` lines name exactly which cases to read.

### Keeping CI evals fast and stable

An eval gate that's slow, expensive or flaky gets switched off within a month. Some habits keep it useful:

- **Small set on pull requests, full set nightly.** Choose 20 to 50 smoke cases that cover your main input types and your known past failures. Keep the full set for the nightly run and before releases.
- **Set the tolerance from measured noise.** Run the smoke set twice on the same code and see how far the score moves. If it moves 3 points between identical runs, a `--max-drop` of 0.02 will fail innocent pull requests. Start around 5 points and adjust.
- **Rerun flaky cases.** If a case passes some runs and fails others on the same code, run it three times and count the majority, or fix the case. A flaky case teaches everyone to ignore red builds.
- **Use the cheap model for judges where you've validated it.** If your judge's TPR and TNR on the [cheap model](#/models) are as good as on the capable one, CI should use the cheap one.
- **Cap the time.** `timeout-minutes` stops a hung job before it burns an hour of runner time and API credit.

Pin your actions to versions, as in the workflow above, so a new release can't change your CI without a commit. For extra safety, pin them to a full commit SHA, which is what the setup-uv README recommends.

### Secrets and pull requests from forks

Add your API key in GitHub under **Settings → Secrets and variables → Actions → New repository secret**, named `ANTHROPIC_API_KEY`, and read it in the workflow with `${{ secrets.ANTHROPIC_API_KEY }}`. Never write the key into the workflow file. GitHub masks secret values in logs, but your own scripts should still never print them.

Pull requests from forks get no secrets by default, which is a safety feature: otherwise anyone could open a pull request that sends your key to their server. That's why the workflow skips fork pull requests. You'll see advice to use the `pull_request_target` trigger to get around it. Don't, unless you deeply understand it: it runs with your secrets, and combined with checking out the pull request's code it lets a stranger's code read them. For an open-source project, a maintainer can instead review the change and rerun the eval from a branch in the main repository.

Also give the key in CI its own workspace and a low spending limit in your provider's console, so a runaway loop costs dollars, not hundreds.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Work through the [GitHub Actions quickstart](https://docs.github.com/en/actions/get-started/quickstart) to create your first workflow, if you didn't in Linting, Formatting and CI.
   - Then browse the [GitHub Actions docs](https://docs.github.com/en/actions) for the reference pages on [events that trigger workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows) (read `pull_request` and `schedule`) and [workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax) (read `on.<event>.paths`, `concurrency`, `jobs.<job_id>.if` and `defaults.run.shell`). Together they explain every line of the workflow above.
1. Read [Using secrets in GitHub Actions](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets) so your eval job can call a model without exposing your key.
   - Then skim the [secure use reference](https://docs.github.com/en/actions/reference/security/secure-use) for its warnings about `pull_request_target` and untrusted input.
1. Read the [promptfoo GitHub Action guide](https://www.promptfoo.dev/docs/integrations/github-action/) to see a ready-made eval-on-every-PR setup that posts a before-and-after comparison as a pull request comment.
   - If you haven't used promptfoo before, skim the [promptfoo introduction](https://www.promptfoo.dev/docs/intro/) first. Compare what it gives you with the hand-written gate in this lesson.
1. Read the [Langfuse prompt management overview](https://langfuse.com/docs/prompt-management/overview) to see what a dedicated prompt tool adds over files in Git, and note which of its features you'd actually need.
1. Practice: in one of your earlier project repos, move every prompt into a `prompts/` folder with a loader like the one above, and log the prompt name, version and hash in your traces.
   - Add the workflow and gate from this lesson, with a smoke set of at least 20 cases. Run it twice on the same commit and set `--max-drop` from the difference you see.
   - Mark the check as required in your branch protection settings ([about protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches) explains how).
   - Open a pull request that makes a prompt deliberately worse and confirm CI fails, with the broken cases listed in the run summary.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [What three habits does treating prompts as code involve?](#prompts-are-code)
- [Why store a hash of the prompt text as well as a version number?](#storing-prompts-as-files)
- [What do you gain by logging the prompt version with every trace?](#log-the-prompt-version-with-every-trace)
- [When is a prompt management tool worth it, and what does it cost you?](#do-you-need-a-prompt-management-tool)
- [Why evaluate the base branch in the same job instead of comparing against a committed baseline?](#a-workflow-that-fails-on-a-score-drop)
- [How should you choose the tolerance for a score drop?](#keeping-ci-evals-fast-and-stable)
- [Why don't pull requests from forks get your secrets, and why shouldn't you work around it with pull_request_target?](#secrets-and-pull-requests-from-forks)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [What We Learned from a Year of Building with LLMs](https://applied-llms.org/) includes practical advice on evals, prompt changes and operating LLM apps.
- [promptfoo assertions and metrics](https://www.promptfoo.dev/docs/configuration/expected-outputs/) lists the built-in checks you can use in an eval config.
- [uv's GitHub Actions guide](https://docs.astral.sh/uv/guides/integration/github/) covers caching and Python versions for `setup-uv`, which can make your CI runs noticeably faster.
- [GitHub's workflow commands reference](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands) explains `GITHUB_STEP_SUMMARY` and other ways a step can talk back to the run page.
