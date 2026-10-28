"""Check that the curriculum is consistent with the layout style guide.

Usage:
    python3 scripts/validate.py            # structure checks
    python3 scripts/validate.py --links    # also check every external link resolves
"""
import json
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CURRICULUM = ROOT / "curriculum"
LINK_RE = re.compile(r"\]\((https?://[^)\s]+)\)")
FENCE_RE = re.compile(r"^ *(`{3,}|~{3,}).*?^ *\1", re.M | re.S)
MODEL_ID_RE = re.compile(r"claude-(haiku|sonnet|opus|fable)-\d")
HEADING_RE = re.compile(r"^### (.+)$", re.M)
ANCHOR_LINK_RE = re.compile(r"\]\(#([a-z0-9-]+)\)")
OUTLINE_MARK = "#### Outline lesson"
PAGES = ("about.md", "models.md")  # standalone pages, not listed in curriculum.json
# Sites that block automated requests but are known to exist.
BOT_BLOCKERS = ("realpython.com", "openai.com", "medium.com", "coursera.org")


def slug(text):
    """Same rule as slug() in assets/js/app.js."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def check_lesson(lesson, text, prose):
    errors = []
    name = lesson["file"]
    if MODEL_ID_RE.search(prose):
        errors.append(f"{name}: hard-coded model ID in prose (link to #/models instead; IDs are fine in code blocks)")
    anchors = {slug(h) for h in HEADING_RE.findall(prose)}
    for a in ANCHOR_LINK_RE.findall(prose):
        if a not in anchors:
            errors.append(f"{name}: link to #{a}, but no ### heading has that anchor")
    if not lesson.get("project") and OUTLINE_MARK not in text and "### Knowledge check" not in text:
        errors.append(f"{name}: written lesson missing ### Knowledge check")
    return errors


def check_structure(manifest):
    errors = []
    listed = set()
    path_ids = {p["id"] for p in manifest["paths"]}
    for path in manifest["paths"]:
        for req in path.get("requires", []):
            if req not in path_ids:
                errors.append(f'{path["id"]}: requires unknown path "{req}"')
        ids = set()
        for section in path["sections"]:
            for lesson in section["lessons"]:
                where = f'{path["id"]}/{lesson["id"]}'
                if lesson["id"] in ids:
                    errors.append(f"{where}: duplicate lesson id in path")
                ids.add(lesson["id"])
                file = CURRICULUM / lesson["file"]
                listed.add(file)
                if not file.exists():
                    errors.append(f"{where}: missing file {lesson['file']}")
                    continue
                text = file.read_text(encoding="utf-8")
                prose = FENCE_RE.sub("", text)  # '#' inside code blocks is a comment, not a heading
                if re.search(r"^#{1,2} ", prose, re.M):
                    errors.append(f"{lesson['file']}: uses # or ## headings (lessons start at ###)")
                if "### Introduction" not in text:
                    errors.append(f"{lesson['file']}: missing ### Introduction")
                if "### Assignment" not in text:
                    errors.append(f"{lesson['file']}: missing ### Assignment")
                if lesson.get("project") and "#### Extra credit" not in text:
                    errors.append(f"{lesson['file']}: project missing #### Extra credit")
                errors += check_lesson(lesson, text, prose)
    for file in CURRICULUM.rglob("*.md"):
        if file.name not in PAGES and file not in listed:
            errors.append(f"{file.relative_to(CURRICULUM)}: not listed in curriculum.json")
    return errors


def check_url(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (link-check)"})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            return url, res.status
    except urllib.error.HTTPError as e:
        return url, e.code
    except Exception:
        return url, 0


def check_links():
    urls = sorted({u for f in CURRICULUM.rglob("*.md") for u in LINK_RE.findall(f.read_text(encoding="utf-8"))})
    errors = []
    with ThreadPoolExecutor(max_workers=12) as pool:
        for url, status in pool.map(check_url, urls):
            if status == 200 or (status == 403 and any(b in url for b in BOT_BLOCKERS)):
                continue
            errors.append(f"{status or 'ERR'} {url}")
    print(f"Checked {len(urls)} links.")
    return errors


def main():
    manifest = json.loads((CURRICULUM / "curriculum.json").read_text(encoding="utf-8"))
    errors = check_structure(manifest)
    if "--links" in sys.argv:
        errors += check_links()
    lessons = sum(len(s["lessons"]) for p in manifest["paths"] for s in p["sections"])
    print(f"{len(manifest['paths'])} paths, {lessons} lessons.")
    for p in manifest["paths"]:
        files = [CURRICULUM / l["file"] for s in p["sections"] for l in s["lessons"]]
        outlines = sum(1 for f in files if f.exists() and OUTLINE_MARK in f.read_text(encoding="utf-8"))
        print(f"  {p['id']:<12} {len(files):>3} lessons, {outlines:>3} still outlines")
    for e in errors:
        print("  ✗", e)
    print("OK" if not errors else f"{len(errors)} problem(s) found.")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
