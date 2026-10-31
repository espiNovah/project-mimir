# Project Mímir

A free, open-source, project-based curriculum that takes you from zero coding experience to a career building AI agents. It is modeled on [The Odin Project](https://www.theodinproject.com/).

**Start learning:** https://espinovah.github.io/project-mimir/

## What's inside

| Path | Focus |
| --- | --- |
| 01 · Foundations | Terminal, Git, Python, data tools, AI coding assistants, HTTP/APIs, how LLMs work, your first LLM app |
| 02 · AI Engineering Core | Prompt & context engineering, evals, structured outputs, classic ML, FastAPI + Postgres backends, RAG, TypeScript/React frontend |
| 03 · Agentic Systems | Agent loops, tool design, MCP, memory, frameworks, coding/browser agents, multi-agent, safety, agent evals |
| 04 · Production & LLMOps | Deployment, tracing, cost & latency, CI evals, security |
| 05 · ML Foundations (elective) | Math intuition, neural nets, serving and fine-tuning open models |
| 06 · Research Track (elective) | Math for research, reinforcement learning, planning, multi-agent theory, reading and reproducing papers. For a master's degree or research roles. Requires ML Foundations |
| 07 · Final Capstone | A real system for real users |
| 08 · Getting Hired | Portfolio, open source, interviews |

Each lesson follows the same layout: an introduction, a lesson overview, written explanation, an assignment built from the best **free** resources online, and optional additional resources. Projects come every few lessons, and each one goes on your GitHub.

## Repository layout

```text
index.html                 # the site (plain HTML/JS, no build step)
assets/                    # site CSS and JS
curriculum/
  curriculum.json          # order of paths → sections → lessons
  about.md
  <path>/<section>/*.md    # lesson and project files
templates/                 # starting points for new lessons and projects
scripts/validate.py        # structure + link checks (also run by GitHub Actions)
LAYOUT_STYLE_GUIDE.md      # how lessons are written
CONTRIBUTING.md
```

## Run the site locally

The site loads lesson files with `fetch`, so it needs a local web server. Opening `index.html` directly won't work.

```bash
git clone https://github.com/espiNovah/project-mimir.git
cd project-mimir
python3 -m http.server 8000
# open http://localhost:8000
```

## Publish with GitHub Pages

In the repo, go to **Settings → Pages**. Under **Build and deployment**, set Source to **Deploy from a branch**, then choose the `main` branch and the `/ (root)` folder. The site goes live at `https://<user>.github.io/project-mimir/`.

## Status

- **Foundations:** fully written lessons and projects.
- **All other paths:** structured outlines with curated resources and full project briefs. They will be written out to Foundations' depth over time. Contributions are welcome.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and the [layout style guide](LAYOUT_STYLE_GUIDE.md).

## License

- Code (site): [MIT](LICENSE)
- Curriculum content: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
