# Contributing to Project Mímir

Thanks for helping. This curriculum only stays current because people fix it, and in AI it goes stale quickly.

## Ways to help

- Fix typos, unclear explanations or broken links.
- Suggest a better **free** resource for a lesson, and say why it beats the current one.
- Flag outdated content, such as a deprecated API, a renamed library or a moved doc.
- Write out a lesson that is still an outline (look for the "Outline lesson" box at the top). `python3 scripts/validate.py` prints how many outlines each path still has.
- Add or improve a practice exercise in [exercises/](exercises/).
- Help with the work planned in the [roadmap](ROADMAP.md).
- Propose a new lesson or project. Open an issue first so we can agree on where it fits.

## Workflow

1. Fork the repo and create a branch: `git checkout -b fix/rag-chunking-link`.
1. Make your change following the [layout style guide](LAYOUT_STYLE_GUIDE.md).
1. Preview locally (see [Run the site locally](README.md#run-the-site-locally)).
1. Run `python3 scripts/validate.py` (add `--links` to check every link). If you changed exercises, also run `python3 scripts/check_exercises.py`. CI runs the same checks.
1. Open a pull request that describes what you changed and why.

## Adding a lesson

1. Copy `templates/lesson-template.md` (or `project-template.md`) into the right folder under `curriculum/`.
1. Add an entry for it in `curriculum/curriculum.json`, in the position where it should appear.
1. Check that it renders and that every link works.

A lesson counts as written when it meets the definition in the [layout style guide](LAYOUT_STYLE_GUIDE.md#lesson-layout): explanation in your own words, runnable code where the topic is code, a practice step, and a knowledge check. Remove the "Outline lesson" box when it does.

Before you start on a lesson, open an issue (or comment on an existing one) so two people don't write the same lesson.

## Ground rules

- Resources must be free to access.
- Don't hard-code model names in lesson text. Link to [Current Models](curriculum/models.md) instead, and update that page when models change.
- Be kind in reviews and issues. Everyone here is learning.
