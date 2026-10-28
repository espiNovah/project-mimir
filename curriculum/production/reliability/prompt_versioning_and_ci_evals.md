<div class="lesson-note lesson-note--warning" markdown="1">

#### Outline lesson

This lesson has its key ideas and a full assignment, but the written explanation is still to come. Want to help write it? See the [contributing guide](https://github.com/espiNovah/project-mimir/blob/main/CONTRIBUTING.md).

</div>

### Introduction

A one-word change to a prompt can fix one bug and quietly create three more. If prompts live as strings scattered through your code, nobody knows which version is running or when behavior changed. This lesson treats prompts like code: stored in files, versioned in Git, reviewed in pull requests and tested automatically. You will set up continuous integration (CI), which means running checks automatically on every change, so a pull request that lowers your eval score can't be merged by accident.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why prompts need version control.
- Storing prompts as files and loading them by name and version.
- Prompt management tools and when they help.
- What CI is and how GitHub Actions runs it.
- Running evals on every pull request and failing on a score drop.
- Keeping CI evals fast, cheap and stable.

### Key ideas

- **Prompts are code.** They change your app's behavior as much as any function does, so they belong in version control. Store each prompt in its own file (for example `prompts/triage_v3.md` or a YAML file with the prompt and its settings) and load it by name. Every Git commit then records exactly which prompt shipped.
- **Log the prompt version with every trace.** When a trace looks wrong, you should be able to tell which prompt version produced it. Add a version or Git commit hash as an attribute on your model call spans.
- **Prompt management tools are optional.** Tools like Langfuse prompt management store versions outside the code and let non-engineers edit prompts with labels like `production` and `staging`. They help on teams; for a solo project, files in Git are enough.
- **CI runs your checks on every push.** GitHub Actions is free for public repos. A workflow file in `.github/workflows/` describes what to run (install with `uv`, run `pytest`, run evals) and when (on every pull request).
- **Gate merges on evals.** Run your eval set in CI and fail the job if the score drops below a threshold or below the main branch's score. Tools like promptfoo have a ready-made GitHub Action that posts a before-and-after comparison on the pull request.
- **Keep CI evals fast and stable.** Use a small, representative subset (20 to 50 cases) on every pull request and the full set nightly. LLM outputs vary, so set thresholds with a little slack, or run a flaky case several times. Use a cheap model for judges where you've validated it.
- **Secrets in CI go in the repo's secret store.** Add your API key as a GitHub Actions secret, never in the workflow file. Be careful with pull requests from forks, which by default cannot read your secrets.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Work through the [GitHub Actions quickstart](https://docs.github.com/en/actions/writing-workflows/quickstart) to create your first workflow.
   - Then browse the [GitHub Actions docs](https://docs.github.com/en/actions) for the pages on events (`pull_request`) and workflow syntax.
1. Read [Using secrets in GitHub Actions](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions) so your eval job can call a model without exposing your key.
1. Read the [promptfoo GitHub Action guide](https://www.promptfoo.dev/docs/integrations/github-action/) to see a complete eval-on-every-PR setup.
   - If you haven't used promptfoo before, skim the [promptfoo introduction](https://www.promptfoo.dev/docs/intro/) first. You can also run your own eval script in CI instead; the idea is the same.
1. Read the [Langfuse prompt management overview](https://langfuse.com/docs/prompt-management/overview) to see what a dedicated prompt tool adds over files in Git.
1. Practice: in one of your earlier project repos, move every prompt into a `prompts/` folder, then add a GitHub Actions workflow that runs your tests and a small eval subset on each pull request.
   - Open a pull request that makes a prompt deliberately worse and confirm CI fails.

</div>

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [What We Learned from a Year of Building with LLMs](https://applied-llms.org/) includes practical advice on evals, prompt changes and operating LLM apps.
- [promptfoo assertions and metrics](https://www.promptfoo.dev/docs/configuration/expected-outputs/) lists the built-in checks you can use in an eval config.
