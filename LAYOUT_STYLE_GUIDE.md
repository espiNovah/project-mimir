# Layout style guide

This guide keeps every lesson and project consistent, so learners always know where to look. It is adapted from [The Odin Project's layout style guide](https://github.com/TheOdinProject/curriculum/blob/main/LAYOUT_STYLE_GUIDE.md).

## Where files live

```text
curriculum/
  curriculum.json          # order of paths → sections → lessons (the site reads this)
  about.md                 # the About page
  <path>/<section>/<lesson>.md
```

- Folder and file names use `snake_case`.
- Project files start with `project_`, for example `foundations/git/project_hello_github.md`.
- A lesson only appears on the site once it is listed in `curriculum.json`. Each entry has an `id` (kebab-case, unique within its path), a `title`, a one-line `description`, the `file` path relative to `curriculum/`, and `"project": true` for projects.

## Lesson layout

Copy [templates/lesson-template.md](templates/lesson-template.md). Sections, in order:

1. `### Introduction`: what the lesson is about and why it matters.
1. `### Lesson overview`: up to 7 bullets naming what the learner will *learn about*.
1. Custom sections (`### Your heading`): the actual teaching, written in your own words. Short code examples are encouraged. This is what makes a lesson more than a reading list.
1. `### Assignment`: a numbered list of the resources to read or watch and the exercises to do, wrapped in `<div class="lesson-content__panel" markdown="1">`. Aim for 3–5 items. Say why each one is there, and which parts to read when not all of it is needed.
1. `### Additional resources` (optional): supplemental links, each with a sentence on what it adds. Leave the section out entirely if there are none.

## Project layout

Copy [templates/project-template.md](templates/project-template.md): `### Introduction`, an optional pre-assignment section, `### Assignment` (numbered requirements plus `#### Extra credit`), and an optional post-assignment section.

Every project ends up on GitHub with a README. Projects should require evidence that the thing works, such as tests, an eval score, or a demo, and not only that it exists.

## Headings

- Lessons start at `###`. The site renders the lesson title as the page heading, so never use `#` or `##`.
- `###` headings appear in the "On this page" sidebar, so keep them short and descriptive.
- No code in headings.

## Note boxes

Leave a blank line after the opening `<div>` and before the closing `</div>`, and always give the box a `####` title.

```markdown
<div class="lesson-note lesson-note--tip" markdown="1">

#### Title

Text.

</div>
```

Variants: `lesson-note` (info), `lesson-note--tip`, `lesson-note--warning`, `lesson-note--critical`.

## Links

- Use descriptive link text such as `[the FastAPI tutorial](…)`, never "click here".
- **Free resources only.** No paywalls, no required sign-ups where a free alternative exists, no affiliate links.
- Prefer, in order: official docs; well-known free courses and books; respected practitioner writing. Avoid SEO content farms.
- AI tooling changes fast. When you link versioned docs, check that they match current releases.

## Code

- Always give fenced code blocks a language, such as ` ```python ` or ` ```bash `.
- Examples default to Python and the Claude API, but stay provider-neutral in explanations.
- Never put a real API key in an example. Use `os.environ["ANTHROPIC_API_KEY"]`.

## Language

Use American English and plain, direct sentences. Write for someone who started from zero, and define jargon the first time it appears.
