### Introduction

Every RAG system starts with documents, and real documents are rarely clean text. They arrive as PDFs with page numbers in the footer, web pages wrapped in menus and cookie banners, Word files full of tables, and scans that are just photos of paper. Whatever your parser gets wrong, your search can't fix later. A table that turns into a jumble of numbers can't answer "How much is the Team plan?", and a page header repeated on every chunk drowns out the words that matter.

In Long Context and Context Engineering you pulled raw text out of a PDF with pypdf and saw how messy it was. This lesson does the job properly. You'll learn which tool to pick for each format, how to keep headings and tables intact, which metadata to keep so you can cite pages later, and how to inspect your output before you trust it. You'll finish with a script that turns a folder of mixed files into clean Markdown and JSON records, ready for the next lesson, Chunking and Vector Databases.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why parsing quality limits retrieval quality.
- What a parsed record should contain, and why page and section matter for citations.
- How to choose a parser for PDFs, HTML, Word files and scans, and which licenses to watch.
- How to keep headings and tables, and drop headers and footers, with pdfplumber.
- How to turn a folder of mixed files into records the chunking lesson can use.
- When to use OCR, and when to send a page straight to a vision model.
- How to inspect parser output and spot the common failure modes.

### Why parsing matters

**Parsing** means turning a file into text your program can work with. For a plain `.txt` file that's just reading it. For everything else, the parser has to reconstruct something the file never stored directly.

A PDF is the hardest case. A PDF isn't a document of paragraphs. It's a set of drawing instructions: "put the letter R at these coordinates, in this font, at this size." There is no "paragraph," "heading" or "table" inside it, only characters and lines placed on a page. A parser has to guess the reading order and structure from positions and font sizes. Here is what pypdf returns for the second page of a small test handbook used in this lesson:

```text
ACME Customer Handbook - Internal
Page 2 of 2
3 Plans and prices
 Plan
Price
Seats
Starter
$10
1
...
```

The running header and the page number come first, the heading looks like any other line, and the table has become one value per line. A chunk made from this text says "Starter $10 1 Team $45 5," and nothing links a price to a plan. Good parsing aims for three things:

1. **Clean text.** Navigation, boilerplate, headers, footers and page numbers are removed.
1. **Structure kept.** Headings stay headings and tables stay tables, so chunks can follow sections and keep rows whole.
1. **Location kept.** You know which file, page and section each piece came from.

### What a parsed record holds

Have every parser in your pipeline produce the same shape of output: a list of **records**, one per section of a document (or per section per page for PDFs). A record is a plain dictionary you can save as one line of **JSONL** (JSON Lines: a text file with one JSON object per line).

```json
{"source": "handbook.pdf", "page": 2, "section": "3 Plans and prices",
 "text": "| Plan | Price | Seats |\n| --- | --- | --- |\n| Starter | $10 | 1 |...",
 "position": 2, "parser": "pdfplumber", "parsed_on": "2026-10-28"}
```

Each field earns its place:

- **`source`** is the file name or URL. Citations and filters need it.
- **`page`** is the page number for PDFs and `null` for formats without pages. In Citations and Grounding you'll show "handbook.pdf, page 2" next to an answer, which only works if the page survives from here.
- **`section`** is the nearest heading. It tells a reader where a passage sits, and it makes a useful prefix when you embed the chunk.
- **`position`** keeps records in document order, so you can rebuild the document or fetch a record's neighbors.
- **`parser`** and **`parsed_on`** record how and when you parsed the file. When you switch tools later, you'll know which records came from the old one and need re-parsing.

Once every format produces this shape, the rest of the pipeline doesn't care where text came from.

### Choosing a parser

There's no single best parser. Pick by format, by how complex the layout is, and by license. A **license** is the legal terms for using someone's code, and some open-source licenses place conditions on how you ship your own software.

| Format | Start with | Reach for this when it isn't enough |
| --- | --- | --- |
| Digital PDF (has a text layer) | **pdfplumber** (MIT): characters with positions and font sizes, plus table detection. **pypdf** (BSD) for plain text only. | **Docling** (MIT): a layout model and a table model that rebuild reading order and tables, with OCR built in. |
| HTML | **trafilatura** (Apache 2.0): keeps the main content and drops menus, ads and footers. | **BeautifulSoup** (MIT), when you know the page's structure, for example your own docs site where everything sits in `<main>`. |
| Word, PowerPoint, Excel | **MarkItDown** (MIT, from Microsoft): converts many formats to Markdown. | **Docling** or **Unstructured** (Apache 2.0), which label each element as a title, paragraph or table. |
| Markdown, text | Read it directly. | |
| Scanned PDF or image | **OCRmyPDF** (MPL 2.0) with **Tesseract** (Apache 2.0) to add a text layer, then parse as normal. | A vision-capable model, page by page. |

<div class="lesson-note lesson-note--warning" markdown="1">

#### Watch the AGPL license on PyMuPDF

**PyMuPDF** (imported as `fitz` or `pymupdf`) and its `pymupdf4llm` helper are fast and popular, and you'll see them in many tutorials. They're dual-licensed: **AGPL-3.0** or a paid commercial license from Artifex. The AGPL says that if you distribute your program, *or let people use it over a network*, you must publish your program's source code under the AGPL too. For a personal learning project that's fine. At a company, check with someone before you add it. Many teams can't ship AGPL code in a closed-source web service. This lesson uses MIT- and Apache-licensed tools so you never have to ask.

</div>

Heavier isn't always better. Docling and Unstructured download machine-learning models and can take seconds per page on a laptop. pdfplumber takes milliseconds. Start light, look at the output, and upgrade only for the documents that need it.

### Parsing PDFs with pdfplumber

pdfplumber gives you every character on a page with its position and font size. That's enough to solve three problems from the pypdf output above:

- **Tables.** `page.find_tables()` finds ruled tables, and you can remove their characters from the body text and write them out as Markdown tables instead.
- **Headings.** A line set in a clearly larger font than the body is probably a heading.
- **Headers and footers.** A line that appears on most pages, like "Page 2 of 9" once you ignore the digits, is a running header or footer.

```python
# parse_pdf.py: turn a PDF into section records with pdfplumber (MIT license)
import re
import unicodedata
from collections import Counter
from statistics import median

import pdfplumber


def table_to_markdown(rows: list[list[str | None]]) -> str:
    rows = [[(cell or "").replace("\n", " ").strip() for cell in row] for row in rows]
    lines = ["| " + " | ".join(rows[0]) + " |", "|" + " --- |" * len(rows[0])]
    return "\n".join(lines + ["| " + " | ".join(row) + " |" for row in rows[1:]])


def read_page(page) -> list[tuple[float, str, float]]:
    """Return (top, text, font_size) for each line and table, top to bottom."""
    tables = page.find_tables()
    boxes = [t.bbox for t in tables]                      # (x0, top, x1, bottom)

    def not_in_table(obj) -> bool:                        # keep chars outside every table
        x, y = (obj["x0"] + obj["x1"]) / 2, (obj["top"] + obj["bottom"]) / 2
        return not any(x0 <= x <= x1 and t <= y <= b for x0, t, x1, b in boxes)

    lines = page.filter(not_in_table).extract_text_lines(return_chars=True)
    # NFKC turns ligature characters such as "ﬁ" back into plain "fi".
    items = [(ln["top"], unicodedata.normalize("NFKC", ln["text"]).strip(),
              median(c["size"] for c in ln["chars"]))
             for ln in lines if ln["text"].strip()]
    items += [(t.bbox[1], "\n" + table_to_markdown(t.extract()) + "\n", 0.0) for t in tables]
    return sorted(items)


def shape(text: str) -> str:
    return re.sub(r"\d+", "#", text)                     # "Page 2 of 9" -> "Page # of #"


def parse_pdf(path: str) -> list[dict]:
    with pdfplumber.open(path) as pdf:
        pages = [read_page(page) for page in pdf.pages]

    # Running headers and footers: the same line shape on most pages.
    seen = Counter(s for items in pages for s in {shape(text) for _, text, _ in items})
    repeated = {s for s, n in seen.items() if n >= max(2, 0.6 * len(pages))}
    # Headings: lines in a clearly bigger font than the body text.
    sizes = [size for items in pages for _, _, size in items if size]
    body_size = median(sizes) if sizes else 0             # 0 for a scanned PDF: no text at all

    records, section = [], ""
    for page_no, items in enumerate(pages, start=1):
        buffer: list[str] = []
        for _, text, size in items:
            if shape(text) in repeated:
                continue                                  # drop headers and footers
            if size >= 1.25 * body_size:                  # a heading starts a new section
                if buffer:
                    records.append({"page": page_no, "section": section, "text": "\n".join(buffer).strip()})
                section, buffer = text, []
            else:
                buffer.append(text)
        if buffer:                                        # a section can continue onto the next page
            records.append({"page": page_no, "section": section, "text": "\n".join(buffer).strip()})
    return records
```

Walk through the important parts:

- **`page.filter(not_in_table)`** returns a copy of the page without the table's characters, so table cells don't appear twice. The tables come back as Markdown and get sorted into place by their `top` position.
- **The repeated-line rule** needs a line to appear on at least two pages and on 60% of them. Replacing digits with `#` makes every "Page N of M" look the same.
- **The heading rule** compares each line's median font size with the median of the whole document. It's a heuristic: a guess that's right most of the time. Headings that are bold but not bigger slip through, and the Assignment asks you to handle them.
- **A new record starts at every heading and every page**, so each record has exactly one page number, and a section that spans two pages becomes two records with the same `section`.

### Turning every file into records

The second file sends each file to the right parser, adds the shared metadata and writes two outputs: `records.jsonl` with full metadata, and one Markdown file per document in `docs/`, which is exactly what the chunking lesson's `ingest.py` reads. Install the tools with `uv add pdfplumber trafilatura "markitdown[docx]"`, put your files in `inbox/`, and run `uv run python parse_docs.py`.

```python
# parse_docs.py: parse every file in inbox/ into records.jsonl and docs/*.md
import json
import re
from datetime import date
from pathlib import Path

import trafilatura
from markitdown import MarkItDown

from parse_pdf import parse_pdf


def markdown_to_records(markdown: str) -> list[dict]:
    """Split Markdown into one record per heading. These formats have no pages."""
    records, section, lines = [], "", []
    for line in markdown.splitlines() + ["# end"]:       # sentinel flushes the last section
        if re.match(r"#{1,6} ", line):
            if "\n".join(lines).strip():
                records.append({"page": None, "section": section, "text": "\n".join(lines).strip()})
            section, lines = line.lstrip("#").strip(), []
        else:
            lines.append(line)
    return records


def parse_file(path: Path) -> tuple[str, list[dict]]:
    """Return (parser name, records) for one file, based on its extension."""
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return "pdfplumber", parse_pdf(str(path))
    if suffix in {".html", ".htm"}:
        # trafilatura keeps the main article and drops menus, cookie banners and footers.
        md = trafilatura.extract(path.read_text(encoding="utf-8"), output_format="markdown",
                                 include_tables=True) or ""
        return "trafilatura", markdown_to_records(md)
    if suffix in {".docx", ".pptx", ".xlsx"}:
        return "markitdown", markdown_to_records(MarkItDown().convert(str(path)).markdown)
    if suffix in {".md", ".txt"}:
        return "plain", markdown_to_records(path.read_text(encoding="utf-8"))
    raise ValueError(f"no parser for {path.name}")


def main(inbox: str = "inbox", out: str = "docs") -> None:
    Path(out).mkdir(exist_ok=True)
    with open("records.jsonl", "w", encoding="utf-8") as jsonl:
        for path in sorted(Path(inbox).iterdir()):
            try:
                parser, records = parse_file(path)
            except Exception as err:                      # one bad file shouldn't stop the run
                print(f"SKIP {path.name}: {err}")
                continue
            if sum(len(r["text"]) for r in records) < 100:
                print(f"WARN {path.name}: almost no text. Scanned? Try OCR or a vision model.")
            markdown = []
            for i, rec in enumerate(records):
                rec.update(source=path.name, position=i, parser=parser,
                           parsed_on=date.today().isoformat())
                jsonl.write(json.dumps(rec, ensure_ascii=False) + "\n")
                if i == 0 or rec["section"] != records[i - 1]["section"]:
                    markdown.append(f"## {rec['section'] or path.stem}")
                markdown.append(rec["text"])
            # Markdown with headings is exactly what the chunking lesson's ingest.py reads.
            Path(out, path.stem + ".md").write_text("\n\n".join(markdown) + "\n", encoding="utf-8")
            print(f"{path.name}: {len(records)} records via {parser}")


if __name__ == "__main__":
    main()
```

On the test handbook, the table now comes out as a real Markdown table under `## 3 Plans and prices`, and the header and page numbers are gone. Two things to notice. First, the **warning for near-empty output** is your scanned-PDF detector: an image-only PDF has no text layer, so pdfplumber returns nothing. Second, `docs/*.md` loses page numbers, because the chunking lesson's simple loader only reads Markdown. That's fine for now. In the Chat With Your Docs project you'll have `ingest.py` read `records.jsonl` instead, so every chunk inherits its record's `source`, `page` and `section`.

### Scanned pages, OCR and vision models

A scanned page is a picture. To get text out of it you have two choices.

**OCR** (optical character recognition) software recognizes letters in an image. Tesseract is the standard free engine. The easiest way to use it on PDFs is OCRmyPDF, which adds an invisible text layer to a scanned PDF (`ocrmypdf scan.pdf scan_ocr.pdf`) so the parser above works unchanged. OCR is free and runs locally, but it struggles with low-resolution scans, tables and handwriting, and it knows nothing about headings.

**A vision-capable model** can read the page image and write Markdown directly, headings and tables included. It handles messy scans, charts and odd layouts far better, but it costs money per page and can quietly make mistakes: skipping a line, "fixing" a number or inventing a cell. Images, PDFs and Audio introduced sending PDFs to a model. Here's the parsing version, which sends one page per request so page numbers stay exact:

```python
# vision_parse.py: transcribe scanned PDF pages with a vision-capable model
# uv add anthropic pypdf   (needs ANTHROPIC_API_KEY, and costs a little per page)
import base64
import io
import os
import sys

import anthropic
from pypdf import PdfReader, PdfWriter

from parse_docs import markdown_to_records

MODEL = os.environ.get("MIMIR_MODEL", "claude-haiku-5-5")
client = anthropic.Anthropic()

PROMPT = """Transcribe this page into Markdown. Keep the reading order, use # headings
for headings and Markdown tables for tables. Leave out running headers, footers and
page numbers. Output only the Markdown. If the page is blank, output nothing."""


def one_page_pdf(reader: PdfReader, index: int) -> str:
    """Copy a single page into its own small PDF, returned as base64 text."""
    writer = PdfWriter()
    writer.add_page(reader.pages[index])
    buffer = io.BytesIO()
    writer.write(buffer)
    return base64.standard_b64encode(buffer.getvalue()).decode()


def vision_parse(path: str) -> list[dict]:
    reader, records, section = PdfReader(path), [], ""
    for i in range(len(reader.pages)):                  # one call per page keeps page numbers exact
        response = client.messages.create(
            model=MODEL,
            max_tokens=8000,
            messages=[{"role": "user", "content": [
                {"type": "document", "source": {"type": "base64", "media_type": "application/pdf",
                                                "data": one_page_pdf(reader, i)}},
                {"type": "text", "text": PROMPT},
            ]}],
        )
        if response.stop_reason != "end_turn":            # e.g. "max_tokens": the page was cut off
            print(f"page {i + 1}: stopped with {response.stop_reason}", file=sys.stderr)
        markdown = "".join(block.text for block in response.content if block.type == "text")
        for rec in markdown_to_records(markdown):
            section = rec["section"] or section           # text above the first heading continues
            records.append({**rec, "page": i + 1, "section": section})  # the previous section
    return records


if __name__ == "__main__":
    for rec in vision_parse(sys.argv[1]):
        print(rec)
```

Anthropic's docs say each PDF page typically costs 1,500 to 3,000 text tokens plus image tokens, because every page is also sent as an image. With the [cheap model](#/models) that's a fraction of a cent per page. That's fine for a hundred scanned pages, but it adds up for a hundred thousand. A sensible rule: use a text parser for digital PDFs, OCR for clean scans in bulk, and a vision model for the pages the others get wrong. Save `parser="vision"` in those records so you can spot-check them.

Sending a whole PDF as a `document` block, with text and page images extracted for you, is a Claude feature. Other providers accept PDFs in a different shape or not at all, and most open vision models take only images, so there you render each page to an image first (see [On other providers](#on-other-providers)).

There's also a third option: don't parse at all. If a user asks about one 30-page report, sending the whole PDF with the question (as in Long Context and Context Engineering) is simpler and often better than RAG. Parse and index when you have more documents than fit in a prompt, or the same documents are queried over and over.

### Inspecting your output

Never index a parser's output you haven't read. Open `docs/*.md` for a few documents of each type and compare them with the originals side by side. These are the failures you'll meet most often:

- **Headers and footers.** Running titles, page numbers and "Confidential" stamps repeat in every chunk. Look for lines that appear many times in `records.jsonl`.
- **Multi-column layouts.** Line-based extraction reads straight across the page, so a two-column page gives you lines like "Refunds are issued to the Standard shipping takes." Crop each column with `page.crop((0, 0, page.width / 2, page.height))`, or switch that document to Docling, which detects columns.
- **Tables.** Tables without ruling lines often aren't detected, and merged cells shift columns. MarkItDown turns a Word table with no header row into a table with an empty header. Search your output for prices or numbers you know and check that each sits in the right row.
- **Ligatures and odd characters.** Many fonts draw "fi" and "fl" as a single character (a *ligature*), so "efficient" becomes "eﬃcient" and keyword search for it fails. `unicodedata.normalize("NFKC", text)` fixes those. Also watch for words hyphenated across line breaks ("infor-\nmation") and for gibberish from PDFs with broken font encodings, which usually need OCR.
- **Empty or near-empty output.** It usually means a scan, an image-only page or a password-protected file.

A cheap habit that catches most of this is a small table per file: number of records, total characters, characters per page and the most repeated lines. A file that's far off from its neighbors is worth opening.

### On other providers

Most of this lesson has nothing to do with any model provider. pdfplumber, trafilatura, MarkItDown, OCRmyPDF, the record format and the inspection habits work the same whatever model reads the result. Only `vision_parse.py` changes, because PDF input is where providers differ most. OpenAI also accepts a PDF directly, as an `input_file` content part with the file as base64 `file_data`, and like Claude it sends the model both the extracted text and an image of each page ([OpenAI's file inputs guide](https://developers.openai.com/api/docs/guides/pdf-files) shows the shape and the limits). Many other providers, and almost every open model, accept images but not PDFs. The approach that works everywhere is to render each page to a PNG yourself and send it as an image, which also keeps one call per page and exact page numbers. pdfplumber can render pages, so you need no new library. Here is the per-page call for a local open vision model, such as [Qwen3-VL in the Ollama library](https://ollama.com/library/qwen3-vl), through Ollama's [OpenAI-compatible API](https://docs.ollama.com/api/openai-compatibility); `prompt` is the same transcription prompt as in `vision_parse.py`:

```python
import base64, io, os
import pdfplumber
from openai import OpenAI  # uv add openai

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")  # local Ollama server
MODEL = os.environ.get("MIMIR_MODEL", "qwen3-vl:8b")

def transcribe_page(path: str, index: int, prompt: str) -> str:
    with pdfplumber.open(path) as pdf:  # render the page as a PNG image
        image = pdf.pages[index].to_image(resolution=150).original
    image.save(buffer := io.BytesIO(), format="PNG")
    url = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()
    reply = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": [
        {"type": "image_url", "image_url": {"url": url}}, {"type": "text", "text": prompt}]}])
    return reply.choices[0].message.content or ""
```

The same code works with OpenAI's vision models if you use `OpenAI()` and one of its model IDs. A local model costs nothing per page but is slower and makes more transcription mistakes than the hosted ones, so spot-check its records just as carefully. Record which model you used in the `parser` field, for example `"vision:qwen3-vl:8b"`.

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Read [pypdf's guide to extracting text](https://pypdf.readthedocs.io/en/stable/user/extract-text.html).
   - Read the whole page. It explains why PDF text extraction is hard in the first place (PDFs store glyph positions, not paragraphs), and lists the problems no library fully solves.
1. Read the [pdfplumber README](https://github.com/jsvine/pdfplumber).
   - Read "Extracting text," "Extracting tables" and "Table-extraction settings," and the "char properties" list (you'll need `fontname` in the practice task). Skim "Visual debugging," which draws what pdfplumber found onto the page image. It's the fastest way to see why a table was missed.
1. Skim the docs for the heavier tools so you know what they offer: the [Docling documentation](https://docling-project.github.io/docling/) and the [MarkItDown README](https://github.com/microsoft/markitdown).
   - For Docling, read the overview and the usage page. For MarkItDown, note the list of supported formats.
1. Read the [trafilatura quickstart](https://trafilatura.readthedocs.io/en/latest/quickstart.html).
   - Focus on the Python examples, `output_format` and the options for keeping tables and links.
1. Read Anthropic's [PDF support guide](https://platform.claude.com/docs/en/build-with-claude/pdf-support).
   - Read "Before you start," "How PDF support works" and "Estimate your costs," so you know how pages are billed before you send a scan to a model.
1. Practice: build the parsing pipeline from this lesson for a folder of real documents you'll use in Chat With Your Docs.
   - Collect at least six files: two digital PDFs (one with a table), one scanned PDF (scan a page with your phone and save it as a PDF), two web pages saved as HTML and one Word file.
   - Run `parse_docs.py`, then read every output file next to its original. Write a short `PARSING_NOTES.md` listing each failure you found and the fix you chose.
   - Extend the heading rule so bold lines at body size also count as headings (each pdfplumber character has a `fontname`, which contains "Bold" for bold fonts), and write a pytest test for it using a small PDF you generate or download.
   - Parse your scanned PDF two ways, with OCRmyPDF and with `vision_parse.py`, and compare them line by line against the original. Note which made fewer errors and what each one cost.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Why does a PDF give a parser so little to work with, and what three things should good parsing achieve?](#why-parsing-matters)
- [Which fields belong in a parsed record, and why must the page number survive parsing?](#what-a-parsed-record-holds)
- [Which tool would you start with for HTML, for Word files and for a complex PDF, and why should you be careful with PyMuPDF?](#choosing-a-parser)
- [How does the pdfplumber parser detect headings, tables and running headers?](#parsing-pdfs-with-pdfplumber)
- [What two outputs does the parsing script write, and how does it detect a scanned PDF?](#turning-every-file-into-records)
- [When would you use OCR, a vision model, or no parsing at all?](#scanned-pages-ocr-and-vision-models)
- [What goes wrong with multi-column pages and ligatures, and how do you fix each?](#inspecting-your-output)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [Tesseract's guide to improving OCR quality](https://tesseract-ocr.github.io/tessdoc/ImproveQuality.html) explains resolution, binarization and deskewing, the preprocessing steps that decide whether OCR output is usable.
- [The OCRmyPDF documentation](https://ocrmypdf.readthedocs.io/en/latest/) covers installing Tesseract and the options for deskewing and cleaning scans before OCR.
- [The Unstructured open-source docs](https://docs.unstructured.io/open-source/introduction/overview) show an element-based approach, where each piece of a document comes back labeled as a title, list item, table and so on.
- [The PyMuPDF license page](https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright) states the AGPL and commercial terms in Artifex's own words.
