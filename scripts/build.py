"""Generate the SEO-friendly static home page (index.html), sitemap.xml and robots.txt
from curriculum/curriculum.json.

Usage:
    python3 scripts/build.py           # write files
    python3 scripts/build.py --check   # exit 1 if the files are out of date (used by CI)
"""
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_URL = "https://espinovah.github.io/project-mimir/"
REPO_URL = "https://github.com/espiNovah/project-mimir"

TITLE = "Project Mímir: Free Curriculum to Learn AI Agents"
DESCRIPTION = (
    "Learn to build AI agents for free, from zero coding to job-ready. "
    "Python, LLMs, RAG, evals, MCP and agentic systems, with a real project every few lessons."
)
H1 = "Learn to build AI agents, from zero to hired"
LEAD = (
    "Project Mímir is a free, open-source curriculum for becoming an AI engineer. Written lessons, "
    "the best free resources on the internet, and a real project every few lessons that "
    "goes straight into your portfolio."
)

FAQ = [
    ("Is Project Mímir really free?",
     "Yes. Every lesson is free, and every linked resource is free to read or watch. The only cost is a few dollars of AI model usage for some projects, and free local models work for nearly everything."),
    ("Do I need coding experience to start?",
     "No. The Foundations path starts from zero: the terminal, Git, Python, how the web works and how language models work. If you already code, skim Foundations and use its projects to test yourself."),
    ("How long does it take to finish?",
     "The core paths take about 1,100 hours, roughly 12 to 18 months at 15 to 20 hours a week. Two optional electives, ML Foundations and the Research Track, add about 350 hours."),
    ("What jobs does it prepare me for?",
     "Applied AI roles: AI engineer, agent or automation engineer, forward-deployed or AI solutions engineer, and LLMOps engineer. The Research Track adds the theory needed for a master's degree or research work."),
    ("How is Project Mímir different from a course or a bootcamp?",
     "It follows the method of The Odin Project: one ordered path, written lessons that link the best free material instead of recording new lectures, and a project you build and publish on GitHub every few lessons."),
]

WHO = [
    ("AI Engineer", "Builds LLM features into products: retrieval, structured extraction, evals and APIs."),
    ("Agent Engineer", "Designs tools and agent loops that complete multi-step work on their own."),
    ("AI Solutions Engineer", "Works with customers to turn messy workflows into working AI systems."),
    ("Master's & research", "The Research Track covers the math, RL, planning and research skills a degree expects."),
]

e = html.escape


def lesson_count(path):
    lessons = [l for s in path["sections"] for l in s["lessons"]]
    return len(lessons), sum(1 for l in lessons if l.get("project"))


def json_ld(manifest):
    provider = {"@type": "Organization", "name": "Project Mímir", "url": SITE_URL, "sameAs": [REPO_URL]}
    graph = [
        {"@type": "WebSite", "@id": SITE_URL + "#website", "url": SITE_URL, "name": "Project Mímir",
         "description": DESCRIPTION, "inLanguage": "en"},
        {"@type": "Course", "@id": SITE_URL + "#course", "name": "Project Mímir", "url": SITE_URL,
         "description": LEAD, "provider": provider, "isAccessibleForFree": True,
         "inLanguage": "en", "educationalLevel": "Beginner",
         "teaches": ["Python", "Large language models", "Retrieval-augmented generation", "LLM evaluation",
                     "Model Context Protocol", "AI agents", "LLMOps", "Reinforcement learning"],
         "hasPart": [{"@type": "Course", "name": p["title"], "description": p["description"],
                      "provider": provider, "isAccessibleForFree": True} for p in manifest["paths"]]},
        {"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
    ]
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)


def render_index(manifest):
    path_items = []
    for i, p in enumerate(manifest["paths"]):
        total, projects = lesson_count(p)
        tag = ' <span class="tag optional">Elective</span>' if p.get("optional") else ""
        path_items.append(f"""        <li><a class="path-card" href="#/paths/{p['id']}" data-path="{p['id']}">
          <span class="num">{i:02d}</span>
          <div><h3>{e(p['title'])}{tag}</h3><p>{e(p['description'])}</p></div>
          <div class="meta"><span>{total} lessons · {projects} projects<br>~{p['hours']} hours</span><div class="progress"><i></i></div></div>
        </a></li>""")
    who = "\n".join(f'        <li><h3>{e(t)}</h3><p>{e(d)}</p></li>' for t, d in WHO)
    faq = "\n".join(f'        <details class="faq-item"><summary><h3>{e(q)}</h3></summary><p>{e(a)}</p></details>' for q, a in FAQ)
    first = manifest["paths"][0]
    total_lessons = sum(lesson_count(p)[0] for p in manifest["paths"])
    total_projects = sum(lesson_count(p)[1] for p in manifest["paths"])

    return f"""<!doctype html>
<!-- Generated by scripts/build.py from curriculum/curriculum.json. Edit the script, not this file. -->
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(TITLE)}</title>
  <meta name="description" content="{e(DESCRIPTION)}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{SITE_URL}">
  <meta name="theme-color" content="#ffd84d">
  <link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Project Mímir">
  <meta property="og:title" content="{e(TITLE)}">
  <meta property="og:description" content="{e(DESCRIPTION)}">
  <meta property="og:url" content="{SITE_URL}">
  <meta property="og:locale" content="en_US">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{e(TITLE)}">
  <meta name="twitter:description" content="{e(DESCRIPTION)}">
  <script type="application/ld+json">
{json_ld(manifest)}
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@100..125,400..900&family=JetBrains+Mono:wght@400;700&family=Public+Sans:ital,wght@0,400..800;1,400..800&display=swap">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css" media="(prefers-color-scheme: light)">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css" media="(prefers-color-scheme: dark)">
  <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  <header class="topbar">
    <div class="container topbar-inner">
      <a class="brand" href="#/">Project Mímir</a>
      <nav class="topnav" aria-label="Main">
        <a href="#/" data-nav="home">Paths</a>
        <a href="#/about" data-nav="about">About</a>
        <a href="{REPO_URL}" target="_blank" rel="noopener">GitHub</a>
      </nav>
    </div>
  </header>

  <main id="main" class="container" tabindex="-1">
    <div id="home">
      <section class="hero">
        <div class="eyebrow">Free · Open source · Project-based</div>
        <h1>{e(H1)}</h1>
        <p class="lead">{e(LEAD)}</p>
        <div class="actions">
          <a class="btn" href="#/paths/{first['id']}">Start with {e(first['title'])}</a>
          <a class="btn secondary" href="#/about">How it works</a>
        </div>
        <p class="hero-stats">{len(manifest['paths'])} paths · {total_lessons} lessons · {total_projects} portfolio projects</p>
      </section>

      <section aria-labelledby="paths-title">
        <h2 class="section-title" id="paths-title">The curriculum</h2>
        <ol class="paths">
{chr(10).join(path_items)}
        </ol>
      </section>

      <section class="home-block" aria-labelledby="who-title">
        <h2 class="section-title" id="who-title">Who it's for</h2>
        <ul class="who">
{who}
        </ul>
      </section>

      <section class="home-block" aria-labelledby="faq-title">
        <h2 class="section-title" id="faq-title">Frequently asked questions</h2>
        <div class="faq">
{faq}
        </div>
      </section>
    </div>
  </main>

  <footer class="footer">
    <div class="container">
      Project Mímir is free and open source, inspired by <a href="https://www.theodinproject.com/" target="_blank" rel="noopener">The Odin Project</a> (not affiliated).
      Found a broken link or a better resource? <a href="{REPO_URL}/blob/main/CONTRIBUTING.md" target="_blank" rel="noopener">Contribute on GitHub</a>.
    </div>
  </footer>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js" defer></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/dompurify/3.1.6/purify.min.js" defer></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js" defer></script>
  <script src="assets/js/app.js" defer></script>
</body>
</html>
"""


def render_sitemap():
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{SITE_URL}</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>
</urlset>
"""


def render_robots():
    return f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml\n"


def main():
    manifest = json.loads((ROOT / "curriculum" / "curriculum.json").read_text(encoding="utf-8"))
    outputs = {
        ROOT / "index.html": render_index(manifest),
        ROOT / "sitemap.xml": render_sitemap(),
        ROOT / "robots.txt": render_robots(),
    }
    if "--check" in sys.argv:
        stale = [p.name for p, text in outputs.items() if not p.exists() or p.read_text(encoding="utf-8") != text]
        if stale:
            print("Out of date (run python3 scripts/build.py):", ", ".join(stale))
            sys.exit(1)
        print("Generated files are up to date.")
        return
    for p, text in outputs.items():
        p.write_text(text, encoding="utf-8")
        print("wrote", p.relative_to(ROOT))


if __name__ == "__main__":
    main()
